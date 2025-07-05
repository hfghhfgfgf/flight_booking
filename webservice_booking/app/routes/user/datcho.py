from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models import *
from app import db
from email_utils import send_booking_confirmation_email, send_booking_cancellation_email, send_booking_cancellation_rejected_email
from sqlalchemy import case, or_
from sqlalchemy.orm import aliased
from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

datcho = Blueprint('datcho', __name__)

now = datetime.utcnow() + timedelta(hours=7)

# @datcho.route('/api/booking', methods=['POST'])
# def create_booking():
#     try:
#         BookingTamThoi.cleanup_expired()
        
#         data = request.get_json()
        
#         required_contact = ['ho_nlh', 'ten_nlh', 'email', 'sdt']
#         for field in required_contact:
#             if field not in data['nguoi_lien_he']:
#                 return jsonify({'error': f'Thiếu thông tin người liên hệ: {field}'}), 400

#         required_passenger = ['ho_hk', 'ten_hk', 'danh_xung', 'cccd', 'ngay_sinh', 'quoc_tich', 'loai_hk']
#         for passenger in data['hanh_khach']:
#             for field in required_passenger:
#                 if field not in passenger:
#                     return jsonify({'error': f'Thiếu thông tin hành khách: {field}'}), 400
            
#             if 'dich_vu_hanh_ly' in passenger:
#                 for flight_luggage in passenger['dich_vu_hanh_ly']:
#                     ma_chuyen_bay = flight_luggage.get('ma_chuyen_bay')
#                     ma_dich_vu = flight_luggage.get('ma_dich_vu_hanh_ly') 
                    
#                     if ma_dich_vu:
#                         dich_vu = DichVuHanhLy.query.get(ma_dich_vu)
#                         if not dich_vu or dich_vu.MaCB != ma_chuyen_bay:
#                             return jsonify({'error': f'Dịch vụ hành lý không hợp lệ cho chuyến bay {ma_chuyen_bay}'}), 400

#         flight_updates = {}
#         first_flight = None
#         for flight_info in data['chuyen_bay']:
#             ma_chuyen_bay = flight_info['ma_chuyen_bay']
#             so_ghe_bus = flight_info.get('so_ghe_bus', 0) 
#             so_ghe_eco = flight_info.get('so_ghe_eco', 0)
#             ma_goi = flight_info.get('ma_goi')
            
#             flight = ChuyenBay.query.get(ma_chuyen_bay)
#             if not flight:
#                 return jsonify({'error': f'Không tìm thấy chuyến bay {ma_chuyen_bay}'}), 404
            
#             if ma_goi:
#                 goi_dv = GoiDichVu.query.get(ma_goi)
#                 if not goi_dv:
#                     return jsonify({'error': f'Không tìm thấy gói dịch vụ {ma_goi}'}), 404
#                 if goi_dv.TrangThai != 0:  
#                     return jsonify({'error': f'Gói dịch vụ {ma_goi} không khả dụng'}), 400
            
#             if first_flight is None:
#                 first_flight = flight
                
#             if flight.SLBusConLai < so_ghe_bus:
#                 return jsonify({'error': f'Không đủ ghế Business cho chuyến bay {ma_chuyen_bay}'}), 400
#             if flight.SLEcoConLai < so_ghe_eco:
#                 return jsonify({'error': f'Không đủ ghế Economy cho chuyến bay {ma_chuyen_bay}'}), 400
                
#             flight_updates[ma_chuyen_bay] = {
#                 'ma_hhk': flight.may_bay.MaHHK,  
#                 'SLBusConLai': flight.SLBusConLai - so_ghe_bus,
#                 'SLEcoConLai': flight.SLEcoConLai - so_ghe_eco
#             }

#         ma_hhk = first_flight.may_bay.MaHHK if first_flight else "unknown" 
#         generated_code = ChuyenBay.generate_flight_code(ma_hhk)
#         timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  
#         booking_code = f"{generated_code}-{timestamp}"

#         response_data = {
#             'booking_id': booking_code,
#             'expires_in': 600,
#             'thong_tin_dat_cho': {
#                 'nguoi_lien_he': {
#                     'ho_ten': f"{data['nguoi_lien_he']['ho_nlh']} {data['nguoi_lien_he']['ten_nlh']}",
#                     'email': data['nguoi_lien_he']['email'],
#                     'sdt': data['nguoi_lien_he']['sdt']
#                 },
#                 'hanh_khach': [{
#                     'ho_ten': f"{p['ho_hk']} {p['ten_hk']}",
#                     'cccd': p['cccd'],
#                     'danh_xung': p['danh_xung'],
#                     'ngay_sinh': p['ngay_sinh'],
#                     'quoc_tich': p['quoc_tich'],
#                     'loai_hk': p['loai_hk'],
#                     'dich_vu_hanh_ly': p.get('dich_vu_hanh_ly', [])
#                 } for p in data['hanh_khach']],
#                 'chuyen_bay': [{
#                     'ma_chuyen_bay': flight['ma_chuyen_bay'],
#                     'so_ghe_bus': flight.get('so_ghe_bus', 0),
#                     'so_ghe_eco': flight.get('so_ghe_eco', 0),
#                     'ma_goi': flight.get('ma_goi')
#                 } for flight in data['chuyen_bay']],
#                 'flight_updates': flight_updates
#             }
#         }

#         temp_booking = BookingTamThoi(
#             BookingId=booking_code,
#             Data=response_data,
#             CreatedAt=now,
#             ExpiresAt=now + timedelta(minutes=10)
#         )

#         db.session.add(temp_booking)
#         db.session.commit()
#         return jsonify(response_data)

#     except Exception as e:
#         db.session.rollback()
#         print(f"Booking error: {str(e)}")
#         return jsonify({'error': str(e)}), 500 

# @datcho.route('/api/bookings/<booking_id>/<user_id>/confirm', methods=['POST'])
# def confirm_booking(booking_id, user_id):
#     try:
#         data = request.get_json()
#         print('data', data)
#         phuong_thuc = data.get('phuong_thuc')
#         if phuong_thuc == 'Card':
#             card_info = data.get('card_info')
#             if not card_info:
#                 return jsonify({'error': 'Thiếu thông tin thẻ thanh toán'}), 400
                
#             the_tt = TheThanhToan.query.filter_by(
#                 SoThe=card_info['so_the'].replace(" ", ""),
#                 TenChuThe=card_info['ten_chu_the'],
#                 NganHang=card_info['ngan_hang']
#             ).first()

#             if not the_tt:
#                 return jsonify({'error': 'Thông tin thẻ không hợp lệ'}), 400
                
