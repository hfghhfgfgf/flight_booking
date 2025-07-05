from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from app.models import *
from app import db
from sqlalchemy import and_

dichvuve = Blueprint('dichvuve', __name__)

def get_flight_services(flight_dict):
    try:
        ma_hhk = flight_dict['ma_hhk']
        loai_ve = 'Business' if flight_dict.get('loai_ghe', '').upper() == 'BUS' else 'Economy'
        
        services = db.session.query(
            DichVuVe, DichVu, GoiDichVu
        ).join(
            DichVu,
            DichVuVe.MaDV == DichVu.MaDV
        ).join(
            GoiDichVu,
            DichVuVe.MaGoi == GoiDichVu.MaGoi
        ).filter(
            DichVuVe.MaHHK == ma_hhk,
            DichVuVe.LoaiVeApDung == loai_ve,
            GoiDichVu.TrangThai == 0
        ).all()

        if not services:
            return {}

        packages = {}
        for dv_ve, dv, goi in services:
            if goi.MaGoi not in packages:
                base_price = flight_dict['gia_ve_bus'] if loai_ve == 'Business' else flight_dict['gia_ve_eco']
                if base_price is None:
                    continue
                    
                package_price = float(base_price) * float(goi.HeSoGia)
                
                packages[goi.MaGoi] = {
                    'ma_goi': goi.MaGoi,
                    'ten_goi': goi.TenGoi,
                    'mo_ta': goi.MoTa,
                    'gia_goi': package_price,
                    'dich_vu': []
                }
            
            chi_tiet = ''
            if 'xách tay' in dv.TenDichVu.lower():
                chi_tiet = f'Được phép mang {int(dv_ve.ThamSo)}kg hành lý xách tay'
            elif 'ký gửi' in dv.TenDichVu.lower():
                chi_tiet = f'Được phép ký gửi {int(dv_ve.ThamSo)}kg hành lý'
            elif 'đổi' in dv.TenDichVu.lower():
                chi_tiet = f'Phí đổi vé: {int(dv_ve.ThamSo)}% giá vé'
            elif 'hoàn' in dv.TenDichVu.lower():
                chi_tiet = f'Hoàn {int(dv_ve.ThamSo)}% giá vé'
            elif 'bảo hiểm' in dv.TenDichVu.lower():
                chi_tiet = 'Có bảo hiểm du lịch' if dv_ve.ThamSo > 0 else 'Không có bảo hiểm'

            packages[goi.MaGoi]['dich_vu'].append({
                'ma_dv': dv.MaDV,
                'ten_dich_vu': dv.TenDichVu,
                'mo_ta': dv.MoTa,
                'tham_so': float(dv_ve.ThamSo),
                'chi_tiet': chi_tiet
            })
        
        return packages
        
    except Exception as e:
        print(f"Get flight services error: {str(e)}")
        return {}

def flight_to_dict(flight, loai_ghe='ECO'):
    try:
        return {
            'ma_chuyen_bay': flight.MaChuyenBay,
            'hang_hang_khong': flight.may_bay.hang_hang_khong.TenHHK,
            'ma_hhk': flight.may_bay.MaHHK,
            'san_bay_di': flight.san_bay_di.ThanhPho,
            'san_bay_den': flight.san_bay_den.ThanhPho,
            'ma_sb_di' : flight.MaSanBayDi,
            'ma_sb_den' : flight.MaSanBayDen,
            'thoi_gian_di': flight.ThoiGianDi.isoformat(),
            'thoi_gian_den': flight.ThoiGianDen.isoformat(),
            'gia_ve_eco': float(flight.GiaVeEco) if flight.GiaVeEco else None,
            'gia_ve_bus': float(flight.GiaVeBus) if flight.GiaVeBus else None,
            'loai_ghe': loai_ghe.upper(),
            'thoi_gian_bay': (flight.ThoiGianDen - flight.ThoiGianDi).total_seconds() / 3600,
        }
    except Exception as e:
        print(f"Convert flight to dict error: {str(e)}")
        return {}

