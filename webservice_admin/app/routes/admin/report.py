
from flask import Blueprint, jsonify, request
from app import db
from app.models import *
from sqlalchemy import func
from datetime import datetime, timedelta

report = Blueprint('report', __name__)

@report.route('/api/report/market_share', methods=['GET'])
def get_market_share():
    try:
        time_filter = request.args.get('time', 'today')
        now = datetime.now()

        if time_filter == 'today':
            start_date = now.date()
            end_date = start_date + timedelta(days=1)
        elif time_filter == 'yesterday':
            start_date = (now - timedelta(days=1)).date()
            end_date = start_date + timedelta(days=1)
        elif time_filter == 'last_7_days':
            start_date = (now - timedelta(days=7)).date()
            end_date = now.date() + timedelta(days=1)
        elif time_filter == 'last_14_days':
            start_date = (now - timedelta(days=14)).date()
            end_date = now.date() + timedelta(days=1)
        elif time_filter == 'last_21_days':
            start_date = (now - timedelta(days=21)).date()
            end_date = now.date() + timedelta(days=1)
        elif time_filter == 'last_month':
            start_date = (now - timedelta(days=30)).date()
            end_date = now.date() + timedelta(days=1)
        else:
            return jsonify({"status": "error", "message": "Invalid time filter"}), 400

        total_bookings = db.session.query(
            HangHangKhong.MaHHK,
            HangHangKhong.TenHHK,
            func.count(DatCho.MaDatCho).label('booking_count')
        ).join(
            MayBay, HangHangKhong.MaHHK == MayBay.MaHHK
        ).join(
            ChuyenBay, MayBay.MaMayBay == ChuyenBay.MaMB
        ).join(
            DatCho, ChuyenBay.MaChuyenBay == DatCho.MaCB
        ).filter(
            DatCho.TrangThai == 'Đã thanh toán',
            func.date(DatCho.NgayMua) >= start_date,
            func.date(DatCho.NgayMua) < end_date
        ).group_by(
            HangHangKhong.MaHHK,
            HangHangKhong.TenHHK
        ).all()

        total = sum(booking.booking_count for booking in total_bookings)

        result = [
            {
                "airline_code": booking.MaHHK,
                "airline_name": booking.TenHHK,
                "total_bookings": int(booking.booking_count),
                "market_share": round((booking.booking_count / total * 100), 1) if total > 0 else 0.0
            }
            for booking in total_bookings
        ]

        return jsonify({"status": "success", "data": result, "time_filter": time_filter}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@report.route('/api/report/revenue', methods=['GET'])
def get_revenue_report():
    try:
        current_date = datetime.now()

        report_type = request.args.get('type', 'monthly')
        month = request.args.get('month', str(current_date.month)) 
        year = request.args.get('year', str(current_date.year))   
        include_growth = request.args.get('include_growth', 'false').lower() == 'true'

        if report_type == 'monthly':
            base_query = db.session.query(
                func.date(DatCho.NgayMua).label('date'),
                func.count(DatCho.MaDatCho).label('total_orders'),
                func.coalesce(func.sum(ThanhToan.SoTien), 0).label('total_revenue')
            ).join(
                ThanhToan, DatCho.MaDatCho == ThanhToan.MaDatCho
            ).filter(
                DatCho.TrangThai == 'Đã thanh toán'
            )

            if month != 'all':
                base_query = base_query.filter(func.month(DatCho.NgayMua) == int(month))

            if year != 'all':
                base_query = base_query.filter(func.year(DatCho.NgayMua) == int(year))

            query = base_query.group_by(
                func.date(DatCho.NgayMua)
            ).order_by(
                func.date(DatCho.NgayMua)
            )

            result = [
                {
                    "date": record.date.strftime('%Y-%m-%d'),
                    "total_orders": int(record.total_orders),
                    "total_revenue": float(record.total_revenue)
                }
                for record in query.all()
            ]

        elif report_type == 'weekly':
            base_query = db.session.query(
                func.week(DatCho.NgayMua).label('week_number'),
                func.year(DatCho.NgayMua).label('year'),
                func.count(DatCho.MaDatCho).label('total_orders'),
                func.coalesce(func.sum(ThanhToan.SoTien), 0).label('total_revenue')
            ).join(
                ThanhToan, DatCho.MaDatCho == ThanhToan.MaDatCho
            ).filter(
                DatCho.TrangThai == 'Đã thanh toán'
            )

            if month != 'all':
                base_query = base_query.filter(func.month(DatCho.NgayMua) == int(month))
            if year != 'all':
                base_query = base_query.filter(func.year(DatCho.NgayMua) == int(year))

            query = base_query.group_by(
                func.week(DatCho.NgayMua),
                func.year(DatCho.NgayMua)
            ).order_by(
                func.year(DatCho.NgayMua),
                func.week(DatCho.NgayMua)
            )

            weekly_data = query.all()
            result = [
                {
                    "week_number": int(week.week_number),
                    "year": int(week.year),
                    "total_orders": int(week.total_orders),
                    "total_revenue": float(week.total_revenue)
                }
                for week in weekly_data
            ]

            if include_growth:
                full_query = db.session.query(
                    func.week(DatCho.NgayMua).label('week_number'),
                    func.year(DatCho.NgayMua).label('year'),
                    func.count(DatCho.MaDatCho).label('total_orders'),
                    func.coalesce(func.sum(ThanhToan.SoTien), 0).label('total_revenue')
                ).join(
                    ThanhToan, DatCho.MaDatCho == ThanhToan.MaDatCho
                ).filter(
                    DatCho.TrangThai == 'Đã thanh toán'
                ).group_by(
                    func.week(DatCho.NgayMua),
                    func.year(DatCho.NgayMua)
                ).order_by(
                    func.year(DatCho.NgayMua),
                    func.week(DatCho.NgayMua)
                )

                full_data = full_query.all()
                full_result = [
                    {
                        "week_number": int(week.week_number),
                        "year": int(week.year),
                        "total_orders": int(week.total_orders),
                        "total_revenue": float(week.total_revenue)
                    }
                    for week in full_data
                ]

                full_result_sorted = sorted(full_result, key=lambda x: (x['year'], x['week_number']))
                prev_week_map = {}
                for i, row in enumerate(full_result_sorted):
                    if i > 0:  # Bắt đầu từ tuần thứ hai
                        prev_week_map[(row['year'], row['week_number'])] = full_result_sorted[i - 1]

                for row in result:
                    key = (row['year'], row['week_number'])
                    if key in prev_week_map:
                        prev_revenue = prev_week_map[key]["total_revenue"]
                        current_revenue = row["total_revenue"]
                        if prev_revenue != 0:
                            row["growth_rate"] = round((current_revenue - prev_revenue) / prev_revenue * 100, 2)
                        else:
                            row["growth_rate"] = 0
                    else:
                        row["growth_rate"] = 0

        else:
            return jsonify({
                "status": "error",
                "message": "Invalid report type. Use 'monthly' or 'weekly'."
            }), 400

        return jsonify({
            "status": "success",
            "data": result,
            "report_type": report_type,
            "month": month,
            "year": year
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@report.route('/api/report/passengers', methods=['GET']) 
def get_passengers():
    try:
        total_users = NguoiDung.query.filter_by(MaNND=2).count()
        total_passengers = HanhKhach.query.count()
        
        user_passenger_ratio = 0
        if total_passengers > 0:
            user_passenger_ratio = round(( total_users / total_passengers) * 100, 2)
        
        result = {
            "total_users": total_users,
            "total_passengers": total_passengers,
            "user_passenger_ratio": user_passenger_ratio
        }
        
        return jsonify({"status": "success", "data": result}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@report.route('/api/report/booking_stats', methods=['GET'])
def get_booking_stats():
    try:
        time_range = request.args.get('time_range', 'last_7_days')
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if time_range == 'today':
            start_date = today
            end_date = datetime.now()
        elif time_range == 'yesterday':
            start_date = today - timedelta(days=1)
            end_date = today
        elif time_range == 'last_7_days':
            start_date = today - timedelta(days=7)
            end_date = datetime.now()
        elif time_range == 'last_14_days':
            start_date = today - timedelta(days=14)
            end_date = datetime.now()
        elif time_range == 'last_21_days':
            start_date = today - timedelta(days=21)
            end_date = datetime.now()
        elif time_range == 'last_month':
            start_date = today - timedelta(days=30)
            end_date = today
        else:  # last_3_months
            start_date = today - timedelta(days=90)
            end_date = datetime.now()

        stats = db.session.query(
            func.date(DatCho.NgayMua).label('date'),
            func.count(DatCho.MaDatCho).label('total_bookings'),
            func.sum(DatCho.SoLuongGheBus + DatCho.SoLuongGheEco).label('total_passengers')
        ).filter(
            DatCho.NgayMua.between(start_date, end_date),
            DatCho.TrangThai == 'Đã thanh toán'
        ).group_by(
            func.date(DatCho.NgayMua)
        ).order_by(
            func.date(DatCho.NgayMua)
        ).all()

        result = [{
            'date': stat.date.strftime('%Y-%m-%d'),
            'total_bookings': int(stat.total_bookings or 0),
            'total_passengers': int(stat.total_passengers or 0)
        } for stat in stats]

        total_bookings = sum(item['total_bookings'] for item in result)
        total_passengers = sum(item['total_passengers'] for item in result)

        return jsonify({
            "status": "success",
            "data": {
                "stats": result,
                "total_bookings": total_bookings,
                "total_passengers": total_passengers
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@report.route('/api/report/baggage_service_stats', methods=['GET'])
def get_baggage_service_stats():
    """Gets baggage service statistics for different time periods."""
    try:
        time_range = request.args.get('time_range', 'last_7_days')
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if time_range == 'today':
            start_date = today
            end_date = datetime.now()
        elif time_range == 'yesterday':
            start_date = today - timedelta(days=1)
            end_date = today
        elif time_range == 'last_7_days':
            start_date = today - timedelta(days=7)
            end_date = datetime.now()
        elif time_range == 'last_14_days':
            start_date = today - timedelta(days=14)
            end_date = datetime.now()
        elif time_range == 'last_21_days':
            start_date = today - timedelta(days=21)
            end_date = datetime.now()
        elif time_range == 'last_month':
            start_date = today - timedelta(days=31)
            end_date = datetime.now()
        else:  
            start_date = today - timedelta(days=93)
            end_date = datetime.now()
        print(start_date, "-", end_date)

        stats = db.session.query(
            DichVuHanhLy.SoKy.label('weight'),
            func.count(ChiTietDatCho.MaDatCho).label('bookings'),
            func.sum(DichVuHanhLy.Gia).label('revenue')
        ).join(
            ChiTietDatCho, DichVuHanhLy.MaDichVu == ChiTietDatCho.MaDichVu
        ).join(
            DatCho, ChiTietDatCho.MaDatCho == DatCho.MaDatCho
        ).filter(
            DatCho.NgayMua.between(start_date, end_date)
        ).group_by(
            DichVuHanhLy.SoKy
        ).order_by(
            DichVuHanhLy.SoKy
        ).all()

        result = [{
            'weight': f'{stat.weight}kg',
            'bookings': int(stat.bookings),
            'revenue': float(stat.revenue),
            'percentage': 0  
        } for stat in stats]

        total_bookings = sum(item['bookings'] for item in result)
        if total_bookings > 0:
            for item in result:
                item['percentage'] = round(item['bookings'] / total_bookings * 100, 1)

        return jsonify({
            "status": "success",
            "data": {
                "stats": result,
                "total_bookings": total_bookings,
                "total_revenue": sum(item['revenue'] for item in result)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500