#             if the_tt.SoDu < data.get('tong_tien', 0):
#                 return jsonify({'error': 'Số dư không đủ để thực hiện giao dịch'}), 400
                
#             the_tt.SoDu -= data.get('tong_tien', 0)
#             db.session.add(the_tt)

#         BookingTamThoi.cleanup_expired()
#         temp_booking = BookingTamThoi.query.get(booking_id)
#         if not temp_booking or temp_booking.ExpiresAt < now:
#             return jsonify({'error': 'Đặt chỗ đã hết hạn hoặc không tồn tại'}), 404

#         booking_data = temp_booking.Data
#         thong_tin = booking_data['thong_tin_dat_cho']
#         flight_updates = thong_tin.get('flight_updates', {})
       
#         tien_giam = 0
#         ma_khuyen_mai = data.get('ma_khuyen_mai')  
#         tong_tien = data.get('tong_tien', 0) 

#         if ma_khuyen_mai: 
#             khuyen_mai = KhuyenMai.query.get(ma_khuyen_mai)
#             if khuyen_mai and khuyen_mai.is_valid():
#                 tien_giam = khuyen_mai.calculate_discount(tong_tien)
#             else:
#                 return jsonify({'error': 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn'}), 400

#         email = thong_tin['nguoi_lien_he']['email']
#         nguoi_lien_he = NguoiLienHe.query.filter_by(Email=email).first()
#         if nguoi_lien_he:
#             nguoi_lien_he.HoNLH = " ".join(thong_tin['nguoi_lien_he']['ho_ten'].split()[:-1])
#             nguoi_lien_he.TenNLH = thong_tin['nguoi_lien_he']['ho_ten'].split()[-1]
#             nguoi_lien_he.SDT = thong_tin['nguoi_lien_he']['sdt']
#         else:
#             nguoi_lien_he = NguoiLienHe(
#                 HoNLH=" ".join(thong_tin['nguoi_lien_he']['ho_ten'].split()[:-1]),
#                 TenNLH=thong_tin['nguoi_lien_he']['ho_ten'].split()[-1],
#                 Email=email,
#                 SDT=thong_tin['nguoi_lien_he']['sdt']
#             )
#             db.session.add(nguoi_lien_he)
#         db.session.flush()

#         dat_cho_goc = DatCho(
#             MaCB=thong_tin['chuyen_bay'][0]['ma_chuyen_bay'],
#             MaNLH=nguoi_lien_he.MaNLH,
#             SoLuongGheBus=thong_tin['chuyen_bay'][0]['so_ghe_bus'],
#             SoLuongGheEco=thong_tin['chuyen_bay'][0]['so_ghe_eco'],
#             MaGoi=thong_tin['chuyen_bay'][0].get('ma_goi'),  
#             TrangThai='Đã thanh toán',
#             NgayMua=now,
#             MaND=user_id
#         )
#         db.session.add(dat_cho_goc)
#         db.session.flush()

#         danh_sach_dat_cho = [dat_cho_goc]

#         for chuyen_bay in thong_tin['chuyen_bay'][1:]:
#             dat_cho = DatCho(
#                 MaCB=chuyen_bay['ma_chuyen_bay'],
#                 MaNLH=nguoi_lien_he.MaNLH,
#                 SoLuongGheBus=chuyen_bay['so_ghe_bus'],
#                 SoLuongGheEco=chuyen_bay['so_ghe_eco'],
#                 MaGoi=chuyen_bay.get('ma_goi'), 
#                 TrangThai='Đã thanh toán',
#                 NgayMua=now,
#                 MaND=user_id,
#                 MaDatChoGoc=dat_cho_goc.MaDatCho 
#             )
#             db.session.add(dat_cho)
#             db.session.flush()
#             danh_sach_dat_cho.append(dat_cho)

#         for hanh_khach_data in thong_tin['hanh_khach']:
#             cccd = hanh_khach_data['cccd']
#             hanh_khach = HanhKhach.query.filter_by(CCCD=cccd).first()
#             if hanh_khach:
#                 hanh_khach.HoHK = " ".join(hanh_khach_data['ho_ten'].split()[:-1])
#                 hanh_khach.TenHK = hanh_khach_data['ho_ten'].split()[-1]
#                 hanh_khach.DanhXung = hanh_khach_data.get('danh_xung', '')
#                 hanh_khach.NgaySinh = datetime.strptime(hanh_khach_data['ngay_sinh'], '%d-%m-%Y').date()
#                 hanh_khach.QuocTich = hanh_khach_data.get('quoc_tich', 'Việt Nam')
#                 hanh_khach.LoaiHK = hanh_khach_data['loai_hk']
#             else:
#                 hanh_khach = HanhKhach(
#                     HoHK=" ".join(hanh_khach_data['ho_ten'].split()[:-1]),
#                     TenHK=hanh_khach_data['ho_ten'].split()[-1],
#                     DanhXung=hanh_khach_data.get('danh_xung', ''),
#                     CCCD=cccd,
#                     NgaySinh=datetime.strptime(hanh_khach_data['ngay_sinh'], '%d-%m-%Y').date(),
#                     QuocTich=hanh_khach_data.get('quoc_tich', 'Việt Nam'),
#                     LoaiHK=hanh_khach_data['loai_hk']
#                 )
#                 db.session.add(hanh_khach)
#             db.session.flush()
#             dich_vu_hanh_ly = hanh_khach_data.get('dich_vu_hanh_ly', [])
#             dich_vu_map = {item['ma_chuyen_bay']: item['ma_dich_vu_hanh_ly'] for item in dich_vu_hanh_ly}

#             for dat_cho in danh_sach_dat_cho:
#                 chi_tiet = ChiTietDatCho(
#                     MaDatCho=dat_cho.MaDatCho,
#                     MaHK=hanh_khach.MaHanhKhach,
#                     MaDichVu=dich_vu_map.get(dat_cho.MaCB) 
#                 )
#                 db.session.add(chi_tiet)

#         for ma_chuyen_bay, update_data in flight_updates.items():
#             flight = ChuyenBay.query.get(ma_chuyen_bay)
#             if flight:
#                 flight.SLBusConLai = update_data['SLBusConLai']
#                 flight.SLEcoConLai = update_data['SLEcoConLai']
#                 db.session.add(flight)

