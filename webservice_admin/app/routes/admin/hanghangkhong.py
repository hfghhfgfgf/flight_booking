from flask import Blueprint, request, jsonify
from app.models import HangHangKhong, QuocGia, DichVu, DichVuVe, GoiDichVu, MayBay
from app import db
from sqlalchemy import or_
from math import ceil
hanghangkhong = Blueprint('hanghangkhong', __name__)

def validate_service_param(ma_dv, tham_so):
    try:
        if ma_dv == 1:  # Hành lý xách tay
            if not (0 <= tham_so <= 30):
                return False, "Hành lý xách tay phải từ 0 đến 30 kg"
        
        elif ma_dv == 2:  # Hành lý ký gửi
            if not (10 <= tham_so <= 50):
                return False, "Hành lý ký gửi phải từ 10 đến 50 kg"
        
        elif ma_dv == 3:  # Phí đổi lịch bay
            if not (0 <= tham_so <= 50):
                return False, "Phí đổi lịch bay không được vượt quá 50%"
        
        elif ma_dv == 4:  # Hoàn vé
            if not (0 <= tham_so <= 80):
                return False, "Phí hoàn vé không được vượt quá 80%"
        
        elif ma_dv == 5:  # Bảo hiểm du lịch
            if tham_so not in [0, 1]:
                return False, "Bảo hiểm du lịch chỉ có thể là có (1) hoặc không (0)"
                
        return True, None
    except Exception as e:
        return False, f"Lỗi kiểm tra tham số: {str(e)}"

def validate_airline_data(data):
    try:
        if not data.get('MaHHK') or len(data['MaHHK']) > 5:
            return False, "Mã hãng hàng không không được để trống và không được vượt quá 5 ký tự"
            
        if not data.get('TenHHK') or len(data['TenHHK']) > 100:
            return False, "Tên hãng hàng không không được để trống và không được vượt quá 100 ký tự"
            
        if not data.get('MaQG') or len(data['MaQG']) > 5:
            return False, "Mã quốc gia không được để trống và không được vượt quá 5 ký tự"

        if not data.get('dich_vu_ve') or not isinstance(data['dich_vu_ve'], list):
            return False, "Danh sách dịch vụ không hợp lệ"
            
        service_packages = {} 
        economy_packages = set()  
        business_packages = set() 
        
        for service in data['dich_vu_ve']:
            if not all(key in service for key in ['MaDV', 'MaGoi', 'LoaiVeApDung', 'ThamSo']):
                return False, "Thiếu thông tin dịch vụ"
                
            # Kiểm tra tham số của dịch vụ
            is_valid, message = validate_service_param(service['MaDV'], service['ThamSo'])
            if not is_valid:
                return False, message

            package_key = f"{service['MaGoi']}_{service['LoaiVeApDung']}"
            
            if package_key not in service_packages:
                service_packages[package_key] = set()
            
            if service['MaDV'] in service_packages[package_key]:
                return False, f"Dịch vụ trùng lặp trong gói {service['MaGoi']} - {service['LoaiVeApDung']}"
                
            service_packages[package_key].add(service['MaDV'])

            if service['LoaiVeApDung'] == 'Economy':
                economy_packages.add(service['MaGoi'])
            else:
                business_packages.add(service['MaGoi'])

        if not economy_packages and not business_packages:
            return False, "Phải có ít nhất một gói dịch vụ cho hạng Economy hoặc Business"
            
        if not economy_packages:
            return False, "Phải có ít nhất một gói dịch vụ cho hạng Economy"
            
        if not business_packages:
            return False, "Phải có ít nhất một gói dịch vụ cho hạng Business"

        return True, None
        
    except Exception as e:
        return False, f"Lỗi validation: {str(e)}"


@hanghangkhong.route('/api/hang-hang-khong', methods=['GET'])
def get_all_hang_hang_khong():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        ma_hhk = request.args.get('ma_hhk', '')
        ten_hhk = request.args.get('ten_hhk', '')
        ma_qg = request.args.get('ma_qg', '')

        query = HangHangKhong.query

        if ma_hhk:
            query = query.filter(HangHangKhong.MaHHK.ilike(f'%{ma_hhk}%'))
        if ten_hhk:
            query = query.filter(HangHangKhong.TenHHK.ilike(f'%{ten_hhk}%'))
        if ma_qg:
            query = query.filter(HangHangKhong.MaQG.ilike(f'%{ma_qg}%'))

        sort_by = request.args.get('sort_by', 'MaHHK') 
        order = request.args.get('order', 'asc')
        
        if hasattr(HangHangKhong, sort_by):
            sort_column = getattr(HangHangKhong, sort_by)
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
            'MaHHK': hhk.MaHHK,
            'TenHHK': hhk.TenHHK,
            'MaQG': hhk.quoc_gia.TenQuocGia
        } for hhk in pagination.items]

        return jsonify({
            'status': True,
            'message': 'Lấy danh sách hãng hàng không thành công',
            'data': data,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': page,
                'per_page': per_page
            },
            'filters': { 
                'ma_hhk': ma_hhk,
                'ten_hhk': ten_hhk,
                'ma_qg': ma_qg,
                'sort_by': sort_by,
                'order': order
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách hãng hàng không',
            'error': str(e)
        }), 500

