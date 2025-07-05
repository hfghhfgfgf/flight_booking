from flask import Blueprint, request, jsonify, current_app, session
from app import db
from app.models import NguoiDung, NhomNguoiDung
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import logout_user, login_required, login_user, current_user
import requests
from oauthlib.oauth2 import WebApplicationClient
import secrets, json

auth_bp = Blueprint('auth', __name__)

google_client = None 

def init_oauth(app):
    global google_client
    google_client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])

@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'status': False,
                'message': 'Vui lòng nhập username và password'
            }), 400

        user = NguoiDung.query.filter_by(TenDangNhap=data['username']).first()

        if not user or not check_password_hash(user.MatKhau, data['password']):
            return jsonify({
                'status': False,
                'message': 'Username hoặc password không đúng'
            }), 401

        if user.TrangThai == 1:
            return jsonify({
                'status': False,
                'message': 'Tài khoản đã bị khóa'
            }), 401

        nhom = NhomNguoiDung.query.get(user.MaNND)

        login_user(user)  
        return jsonify({
            'status': True,
            'message': 'Đăng nhập thành công',
            'data': {
                'MaND': user.MaND,
                'TenDangNhap': user.TenDangNhap,
                'NhomNguoiDung': {
                    'MaNND': nhom.MaNND,
                    'TenNhomNguoiDung': nhom.TenNhomNguoiDung
                } if nhom else None
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi đăng nhập',
            'error': str(e)
        }), 500

# @auth_bp.route('/api/logout', methods=['GET'])
# @login_required
# def logout():
#     session.clear()
#     logout_user()  
#     return jsonify({'status': True, 'message': 'Đăng xuất thành công'}), 200


@auth_bp.route('/login/google')
def google_login():
    google_provider_cfg = requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return jsonify({"authorization_url": request_uri})


@auth_bp.route('/login/google/callback')
def google_callback():
    try:
        code = request.args.get("code")
        if not code:
            return jsonify({'status': False, 'message': 'Không tìm thấy mã xác thực'}), 400

        google_provider_cfg = requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        token_url, headers, body = google_client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
        )
        token_response.raise_for_status()

        google_client.parse_request_body_response(token_response.text)

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = google_client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        if user_info.get("email_verified"):
            email = user_info["email"]

            user = NguoiDung.query.filter_by(TenDangNhap=email).first()

            if not user:
                username = email
                password = generate_password_hash(secrets.token_hex(10))

                user = NguoiDung(
                    TenDangNhap=username,
                    MatKhau=password, 
                    TrangThai=0,
                    MaNND=2 
                )
                db.session.add(user)
                db.session.commit()

            login_user(user) 

            user_data = {
                'MaND': user.MaND,
                'TenDangNhap': user.TenDangNhap,
                'NhomNguoiDung': {
                    'MaNND': user.MaNND,
                    'TenNhomNguoiDung': user.nhom_nguoi_dung.TenNhomNguoiDung
                } 
            }

            return f"""
                <html>
                    <head>
                        <script>
                            // Gửi dữ liệu người dùng trở lại cửa sổ mở
                            window.opener.postMessage({json.dumps(user_data)}, "{current_app.config['CLIENT_URL']}");
                            window.close();
                        </script>
                    </head>
                    <body>
                        <p>Đăng nhập thành công. Bạn có thể đóng cửa sổ này.</p>
                    </body>
                </html>
            """

        else:
            return jsonify({'status': False, 'message': 'Email chưa được xác minh'}), 400

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi đăng nhập',
            'error': str(e)
        }), 500

@auth_bp.route('/api/user_info', methods=['GET'])
def get_user_info_api():
    if not current_user.is_authenticated:
        return jsonify({
            'status': False,
            'message': 'Người dùng chưa đăng nhập',
            'data': None
        }), 401

    try:
        nhom = NhomNguoiDung.query.get(current_user.MaNND)
        
        return jsonify({
            'status': True,
            'message': 'Lấy thông tin thành công',
            'data': {
                'MaND': current_user.MaND,
                'TenDangNhap': current_user.TenDangNhap,
                'NhomNguoiDung': {
                    'MaNND': nhom.MaNND,
                    'TenNhomNguoiDung': nhom.TenNhomNguoiDung
                } if nhom else None
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy thông tin người dùng',
            'error': str(e)
        }), 500
