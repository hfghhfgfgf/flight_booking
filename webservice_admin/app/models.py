from app import db
from datetime import datetime
from flask_login import UserMixin

class ChucNang(db.Model):
    __tablename__ = 'CHUCNANG'
    
    MaCN = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenManHinh = db.Column(db.String(50), nullable=False, unique=True)

class NhomNguoiDung(db.Model):
    __tablename__ = 'NHOMNGUOIDUNG'
    
    MaNND = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenNhomNguoiDung = db.Column(db.String(50), nullable=False, unique=True)
    
    ds_nguoi_dung = db.relationship('NguoiDung', backref='nhom_nguoi_dung', lazy=True)
    ds_chuc_nang = db.relationship(
        'ChucNang',
        secondary='PHANQUYEN',
        lazy='select',
        backref=db.backref('ds_nhom_nguoi_dung', lazy=True)
    )

class PhanQuyen(db.Model):
    __tablename__ = 'PHANQUYEN'
    
    idNND = db.Column(db.Integer, db.ForeignKey('NHOMNGUOIDUNG.MaNND', ondelete='CASCADE'), primary_key=True)
    idCN = db.Column(db.Integer, db.ForeignKey('CHUCNANG.MaCN', ondelete='CASCADE'), primary_key=True)

class NguoiDung(db.Model, UserMixin):
    __tablename__ = 'NGUOIDUNG'
    
    MaND = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenDangNhap = db.Column(db.String(20), nullable=False, unique=True)
    MatKhau = db.Column(db.String(20))
    TrangThai = db.Column(db.Integer, nullable=False, default=0)
    MaNND = db.Column(db.Integer, db.ForeignKey('NHOMNGUOIDUNG.MaNND', ondelete='CASCADE'), nullable=False)
    
    def get_id(self):
        return str(self.MaND)

class QuocGia(db.Model):
    __tablename__ = 'QUOCGIA'
    
    MaQG = db.Column(db.String(5), primary_key=True)
    TenQuocGia = db.Column(db.String(50), nullable=False, unique=True)
    
    ds_san_bay = db.relationship('SanBay', backref='quoc_gia', lazy=True)
    ds_hang_hang_khong = db.relationship('HangHangKhong', backref='quoc_gia', lazy=True)

class SanBay(db.Model):
    __tablename__ = 'SANBAY'
    
    MaSanBay = db.Column(db.String(5), primary_key=True)
    TenSanBay = db.Column(db.String(100), nullable=False, unique=True)
    ThanhPho = db.Column(db.String(50), nullable=False)
    MaQG = db.Column(db.String(5), db.ForeignKey('QUOCGIA.MaQG', ondelete='CASCADE'), nullable=False)
    LoaiSB = db.Column(db.String(20), nullable=False)
    
    chuyen_bay_di = db.relationship('ChuyenBay', backref='san_bay_di', lazy=True, foreign_keys='ChuyenBay.MaSanBayDi')
    chuyen_bay_den = db.relationship('ChuyenBay', backref='san_bay_den', lazy=True, foreign_keys='ChuyenBay.MaSanBayDen')

    __table_args__ = (
        db.CheckConstraint(LoaiSB.in_(['Quốc tế', 'Nội địa'])),
    )

class HangHangKhong(db.Model):
    __tablename__ = 'HANGHANGKHONG'
    
    MaHHK = db.Column(db.String(5), primary_key=True)
    TenHHK = db.Column(db.String(100), nullable=False, unique=True)
    MaQG = db.Column(db.String(5), db.ForeignKey('QUOCGIA.MaQG', ondelete='CASCADE'), nullable=False)
    ds_may_bay = db.relationship('MayBay', backref='hang_hang_khong', lazy=True)

class DichVu(db.Model):
    __tablename__ = 'DICHVU'
    
    MaDV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenDichVu = db.Column(db.String(50), nullable=False)
    MoTa = db.Column(db.String(200))
    TrangThai = db.Column(db.Integer, default=0)

    dich_vu_ve = db.relationship('DichVuVe', backref='dich_vu', lazy='dynamic')

