from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models import DichVuHanhLy, HanhKhach, DatCho, ChiTietDatCho
from app import db

dichvuhanhly = Blueprint('dichvuhanhly', __name__)

@dichvuhanhly.route('/api/flights/<ma_chuyen_bay>/luggage-services', methods=['GET'])
def get_luggage_services(ma_chuyen_bay):
    try:
        services = DichVuHanhLy.query.filter_by(MaCB=ma_chuyen_bay).all()
        
        return jsonify({
            'dich_vu_hanh_ly': [{
                'ma_dich_vu': dv.MaDichVu,
                'so_ky': dv.SoKy,
                'gia': float(dv.Gia),
                'mo_ta': dv.MoTa
            } for dv in services]
        })
    except Exception as e:
        print(f"Get luggage services error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# @dichvuhanhly.route('/api/booking/<ma_dat_cho>/luggage', methods=['POST'])
# def add_luggage_services(ma_dat_cho):
#     try:
#         data = request.get_json()
        
#         booking = DatCho.query.get(ma_dat_cho)
#         if not booking:
#             return jsonify({'error': 'Không tìm thấy đặt chỗ'}), 404
            
#         if booking.TrangThai != 'Đang thanh toán':
#             return jsonify({'error': 'Không thể thêm dịch vụ cho đặt chỗ này'}), 400

#         for luggage_data in data['dich_vu_hanh_ly']:
#             ma_hk = luggage_data.get('ma_hanh_khach')
#             ma_dv = luggage_data.get('ma_dich_vu')
            
#             if not ma_hk or not ma_dv:
#                 continue
                
#             dich_vu = DichVuHanhLy.query.filter_by(
#                 MaDichVu=ma_dv,
#                 MaCB=booking.MaCB
#             ).first()
            
#             if not dich_vu:
#                 return jsonify({'error': f'Dịch vụ hành lý không hợp lệ: {ma_dv}'}), 400

#             chi_tiet = ChiTietDatCho.query.filter_by(
#                 MaDatCho=ma_dat_cho,
#                 MaHK=ma_hk
#             ).first()
            
#             if chi_tiet:
#                 chi_tiet.MaDichVu = ma_dv

#         db.session.commit()
        
#         updated_services = db.session.query(
#             HanhKhach, DichVuHanhLy
#         ).join(
#             ChiTietDatCho, HanhKhach.MaHanhKhach == ChiTietDatCho.MaHK
#         ).outerjoin(
#             DichVuHanhLy, ChiTietDatCho.MaDichVu == DichVuHanhLy.MaDichVu
#         ).filter(
#             ChiTietDatCho.MaDatCho == ma_dat_cho
#         ).all()

#         return jsonify({
#             'hanh_khach': [{
#                 'ma_hk': hk.MaHanhKhach,
#                 'ho_ten': f"{hk.HoHK} {hk.TenHK}",
#                 'dich_vu_hanh_ly': {
#                     'ma_dich_vu': dv.MaDichVu,
#                     'so_ky': dv.SoKy,
#                     'gia': float(dv.Gia),
#                     'mo_ta': dv.MoTa
#                 } if dv else None
#             } for hk, dv in updated_services]
#         })

#     except Exception as e:
#         db.session.rollback()
#         print(f"Add luggage services error: {str(e)}")
#         return jsonify({'error': str(e)}), 500