@hanghangkhong.route('/api/hang-hang-khong', methods=['POST'])
def create_hang_hang_khong():
    try:
        data = request.get_json()
        perPage = 10
        
        # Validate data
        is_valid, error_message = validate_airline_data(data)
        if not is_valid:
            return jsonify({
                'status': False,
                'message': error_message
            }), 400

        # Check existing airline code
        existing_airline = HangHangKhong.query.filter_by(MaHHK=data['MaHHK']).first()
        if existing_airline:
            return jsonify({
                'status': False,
                'message': f"Mã hãng hàng không '{data['MaHHK']}' đã tồn tại"
            }), 400

        # Check existing airline name
        existing_airline_name = HangHangKhong.query.filter_by(TenHHK=data['TenHHK']).first()
        if existing_airline_name:
            return jsonify({
                'status': False,
                'message': f"Tên hãng hàng không '{data['TenHHK']}' đã tồn tại"
            }), 400
            
        # Check if country exists
        country = QuocGia.query.filter_by(MaQG=data['MaQG']).first()
        if not country:
            return jsonify({
                'status': False,
                'message': f"Mã quốc gia '{data['MaQG']}' không tồn tại"
            }), 400

        # Create new airline
        new_airline = HangHangKhong(
            MaHHK=data['MaHHK'].strip(),  # Trim whitespace
            TenHHK=data['TenHHK'].strip(),
            MaQG=data['MaQG']
        )
        db.session.add(new_airline)

        # Add services for the airline
        for service in data['dich_vu_ve']:
            new_service = DichVuVe(
                MaDV=service['MaDV'],
                MaHHK=data['MaHHK'],
                MaGoi=service['MaGoi'],
                LoaiVeApDung=service['LoaiVeApDung'],
                ThamSo=service['ThamSo']
            )
            db.session.add(new_service)

        db.session.commit()

        total = HangHangKhong.query.count()
        pages = ceil(total / perPage) 

        return jsonify({
            'status': True,
            'message': 'Thêm hãng hàng không thành công.',
            'pagination': {
                'total': total,
                'pages': pages
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi thêm hãng hàng không',
            'error': str(e)
        }), 500

@hanghangkhong.route('/api/quoc-gia', methods=['GET'])
def get_quoc_gia():
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
            'message': 'Có lỗi xảy ra khi lấy danh sách quốc gia',
            'error': str(e)
        }), 500

@hanghangkhong.route('/api/dich-vu', methods=['GET'])
def get_dich_vu():
    """API to get list of services"""
    try:
        services = DichVu.query.filter_by(TrangThai=0).all()
        
        result = []
        for service in services:
            result.append({
                'MaDV': service.MaDV,
                'TenDichVu': service.TenDichVu,
                'MoTa': service.MoTa,
                'TrangThai': service.TrangThai
            })
            
        return jsonify({
            'status': True,
            'message': 'Lấy danh sách dịch vụ thành công',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy danh sách dịch vụ',
            'error': str(e)
        }), 500

