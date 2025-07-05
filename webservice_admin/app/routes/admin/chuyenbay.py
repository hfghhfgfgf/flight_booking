from sqlite3 import IntegrityError
from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from app.models import *
from app import db
chuyenbay_admin = Blueprint('chuyenbay_admin', __name__)

@chuyenbay_admin.route('/api/airlines', methods=['GET'])
def get_airlines():
    try:
        airlines = HangHangKhong.query.all()
        return jsonify({
            'status': 'success',
            'data': [{
                'code': airline.MaHHK,
                'name': airline.TenHHK
            } for airline in airlines]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chuyenbay_admin.route('/api/airports', methods=['GET'])
def get_airports():
    try:
        airports = SanBay.query.all()
        return jsonify({
            'status': 'success',
            'data': [{
                'code': airport.MaSanBay,
                'name': airport.TenSanBay,
                'city': airport.ThanhPho,
                'type': airport.LoaiSB
            } for airport in airports]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chuyenbay_admin.route('/api/aircrafts', methods=['GET'])
def get_aircrafts():
    try:
        aircrafts = MayBay.query.join(HangHangKhong).all()

        result = [{
            'id': aircraft.MaMayBay,
            'name': f"{aircraft.TenMayBay} - {aircraft.hang_hang_khong.TenHHK}",
            'seats_bus': aircraft.SoChoNgoiBus,
            'seats_eco': aircraft.SoChoNgoiEco
        } for aircraft in aircrafts]

        return jsonify({
            'status': 'success',
            'data': result
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chuyenbay_admin.route('/api/flights', methods=['GET'])
def get_filtered_flights():
    try:
        filters = {
            'MaChuyenBay': request.args.get('flight_code'),
            'MaMB': request.args.get('aircraft_id', type=int),
            'MaSanBayDi': request.args.get('departure_airport'),
            'MaSanBayDen': request.args.get('arrival_airport'),
            'ThoiGianDi': request.args.get('departure_time'),
            'ThoiGianDen': request.args.get('arrival_time'),
            'SLGheBus': request.args.get('business_seats', type=int),
            'SLGheEco': request.args.get('economy_seats', type=int),
            'SLBusConLai': request.args.get('available_business', type=int),
            'SLEcoConLai': request.args.get('available_economy', type=int),
            'LoaiChuyenBay': request.args.get('flight_type'),
            'GiaVeBus': request.args.get('business_price', type=float),
            'GiaVeEco': request.args.get('economy_price', type=float),
            'TrangThaiVe': request.args.get('ticket_status', type=int),
            'TrangThai': request.args.get('status', type=int)
        }

        query = ChuyenBay.query

        ma_hhk = request.args.get('airline_code')
        if ma_hhk:
            query = query.join(MayBay).filter(MayBay.MaHHK == ma_hhk)
        
        filter_conditions = []
        for field, value in filters.items():
            if value is not None:
                if field in ['ThoiGianDi', 'ThoiGianDen']:
                    try:
                        date_range = value.split(',')
                        if len(date_range) == 2:
                            start_date, end_date = date_range
                            filter_conditions.append(
                                and_(
                                    getattr(ChuyenBay, field) >= start_date,
                                    getattr(ChuyenBay, field) <= end_date
                                )
                            )
                        else:
                            filter_conditions.append(getattr(ChuyenBay, field) == value)
                    except:
                        filter_conditions.append(getattr(ChuyenBay, field) == value)
                else:
                    filter_conditions.append(getattr(ChuyenBay, field) == value)
        
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))

        sort_by = request.args.get('sort_by', 'ThoiGianDi')  
        sort_order = request.args.get('sort_order', 'asc')  
        
        if hasattr(ChuyenBay, sort_by):
            if sort_order == 'desc':
                query = query.order_by(getattr(ChuyenBay, sort_by).desc())
            else:
                query = query.order_by(getattr(ChuyenBay, sort_by).asc())

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        flights = [{
            'flight_code': flight.MaChuyenBay,
            'aircraft_id': flight.MaMB,
            'departure_airport': flight.MaSanBayDi,
            'departure_time': flight.ThoiGianDi.isoformat() if flight.ThoiGianDi else None,
            'arrival_airport': flight.MaSanBayDen,
            'arrival_time': flight.ThoiGianDen.isoformat() if flight.ThoiGianDen else None,
            'business_seats': flight.SLGheBus,
            'economy_seats': flight.SLGheEco,
            'available_business': flight.SLBusConLai,
            'available_economy': flight.SLEcoConLai,
            'flight_type': flight.LoaiChuyenBay,
            'business_price': float(flight.GiaVeBus) if flight.GiaVeBus else None,
            'economy_price': float(flight.GiaVeEco) if flight.GiaVeEco else None,
            'ticket_status': flight.TrangThaiVe,
            'status': flight.TrangThai
        } for flight in pagination.items]

        return jsonify({
            'status': 'success',
            'data': {
                'flights': flights,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chuyenbay_admin.route('/api/flight', methods=['POST'])
def create_flight():
    try:
        data = request.get_json()
        
        required_fields = [
            'MaMB', 'MaSanBayDi', 'MaSanBayDen', 'ThoiGianDi', 
            'ThoiGianDen', 'LoaiChuyenBay', 'GiaVeBus', 'GiaVeEco'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Thiếu trường {field}'
                }), 400

        may_bay = MayBay.query.get(data['MaMB'])
        if not may_bay:
            return jsonify({
                'status': 'error',
                'message': 'Không tìm thấy máy bay'
            }), 404

        hang_hang_khong = may_bay.hang_hang_khong

        try:
            ma_chuyen_bay = ChuyenBay.generate_flight_code(hang_hang_khong.MaHHK)

            thoi_gian_di = datetime.strptime(data['ThoiGianDi'], '%Y-%m-%dT%H:%M')
            thoi_gian_den = datetime.strptime(data['ThoiGianDen'], '%Y-%m-%dT%H:%M')

            chuyen_bay = ChuyenBay(
                MaChuyenBay=ma_chuyen_bay,
                MaMB=data['MaMB'],
                MaSanBayDi=data['MaSanBayDi'],
                ThoiGianDi=thoi_gian_di,
                MaSanBayDen=data['MaSanBayDen'],
                ThoiGianDen=thoi_gian_den,
                SLGheBus=may_bay.SoChoNgoiBus,
                SLGheEco=may_bay.SoChoNgoiEco,
                SLBusConLai=may_bay.SoChoNgoiBus,
                SLEcoConLai=may_bay.SoChoNgoiEco,
                LoaiChuyenBay=data['LoaiChuyenBay'],
                GiaVeBus=data['GiaVeBus'],
                GiaVeEco=data['GiaVeEco'],
                TrangThaiVe=0,
                TrangThai=0
            )
            
            db.session.add(chuyen_bay)
            
            if 'DichVuHanhLy' in data and isinstance(data['DichVuHanhLy'], list):
                for dich_vu in data['DichVuHanhLy']:
                    if not all(k in dich_vu for k in ('SoKy', 'Gia', 'MoTa')):
                        raise ValueError('Thiếu thông tin dịch vụ hành lý')

                    dich_vu_hanh_ly = DichVuHanhLy(
                        MaCB=ma_chuyen_bay,
                        SoKy=dich_vu['SoKy'],
                        Gia=dich_vu['Gia'],
                        MoTa=dich_vu['MoTa']
                    )
                    db.session.add(dich_vu_hanh_ly)

            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'Tạo chuyến bay thành công',
                'data': {
                    'flight_code': ma_chuyen_bay
                }
            }), 201

        except (IntegrityError, ValueError) as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chuyenbay_admin.route('/api/flight/<string:ma_chuyen_bay>', methods=['PUT'])
def update_flight(ma_chuyen_bay):
    try:
        data = request.get_json()
        
        chuyen_bay = ChuyenBay.query.get(ma_chuyen_bay)
        if not chuyen_bay:
            return jsonify({
                'status': 'error',
                'message': 'Không tìm thấy chuyến bay'
            }), 404
        print(data['TrangThai'])
        if data['TrangThai'] == 1:  
            if (chuyen_bay.SLGheBus != chuyen_bay.SLBusConLai or 
                chuyen_bay.SLGheEco != chuyen_bay.SLEcoConLai):
                return jsonify({
                    'status': 'error',
                    'message': 'Không thể sửa chuyến bay vì đã có vé được bán ra'
                }), 400

        required_fields = [
            'MaMB', 'MaSanBayDi', 'MaSanBayDen', 
            'ThoiGianDi', 'ThoiGianDen', 'LoaiChuyenBay', 
            'GiaVeEco'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Thiếu trường {field}'
                }), 400
                
        try:
            may_bay = MayBay.query.get(data['MaMB'])
            if not may_bay:
                return jsonify({
                    'status': 'error',
                    'message': 'Không tìm thấy máy bay'
                }), 404
                
            thoi_gian_di = datetime.strptime(data['ThoiGianDi'], '%Y-%m-%dT%H:%M')
            thoi_gian_den = datetime.strptime(data['ThoiGianDen'], '%Y-%m-%dT%H:%M')
            
            if thoi_gian_di >= thoi_gian_den:
                return jsonify({
                    'status': 'error',
                    'message': 'Thời gian đến phải sau thời gian đi'
                }), 400
            
            chuyen_bay.MaMB = data['MaMB']
            chuyen_bay.MaSanBayDi = data['MaSanBayDi']
            chuyen_bay.MaSanBayDen = data['MaSanBayDen']
            chuyen_bay.ThoiGianDi = thoi_gian_di
            chuyen_bay.ThoiGianDen = thoi_gian_den
            chuyen_bay.LoaiChuyenBay = data['LoaiChuyenBay']
            chuyen_bay.GiaVeBus = data.get('GiaVeBus', 0)
            chuyen_bay.GiaVeEco = data['GiaVeEco']
            chuyen_bay.TrangThai = data['TrangThai'] 

            # if data['TrangThai'] == 1:
            #     chuyen_bay.TrangThaiVe = 1
            
            if may_bay.MaMayBay != chuyen_bay.MaMB:
                if (may_bay.SoChoNgoiBus < (may_bay.SoChoNgoiBus - chuyen_bay.SLBusConLai) or 
                    may_bay.SoChoNgoiEco < (may_bay.SoChoNgoiEco - chuyen_bay.SLEcoConLai)):
                    return jsonify({
                        'status': 'error',
                        'message': 'Máy bay mới không đủ chỗ cho các vé đã đặt'
                    }), 400
                
                chuyen_bay.SLGheBus = may_bay.SoChoNgoiBus
                chuyen_bay.SLGheEco = may_bay.SoChoNgoiEco
                chuyen_bay.SLBusConLai = may_bay.SoChoNgoiBus - (may_bay.SoChoNgoiBus - chuyen_bay.SLBusConLai)
                chuyen_bay.SLEcoConLai = may_bay.SoChoNgoiEco - (may_bay.SoChoNgoiEco - chuyen_bay.SLEcoConLai)
            
            if 'DichVuHanhLy' in data:
                DichVuHanhLy.query.filter_by(MaCB=ma_chuyen_bay).delete()
                
                for dich_vu in data['DichVuHanhLy']:
                    if not all(k in dich_vu for k in ('SoKy', 'Gia', 'MoTa')):
                        raise ValueError('Thiếu thông tin dịch vụ hành lý')
                        
                    dich_vu_hanh_ly = DichVuHanhLy(
                        MaCB=ma_chuyen_bay,
                        SoKy=dich_vu['SoKy'],
                        Gia=dich_vu['Gia'],
                        MoTa=dich_vu['MoTa']
                    )
                    db.session.add(dich_vu_hanh_ly)
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Cập nhật chuyến bay thành công',
                'data': {
                    'flight_code': ma_chuyen_bay
                }
            }), 200
            
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': 'Lỗi cập nhật dữ liệu: ' + str(e)
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chuyenbay_admin.route('/api/flight/<string:ma_chuyen_bay>', methods=['GET'])
def get_flight(ma_chuyen_bay):
    try:
        chuyen_bay = ChuyenBay.query.get(ma_chuyen_bay)
        if not chuyen_bay:
            return jsonify({
                'status': 'error',
                'message': 'Không tìm thấy chuyến bay'
            }), 404
            
        dich_vu_hanh_ly = DichVuHanhLy.query.filter_by(MaCB=ma_chuyen_bay).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'MaMB': chuyen_bay.MaMB,
                'LoaiChuyenBay': chuyen_bay.LoaiChuyenBay,
                'MaSanBayDi': chuyen_bay.MaSanBayDi,
                'MaSanBayDen': chuyen_bay.MaSanBayDen,
                'ThoiGianDi': chuyen_bay.ThoiGianDi.isoformat(),
                'ThoiGianDen': chuyen_bay.ThoiGianDen.isoformat(),
                'GiaVeBus': float(chuyen_bay.GiaVeBus) if chuyen_bay.GiaVeBus else 0,
                'GiaVeEco': float(chuyen_bay.GiaVeEco),
                'TrangThai': float(chuyen_bay.TrangThai),
                'DichVuHanhLy': [{
                    'SoKy': dv.SoKy,
                    'Gia': float(dv.Gia),
                    'MoTa': dv.MoTa
                } for dv in dich_vu_hanh_ly]
            }
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