class GoiDichVu(db.Model):
    __tablename__ = 'GOIDICHVU'
    
    MaGoi = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenGoi = db.Column(db.String(100), nullable=False)
    MoTa = db.Column(db.String(500))
    HeSoGia = db.Column(db.Numeric(3,2), default=1.00)
    TrangThai = db.Column(db.Integer, default=0)

    ds_dat_cho = db.relationship('DatCho', backref='goi_dich_vu', lazy=True)
    dich_vu_ve = db.relationship('DichVuVe', backref='goi_dich_vu', lazy='dynamic', cascade='all, delete-orphan')

class DichVuVe(db.Model):
    __tablename__ = 'DICHVUVE'
    
    MaDV = db.Column(db.Integer, db.ForeignKey('DICHVU.MaDV'), primary_key=True)
    MaHHK = db.Column(db.String(5), db.ForeignKey('HANGHANGKHONG.MaHHK'), primary_key=True)
    MaGoi = db.Column(db.Integer, db.ForeignKey('GOIDICHVU.MaGoi'), primary_key=True)
    LoaiVeApDung = db.Column(db.String(20), primary_key=True)
    ThamSo = db.Column(db.Numeric(10,2))

    hang_hang_khong = db.relationship('HangHangKhong', backref='dich_vu_ve')
    __table_args__ = (
        db.CheckConstraint(LoaiVeApDung.in_(['Economy', 'Business']), name='check_loai_ve'),
    )

class MayBay(db.Model):
    __tablename__ = 'MAYBAY'
    
    MaMayBay = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenMayBay = db.Column(db.String(50), nullable=False)
    MaHHK = db.Column(db.String(5), db.ForeignKey('HANGHANGKHONG.MaHHK', ondelete='CASCADE'), nullable=False)
    SoChoNgoiBus = db.Column(db.Integer, nullable=False)
    SoChoNgoiEco = db.Column(db.Integer, nullable=False)
    LoaiMB = db.Column(db.String(20), nullable=False)
    
    ds_chuyen_bay = db.relationship('ChuyenBay', backref='may_bay', lazy=True)

class ChuyenBay(db.Model):
    __tablename__ = 'CHUYENBAY'
    
    MaChuyenBay = db.Column(db.String(8), primary_key=True)  # VN000001
    MaMB = db.Column(db.Integer, db.ForeignKey('MAYBAY.MaMayBay', ondelete='CASCADE'), nullable=False)
    MaSanBayDi = db.Column(db.String(5), db.ForeignKey('SANBAY.MaSanBay', ondelete='CASCADE'), nullable=False)
    ThoiGianDi = db.Column(db.DateTime, nullable=False)
    MaSanBayDen = db.Column(db.String(5), db.ForeignKey('SANBAY.MaSanBay', ondelete='CASCADE'), nullable=False)
    ThoiGianDen = db.Column(db.DateTime, nullable=False)
    SLGheBus = db.Column(db.Integer)
    SLGheEco = db.Column(db.Integer)
    SLBusConLai = db.Column(db.Integer)
    SLEcoConLai = db.Column(db.Integer)
    LoaiChuyenBay = db.Column(db.String(20), nullable=False)
    GiaVeBus = db.Column(db.DECIMAL(15,2))
    GiaVeEco = db.Column(db.DECIMAL(15,2))
    TrangThaiVe = db.Column(db.Integer, default=0)
    TrangThai = db.Column(db.Integer, default=0) # =1: Đã hủy, =0: Đang hoạt động

    __table_args__ = (
        db.CheckConstraint(LoaiChuyenBay.in_(['Quốc tế', 'Nội địa'])),
    )
    
    @staticmethod
    def generate_flight_code(ma_hhk):
        last_flight = ChuyenBay.query.filter(
            ChuyenBay.MaChuyenBay.regexp_match(f'^{ma_hhk}[0-9]{{6}}$')
        ).order_by(ChuyenBay.MaChuyenBay.desc()).first()

        if not last_flight:
            return f'{ma_hhk}000001'

        try:
            last_number = int(last_flight.MaChuyenBay[-6:])
            new_number = str(last_number + 1).zfill(6)
            return f'{ma_hhk}{new_number}'
        except ValueError:
            return f'{ma_hhk}000001'

    def get_available_seats(self):
        """Lấy số ghế còn trống"""
        return {
            'business': self.SLGheBus,
            'economy': self.SLGheEco
        }
    
    def check_seats_availability(self, hang_ve, so_luong):
        """Kiểm tra còn đủ ghế trống không"""
        if hang_ve == 'Business':
            return self.SLGheBus >= so_luong
        return self.SLGheEco >= so_luong
    
    def update_seats_count(self, hang_ve, so_luong, operation='subtract'):
        """Cập nhật số ghế sau khi đặt/hủy"""
        if hang_ve == 'Business':
            if operation == 'subtract':
                self.SLGheBus -= so_luong
            else:
                self.SLGheBus += so_luong
        else:
            if operation == 'subtract':
                self.SLGheEco -= so_luong
            else:
                self.SLGheEco += so_luong
    
    def get_flight_duration(self):
        """Tính thời gian bay"""
        return self.ThoiGianDen - self.ThoiGianDi
    
    def is_international(self):
        """Kiểm tra có phải chuyến bay quốc tế không"""
        return self.san_bay_di.MaQG != self.san_bay_den.MaQG