@hanghangkhong.route('/api/hang-hang-khong/<string:ma_hhk>', methods=['PUT'])
def update_hang_hang_khong(ma_hhk):
    try:
        data = request.get_json()
        
        airline = HangHangKhong.query.filter_by(MaHHK=ma_hhk).first()
        if not airline:
            return jsonify({
                'status': False,
                'message': f"Không tìm thấy hãng hàng không với mã '{ma_hhk}'"
            }), 404

        if 'TenHHK' in data:
            air1 = HangHangKhong.query.filter_by(TenHHK=data['TenHHK']).first()
            if air1 and air1.MaHHK != ma_hhk:
                return jsonify({
                    'status': False,
                    'message': f"Tên hãng hàng không '{data['TenHHK']}' đã tồn tại"
                }), 400

        data['MaHHK'] = ma_hhk 
        is_valid, message = validate_airline_data(data)
        if not is_valid:
            return jsonify({
                'status': False,
                'message': message
            }), 400

 
        if 'TenHHK' in data:
            airline.TenHHK = data['TenHHK']
        if 'MaQG' in data:
            airline.MaQG = data['MaQG']

        if 'dich_vu_ve' in data:
            DichVuVe.query.filter_by(MaHHK=ma_hhk).delete()

            for service in data['dich_vu_ve']:
                new_service = DichVuVe(
                    MaDV=service['MaDV'],
                    MaHHK=ma_hhk,
                    MaGoi=service['MaGoi'],
                    LoaiVeApDung=service['LoaiVeApDung'],
                    ThamSo=service['ThamSo']
                )
                db.session.add(new_service)

        db.session.commit()

        services = DichVuVe.query.filter_by(MaHHK=ma_hhk).all()
        services_data = [{
            'MaDV': service.MaDV,
            'MaGoi': service.MaGoi,
            'LoaiVeApDung': service.LoaiVeApDung,
            'ThamSo': float(service.ThamSo)
        } for service in services]

        return jsonify({
            'status': True,
            'message': 'Cập nhật hãng hàng không và dịch vụ vé thành công',
            'data': {
                'MaHHK': airline.MaHHK,
                'TenHHK': airline.TenHHK,
                'MaQG': airline.MaQG,
                'dich_vu_ve': services_data
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'status': False,
            'message': 'Dữ liệu không hợp lệ',
            'error': str(e)
        }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi cập nhật hãng hàng không',
            'error': str(e)
        }), 500
@hanghangkhong.route('/api/hang-hang-khong/<string:ma_hhk>', methods=['GET'])
def get_hang_hang_khong_detail(ma_hhk):
    try:
        airline = HangHangKhong.query.filter_by(MaHHK=ma_hhk).first()
        if not airline:
            return jsonify({
                'status': False,
                'message': f"Không tìm thấy hãng hàng không với mã '{ma_hhk}'"
            }), 404
            
        # Get related services information
        dich_vu_ve_list = DichVuVe.query.filter_by(MaHHK=ma_hhk).all()
        services_data = []
        
        for dv_ve in dich_vu_ve_list:
            dich_vu = DichVu.query.get(dv_ve.MaDV)
            goi_dv = GoiDichVu.query.get(dv_ve.MaGoi)
            
            service_info = {
                'dich_vu': {
                    'MaDV': dich_vu.MaDV,
                    'TenDichVu': dich_vu.TenDichVu,
                    'MoTa': dich_vu.MoTa,
                    'TrangThai': dich_vu.TrangThai
                },
                'goi_dich_vu': {
                    'MaGoi': goi_dv.MaGoi,
                    'TenGoi': goi_dv.TenGoi,
                    'MoTa': goi_dv.MoTa,
                    'HeSoGia': float(goi_dv.HeSoGia),
                    'TrangThai': goi_dv.TrangThai
                },
                'dich_vu_ve': {
                    'LoaiVeApDung': dv_ve.LoaiVeApDung,
                    'ThamSo': float(dv_ve.ThamSo) if dv_ve.ThamSo else None
                }
            }
            services_data.append(service_info)
            
        return jsonify({    
            'status': True,
            'message': 'Lấy thông tin hãng hàng không thành công',
            'data': {
                'MaHHK': airline.MaHHK,
                'TenHHK': airline.TenHHK,
                'MaQG': airline.MaQG,
                'dich_vu': services_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Có lỗi xảy ra khi lấy thông tin hãng hàng không',
            'error': str(e)
        }), 500

@hanghangkhong.route('/api/hang-hang-khong/<string:ma_hhk>', methods=['DELETE'])
def delete_hang_hang_khong(ma_hhk):
    try:
        airline = HangHangKhong.query.filter_by(MaHHK=ma_hhk).first()
        
        if not airline:
            return jsonify({
                'status': False,
                'message': f"Không tìm thấy hãng hàng không với mã '{ma_hhk}'"
            }), 404
            
        existing_planes = MayBay.query.filter_by(MaHHK=ma_hhk).first()
        if existing_planes:
            return jsonify({
                'status': False,
                'message': 'Không thể xóa hãng hàng không vì vẫn còn dữ liệu thuộc hãng này'
            }), 400


        DichVuVe.query.filter_by(MaHHK=ma_hhk).delete()
        
        db.session.delete(airline)
        db.session.commit()
        
        return jsonify({
            'status': True,
            'message': 'Xóa hãng hàng không và các dịch vụ vé liên quan thành công',
            'data': {
                'MaHHK': airline.MaHHK,
                'TenHHK': airline.TenHHK,
                'MaQG': airline.MaQG
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': 'Có lỗi khi xóa hãng hàng không',
            'error': str(e)
        }), 500