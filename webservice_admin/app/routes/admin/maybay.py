from flask import Blueprint, request, jsonify
from app.models import MayBay, HangHangKhong, ChuyenBay
from app import db

maybay = Blueprint('maybay', __name__)

# API: Lấy danh sách máy bay theo hãng hàng không
# @maybay.route('/api/hang-hang-khong/<string:ma_hhk>/may-bay', methods=['GET'])
# def get_may_bay_by_hang_hang_khong(ma_hhk):
#     try:
#         hang_hang_khong = HangHangKhong.query.get(ma_hhk)

#         if not hang_hang_khong:
#             return jsonify({
#                 'status': False,
#                 'message': 'Không tìm thấy hãng hàng không'
#             }), 404

#         may_bay_list = MayBay.query.filter_by(MaHHK=ma_hhk).all()
#         result = [{
#             'MaMB': mb.MaMB,
#             'TenMB': mb.TenMB,
#             'MaHHK': mb.MaHHK
#         } for mb in may_bay_list]

#         return jsonify({
#             'status': True,
#             'message': 'Lấy danh sách máy bay thành công',
#             'data': result
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': False,
#             'message': 'Có lỗi xảy ra khi lấy danh sách máy bay',
#             'error': str(e)
#         }), 500

@maybay.route('/api/hang-hang-khong', methods=['GET'])
def get_hang_hang_khong():
    try:
        hang_hang_khong = HangHangKhong.query.all()

        data = [{
            'MaHHK': hhk.MaHHK,
            'TenHHK': hhk.TenHHK
        } for hhk in hang_hang_khong]
        
        return jsonify({
            'status': True,
            'message': 'Lấy danh sách hãng hàng không',
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách quốc gia',
            'error': str(e)
        }), 500

# lấy ds máy bay
@maybay.route('/api/may-bay', methods=['GET'])
def get_all_may_bay():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        maMb = request.args.get('ma_may_bay', '')
        tenMb = request.args.get('ten_may_bay', '')
        maHhk = request.args.get('ma_hhk_may_bay', '')
        # gheBus = request.args.get('so_ghe', '')
        # gheBus = request.args.get('thanh_pho', '')
        loaiMb = request.args.get('loai_mb', '')

        query = MayBay.query

        if maMb:
            query = query.filter(MayBay.MaMayBay.ilike(f'%{maMb}%'))
        if tenMb:
            query = query.filter(MayBay.TenMayBay.ilike(f'%{tenMb}%'))
        if maHhk:
            query = query.filter(MayBay.MaHHK.ilike(f'%{maHhk}%'))
        if loaiMb:
            query = query.filter(MayBay.LoaiMB.ilike(f'%{loaiMb}%'))

        sort_by = request.args.get('sort_by_may_bay', 'MaMayBay')  
        order = request.args.get('order_may_bay', 'asc') 
        
        if hasattr(MayBay, sort_by):
            sort_column = getattr(MayBay, sort_by)
            if sort_column == MayBay.MaHHK:
                query = query.join(HangHangKhong)
                sort_column  = HangHangKhong.TenHHK
            
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
            'MaMayBay': mb.MaMayBay,
            'TenMayBay': mb.TenMayBay,
            'MaHHK': mb.MaHHK,
            'SoChoNgoiBus': mb.SoChoNgoiBus,
            'SoChoNgoiEco': mb.SoChoNgoiEco,
            'LoaiMB': mb.LoaiMB
        } for mb in pagination.items]
        
        return jsonify({
            'status': True,
            'message': 'Lấy danh sách máy bay thành công',
            'data': data,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': page,
                'per_page': per_page
            },
            'filters': { 
                'ma_may_bay': maMb,
                'ten_may_bay': tenMb,
                'ma_hhk_may_bay': maHhk,
                'loai_mb': loaiMb,
                'sort_by_may_bay': sort_by,
                'order': order
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách sân bay',
            'error': str(e)
        }), 500

# lấy máy bay theo mã
@maybay.route('/api/may-bay/<string:ma_mb>', methods=['GET'])
def get_may_bay(ma_mb):
    try:
        maybay = MayBay.query.filter_by(MaMayBay=ma_mb).first()
        if not maybay:
            return jsonify({
                'status': False,
                'message': 'Máy bay không tồn tại'
            }), 404

        data = {
            'MaMayBay': maybay.MaMayBay,
            'TenMayBay': maybay.TenMayBay,
            'MaHHK': maybay.MaHHK,
            'SoChoNgoiBus': maybay.SoChoNgoiBus,
            'SoChoNgoiEco': maybay.SoChoNgoiEco,
            'LoaiMB': maybay.LoaiMB
        }

        return jsonify({
            'status': True,
            'message': 'Lấy thông tin máy bay thành công',
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy thông tin máy bay',
            'error': str(e)
        }), 500