class DichVuHanhLy(db.Model):
    __tablename__ = 'DICHVUHANHLY'
    
    MaDichVu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaCB = db.Column(db.String(8), db.ForeignKey('CHUYENBAY.MaChuyenBay', ondelete='CASCADE'), nullable=False)
    SoKy = db.Column(db.Integer, nullable=False)
    Gia = db.Column(db.DECIMAL(15,2), nullable=False)
    MoTa = db.Column(db.String(500))

    chuyen_bay = db.relationship('ChuyenBay', backref='dichvuhanhly')

class HanhKhach(db.Model):
    __tablename__ = 'HANHKHACH'
    
    MaHanhKhach = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoHK = db.Column(db.String(100), nullable=False)
    TenHK = db.Column(db.String(10), nullable=False)
    DanhXung = db.Column(db.String(5), nullable=False)
    CCCD = db.Column(db.String(12), nullable=False, unique=True)
    NgaySinh = db.Column(db.Date, nullable=False)
    QuocTich = db.Column(db.String(25), nullable=False)
    LoaiHK = db.Column(db.String(25), nullable=False)
    
    __table_args__ = (
        db.CheckConstraint(LoaiHK.in_(['Người lớn', 'Trẻ em', 'Em bé'])),
        db.CheckConstraint(CCCD.regexp_match('^[0-9]+$'))
    )


class NguoiLienHe(db.Model):
    __tablename__ = 'NGUOILIENHE'
    
    MaNLH = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoNLH = db.Column(db.String(100), nullable=False)
    TenNLH = db.Column(db.String(10), nullable=False)
    SDT = db.Column(db.String(10))
    Email = db.Column(db.String(100), nullable=False, unique=True)
    
    __table_args__ = (
        db.CheckConstraint(SDT.regexp_match('^[0-9]+$')),
    )

class DatCho(db.Model):
    __tablename__ = 'DATCHO'
    
    MaDatCho = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaCB = db.Column(db.String(8), db.ForeignKey('CHUYENBAY.MaChuyenBay', ondelete='CASCADE'), nullable=False)
    MaNLH = db.Column(db.Integer, db.ForeignKey('NGUOILIENHE.MaNLH', ondelete='CASCADE'), nullable=False)
    MaGoi = db.Column(db.Integer, db.ForeignKey('GOIDICHVU.MaGoi', ondelete='SET NULL'), nullable=True)
    SoLuongGheBus = db.Column(db.Integer, nullable=False)
    SoLuongGheEco = db.Column(db.Integer, nullable=False)
    NgayMua = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    TrangThai = db.Column(db.String(25), nullable=False)
    MaND = db.Column(db.Integer, db.ForeignKey('NGUOIDUNG.MaND', ondelete='CASCADE'), nullable=True)
    MaDatChoGoc = db.Column(db.Integer, db.ForeignKey('DATCHO.MaDatCho'), nullable=True) 

    # Relationships
    nguoi_lien_he = db.relationship('NguoiLienHe', backref='ds_dat_cho')
    chuyen_bay = db.relationship('ChuyenBay', backref='ds_dat_cho')
    nguoi_dung = db.relationship('NguoiDung', backref='ds_dat_cho')
    ds_hanh_khach = db.relationship('HanhKhach', 
                                 secondary='CHITIETDATCHO',
                                 backref=db.backref('ds_dat_cho', lazy=True))
    dat_cho_lien_quan = db.relationship('DatCho',
                                    remote_side=[MaDatCho],
                                    backref=db.backref('dat_cho_goc', remote_side=[MaDatChoGoc]))
    
    __table_args__ = (
        db.CheckConstraint(TrangThai.in_(['Đang xử lý', 'Đã thanh toán', 'Đã hủy'])),
    )
    @staticmethod
    def generate_booking_code(ma_hhk):
        """Tạo mã đặt chỗ theo format: MaHHK + năm + số tự động tăng"""
        year = datetime.now().year % 100
        last_booking = DatCho.query.filter(
            DatCho.MaDatCho.like(f'{ma_hhk}{year}%')
        ).order_by(DatCho.MaDatCho.desc()).first()
        
        if not last_booking:
            return f'{ma_hhk}{year}000001'
        
        last_number = int(str(last_booking.MaDatCho)[-6:])
        new_number = str(last_number + 1).zfill(6)
        return f'{ma_hhk}{year}{new_number}'

