from flask import Blueprint, request, jsonify
from app.models import QuocGia
from app import db

quocgia = Blueprint('quocgia', __name__)

def serialize_quoc_gia(quocgia):
    return {
        'MaQG': quocgia.MaQG,
        'TenQuocGia': quocgia.TenQuocGia
    }

@quocgia.route('/api/quoc-gia', methods=['GET'])
def get_all_quoc_gia():
    try:
        quoc_gia = QuocGia.query.all()
        
        data = [{
            'MaQG': qg.MaQG,
            'TenQG': qg.TenQuocGia
        } for qg in quoc_gia]
        
        return jsonify({
            'status': True,
            'message': 'Lấy danh sách quốc gia thành công',
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách quốc gia.',
            'error': str(e)
        }), 500

@quocgia.route('/api/quoc-gia/<string:MaQG>', methods=['GET'])
def get_quoc_gia(MaQG):
    try:
        quocgia = QuocGia.query.get(MaQG)
        if not quocgia:
            return jsonify({
                'status': False,
                'message': 'Không tìm thấy quốc gia.'
            }), 404
        
        data = serialize_quoc_gia(quocgia)
        
        return jsonify({
            'status': True,
            'message': 'Lấy thông tin quốc gia thành công.',
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy thông tin quốc gia.',
            'error': str(e)
        }), 500

@quocgia.route('/api/quoc-gia', methods=['POST'])
def add_quoc_gia():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': False, 'message': 'Không có dữ liệu được gửi.'}), 400
        
        # Lấy dữ liệu từ JSON
        MaQG = json_data.get('MaQG', '').strip()
        TenQuocGia = json_data.get('TenQuocGia', '').strip()
        
        # Kiểm tra dữ liệu bắt buộc
        if not MaQG or not TenQuocGia:
            return jsonify({'status': False, 'message': 'Vui lòng cung cấp đầy đủ MaQG và TenQuocGia.'}), 400
        
        # Kiểm tra định dạng và độ dài
        if not MaQG.isalnum() or len(MaQG) > 5:
            return jsonify({'status': False, 'message': 'MaQG phải là ký tự alphanumeric và không vượt quá 5 ký tự.'}), 400
        if len(TenQuocGia) > 50:
            return jsonify({'status': False, 'message': 'TenQuocGia không được vượt quá 50 ký tự.'}), 400
        
        # Kiểm tra tính duy nhất của MaQG và TenQuocGia
        existing_ma_qg = QuocGia.query.get(MaQG)
        if existing_ma_qg:
            return jsonify({'status': False, 'message': 'Mã quốc gia đã tồn tại.'}), 400
        existing_ten_quoc_gia = QuocGia.query.filter_by(TenQuocGia=TenQuocGia).first()
        if existing_ten_quoc_gia:
            return jsonify({'status': False, 'message': 'Tên quốc gia đã tồn tại.'}), 400
        
        # Tạo đối tượng QuocGia mới
        new_quocgia = QuocGia(MaQG=MaQG, TenQuocGia=TenQuocGia)
        
        # Thêm vào database
        db.session.add(new_quocgia)
        db.session.commit()
        
        data = serialize_quoc_gia(new_quocgia)
        
        return jsonify({
            'status': True,
            'message': 'Thêm quốc gia thành công.',
            'data': data
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi thêm quốc gia.',
            'error': str(e)
        }), 500

@quocgia.route('/api/quoc-gia/<string:MaQG>', methods=['PUT'])
def update_quoc_gia(MaQG):
    try:
        quocgia = QuocGia.query.get(MaQG)
        if not quocgia:
            return jsonify({'status': False, 'message': 'Không tìm thấy quốc gia.'}), 404
        
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': False, 'message': 'Không có dữ liệu được gửi.'}), 400
        
        # Lấy dữ liệu từ JSON
        TenQuocGia = json_data.get('TenQuocGia', '').strip()
        
        # Kiểm tra nếu TenQuocGia được cung cấp
        if 'TenQuocGia' in json_data:
            if not TenQuocGia:
                return jsonify({'status': False, 'message': 'TenQuocGia không được để trống.'}), 400
            if len(TenQuocGia) > 50:
                return jsonify({'status': False, 'message': 'TenQuocGia không được vượt quá 50 ký tự.'}), 400
            
            # Kiểm tra tính duy nhất của TenQuocGia
            existing_ten_quoc_gia = QuocGia.query.filter_by(TenQuocGia=TenQuocGia).first()
            if existing_ten_quoc_gia and existing_ten_quoc_gia.MaQG != MaQG:
                return jsonify({'status': False, 'message': 'TenQuocGia đã tồn tại.'}), 400
            
            # Cập nhật TenQuocGia
            quocgia.TenQuocGia = TenQuocGia
        
        
        # Commit thay đổi
        db.session.commit()
        
        data = serialize_quoc_gia(quocgia)
        
        return jsonify({
            'status': True,
            'message': 'Cập nhật quốc gia thành công.',
            'data': data
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi cập nhật quốc gia.',
            'error': str(e)
        }), 500

@quocgia.route('/api/quoc-gia/<string:MaQG>', methods=['DELETE'])
def delete_quoc_gia(MaQG):
    """
    Xóa một quốc gia dựa trên MaQG.
    """
    try:
        quocgia = QuocGia.query.get(MaQG)
        if not quocgia:
            return jsonify({'status': False, 'message': 'Không tìm thấy quốc gia.'}), 404
        
        # Kiểm tra nếu quốc gia có liên kết với sân bay hoặc hãng hàng không
        if quocgia.ds_san_bay or quocgia.ds_hang_hang_khong:
            return jsonify({
                'status': False,
                'message': 'Không thể xóa quốc gia này vì có liên kết với sân bay hoặc hãng hàng không.'
            }), 400
        
        # Xóa quốc gia
        db.session.delete(quocgia)
        db.session.commit()
        
        return jsonify({
            'status': True,
            'message': 'Xóa quốc gia thành công.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi xóa quốc gia.',
            'error': str(e)
        }), 500