#         tong_tien_hanh_ly = 0
#         for hanh_khach_data in thong_tin['hanh_khach']:
#             dich_vu_hanh_ly = hanh_khach_data.get('dich_vu_hanh_ly', [])
#             for hanh_ly in dich_vu_hanh_ly:
#                 dich_vu = DichVuHanhLy.query.filter_by(
#                     MaDichVu=hanh_ly['ma_dich_vu_hanh_ly'],
#                     MaCB=hanh_ly['ma_chuyen_bay']
#                 ).first()
#                 if dich_vu:
#                     tong_tien_hanh_ly += dich_vu.Gia

#         thanh_toan = ThanhToan(
#             MaDatCho=dat_cho_goc.MaDatCho,  
#             MaKhuyenMai=ma_khuyen_mai if ma_khuyen_mai else None,
#             TienGiam=tien_giam,
#             Thue=0,
#             SoTien=tong_tien - tien_giam + tong_tien_hanh_ly,
#             NgayThanhToan=now,
#             PhuongThuc=phuong_thuc
#         )
#         db.session.add(thanh_toan)

#         db.session.delete(temp_booking)
#         db.session.commit()

#         booking_info = {
#             'ma_dat_cho_goc': dat_cho_goc.MaDatCho,
#             'ho_ten_lien_he': thong_tin['nguoi_lien_he']['ho_ten'],
#             'email_lien_he': email,
#             'ngay_mua': dat_cho_goc.NgayMua.strftime('%d-%m-%Y %H:%M:%S'), 
#             'tong_tien': f"{tong_tien + tong_tien_hanh_ly:,.0f}", 
#             'tien_giam': f"{tien_giam:,.0f}", 
#             'phuong_thuc': phuong_thuc
#         }
#         send_booking_confirmation_email(to_email=email, booking_info=booking_info)

#         return jsonify({
#             'success': True,
#             'ma_dat_cho': [dat_cho.MaDatCho for dat_cho in danh_sach_dat_cho],
#             'ma_dat_cho_goc': dat_cho_goc.MaDatCho,
#             'tien_giam': tien_giam,
#             'tong_tien': thanh_toan.SoTien,
#             'message': 'Đặt chỗ thành công'
#         })

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

