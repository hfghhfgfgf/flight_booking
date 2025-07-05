from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.models import SanBay, QuocGia, ChuyenBay
from math import ceil
from app import db

sanbay = Blueprint('sanbay', __name__)

@sanbay.route('/api/san-bay', methods=['GET'])
def get_all_san_bay():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        ma_san_bay = request.args.get('ma_san_bay', '')
        ten_san_bay = request.args.get('ten_san_bay', '')
        thanh_pho = request.args.get('thanh_pho', '')
        ma_qg = request.args.get('ma_qg', '')
        loai_sb = request.args.get('loai_sb', '')

        query = SanBay.query

        if ma_san_bay:
            query = query.filter(SanBay.MaSanBay.ilike(f'%{ma_san_bay}%'))
        if ten_san_bay:
            query = query.filter(SanBay.TenSanBay.ilike(f'%{ten_san_bay}%'))
        if thanh_pho:
            query = query.filter(SanBay.ThanhPho.ilike(f'%{thanh_pho}%'))
        if ma_qg:
            query = query.filter(SanBay.MaQG.ilike(f'%{ma_qg}%'))
        if loai_sb:
            query = query.filter(SanBay.LoaiSB.ilike(f'%{loai_sb}%'))

        sort_by = request.args.get('sort_by', 'MaSanBay')  
        order = request.args.get('order', 'asc') 
        
        if hasattr(SanBay, sort_by):
            sort_column = getattr(SanBay, sort_by)
            print(sort_by, sort_column)
            if sort_column == SanBay.MaQG:
                query = query.join(QuocGia)
                sort_column  = QuocGia.TenQuocGia
            
            if order == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        data = [{
            'MaSanBay': sb.MaSanBay,
            'TenSanBay': sb.TenSanBay,
            'ThanhPho': sb.ThanhPho,
            'MaQG': sb.quoc_gia.TenQuocGia, 
            'LoaiSB': sb.LoaiSB
        } for sb in pagination.items]

        return jsonify({
            'status': True,
            'message': 'Lấy danh sách sân bay thành công',
            'data': data,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': page,
                'per_page': per_page
            },
            'filters': { 
                'ma_san_bay': ma_san_bay,
                'ten_san_bay': ten_san_bay,
                'thanh_pho': thanh_pho,
                'ma_qg': ma_qg,
                'loai_sb': loai_sb,
                'sort_by': sort_by,
                'order': order
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách sân bay',
            'error': str(e)
        }), 500