# API: Thêm máy bay
@maybay.route('/api/may-bay', methods=['POST'])
def add_may_bay():
    try:
        data = request.get_json()
        perPage = 10
        
        required_fields = ['TenMayBay', 'MaHHK', 'SoChoNgoiBus', 'SoChoNgoiEco', 'LoaiMB']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': False,
                'message': 'Thiếu thông tin bắt buộc'
            }), 400

        hang_hang_khong = HangHangKhong.query.get(data['MaHHK'])

        if not hang_hang_khong:
            return jsonify({
                'status': False,
                'message': 'Hãng hàng không không tồn tại'
            }), 404
        
        existing_mb_name = MayBay.query.filter_by(TenMayBay=data['TenMayBay']).first()
        if existing_mb_name:
            return jsonify({
                'status': False,
                'message': f"Tên máy bay '{data['TenMayBay']}' đã tồn tại"
            }), 400
        
        new_may_bay = MayBay(
            TenMayBay=data['TenMayBay'],
            MaHHK=data['MaHHK'],
            SoChoNgoiBus=data['SoChoNgoiBus'],
            SoChoNgoiEco=data['SoChoNgoiEco'],
            LoaiMB=data['LoaiMB']
        )
        
        db.session.add(new_may_bay)
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Thêm máy bay thành công',
            'data': {
                'MaMB': new_may_bay.MaMayBay,
                'TenMB': new_may_bay.TenMayBay,
                'MaHHK': new_may_bay.MaHHK
            }
        }), 201

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi thêm máy bay',
            'error': str(e)
        }), 500

# API: Sửa máy bay
@maybay.route('/api/may-bay/<string:ma_mb>', methods=['PUT'])
def update_may_bay(ma_mb):
    try:
        data = request.get_json()
        required_fields = ['TenMayBay', 'MaHHK', 'SoChoNgoiBus', 'SoChoNgoiEco', 'LoaiMB']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': False,
                'message': 'Thiếu thông tin bắt buộc'
            }), 400
        
        maybay = MayBay.query.get(ma_mb)
        if not maybay:
            return jsonify({
                'status': False,
                'message': 'Máy bay không tồn tại'
            }), 404

        # kiểm tra tên máy bay tồn tại
        # print(may_bay.Ten)
        if maybay.TenMayBay != data['TenMayBay']:
            existTenMB =  MayBay.query.filter_by(TenMayBay=data['TenMayBay']).first()
            if existTenMB:
                return jsonify({
                        'status': False,
                        'message': f"Tên máy bay '{data['TenMayBay']}' đã tồn tại"
                }), 400

        # Cập nhật thông tin máy bay
        maybay.TenMayBay = data['TenMayBay']
        maybay.MaHHK = data['MaHHK']
        maybay.SoChoNgoiBus = data['SoChoNgoiBus']
        maybay.SoChoNgoiEco = data['SoChoNgoiEco']
        maybay.LoaiMB = data['LoaiMB']

        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Cập nhật máy bay thành công',
            'data': {
                'MaMB': maybay.MaMayBay,
                'TenMB': maybay.TenMayBay,
                'MaHHK': maybay.MaHHK
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi cập nhật máy bay',
            'error': str(e)
        }), 500

# API: Xóa máy bay
@maybay.route('/api/may-bay/<string:ma_mb>', methods=['DELETE'])
def delete_may_bay(ma_mb):
    try:
        may_bay = MayBay.query.get(ma_mb)

        if not may_bay:
            return jsonify({
                'status': False,
                'message': 'Không tìm thấy máy bay'
            }), 404

        existMayBay = ChuyenBay.query.filter(ChuyenBay.MaMB==ma_mb).first()
        if existMayBay:
            return jsonify({
                'status': False,
                'message': 'Không thể xóa máy bay đã được tạo chuyến bay'
            })

        db.session.delete(may_bay)
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Xóa máy bay thành công'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi xóa máy bay',
            'error': str(e)
        }), 500
