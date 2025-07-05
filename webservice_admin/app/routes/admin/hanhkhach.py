from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models import HanhKhach
from app import db

hanhkhach = Blueprint('hanhkhach', __name__)

# lấy ds
@hanhkhach.route('/api/hanh-khach', methods=['GET'])
def get_all_hanh_khach():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        maHk = request.args.get('ma_hanh_khach', '')
        hoHk = request.args.get('ho_hk', '')
        tenHk = request.args.get('ten_hk', '')
        danhXung = request.args.get('danh_xung', '')
        cccd = request.args.get('cccd', '')
        ngaySinh = request.args.get('ngay_sinh', '')
        quocTich = request.args.get('quoc_tich', '')
        loaiHk = request.args.get('loai_hk', '')

        query = HanhKhach.query

        if maHk:
            query = query.filter(HanhKhach.MaHanhKhach.ilike(f'%{maHk}%'))
        if hoHk:
            query = query.filter(HanhKhach.HoHK.ilike(f'%{hoHk}%'))
        if tenHk:
            query = query.filter(HanhKhach.TenHK.ilike(f'%{tenHk}%'))
        if danhXung:
            query = query.filter(HanhKhach.DanhXung.ilike(f'%{danhXung}%'))
        if cccd:
            query = query.filter(HanhKhach.CCCD.ilike(f'%{cccd}%'))
        if ngaySinh:
            query = query.filter(HanhKhach.NgaySinh.ilike(f'%{ngaySinh}%'))
        if quocTich:
            query = query.filter(HanhKhach.QuocTich.ilike(f'%{quocTich}%'))
        if loaiHk:
            query = query.filter(HanhKhach.LoaiHK.ilike(f'%{loaiHk}%'))
        

        sort_by = request.args.get('sort_by_hanh_khach', 'MaHanhKhach')  
        order = request.args.get('order_hanh_khach', 'asc') 
        
        if hasattr(HanhKhach, sort_by):
            sort_column = getattr(HanhKhach, sort_by)
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
            'MaHanhKhach': hk.MaHanhKhach,
            'HoHK': hk.HoHK,
            'TenHK': hk.TenHK,
            'DanhXung': hk.DanhXung,
            'CCCD': hk.CCCD,
            'NgaySinh': hk.NgaySinh.strftime("%d/%m/%Y") if hk.NgaySinh else None,
            'QuocTich' : hk.QuocTich,
            'LoaiHK': hk.LoaiHK
        } for hk in pagination.items]
        
        return jsonify({
            'status': True,
            'message': 'Lấy danh sách hành khách thành công',
            'data': data,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': page,
                'per_page': per_page
            },
            'filters': { 
                'ma_hanh_khach': maHk,
                'ho_hk': hoHk,
                'ten_hk': tenHk,
                'danh_xung': danhXung,
                'cccd': cccd,
                'ngay_sinh': ngaySinh,
                'quoc_tich': quocTich,
                'loai_hk': loaiHk,
                'sort_by_hanh_khach': sort_by,
                'order_hanh_khach': order
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách hành khách',
            'error': str(e)
        }), 500

# lấy theo mã
@hanhkhach.route('/api/hanh-khach/<string:ma_hk>', methods=['GET'])
def get_hanh_khach(ma_hk):
    try:
        hanhkhach = HanhKhach.query.filter_by(MaHanhKhach=ma_hk).first()
        if not hanhkhach:
            return jsonify({
                'status': False,
                'message': 'Hành khách không tồn tại'
            }), 404

        data = {
            'MaHanhKhach': hanhkhach.MaHanhKhach,
            'HoHK': hanhkhach.HoHK,
            'TenHK': hanhkhach.TenHK,
            'DanhXung': hanhkhach.DanhXung,
            'CCCD': hanhkhach.CCCD,
            'NgaySinh': hanhkhach.NgaySinh.strftime("%d/%m/%Y") if hanhkhach.NgaySinh else None,
            'QuocTich': hanhkhach.QuocTich,
            'LoaiHK': hanhkhach.LoaiHK
        }

        return jsonify({
            'status': True,
            'message': 'Lấy thông tin hành khách thành công',
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy thông tin hành khách',
            'error': str(e)
        }), 500

# API: Sửa thong tin hành khách
@hanhkhach.route('/api/hanh-khach/<string:ma_hk>', methods=['PUT'])
def update_hanh_khach(ma_hk):
    try:
        data = request.get_json()
        required_fields = ['HoHK', 'TenHK', 'DanhXung', 'CCCD', 'NgaySinh', 'QuocTich', 'LoaiHK']
        print(data)
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': False,
                'message': 'Thiếu thông tin bắt buộc'
            }), 400
        
        hanhkhach = HanhKhach.query.get(ma_hk)
        if not hanhkhach:
            return jsonify({
                'status': False,
                'message': 'Hành khách không tồn tại'
            }), 404

        # kiểm tra cccd duplicate
        if hanhkhach.CCCD != data['CCCD']:
            existHKCCCD =  HanhKhach.query.filter_by(CCCD=data['CCCD']).first()
            if existHKCCCD:
                return jsonify({
                        'status': False,
                        'message': f"Mã CCCD đã tồn tại"
                }), 400
        
        # Cập nhật thông tin
        print("b4", hanhkhach.NgaySinh)

        hanhkhach.HoHK = data['HoHK']
        hanhkhach.TenHK = data['TenHK']
        hanhkhach.DanhXung = data['DanhXung']
        hanhkhach.CCCD = data['CCCD']
        hanhkhach.NgaySinh = datetime.strptime(data['NgaySinh'], "%d/%m/%Y")
        hanhkhach.QuocTich = data['QuocTich']
        hanhkhach.LoaiHK = data['LoaiHK']

        print("after", hanhkhach.NgaySinh)
        db.session.commit()
        
        return jsonify({
            'status': True,
            'message': 'Cập nhật thông tin hành khách thành công',
            'data': {
                'MaHanhKhach': hanhkhach.MaHanhKhach,
                'HoHK': hanhkhach.HoHK,
                'TenHK': hanhkhach.TenHK
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi cập nhật thông tin hành khách',
            'error': str(e)
        }), 500
