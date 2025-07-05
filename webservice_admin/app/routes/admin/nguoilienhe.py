from flask import Blueprint, request, jsonify
from app.models import NguoiLienHe
from app import db

nguoilienhe = Blueprint('nguoilienhe', __name__)

# lấy ds
@nguoilienhe.route('/api/nguoi-lien-he', methods=['GET'])
def get_all_nguoi_lien_he():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        maNlh = request.args.get('ma_nlh', '')
        hoNlh = request.args.get('ho_nlh', '')
        tenNlh = request.args.get('ten_nlh', '')
        sdt = request.args.get('sdt', '')
        email = request.args.get('email', '')

        query = NguoiLienHe.query

        if maNlh:
            query = query.filter(NguoiLienHe.MaNLH.ilike(f'%{maNlh}%'))
        if hoNlh:
            query = query.filter(NguoiLienHe.HoNLH.ilike(f'%{hoNlh}%'))
        if tenNlh:
            query = query.filter(NguoiLienHe.TenNLH.ilike(f'%{tenNlh}%'))
        if sdt:
            query = query.filter(NguoiLienHe.SDT.ilike(f'%{sdt}%'))
        if email:
            query = query.filter(NguoiLienHe.Email.ilike(f'%{email}%'))

        sort_by = request.args.get('sort_by_nlh', 'MaNLH')  
        order = request.args.get('order_nlh', 'asc') 
        
        if hasattr(NguoiLienHe, sort_by):
            sort_column = getattr(NguoiLienHe, sort_by)
            if order == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        print(order)
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        data = [{
            'MaNLH': nlh.MaNLH,
            'HoNLH': nlh.HoNLH,
            'TenNLH': nlh.TenNLH,
            'SDT': nlh.SDT,
            'Email': nlh.Email
        } for nlh in pagination.items]
        
        return jsonify({
            'status': True,
            'message': 'Lấy danh sách người liên hệ thành công',
            'data': data,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': page,
                'per_page': per_page
            },
            'filters': { 
                'ma_nlh': maNlh,
                'ho_nlh': hoNlh,
                'ten_nlh': tenNlh,
                'sdt': sdt,
                'email': email,
                'sort_by_nlh': sort_by,
                'order_nlh': order
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách người liên hệ',
            'error': str(e)
        }), 500

# lấy người liên hệ theo mã
@nguoilienhe.route('/api/nguoi-lien-he/<string:ma_nlh>', methods=['GET'])
def get_nguoi_lien_he(ma_nlh):
    try:
        nguoilienhe = NguoiLienHe.query.filter_by(MaNLH=ma_nlh).first()
        if not nguoilienhe:
            return jsonify({
                'status': False,
                'message': 'Người liên hệ không tồn tại'
            }), 404

        data = {
            'MaNLH': nguoilienhe.MaNLH,
            'HoNLH': nguoilienhe.HoNLH,
            'TenNLH': nguoilienhe.TenNLH,
            'SDT': nguoilienhe.SDT,
            'Email': nguoilienhe.Email
        }

        return jsonify({
            'status': True,
            'message': 'Lấy thông tin người liên hệ thành công',
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy thông tin người liên hệ',
            'error': str(e)
        }), 500

# API: Sửa nlh
@nguoilienhe.route('/api/nguoi-lien-he/<string:ma_nlh>', methods=['PUT'])
def update_nguoi_lien_he(ma_nlh):
    try:
        data = request.get_json()
        print(data)
        required_fields = ['HoNLH', 'TenNLH', 'SDT', 'Email']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': False,
                'message': 'Thiếu thông tin bắt buộc'
            }), 400
        
        nguoilienhe = NguoiLienHe.query.get(ma_nlh)
        if not nguoilienhe:
            return jsonify({
                'status': False,
                'message': 'Người liên hệ không tồn tại'
            }), 404

        # kiểm tra email duplicate
        
        if nguoilienhe.Email != data['Email']:
            existNLHEmail =  NguoiLienHe.query.filter_by(Email=data['Email']).first()
            if existNLHEmail:
                return jsonify({
                        'status': False,
                        'message': f"Email '{data['Email']}' đã tồn tại"
                }), 400

        # Cập nhật thông tin
        nguoilienhe.HoNLH = data['HoNLH']
        nguoilienhe.TenNLH = data['TenNLH']
        nguoilienhe.SDT = data['SDT']
        nguoilienhe.Email = data['Email']

        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Cập nhật thông tin người liên hệ thành công',
            'data': {
                'MaNLH': nguoilienhe.MaNLH,
                'HoNLH': nguoilienhe.HoNLH,
                'TenNLH': nguoilienhe.TenNLH
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi cập nhật thông tin người liên hệ',
            'error': str(e)
        }), 500