class ChiTietDatCho(db.Model):
    __tablename__ = 'CHITIETDATCHO'
    
    MaDatCho = db.Column(db.Integer, db.ForeignKey('DATCHO.MaDatCho', ondelete='CASCADE'), primary_key=True)
    MaHK = db.Column(db.Integer, db.ForeignKey('HANHKHACH.MaHanhKhach', ondelete='CASCADE'), primary_key=True)
    MaDichVu = db.Column(db.Integer, db.ForeignKey('DICHVUHANHLY.MaDichVu', ondelete='CASCADE'))
    
    dich_vu_hanh_ly = db.relationship('DichVuHanhLy')

class KhuyenMai(db.Model):
    __tablename__ = 'KHUYENMAI'
    
    MaKhuyenMai = db.Column(db.String(20), primary_key=True)
    TenKhuyenMai = db.Column(db.String(50), nullable=False)
    MoTa = db.Column(db.String(500))
    LoaiKhuyenMai = db.Column(db.String(20), nullable=False)
    GiaTri = db.Column(db.DECIMAL(15,2), nullable=False)
    NgayBatDau = db.Column(db.Date, nullable=False)
    NgayKetThuc = db.Column(db.Date, nullable=False)
    
    ds_hang_hang_khong = db.relationship('HangHangKhong', 
                                     secondary='HHK_KHUYENMAI',
                                     backref=db.backref('ds_khuyen_mai', lazy=True))
    ds_chuyen_bay = db.relationship('ChuyenBay',
                                secondary='CB_KHUYENMAI',
                                backref=db.backref('ds_khuyen_mai', lazy=True))
    
    __table_args__ = (
        db.CheckConstraint(LoaiKhuyenMai.in_(['Phần trăm', 'Trực tiếp'])),
    )

    def is_valid(self):
        """Kiểm tra khuyến mãi còn hiệu lực không"""
        now = datetime.now().date()
        return self.NgayBatDau <= now <= self.NgayKetThuc
    
    def calculate_discount(self, amount):
        """Tính số tiền giảm"""
        if not self.is_valid():
            return 0
            
        if self.LoaiKhuyenMai == 'Phần trăm':
            return amount * (self.GiaTri / 100)
        return self.GiaTri

class HHK_KhuyenMai(db.Model):
    __tablename__ = 'HHK_KHUYENMAI'
    
    MaHHK = db.Column(db.String(5), db.ForeignKey('HANGHANGKHONG.MaHHK', ondelete='CASCADE'), primary_key=True)
    MaKM = db.Column(db.String(20), db.ForeignKey('KHUYENMAI.MaKhuyenMai', ondelete='CASCADE'), primary_key=True)

class CB_KhuyenMai(db.Model):
    __tablename__ = 'CB_KHUYENMAI'
    
    MaCB = db.Column(db.String(5), db.ForeignKey('CHUYENBAY.MaChuyenBay', ondelete='CASCADE'), primary_key=True)
    MaKM = db.Column(db.String(20), db.ForeignKey('KHUYENMAI.MaKhuyenMai', ondelete='CASCADE'), primary_key=True)