@datcho.route('/api/booking', methods=['POST'])
def create_booking():
    try:
        BookingTamThoi.cleanup_expired()
        
        data = request.get_json()
        
        # Kiểm tra thông tin người liên hệ
        required_contact = ['ho_nlh', 'ten_nlh', 'email', 'sdt']
        for field in required_contact:
            if field not in data['nguoi_lien_he']:
                return jsonify({'error': f'Thiếu thông tin người liên hệ: {field}'}), 400

        # Kiểm tra thông tin hành khách
        required_passenger = ['ho_hk', 'ten_hk', 'danh_xung', 'cccd', 'ngay_sinh', 'quoc_tich', 'loai_hk']
        for passenger in data['hanh_khach']:
            for field in required_passenger:
                if field not in passenger:
                    return jsonify({'error': f'Thiếu thông tin hành khách: {field}'}), 400
            
            # Kiểm tra dịch vụ món ăn
            if 'dich_vu_mon_an' in passenger:
                for meal in passenger['dich_vu_mon_an']:
                    ma_mon = meal.get('ma_mon')
                    if ma_mon:
                        mon_an = MonAn.query.get(ma_mon)
                        if not mon_an:
                            return jsonify({'error': f'Món ăn không tồn tại: {ma_mon}'}), 400
                        if mon_an.TrangThai != 0:
                            return jsonify({'error': f'Món ăn không khả dụng: {mon_an.TenMonAn}'}), 400
                        current_date = datetime.now().date()
                        if current_date < mon_an.NgayBatDau or current_date > mon_an.NgayKetThuc:
                            return jsonify({'error': f'Món ăn không trong thời gian phục vụ: {mon_an.TenMonAn}'}), 400

        # Xử lý thông tin chuyến bay và tạo booking code
        flight_updates = {}
        first_flight = None
        loai_ghe = None  # Để xác định giá món ăn theo hạng vé

        for flight_info in data['chuyen_bay']:
            ma_chuyen_bay = flight_info['ma_chuyen_bay']
            so_ghe_bus = flight_info.get('so_ghe_bus', 0) 
            so_ghe_eco = flight_info.get('so_ghe_eco', 0)
            ma_goi = flight_info.get('ma_goi')
            
            flight = ChuyenBay.query.get(ma_chuyen_bay)
            if not flight:
                return jsonify({'error': f'Không tìm thấy chuyến bay {ma_chuyen_bay}'}), 404
            
            if first_flight is None:
                first_flight = flight
                loai_ghe = 'BUS' if so_ghe_bus > 0 else 'ECO'
            
            if flight.SLBusConLai < so_ghe_bus:
                return jsonify({'error': f'Không đủ ghế Business cho chuyến bay {ma_chuyen_bay}'}), 400
            if flight.SLEcoConLai < so_ghe_eco:
                return jsonify({'error': f'Không đủ ghế Economy cho chuyến bay {ma_chuyen_bay}'}), 400
                
            flight_updates[ma_chuyen_bay] = {
                'ma_hhk': flight.may_bay.MaHHK,  
                'SLBusConLai': flight.SLBusConLai - so_ghe_bus,
                'SLEcoConLai': flight.SLEcoConLai - so_ghe_eco
            }

        # Tạo booking code
        ma_hhk = first_flight.may_bay.MaHHK if first_flight else "unknown" 
        generated_code = ChuyenBay.generate_flight_code(ma_hhk)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  
        booking_code = f"{generated_code}-{timestamp}"

        # Tính tổng tiền món ăn
        tong_tien_mon_an = 0
        for passenger in data['hanh_khach']:
            if 'dich_vu_mon_an' in passenger:
                for meal in passenger['dich_vu_mon_an']:
                    mon_an = MonAn.query.get(meal['ma_mon'])
                    if mon_an:
                        gia = mon_an.GiaBus if loai_ghe == 'BUS' else mon_an.GiaEco
                        tong_tien_mon_an += gia * meal['so_luong']

        response_data = {
            'booking_id': booking_code,
            'expires_in': 600,
            'thong_tin_dat_cho': {
                'nguoi_lien_he': {
                    'ho_ten': f"{data['nguoi_lien_he']['ho_nlh']} {data['nguoi_lien_he']['ten_nlh']}",
                    'email': data['nguoi_lien_he']['email'],
                    'sdt': data['nguoi_lien_he']['sdt']
                },
                'hanh_khach': [{
                    'ho_ten': f"{p['ho_hk']} {p['ten_hk']}",
                    'cccd': p['cccd'],
                    'danh_xung': p['danh_xung'],
                    'ngay_sinh': p['ngay_sinh'],
                    'quoc_tich': p['quoc_tich'],
                    'loai_hk': p['loai_hk'],
                    'dich_vu_hanh_ly': p.get('dich_vu_hanh_ly', []),
                    'dich_vu_mon_an': p.get('dich_vu_mon_an', [])
                } for p in data['hanh_khach']],
                'chuyen_bay': [{
                    'ma_chuyen_bay': flight['ma_chuyen_bay'],
                    'so_ghe_bus': flight.get('so_ghe_bus', 0),
                    'so_ghe_eco': flight.get('so_ghe_eco', 0),
                    'ma_goi': flight.get('ma_goi')
                } for flight in data['chuyen_bay']],
                'flight_updates': flight_updates,
                'tong_tien_mon_an': float(tong_tien_mon_an)  # Chuyển Decimal thành float
            }
        }

        # Chuyển đổi toàn bộ response_data thành JSON với DecimalEncoder
        json_data = json.dumps(response_data, cls=DecimalEncoder)
        response_data = json.loads(json_data)  # Chuyển lại thành dict

        temp_booking = BookingTamThoi(
            BookingId=booking_code,
            Data=response_data,  # Đã được xử lý Decimal
            CreatedAt=now,
            ExpiresAt=now + timedelta(minutes=10)
        )

        db.session.add(temp_booking)
        db.session.commit()
        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        print(f"Booking error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@datcho.route('/api/bookings/<booking_id>/<user_id>/confirm', methods=['POST'])
def confirm_booking(booking_id, user_id):
    try:
        data = request.get_json()
        phuong_thuc = data.get('phuong_thuc')
        
        # Xử lý thanh toán bằng thẻ
        if phuong_thuc == 'Card':
            card_info = data.get('card_info')
            if not card_info:
                return jsonify({'error': 'Thiếu thông tin thẻ thanh toán'}), 400
                
            the_tt = TheThanhToan.query.filter_by(
                SoThe=card_info['so_the'].replace(" ", ""),
                TenChuThe=card_info['ten_chu_the'],
                NganHang=card_info['ngan_hang']
            ).first()

            if not the_tt:
                return jsonify({'error': 'Thông tin thẻ không hợp lệ'}), 400
                
            if the_tt.SoDu < data.get('tong_tien', 0):
                return jsonify({'error': 'Số dư không đủ để thực hiện giao dịch'}), 400
                
            the_tt.SoDu -= data.get('tong_tien', 0)
            db.session.add(the_tt)

        # Kiểm tra và lấy booking tạm thời
        BookingTamThoi.cleanup_expired()
        temp_booking = BookingTamThoi.query.get(booking_id)
        if not temp_booking or temp_booking.ExpiresAt < now:
            return jsonify({'error': 'Đặt chỗ đã hết hạn hoặc không tồn tại'}), 404

        booking_data = temp_booking.Data
        thong_tin = booking_data['thong_tin_dat_cho']
        flight_updates = thong_tin.get('flight_updates', {})
        
        # Xử lý khuyến mãi
        tien_giam = 0
        ma_khuyen_mai = data.get('ma_khuyen_mai')  
        tong_tien = data.get('tong_tien', 0) 

        if ma_khuyen_mai: 
            khuyen_mai = KhuyenMai.query.get(ma_khuyen_mai)
            if khuyen_mai and khuyen_mai.is_valid():
                tien_giam = khuyen_mai.calculate_discount(tong_tien)
            else:
                return jsonify({'error': 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn'}), 400

        # Xử lý người liên hệ
        ho_ten = thong_tin['nguoi_lien_he']['ho_ten'].split()
        email = thong_tin['nguoi_lien_he']['email']
        
        nguoi_lien_he = NguoiLienHe.query.filter_by(Email=email).first()
        if nguoi_lien_he:
            nguoi_lien_he.HoNLH = ' '.join(ho_ten[:-1])
            nguoi_lien_he.TenNLH = ho_ten[-1]
            nguoi_lien_he.SDT = thong_tin['nguoi_lien_he']['sdt']
        else:
            nguoi_lien_he = NguoiLienHe(
                HoNLH=' '.join(ho_ten[:-1]),
                TenNLH=ho_ten[-1],
                Email=email,
                SDT=thong_tin['nguoi_lien_he']['sdt']
            )
            db.session.add(nguoi_lien_he)
        db.session.flush()

        # Tạo đặt chỗ
        danh_sach_dat_cho = []
        for idx, chuyen_bay in enumerate(thong_tin['chuyen_bay']):
            dat_cho = DatCho(
                MaCB=chuyen_bay['ma_chuyen_bay'],
                MaNLH=nguoi_lien_he.MaNLH,
                SoLuongGheBus=chuyen_bay['so_ghe_bus'],
                SoLuongGheEco=chuyen_bay['so_ghe_eco'],
                MaGoi=chuyen_bay.get('ma_goi'),
                TrangThai='Đã thanh toán',
                NgayMua=now,
                MaND=user_id,
            )
            if idx == 0:
                dat_cho_goc = dat_cho
            else:
                dat_cho.MaDatChoGoc = dat_cho_goc.MaDatCho

            db.session.add(dat_cho)
            db.session.flush()
            danh_sach_dat_cho.append(dat_cho)

        # Xử lý hành khách và dịch vụ
        tong_tien_hanh_ly = 0
        tong_tien_mon_an = 0

        for hanh_khach_data in thong_tin['hanh_khach']:
            ho_ten = hanh_khach_data['ho_ten'].split()
            cccd = hanh_khach_data['cccd']
            
            # Xử lý hành khách
            hanh_khach = HanhKhach.query.filter_by(CCCD=cccd).first()
            if hanh_khach:
                hanh_khach.HoHK = ' '.join(ho_ten[:-1])
                hanh_khach.TenHK = ho_ten[-1]
                hanh_khach.DanhXung = hanh_khach_data['danh_xung']
                hanh_khach.NgaySinh = datetime.strptime(hanh_khach_data['ngay_sinh'], '%d-%m-%Y').date()
                hanh_khach.QuocTich = hanh_khach_data['quoc_tich']
                hanh_khach.LoaiHK = hanh_khach_data['loai_hk']
            else:
                hanh_khach = HanhKhach(
                    HoHK=' '.join(ho_ten[:-1]),
                    TenHK=ho_ten[-1],
                    DanhXung=hanh_khach_data['danh_xung'],
                    CCCD=cccd,
                    NgaySinh=datetime.strptime(hanh_khach_data['ngay_sinh'], '%d-%m-%Y').date(),
                    QuocTich=hanh_khach_data['quoc_tich'],
                    LoaiHK=hanh_khach_data['loai_hk']
                )
                db.session.add(hanh_khach)
            db.session.flush()

            dich_vu_mon_an = hanh_khach_data.get('dich_vu_mon_an', [])
            for dat_cho in danh_sach_dat_cho:
                chi_tiet_dat_cho = ChiTietDatCho(
                    MaDatCho=dat_cho.MaDatCho,
                    MaHK=hanh_khach.MaHanhKhach
                )
                db.session.add(chi_tiet_dat_cho)
                db.session.flush()  

                for mon_an_data in dich_vu_mon_an:
                    chi_tiet_mon_an = ChiTietDatChoMonAn(
                        MaDatCho=dat_cho.MaDatCho,
                        MaHK=hanh_khach.MaHanhKhach,
                        MaMonAn=mon_an_data['ma_mon'],
                        SoLuong=mon_an_data['so_luong']
                    )
                    db.session.add(chi_tiet_mon_an)
                    tong_tien_mon_an += mon_an_data['gia'] * mon_an_data['so_luong']

            # Xử lý dịch vụ hành lý
            dich_vu_hanh_ly = hanh_khach_data.get('dich_vu_hanh_ly', [])
            for hanh_ly in dich_vu_hanh_ly:
                dich_vu = DichVuHanhLy.query.filter_by(
                    MaDichVu=hanh_ly['ma_dich_vu_hanh_ly'],
                    MaCB=hanh_ly['ma_chuyen_bay']
                ).first()
                if dich_vu:
                    tong_tien_hanh_ly += dich_vu.Gia

        # Cập nhật số ghế
        for ma_chuyen_bay, update_data in flight_updates.items():
            flight = ChuyenBay.query.get(ma_chuyen_bay)
            if flight:
                flight.SLBusConLai = update_data['SLBusConLai']
                flight.SLEcoConLai = update_data['SLEcoConLai']
                db.session.add(flight)
        
        # Tạo thanh toán
        thanh_toan = ThanhToan(
            MaDatCho=dat_cho_goc.MaDatCho,
            MaKhuyenMai=ma_khuyen_mai if ma_khuyen_mai else None,
            TienGiam=tien_giam,
            Thue=0,
            SoTien=tong_tien - tien_giam + tong_tien_hanh_ly + tong_tien_mon_an,
            NgayThanhToan=now,
            PhuongThuc=phuong_thuc
        )
        db.session.add(thanh_toan)

        # Xóa booking tạm thời và commit
        db.session.delete(temp_booking)
        db.session.commit()

        # Gửi email
        booking_info = {
            'ma_dat_cho_goc': dat_cho_goc.MaDatCho,
            'ho_ten_lien_he': thong_tin['nguoi_lien_he']['ho_ten'],
            'email_lien_he': email,
            'ngay_mua': dat_cho_goc.NgayMua.strftime('%d-%m-%Y %H:%M:%S'),
            'tong_tien': f"{tong_tien + tong_tien_hanh_ly + tong_tien_mon_an:,.0f}",
            'tien_giam': f"{tien_giam:,.0f}",
            'phuong_thuc': phuong_thuc
        }
        send_booking_confirmation_email(to_email=email, booking_info=booking_info)

        return jsonify({
            'success': True,
            'ma_dat_cho': [dat_cho.MaDatCho for dat_cho in danh_sach_dat_cho],
            'ma_dat_cho_goc': dat_cho_goc.MaDatCho,
            'tien_giam': tien_giam,
            'tong_tien': thanh_toan.SoTien,
            'message': 'Đặt chỗ thành công'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error confirming booking: {str(e)}")
        return jsonify({'error': str(e)}), 500


@datcho.route('/api/booking/info/<int:mand>', methods=['GET'])
def get_booking_info(mand):
    try:
        booking_ids = db.session.query(
            case(
                (DatCho.MaDatChoGoc != None, DatCho.MaDatChoGoc),
                else_=DatCho.MaDatCho
            ).label("MaDatCho")
        ).filter(
            DatCho.MaND == mand
        ).distinct().all()

        result = []
        SanBayDen = db.aliased(SanBay)
        
        for booking_id in booking_ids:
            flights = db.session.query(
                DatCho.MaDatCho,
                DatCho.NgayMua,
                DatCho.TrangThai,
                DatCho.SoLuongGheBus,
                DatCho.SoLuongGheEco,
                DatCho.MaCB,
                SanBay.ThanhPho.label('ThanhPhoDi'),
                SanBayDen.ThanhPho.label('ThanhPhoDen')
            ).join(
                ChuyenBay, DatCho.MaCB == ChuyenBay.MaChuyenBay
            ).join(
                SanBay, ChuyenBay.MaSanBayDi == SanBay.MaSanBay
            ).join(
                SanBayDen, ChuyenBay.MaSanBayDen == SanBayDen.MaSanBay
            ).filter(
                or_(
                    DatCho.MaDatCho == booking_id.MaDatCho,
                    DatCho.MaDatChoGoc == booking_id.MaDatCho
                )
            ).all()

            is_round_trip = False
            if len(flights) == 2:
                if flights[0].ThanhPhoDi == flights[1].ThanhPhoDen and flights[0].ThanhPhoDen == flights[1].ThanhPhoDi:
                    is_round_trip = True

            first_flight = flights[0]
            flight_list = []
            
            # Tạo danh sách chuyến bay
            for flight in flights:
                flight_list.append({
                    "MaChuyenBay": flight.MaCB,
                    "ThanhPhoDi": flight.ThanhPhoDi,
                    "ThanhPhoDen": flight.ThanhPhoDen
                })

            result.append({
                "MaDatCho": first_flight.MaDatCho,
                "NgayMua": first_flight.NgayMua.strftime('%Y-%m-%d %H:%M:%S') if first_flight.NgayMua else None,
                "TrangThai": first_flight.TrangThai,
                "SoLuongGheBus": first_flight.SoLuongGheBus,
                "SoLuongGheEco": first_flight.SoLuongGheEco,
                "LoaiVe": "Khứ hồi" if is_round_trip else "Một chiều",
                "ChuyenBay": flight_list
            })

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@datcho.route('/api/booking/all', methods=['GET'])
def get_all_bookings():
    try:
        booking_ids = db.session.query(
            case(
                (DatCho.MaDatChoGoc != None, DatCho.MaDatChoGoc),
                else_=DatCho.MaDatCho
            ).label("MaDatCho")
        ).distinct().all()

        result = []
        SanBayDen = db.aliased(SanBay)
        
        for booking_id in booking_ids:
            flights = db.session.query(
                DatCho.MaDatCho,
                DatCho.NgayMua,
                DatCho.TrangThai,
                DatCho.SoLuongGheBus,
                DatCho.SoLuongGheEco,
                DatCho.MaCB,
                SanBay.ThanhPho.label('ThanhPhoDi'),
                SanBayDen.ThanhPho.label('ThanhPhoDen')
            ).join(
                ChuyenBay, DatCho.MaCB == ChuyenBay.MaChuyenBay
            ).join(
                SanBay, ChuyenBay.MaSanBayDi == SanBay.MaSanBay
            ).join(
                SanBayDen, ChuyenBay.MaSanBayDen == SanBayDen.MaSanBay
            ).filter(
                or_(
                    DatCho.MaDatCho == booking_id.MaDatCho,
                    DatCho.MaDatChoGoc == booking_id.MaDatCho
                )
            ).all()

            is_round_trip = False
            if len(flights) == 2:
                if flights[0].ThanhPhoDi == flights[1].ThanhPhoDen and flights[0].ThanhPhoDen == flights[1].ThanhPhoDi:
                    is_round_trip = True

            first_flight = flights[0]
            flight_list = []
            
            for flight in flights:
                flight_list.append({
                    "MaChuyenBay": flight.MaCB,
                    "ThanhPhoDi": flight.ThanhPhoDi,
                    "ThanhPhoDen": flight.ThanhPhoDen
                })

            result.append({
                "MaDatCho": first_flight.MaDatCho,
                "NgayMua": first_flight.NgayMua.strftime('%Y-%m-%d %H:%M:%S') if first_flight.NgayMua else None,
                "TrangThai": first_flight.TrangThai,
                "SoLuongGheBus": first_flight.SoLuongGheBus,
                "SoLuongGheEco": first_flight.SoLuongGheEco,
                "LoaiVe": "Khứ hồi" if is_round_trip else "Một chiều",
                "ChuyenBay": flight_list
            })

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@datcho.route('/api/get_booking_detailed/<int:madatcho>', methods=['GET'])
def get_booking_detailed(madatcho):
    try:
        booking = DatCho.query.get(madatcho)
        if not booking:
            return jsonify({
                "status": "error",
                "message": 'Mã đặt chỗ không tồn tại! Vui lòng nhập mã đặt chỗ khác!'
            }), 500
        
        SanBayDi = aliased(SanBay)
        SanBayDen = aliased(SanBay)

        bookings = db.session.query(
            DatCho, 
            ChuyenBay,
            NguoiLienHe,
            SanBayDi,
            SanBayDen,
            HangHangKhong,
            MayBay,
            GoiDichVu 
        ).join(
            ChuyenBay, DatCho.MaCB == ChuyenBay.MaChuyenBay
        ).join(
            NguoiLienHe, DatCho.MaNLH == NguoiLienHe.MaNLH
        ).join(
            SanBayDi, ChuyenBay.MaSanBayDi == SanBayDi.MaSanBay
        ).join(
            SanBayDen, ChuyenBay.MaSanBayDen == SanBayDen.MaSanBay
        ).join(
            MayBay, ChuyenBay.MaMB == MayBay.MaMayBay
        ).join(
            HangHangKhong, MayBay.MaHHK == HangHangKhong.MaHHK
        ).outerjoin(  
            GoiDichVu, DatCho.MaGoi == GoiDichVu.MaGoi
        ).filter(
            or_(
                DatCho.MaDatCho == madatcho,
                DatCho.MaDatChoGoc == madatcho,
                DatCho.MaDatCho == db.session.query(DatCho.MaDatChoGoc).filter(
                    DatCho.MaDatCho == madatcho,
                    DatCho.MaDatChoGoc != None
                ).scalar()
            )
        ).all()

        result = []
        for booking, flight, contact, dep_airport, arr_airport, airline, aircraft, goi_dv in bookings:
            dich_vu_ve = []
            if goi_dv:
                dich_vu_ve = db.session.query(
                    DichVuVe, 
                    DichVu
                ).join(
                    DichVu, DichVuVe.MaDV == DichVu.MaDV
                ).filter(
                    DichVuVe.MaGoi == goi_dv.MaGoi,
                    DichVuVe.MaHHK == airline.MaHHK
                ).all()
            payment = db.session.query(ThanhToan).filter(
                ThanhToan.MaDatCho == booking.MaDatCho
            ).first()

            passengers_and_luggage = db.session.query(
                HanhKhach,
                DichVuHanhLy
            ).join(
                ChiTietDatCho, HanhKhach.MaHanhKhach == ChiTietDatCho.MaHK
            ).outerjoin(
                DichVuHanhLy, ChiTietDatCho.MaDichVu == DichVuHanhLy.MaDichVu
            ).filter(
                ChiTietDatCho.MaDatCho == booking.MaDatCho
            ).all()

            booking_info = {
                "MaChuyenBay": flight.MaChuyenBay,
                "MaDatCho": booking.MaDatCho,
                "MaDatChoGoc": booking.MaDatChoGoc,
                "NgayBay": 1 if flight.ThoiGianDi.date() == datetime.now().date() else 0,
                "ChuyenBay": {
                    "ThoiGianDi": flight.ThoiGianDi.strftime('%Y-%m-%d %H:%M:%S'),
                    "ThoiGianDen": flight.ThoiGianDen.strftime('%Y-%m-%d %H:%M:%S'),
                    "SanBayDi": {
                        "MaSanBay": dep_airport.MaSanBay,
                        "TenSanBay": dep_airport.TenSanBay,
                        "ThanhPho": dep_airport.ThanhPho
                    },
                    "SanBayDen": {
                        "MaSanBay": arr_airport.MaSanBay,
                        "TenSanBay": arr_airport.TenSanBay,
                        "ThanhPho": arr_airport.ThanhPho
                    },
                    "HangBay": {
                        "MaHHK": airline.MaHHK,
                        "TenHHK": airline.TenHHK
                    },
                    "MayBay": {
                        "MaMayBay": aircraft.MaMayBay,
                        "TenMayBay": aircraft.TenMayBay,
                        "LoaiMayBay": aircraft.LoaiMB
                    },
                    "LoaiChuyenBay": flight.LoaiChuyenBay,
                    "GiaVe": {
                        "Business": float(flight.GiaVeBus) if flight.GiaVeBus else 0,
                        "Economy": float(flight.GiaVeEco) if flight.GiaVeEco else 0
                    }
                },
                "DatCho": {
                    "SoLuongGhe": {
                        "Business": booking.SoLuongGheBus,
                        "Economy": booking.SoLuongGheEco
                    },
                    "NgayMua": booking.NgayMua.strftime('%Y-%m-%d %H:%M:%S'),
                    "TrangThai": booking.TrangThai,
                    "GoiDichVu": {
                        "MaGoi": goi_dv.MaGoi if goi_dv else None,
                        "TenGoi": goi_dv.TenGoi if goi_dv else None,
                        "MoTa": goi_dv.MoTa if goi_dv else None,
                        "HeSoGia": float(goi_dv.HeSoGia) if goi_dv else None,
                        "DichVu": [{
                            "TenDichVu": dv.TenDichVu,
                            "MoTa": dv.MoTa,
                            "LoaiVeApDung": dv_ve.LoaiVeApDung,
                            "ThamSo": float(dv_ve.ThamSo) if dv_ve.ThamSo else None
                        } for dv_ve, dv in dich_vu_ve] if dich_vu_ve else []
                    } if goi_dv else None
                },
                "NguoiLienHe": {
                    "Ho": contact.HoNLH,
                    "Ten": contact.TenNLH,
                    "SDT": contact.SDT,
                    "Email": contact.Email
                },
                "HanhKhach": [{
                    "DanhXung": passenger.DanhXung,
                    "Ho": passenger.HoHK,
                    "Ten": passenger.TenHK,
                    "CCCD": passenger.CCCD,
                    "NgaySinh": passenger.NgaySinh.strftime('%Y-%m-%d'),
                    "QuocTich": passenger.QuocTich,
                    "LoaiHK": passenger.LoaiHK,
                    "HanhLy": {
                        "SoKy": luggage.SoKy if luggage else None,
                        "Gia": float(luggage.Gia) if luggage else None,
                        "MoTa": luggage.MoTa if luggage else None
                    } if luggage else None
                } for passenger, luggage in passengers_and_luggage],
                "ThanhToan": {
                    "NgayThanhToan": payment.NgayThanhToan.strftime('%Y-%m-%d %H:%M:%S') if payment else None,
                    "PhuongThuc": payment.PhuongThuc if payment else None,
                    "SoTien": float(payment.SoTien) if payment else None,
                    "TienGiam": float(payment.TienGiam) if payment else None,
                    "Thue": float(payment.Thue) if payment else None
                } if payment else None
            }
            result.append(booking_info)

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@datcho.route('/api/datcho/<int:ma_dat_cho>/huy', methods=['POST'])
def huy_dat_cho(ma_dat_cho):
    try:
        data = request.get_json()
        noi_dung = data.get('noi_dung')

        if not noi_dung:
            return jsonify({
                'success': False,
                'message': 'Thiếu nội dung lý do hủy'
            }), 400

        dat_cho = DatCho.query.get(ma_dat_cho)
        if not dat_cho:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy thông tin đặt chỗ'
            }), 404
        if dat_cho.TrangThai == 'Đã hủy':
            return jsonify({
                'success': False,
                'message': 'Đặt chỗ này đã được hủy trước đó'
            }), 400

        ngay_tao = now

        ly_do_huy = LyDoHuy(
            MaDatCho=ma_dat_cho,
            NoiDung=noi_dung,
            NgayTao=ngay_tao
        )

        dat_cho.TrangThai = 'Đang xử lý'

        db.session.add(ly_do_huy)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Hủy đặt chỗ thành công',
            'data': {
                'ma_dat_cho': ma_dat_cho,
                'noi_dung': noi_dung,
                'ngay_huy': ly_do_huy.NgayTao.isoformat()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Lỗi hệ thống: {str(e)}'
        }), 500

@datcho.route('/api/lydohuy', methods=['GET'])
def get_danh_sach_huy():
    try:
        ds_huy = (db.session.query(LyDoHuy, DatCho)
                 .join(DatCho)
                 .order_by(LyDoHuy.NgayTao.desc())
                 .all())
        
        result = []
        for ly_do, dat_cho in ds_huy:
            result.append({
                'ma_ly_do': ly_do.MaLyDo,
                'ma_dat_cho': ly_do.MaDatCho,
                'noi_dung': ly_do.NoiDung,
                'ngay_tao': ly_do.NgayTao.isoformat(),
                'trang_thai': ly_do.TrangThai,
                'dat_cho': {
                    'ma_dat_cho': dat_cho.MaDatCho,
                    'ngay_mua': dat_cho.NgayMua.isoformat(),
                    'trang_thai': dat_cho.TrangThai,
                    'nguoi_lien_he': {
                        'ho_ten': f"{dat_cho.nguoi_lien_he.HoNLH} {dat_cho.nguoi_lien_he.TenNLH}",
                        'sdt': dat_cho.nguoi_lien_he.SDT,
                        'email': dat_cho.nguoi_lien_he.Email
                    }
                }
            })

        return jsonify({
            'success': True,
            'message': 'Lấy danh sách yêu cầu hủy thành công',
            'data': result
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Lỗi khi lấy danh sách yêu cầu hủy: {str(e)}'
        }), 500

@datcho.route('/api/duyet-huy-dat-cho/<int:ma_dat_cho>', methods=['POST']) 
def duyet_huy_dat_cho(ma_dat_cho):
    try:
        ly_do_huy = LyDoHuy.query.filter_by(
            MaDatCho=ma_dat_cho,
            TrangThai='Chờ duyệt'
        ).first()
        if not ly_do_huy:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy yêu cầu hủy cho đặt chỗ này'
            }), 404

        dat_cho = ly_do_huy.dat_cho
        chuyen_bay = dat_cho.chuyen_bay

        thoi_gian_chenh_lech = chuyen_bay.ThoiGianDi - ly_do_huy.NgayTao
        gio_chenh_lech = thoi_gian_chenh_lech.total_seconds() / 3600

        if gio_chenh_lech < 8:
            return jsonify({
                'success': False,
                'message': 'Không thể hủy đặt chỗ do thời gian đến chuyến bay không đủ 8 tiếng'
            }), 400

        if dat_cho.TrangThai == 'Đã hủy':
            return jsonify({
                'success': False,
                'message': 'Đặt chỗ đã được hủy trước đó'
            }), 400
        ds_huy = []
        
        dat_cho = DatCho.query.get(ma_dat_cho)
        if not dat_cho:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy đặt chỗ'
            }), 404

        if dat_cho.TrangThai == 'Đã hủy':
            return jsonify({
                'success': False,
                'message': 'Đặt chỗ đã được hủy trước đó'
            }), 400
            
        ds_huy.append(dat_cho)
        
        if dat_cho.MaDatChoGoc is None:
            dat_cho_lien_quan = DatCho.query.filter_by(MaDatChoGoc=dat_cho.MaDatCho).all()
            ds_huy.extend(dat_cho_lien_quan)
        else:
            dat_cho_goc = DatCho.query.get(dat_cho.MaDatChoGoc)
            ds_huy.append(dat_cho_goc)
            dat_cho_lien_quan = DatCho.query.filter_by(MaDatChoGoc=dat_cho.MaDatChoGoc).all()
            ds_huy.extend([dc for dc in dat_cho_lien_quan if dc.MaDatCho != dat_cho.MaDatCho])

        result = []
        for dc in ds_huy:
            if dc.TrangThai != 'Đã hủy':  
                ty_le_hoan = 0
                if dc.MaGoi:
                    dich_vu_hoan_ve = DichVu.query.filter_by(TenDichVu='Hoàn vé').first()
                    if dich_vu_hoan_ve:
                        dich_vu_ve = DichVuVe.query.filter_by(
                            MaDV=dich_vu_hoan_ve.MaDV,
                            MaGoi=dc.MaGoi,
                            MaHHK=dc.chuyen_bay.may_bay.MaHHK
                        ).first()
                        
                        if dich_vu_ve:
                            ty_le_hoan = float(dich_vu_ve.ThamSo) / 100

                thanh_toan = ThanhToan.query.filter_by(MaDatCho=dc.MaDatCho).first()
                so_tien_hoan = 0

                if ty_le_hoan > 0:
                    tong_gia_ve = (float(dc.chuyen_bay.GiaVeBus) * dc.SoLuongGheBus + 
                                float(dc.chuyen_bay.GiaVeEco) * dc.SoLuongGheEco)
                    so_tien_hoan = tong_gia_ve * ty_le_hoan
                    
                    if thanh_toan:
                        thanh_toan.SoTien = float(thanh_toan.SoTien) - so_tien_hoan
                        db.session.add(thanh_toan)

                chuyen_bay = dc.chuyen_bay
                if dc.SoLuongGheBus > 0:
                    chuyen_bay.SLBusConLai += dc.SoLuongGheBus
                if dc.SoLuongGheEco > 0:
                    chuyen_bay.SLEcoConLai += dc.SoLuongGheEco
                db.session.add(chuyen_bay)

                dc.TrangThai = 'Đã hủy'
                db.session.add(dc)

                result.append({
                    'ma_dat_cho': ma_dat_cho,
                    'ma_chuyen_bay': dc.MaCB,
                    'ty_le_hoan': f"{ty_le_hoan * 100}%",
                    'so_tien_hoan': round(so_tien_hoan, 0)
                })

        ly_do_huy.TrangThai = 'Đã duyệt'
        ly_do_huy.NgayXuLy = now
        db.session.add(ly_do_huy)

        db.session.commit()

        if result:
            try:
                dat_cho = DatCho.query.get(ma_dat_cho)
                nguoi_lien_he = dat_cho.nguoi_lien_he  
                print("kq:", result)
                if nguoi_lien_he and nguoi_lien_he.Email:
                    email_sent = send_booking_cancellation_email(nguoi_lien_he.Email, {
                        'ds_huy': result,
                        'ngay_duyet': now
                    })
                    if not email_sent:
                        print(f"Không thể gửi email đến {nguoi_lien_he.Email}")
                else:
                    print("Không tìm thấy email trong thông tin người liên hệ")
            except Exception as e:
                print(f"Lỗi khi gửi email: {str(e)}")

        return jsonify({
            'success': True,
            'message': 'Duyệt hủy đặt chỗ thành công',
            'data': {
                'ds_huy': result,
                'ngay_duyet': now
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Lỗi khi duyệt hủy đặt chỗ: {str(e)}'
        }), 500

@datcho.route('/api/tu-choi-huy-dat-cho/<int:ma_dat_cho>', methods=['POST'])
def tu_choi_huy_dat_cho(ma_dat_cho):
    try:
        data = request.get_json()
        ly_do_tu_choi = data.get('ly_do')

        if not ly_do_tu_choi:
            return jsonify({
                'success': False,
                'message': 'Vui lòng cung cấp lý do từ chối'
            }), 400

        ly_do_huy = LyDoHuy.query.filter_by(
            MaDatCho=ma_dat_cho,
            TrangThai='Chờ duyệt'
        ).first()

        if not ly_do_huy:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy yêu cầu hủy cho đặt chỗ này'
            }), 404

        dat_cho = DatCho.query.get(ma_dat_cho)
        if not dat_cho:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy đặt chỗ'
            }), 404

        if dat_cho.TrangThai == 'Đã hủy':
            return jsonify({
                'success': False,
                'message': 'Đặt chỗ đã được hủy trước đó'
            }), 400

        nguoi_lien_he = dat_cho.nguoi_lien_he
        chuyen_bay = dat_cho.chuyen_bay

        ly_do_huy.TrangThai = 'Từ chối'
        ly_do_huy.LyDoTuChoi = ly_do_tu_choi
        ly_do_huy.NgayXuLy = now
        dat_cho.TrangThai = 'Đã thanh toán'
        
        db.session.add(ly_do_huy)
        
        db.session.commit()

        if nguoi_lien_he and nguoi_lien_he.Email:
            try:
                reject_info = {
                    'ma_dat_cho': ma_dat_cho,
                    'ma_chuyen_bay': chuyen_bay.MaChuyenBay,
                    'ly_do': ly_do_tu_choi,
                    'thoi_gian': now,
                    'ho_ten': f"{nguoi_lien_he.HoNLH} {nguoi_lien_he.TenNLH}",
                    'thong_tin_chuyen_bay': {
                        'diem_di': chuyen_bay.san_bay_di.ThanhPho,
                        'diem_den': chuyen_bay.san_bay_den.ThanhPho,
                        'thoi_gian_di': chuyen_bay.ThoiGianDi.strftime('%d/%m/%Y %H:%M')
                    }
                }

                send_booking_cancellation_rejected_email(
                    nguoi_lien_he.Email, 
                    reject_info
                )
            except Exception as e:
                print(f"Lỗi khi gửi email: {str(e)}")

        return jsonify({
            'success': True,
            'message': 'Đã từ chối yêu cầu hủy đặt chỗ',
            'data': {
                'ma_dat_cho': ma_dat_cho,
                'ly_do_tu_choi': ly_do_tu_choi,
                'ngay_xu_ly': now
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Lỗi khi từ chối hủy đặt chỗ: {str(e)}'
        }), 500