@sanbay.route('/api/san-bay', methods=['POST'])
def create_san_bay():
    try:
        data = request.get_json()
        perPage = 10 
        
        # Các trường bắt buộc
        required_fields = ['MaSanBay', 'TenSanBay', 'ThanhPho', 'MaQG', 'LoaiSB']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': False,
                'message': 'Thiếu thông tin bắt buộc'
            }), 400
        
        MaSB = data.get('MaSanBay', '').strip()
        if not MaSB.isalnum():
            return jsonify({
                'status': False,
                'message': 'Mã sân bay chỉ được chứa kí tự chữ và số'
            }), 400 
        
        existing_san_bay_name = SanBay.query.filter_by(TenSanBay=data['TenSanBay']).first()
        if existing_san_bay_name:
            return jsonify({
                'status': False,
                'message': f"Tên sân bay '{data['TenSanBay']}' đã tồn tại"
            }), 400
        
        existing_san_bay = SanBay.query.filter_by(MaSanBay=data['MaSanBay']).first()
        if existing_san_bay:
            return jsonify({
                'status': False,
                'message': f"Mã sân bay '{data['MaSanBay']}' đã tồn tại"
            }), 400
        
        ma_qg = data['MaQG']
        quoc_gia = QuocGia.query.filter_by(MaQG=ma_qg).first()
        if not quoc_gia:
            ten_quoc_gia = data.get('TenQuocGia')
            if not ten_quoc_gia:
                return jsonify({
                    'status': False,
                    'message': 'Thiếu thông tin tên quốc gia để tạo mới'
                }), 400
            quoc_gia = QuocGia(MaQG=ma_qg, TenQuocGia=ten_quoc_gia)
            db.session.add(quoc_gia)
        
        if data['LoaiSB'] not in ['Quốc tế', 'Nội địa']:
            return jsonify({
                'status': False,
                'message': 'Loại sân bay phải là "Quốc tế" hoặc "Nội địa"'
            }), 400
        
        # Tạo mới SanBay
        new_san_bay = SanBay(
            MaSanBay=data['MaSanBay'],
            TenSanBay=data['TenSanBay'],
            ThanhPho=data['ThanhPho'],
            MaQG=ma_qg,
            LoaiSB=data['LoaiSB']
        )
        
        db.session.add(new_san_bay)
        db.session.commit()
        
        total = SanBay.query.count()
        pages = ceil(total / perPage)
        
        return jsonify({
            'status': True,
            'message': 'Thêm sân bay thành công.',
            'pagination': {
                'total': total,
                'pages': pages
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi thêm sân bay',
            'error': str(e)
        }), 500

@sanbay.route('/api/san-bay/<string:maSanBay>', methods=['GET'])
def get_san_bay(maSanBay):
    try:
        sanbay = SanBay.query.filter_by(MaSanBay=maSanBay).first()
        if not sanbay:
            return jsonify({
                'status': False,
                'message': 'Sân bay không tồn tại'
            }), 404

        data = {
            'MaSanBay': sanbay.MaSanBay,
            'TenSanBay': sanbay.TenSanBay,
            'ThanhPho': sanbay.ThanhPho,
            'MaQG': sanbay.MaQG,
            'LoaiSB': sanbay.LoaiSB
        }

        return jsonify({
            'status': True,
            'message': 'Lấy thông tin sân bay thành công',
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy thông tin sân bay',
            'error': str(e)
        }), 500

@sanbay.route('/api/san-bay/<string:maSanBay>', methods=['DELETE'])
def delete_san_bay(maSanBay):
    try:
        sanbay = SanBay.query.filter_by(MaSanBay=maSanBay).first()
        if not sanbay:
            return jsonify({
                'status': False,
                'message': 'Sân bay không tồn tại'
            }), 404

        existChuyenBay = ChuyenBay.query.filter(or_(ChuyenBay.MaSanBayDi==maSanBay,ChuyenBay.MaSanBayDen==maSanBay)).first()
        if existChuyenBay:
            return jsonify({
                'status': False,
                'message': 'Không thể xóa sân bay đã được tạo chuyến bay'
            }), 400
        
        db.session.delete(sanbay)
        db.session.commit()

        total = SanBay.query.count()
        pages = ceil(total / 10)  # Assuming perPage = 10

        return jsonify({
            'status': True,
            'message': 'Xóa sân bay thành công.',
            'pagination': {
                'total': total,
                'pages': pages
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi xóa sân bay',
            'error': str(e)
        }), 500

@sanbay.route('/api/san-bay/<string:maSanBay>', methods=['PUT'])
def update_san_bay(maSanBay):
    try:
        data = request.get_json()
        required_fields = ['TenSanBay', 'ThanhPho', 'MaQG', 'LoaiSB']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': False,
                'message': 'Thiếu thông tin bắt buộc'
            }), 400

        sanbay = SanBay.query.filter_by(MaSanBay=maSanBay).first()
        if not sanbay:
            return jsonify({
                'status': False,
                'message': 'Sân bay không tồn tại'
            }), 404

        # Kiểm tra tính duy nhất của TenSanBay nếu thay đổi
        if sanbay.TenSanBay != data['TenSanBay']:
            existing_san_bay_name = SanBay.query.filter_by(TenSanBay=data['TenSanBay']).first()
            if existing_san_bay_name:
                return jsonify({
                    'status': False,
                    'message': f"Tên sân bay '{data['TenSanBay']}' đã tồn tại"
                }), 400

        # Kiểm tra MaQG tồn tại, nếu không thì thêm QuocGia mới
        ma_qg = data['MaQG']
        quoc_gia = QuocGia.query.filter_by(MaQG=ma_qg).first()
        if not quoc_gia:
            # Nếu MaQG chưa tồn tại, cần thông tin TenQuocGia để tạo mới
            ten_quoc_gia = data.get('TenQuocGia')
            if not ten_quoc_gia:
                return jsonify({
                    'status': False,
                    'message': 'Thiếu thông tin tên quốc gia để tạo mới'
                }), 400
            quoc_gia = QuocGia(MaQG=ma_qg, TenQuocGia=ten_quoc_gia)
            db.session.add(quoc_gia)

        # Kiểm tra giá trị LoaiSB hợp lệ
        if data['LoaiSB'] not in ['Quốc tế', 'Nội địa']:
            return jsonify({
                'status': False,
                'message': 'Loại sân bay phải là "Quốc tế" hoặc "Nội địa"'
            }), 400

        # Cập nhật thông tin sân bay
        sanbay.TenSanBay = data['TenSanBay']
        sanbay.ThanhPho = data['ThanhPho']
        sanbay.MaQG = ma_qg
        sanbay.LoaiSB = data['LoaiSB']

        db.session.commit()

        total = SanBay.query.count()
        pages = ceil(total / 10)  # Assuming perPage = 10

        return jsonify({
            'status': True,
            'message': 'Cập nhật sân bay thành công.',
            'pagination': {
                'total': total,
                'pages': pages
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi cập nhật sân bay',
            'error': str(e)
        }), 500