class ThanhToan(db.Model):
    __tablename__ = 'THANHTOAN'
    
    MaThanhToan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaDatCho = db.Column(db.Integer, db.ForeignKey('DATCHO.MaDatCho', ondelete='CASCADE'), nullable=False)
    MaKhuyenMai = db.Column(db.String(20), db.ForeignKey('KHUYENMAI.MaKhuyenMai', ondelete='CASCADE'))
    TienGiam = db.Column(db.DECIMAL(15,2))
    Thue = db.Column(db.Integer)
    SoTien = db.Column(db.DECIMAL(15,2), nullable=False)
    NgayThanhToan = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    PhuongThuc = db.Column(db.String(20), nullable=False)
    
    dat_cho = db.relationship('DatCho', backref='thanh_toan')
    khuyen_mai = db.relationship('KhuyenMai')

class BookingTamThoi(db.Model):
    __tablename__ = 'BOOKINGTAMTHOI'
    
    BookingId = db.Column(db.String(100), primary_key=True)
    Data = db.Column(db.JSON, nullable=False)
    CreatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ExpiresAt = db.Column(db.DateTime, nullable=False)
    
    @classmethod
    def cleanup_expired(cls):
        """Xóa các booking đã hết hạn"""
        try:
            expired = cls.query.filter(cls.ExpiresAt < datetime.utcnow()).all()
            for booking in expired:
                db.session.delete(booking)
            db.session.commit()
        except:
            db.session.rollback()

class LyDoHuy(db.Model):
    __tablename__ = 'LYDOHUY'
    
    MaLyDo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaDatCho = db.Column(db.Integer, db.ForeignKey('DATCHO.MaDatCho', ondelete='CASCADE'), nullable=False)
    NoiDung = db.Column(db.Text, nullable=False)
    NgayTao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    TrangThai = db.Column(db.String(20), nullable=False, default='Chờ duyệt')  # Các trạng thái: Chờ duyệt, Đã duyệt, Từ chối
    LyDoTuChoi = db.Column(db.Text) 
    NgayXuLy = db.Column(db.DateTime)
    
    dat_cho = db.relationship('DatCho', backref=db.backref('ly_do_huy', uselist=False))

class TheThanhToan(db.Model):
    __tablename__ = 'THETHANHTOAN'

    SoThe = db.Column(db.String(16), primary_key=True)
    TenChuThe = db.Column(db.String(100), nullable=False)
    NganHang = db.Column(db.String(50), nullable=False)
    SoDu = db.Column(db.DECIMAL(15,2), default=0)

class MonAn(db.Model):
    __tablename__ = 'MONAN'
    
    MaMonAn = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenMonAn = db.Column(db.String(100), nullable=False)
    MoTa = db.Column(db.String(500))
    HinhAnh = db.Column(db.String(255))
    LoaiMonAn = db.Column(db.String(50), nullable=False)
    NgayBatDau = db.Column(db.Date, nullable=False)
    NgayKetThuc = db.Column(db.Date, nullable=False)
    GiaEco = db.Column(db.DECIMAL(15,2), nullable=False)
    GiaBus = db.Column(db.DECIMAL(15,2), nullable=False)
    TrangThai = db.Column(db.Integer, default=0)

    # Relationship với ChiTietDatChoMonAn
    chi_tiet_dat_cho = db.relationship('ChiTietDatChoMonAn', backref='mon_an')


class ChiTietDatChoMonAn(db.Model):
    __tablename__ = 'CHITIETDATCHO_MONAN'
    
    MaDatCho = db.Column(db.Integer, db.ForeignKey('DATCHO.MaDatCho', ondelete='CASCADE'), primary_key=True)
    MaHK = db.Column(db.Integer, db.ForeignKey('HANHKHACH.MaHanhKhach', ondelete='CASCADE'), primary_key=True)
    MaMonAn = db.Column(db.Integer, db.ForeignKey('MONAN.MaMonAn', ondelete='CASCADE'), primary_key=True)
    SoLuong = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    dat_cho = db.relationship('DatCho', backref='chitietdatcho_monan')
    hanh_khach = db.relationship('HanhKhach', backref='chitietdatcho_monan')