@dichvuve.route('/api/flights/<ma_chuyen_bay>/services', methods=['POST'])
def get_flight_services_api(ma_chuyen_bay):
    try:
        data = request.get_json()
        loai_ghe = data.get('loai_ghe', 'ECO').upper()
        
        flight = ChuyenBay.query\
            .join(MayBay)\
            .join(HangHangKhong)\
            .filter(ChuyenBay.MaChuyenBay == ma_chuyen_bay)\
            .first()
            
        if not flight:
            return jsonify({'error': 'Flight not found'}), 404

        flight_info = {
            'ma_hhk': flight.may_bay.MaHHK,
            'loai_ghe': loai_ghe,
            'gia_ve_eco': float(flight.GiaVeEco) if flight.GiaVeEco else None,
            'gia_ve_bus': float(flight.GiaVeBus) if flight.GiaVeBus else None
        }

        services = get_flight_services(flight_info)

        return jsonify({
            'flight': flight_to_dict(flight, loai_ghe),
            'goi_dich_vu': services
        })

    except Exception as e:
        print(f"Get flight services error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@dichvuve.route('/api/packages/<int:ma_goi>/luggage', methods=['GET'])  
def get_package_luggage(ma_goi):
    try:
        hang_hang_khong = request.args.get('hang_hang_khong')
        loai_ve = request.args.get('loai_ve')

        if not hang_hang_khong or not loai_ve:
            return jsonify({
                'error': 'Thiếu thông tin hãng hàng không hoặc loại vé'
            }), 400

        if loai_ve not in ['ECO', 'BUS']:
            return jsonify({
                'error': 'Loại vé không hợp lệ. Chỉ chấp nhận ECO hoặc BUS'
            }), 400

        loai_ve_mapping = {
            'ECO': 'Economy',
            'BUS': 'Business'
        }
        loai_ve_query = loai_ve_mapping.get(loai_ve)

        hang_hk = HangHangKhong.query.filter(
            (HangHangKhong.TenHHK == hang_hang_khong) | 
            (HangHangKhong.MaHHK == hang_hang_khong)
        ).first()
        
        if not hang_hk:
            return jsonify({
                'error': f'Không tìm thấy hãng hàng không: {hang_hang_khong}'
            }), 404

        goi_dv = GoiDichVu.query.get(ma_goi)
        if not goi_dv:
            return jsonify({'error': f'Không tìm thấy gói dịch vụ với mã {ma_goi}'}), 404

        luggage_info = db.session.query(
            DichVu.MaDV,
            DichVu.TenDichVu,
            DichVuVe.ThamSo,
            HangHangKhong.TenHHK
        ).join(
            DichVuVe, 
            DichVu.MaDV == DichVuVe.MaDV
        ).join(
            HangHangKhong,
            DichVuVe.MaHHK == HangHangKhong.MaHHK
        ).filter(
            DichVuVe.MaGoi == ma_goi,
            DichVuVe.MaHHK == hang_hk.MaHHK, 
            DichVuVe.LoaiVeApDung == loai_ve_query,
            DichVu.TenDichVu.in_(['Hành lý xách tay', 'Hành lý ký gửi'])
        ).all()

        if not luggage_info:
            return jsonify({
                'error': f'Không tìm thấy thông tin hành lý cho gói {ma_goi}, ' + 
                        f'hãng {hang_hang_khong}, loại vé {loai_ve}'
            }), 404

        luggage_details = {}
        total_weight = 0
        ten_hang = None
        
        for item in luggage_info:
            weight = float(item.ThamSo) if item.ThamSo else 0
            luggage_details[item.TenDichVu] = weight
            total_weight += weight
            if not ten_hang:
                ten_hang = item.TenHHK

        return jsonify({
            'ma_goi': ma_goi,
            'ten_goi': goi_dv.TenGoi,
            'hang_hang_khong': ten_hang,
            'loai_ve': loai_ve,  # Trả về ECO/BUS như input
            'tong_hanh_ly': total_weight,
            'chi_tiet': {
                'hanh_ly_xach_tay': luggage_details.get('Hành lý xách tay', 0),
                'hanh_ly_ky_gui': luggage_details.get('Hành lý ký gửi', 0)
            }
        })

    except Exception as e:
        print(f"Error getting luggage info: {str(e)}")
        return jsonify({'error': 'Lỗi hệ thống'}), 500

@dichvuve.route('/api/banks', methods=['GET'])
def get_banks():
    try:
        banks = db.session.query(TheThanhToan.NganHang).distinct().all()
        
        bank_list = [
            {
                'id': index + 1,
                'name': bank[0], 
                'code': bank[0].lower().replace(' ', '_')
            } 
            for index, bank in enumerate(banks)
        ]
        
        return jsonify({
            'success': True,
            'data': bank_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dichvuve.route('/api/meals', methods=['GET'])
def get_meals():
    try:
        # Lấy loại vé từ request (mặc định là economy)
        loai_ve = request.args.get('loai_ve', 'eco').lower()
        
        # Query lấy tất cả món ăn đang phục vụ và còn trong thời gian hiệu lực
        today = datetime.utcnow() + timedelta(hours=7)
        print(today)
        meals = MonAn.query.filter(
            and_(
                MonAn.TrangThai == 0,
                MonAn.NgayBatDau <= today,
                MonAn.NgayKetThuc >= today
            )
        ).order_by(MonAn.LoaiMonAn, MonAn.TenMonAn).all()
        
        # Chuẩn bị dữ liệu trả về
        result = []
        for meal in meals:
            result.append({
                'ma_mon': meal.MaMonAn,
                'ten_mon': meal.TenMonAn,
                'mo_ta': meal.MoTa,
                'hinh_anh': meal.HinhAnh,
                'loai_mon': meal.LoaiMonAn,
                'gia': meal.GiaEco if loai_ve == 'eco' else meal.GiaBus
            })
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500