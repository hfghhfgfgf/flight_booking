from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from app.models import HangHangKhong, KhuyenMai, HHK_KhuyenMai, CB_KhuyenMai
from app import db
from sqlalchemy import or_


khuyenmai = Blueprint('khuyenmai', __name__)

@khuyenmai.route('/api/bookings/temp/promotions', methods=['POST'])
def get_temp_booking_promotions():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Không có dữ liệu gửi lên'}), 400
            
        list_hang_hang_khong = data.get('hang_hang_khong', []) 
        list_ma_chuyen_bay = data.get('ma_chuyen_bay', [])
        tong_tien = data.get('tong_tien', 0)
        
        # if not list_hang_hang_khong or not list_ma_chuyen_bay or not tong_tien:
        #     return jsonify({'error': 'Thiếu thông tin cần thiết'}), 400
            
        hang_hang_khong_info = HangHangKhong.query.filter(
            HangHangKhong.TenHHK.in_(list_hang_hang_khong)
        ).all()
        
        if not hang_hang_khong_info:
            return jsonify({'error': 'Không tìm thấy hãng hàng không'}), 404
            
        ma_hhk_list = [hhk.MaHHK for hhk in hang_hang_khong_info]
        current_date = datetime.now().date()
        
        all_promotions = KhuyenMai.query.filter(
            KhuyenMai.NgayBatDau <= current_date,
            KhuyenMai.NgayKetThuc >= current_date
        ).all()

        promotions_result = {
            'HANG_HANG_KHONG': [],
            'CHUYEN_BAY': []
        }

        for km in all_promotions:
            if km.ds_hang_hang_khong:
                for hhk in km.ds_hang_hang_khong:
                    if hhk.MaHHK in ma_hhk_list:
                        tien_giam = km.calculate_discount(tong_tien)
                        promotions_result['HANG_HANG_KHONG'].append({
                            'ma_khuyen_mai': km.MaKhuyenMai,
                            'ten_khuyen_mai': km.TenKhuyenMai,
                            'mo_ta': km.MoTa,
                            'loai_khuyen_mai': km.LoaiKhuyenMai,
                            'gia_tri': float(km.GiaTri),
                            'tien_giam': float(tien_giam),
                            'ap_dung_cho': hhk.TenHHK
                        })
                        
            if km.ds_chuyen_bay:
                km_flight_codes = {cb.MaChuyenBay for cb in km.ds_chuyen_bay}
                matching_flights = set(list_ma_chuyen_bay) & km_flight_codes
                
                if matching_flights:
                    tien_giam = km.calculate_discount(tong_tien)
                    promotions_result['CHUYEN_BAY'].append({
                        'ma_khuyen_mai': km.MaKhuyenMai,
                        'ten_khuyen_mai': km.TenKhuyenMai,
                        'mo_ta': km.MoTa,
                        'loai_khuyen_mai': km.LoaiKhuyenMai,
                        'gia_tri': float(km.GiaTri),
                        'tien_giam': float(tien_giam),
                        'ap_dung_cho': list(matching_flights)
                    })

        return jsonify({
            'tong_tien': float(tong_tien),
            'khuyen_mai': promotions_result
        })

    except Exception as e:
        print(f"Error getting promotions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@khuyenmai.route('/api/promotions', methods=['GET','POST'])
def get_valid_promotions():
    try:
        data = request.get_json()
        ma_hhk = data.get('ma_hhk', None)
        ma_cb = data.get('ma_cb', None)
        current_date = datetime.now().date()
        current_datetime = datetime.now()

        query = KhuyenMai.query.filter(
            KhuyenMai.NgayBatDau <= current_date,
            KhuyenMai.NgayKetThuc >= current_date
        ).filter(or_(
            KhuyenMai.ds_hang_hang_khong.any(),
            KhuyenMai.ds_chuyen_bay.any()
        ))

        if ma_hhk:
            query = query.filter(KhuyenMai.ds_hang_hang_khong.any(MaHHK=ma_hhk))

        if ma_cb:
            query = query.filter(KhuyenMai.ds_chuyen_bay.any(MaChuyenBay=ma_cb))

        promotions = query.all()
        result = []
        
        for km in promotions:
            valid_flights = []
            if km.ds_chuyen_bay:
                for cb in km.ds_chuyen_bay:
                    if (cb.TrangThai == 0 and 
                        cb.ThoiGianDi > current_datetime): 
                        valid_flights.append({
                            'ma_cb': cb.MaChuyenBay,
                            'thoi_gian_di': cb.ThoiGianDi.strftime('%Y-%m-%d %H:%M:%S'),
                            'thoi_gian_den': cb.ThoiGianDen.strftime('%Y-%m-%d %H:%M:%S')
                        })
            
            if km.ds_hang_hang_khong or valid_flights:
                promotion_data = {
                    'ma_khuyen_mai': km.MaKhuyenMai,
                    'ten_khuyen_mai': km.TenKhuyenMai,
                    'mo_ta': km.MoTa,
                    'loai_khuyen_mai': km.LoaiKhuyenMai,
                    'gia_tri': float(km.GiaTri),
                    'ngay_bat_dau': km.NgayBatDau.strftime('%Y-%m-%d'),
                    'ngay_ket_thuc': km.NgayKetThuc.strftime('%Y-%m-%d'),
                    'hang_hang_khong': [{'ma_hhk': hhk.MaHHK, 'ten_hhk': hhk.TenHHK} 
                                      for hhk in km.ds_hang_hang_khong] if km.ds_hang_hang_khong else [],
                    'chuyen_bay': valid_flights
                }
                result.append(promotion_data)

        return jsonify({
            'status': 'success',
            'message': 'Lấy danh sách khuyến mãi thành công',
            'data': result
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Đã có lỗi xảy ra khi lấy danh sách khuyến mãi'
        }), 500