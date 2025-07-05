
DROP DATABASE IF EXISTS DVMB;


CREATE DATABASE DVMB;
USE DVMB;

ALTER DATABASE DVMB CHARACTER SET UTF8MB4;

CREATE TABLE NHOMNGUOIDUNG 
(
    MaNND INT AUTO_INCREMENT PRIMARY KEY,
    TenNhomNguoiDung NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE CHUCNANG
(
     MaCN INT AUTO_INCREMENT PRIMARY KEY,
     TenManHinh NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE PHANQUYEN 
(
    idNND INT,
    idCN INT,
    PRIMARY KEY (idNND, idCN),
    FOREIGN KEY (idNND) REFERENCES NHOMNGUOIDUNG(MaNND) ON DELETE CASCADE,
    FOREIGN KEY (idCN) REFERENCES CHUCNANG(MaCN) ON DELETE CASCADE
);

CREATE TABLE NGUOIDUNG
(
	MaND INT AUTO_INCREMENT PRIMARY KEY,
	TenDangNhap VARCHAR(100) NOT NULL UNIQUE,
    MatKhau VARCHAR(1000),
    TrangThai INT NOT NULL DEFAULT 0,
    MaNND INT NOT NULL,
    FOREIGN KEY (MaNND) REFERENCES NHOMNGUOIDUNG(MaNND) ON DELETE CASCADE
);

CREATE TABLE QUOCGIA 
(
	MaQG VARCHAR(5) PRIMARY KEY,
    TenQuocGia NVARCHAR(50) NOT NULL UNIQUE
); 

CREATE TABLE SANBAY
(
	MaSanBay VARCHAR(5) PRIMARY KEY,
    TenSanBay NVARCHAR(100) NOT NULL UNIQUE,
    ThanhPho NVARCHAR(50) NOT NULL,
    MaQG VARCHAR(5) NOT NULL,
    LoaiSB NVARCHAR(20) NOT NULL CHECK (LoaiSB IN ('Quốc tế', 'Nội địa')),
    FOREIGN KEY (MaQG) REFERENCES QUOCGIA(MaQG) ON DELETE CASCADE
);

CREATE TABLE HANGHANGKHONG
(
	MaHHK VARCHAR(5) PRIMARY KEY,
    TenHHK NVARCHAR(100) NOT NULL UNIQUE,
    MaQG VARCHAR(5) NOT NULL,
    FOREIGN KEY (MaQG) REFERENCES QUOCGIA(MaQG) ON DELETE CASCADE
);

CREATE TABLE MAYBAY
(
	MaMayBay INT AUTO_INCREMENT PRIMARY KEY,
    TenMayBay NVARCHAR(50) NOT NULL,
    MaHHK VARCHAR(5) NOT NULL,
    SoChoNgoiBus INT NOT NULL,
    SoChoNgoiEco INT NOT NULL,
    LoaiMB VARCHAR(20) NOT NULL,
    FOREIGN KEY (MaHHK) REFERENCES HANGHANGKHONG(MaHHK) ON DELETE CASCADE
);

CREATE TABLE CHUYENBAY
(
	MaChuyenBay VARCHAR(8) PRIMARY KEY, 
    MaMB INT NOT NULL,
    MaSanBayDi VARCHAR(5) NOT NULL,
    ThoiGianDi DATETIME NOT NULL,	
    MaSanBayDen VARCHAR(5) NOT NULL,
    ThoiGianDen DATETIME NOT NULL,
    SLGheBus INT,
    SLGheEco INT,
    SLBusConLai INT,
    SLEcoConLai INT,
    LoaiChuyenBay NVARCHAR(20) NOT NULL CHECK (LoaiChuyenBay IN ('Quốc tế', 'Nội địa')),
    GiaVeBus DECIMAL(15,2),
    GiaVeEco DECIMAL(15,2),
    TrangThaiVe INT DEFAULT 0,
    TrangThai INT DEFAULT 0, -- 0: đang khai thác, 1: dừng khai thác
    FOREIGN KEY (MaMB) REFERENCES MAYBAY(MaMayBay) ON DELETE CASCADE,
    FOREIGN KEY (MaSanBayDi) REFERENCES SANBAY(MaSanBay) ON DELETE CASCADE,
    FOREIGN KEY (MaSanBayDen) REFERENCES SANBAY(MaSanBay) ON DELETE CASCADE,
    CONSTRAINT chk_SLGheBus CHECK (SLBusConLai <= SLGheBus),
    CONSTRAINT chk_SLGheEco CHECK (SLEcoConLai <= SLGheEco)
);

CREATE TABLE HANHKHACH
(
	MaHanhKhach INT AUTO_INCREMENT PRIMARY KEY,
    HoHK NVARCHAR(100) NOT NULL, 
    TenHK NVARCHAR(10) NOT NULL,
    DanhXung NVARCHAR(5) NOT NULL,
    CCCD VARCHAR(12) NOT NULL CHECK (CCCD REGEXP '^[0-9]+$') UNIQUE,
    NgaySinh DATE NOT NULL,
    QuocTich VARCHAR(25) NOT NULL,
    LoaiHK VARCHAR(25) NOT NULL CHECK (LoaiHK IN ('Người lớn', 'Trẻ em', 'Em bé'))
);

CREATE TABLE DICHVU (
    MaDV INT AUTO_INCREMENT PRIMARY KEY,
    TenDichVu NVARCHAR(100) NOT NULL,
    MoTa NVARCHAR(500),
    TrangThai INT DEFAULT 0  
);

CREATE TABLE GOIDICHVU (
    MaGoi INT PRIMARY KEY AUTO_INCREMENT,
    TenGoi NVARCHAR(100) NOT NULL,
    MoTa NVARCHAR(500),
    HeSoGia DECIMAL(3,2) DEFAULT 1.00,
    TrangThai INT DEFAULT 0
);

CREATE TABLE DICHVUVE (
    MaDV INT,
    MaHHK VARCHAR(5),
    MaGoi INT,               
    LoaiVeApDung NVARCHAR(20) NOT NULL CHECK (LoaiVeApDung IN ('Economy', 'Business')),   
    ThamSo DECIMAL(10,2),   
    PRIMARY KEY (MaDV, MaHHK, MaGoi, LoaiVeApDung),
    FOREIGN KEY (MaDV) REFERENCES DICHVU(MaDV),
    FOREIGN KEY (MaHHK) REFERENCES HANGHANGKHONG(MaHHK),
    FOREIGN KEY (MaGoi) REFERENCES GOIDICHVU(MaGoi)
);

CREATE TABLE NGUOILIENHE
(
	MaNLH INT AUTO_INCREMENT PRIMARY KEY,
    HoNLH NVARCHAR(100) NOT NULL,
    TenNLH NVARCHAR(10) NOT NULL,
    SDT VARCHAR(10) CHECK (SDT REGEXP '^[0-9]+$'),
    Email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE DATCHO (
    MaDatCho INT AUTO_INCREMENT,
    MaCB VARCHAR(8),
    MaNLH INT NOT NULL,
    SoLuongGheBus INT NOT NULL,
    SoLuongGheEco INT NOT NULL,
    NgayMua DATETIME NOT NULL,
    TrangThai NVARCHAR(25) NOT NULL,
    MaND INT NOT NULL,
    MaDatChoGoc INT,
    MaGoi INT,
    PRIMARY KEY (MaDatCho),
    FOREIGN KEY (MaCB) REFERENCES CHUYENBAY(MaChuyenBay) ON DELETE CASCADE,
    FOREIGN KEY (MaNLH) REFERENCES NGUOILIENHE(MaNLH) ON DELETE CASCADE,
    FOREIGN KEY (MaND) REFERENCES NGUOIDUNG(MaND) ON DELETE CASCADE,
    FOREIGN KEY (MaDatChoGoc) REFERENCES DATCHO(MaDatCho) ON DELETE CASCADE,
    FOREIGN KEY (MaGoi) REFERENCES GOIDICHVU(MaGoi) ON DELETE SET NULL,
    CONSTRAINT chk_TrangThai CHECK (TrangThai IN ('Đang xử lý', 'Đã thanh toán', 'Đã hủy'))
);

CREATE TABLE DICHVUHANHLY
(
	MaDichVu INT AUTO_INCREMENT PRIMARY KEY,
    MaCB VARCHAR(8) NOT NULL,
    SoKy INT NOT NULL,
    Gia DECIMAL(15,2) NOT NULL,
    MoTa NVARCHAR(500),
    FOREIGN KEY (MaCB) REFERENCES CHUYENBAY(MaChuyenBay) ON DELETE CASCADE
);

CREATE TABLE CHITIETDATCHO
(
	MaDatCho INT,
    MaHK INT,
    MaDichVu INT,
    PRIMARY KEY (MaDatCho, MaHK),
    FOREIGN KEY (MaDatCho) REFERENCES DATCHO(MaDatCho) ON DELETE CASCADE,
    FOREIGN KEY (MaHK) REFERENCES HANHKHACH(MaHanhKhach) ON DELETE CASCADE,
    FOREIGN KEY (MaDichVu) REFERENCES DICHVUHANHLY(MaDichVu) ON DELETE CASCADE
);

CREATE TABLE KHUYENMAI
(
	MaKhuyenMai VARCHAR(20) PRIMARY KEY,
    TenKhuyenMai NVARCHAR(50) NOT NULL,
    MoTa NVARCHAR(500),
    LoaiKhuyenMai NVARCHAR(20) NOT NULL CHECK(LoaiKhuyenMai IN('Phần trăm', 'Trực tiếp')),
    GiaTri DECIMAL(15, 2) NOT NULL,
    NgayBatDau DATE NOT NULL,
    NgayKetThuc DATE NOT NULL
);

CREATE TABLE THANHTOAN (
    MaThanhToan INT AUTO_INCREMENT PRIMARY KEY,
    MaDatCho INT NOT NULL,
    MaKhuyenMai VARCHAR(20),
    TienGiam DECIMAL(15,2) DEFAULT 0,
    Thue DECIMAL(15,2) DEFAULT 0,
    SoTien DECIMAL(15,2) NOT NULL,
    NgayThanhToan DATETIME NOT NULL,
    PhuongThuc VARCHAR(20) NOT NULL,
    FOREIGN KEY (MaDatCho) REFERENCES DATCHO(MaDatCho) ON DELETE CASCADE,
    FOREIGN KEY (MaKhuyenMai) REFERENCES KHUYENMAI(MaKhuyenMai) ON DELETE SET NULL
);

CREATE TABLE HHK_KHUYENMAI
(
	MaHHK VARCHAR(5),
    MaKM VARCHAR(20),
	PRIMARY KEY (MaHHK, MaKM),
    FOREIGN KEY (MaHHK) REFERENCES HANGHANGKHONG(MaHHK) ON DELETE CASCADE,
    FOREIGN KEY (MaKM) REFERENCES KHUYENMAI(MaKhuyenMai) ON DELETE CASCADE
);

CREATE TABLE CB_KHUYENMAI
(
	MaCB VARCHAR(5),
    MaKM VARCHAR(20),
	PRIMARY KEY (MaCB, MaKM),
    FOREIGN KEY (MaCB) REFERENCES CHUYENBAY(MaChuyenBay) ON DELETE CASCADE,
    FOREIGN KEY (MaKM) REFERENCES KHUYENMAI(MaKhuyenMai) ON DELETE CASCADE
);

CREATE TABLE BOOKINGTAMTHOI
(
	BookingId VARCHAR(100) PRIMARY KEY,
    Data json,
    CreatedAt datetime NOT NULL,
    ExpiresAt datetime NOT NULL
);

CREATE TABLE LYDOHUY (
    MaLyDo INT AUTO_INCREMENT PRIMARY KEY,
    MaDatCho INT NOT NULL,
    NoiDung TEXT NOT NULL,
    NgayTao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TrangThai VARCHAR(20) NOT NULL DEFAULT 'Chờ duyệt',
    LyDoTuChoi TEXT,
    NgayXuLy DATETIME,
    FOREIGN KEY (MaDatCho) REFERENCES DATCHO(MaDatCho) ON DELETE CASCADE
);

CREATE TABLE THETHANHTOAN (
   SoThe VARCHAR(16) PRIMARY KEY,
   TenChuThe NVARCHAR(100) NOT NULL,
   NganHang VARCHAR(50) NOT NULL,
   SoDu DECIMAL(15,2) DEFAULT 0
);

CREATE TABLE MONAN (
    MaMonAn INT AUTO_INCREMENT PRIMARY KEY,
    TenMonAn NVARCHAR(100) NOT NULL,
    MoTa NVARCHAR(500),
    HinhAnh VARCHAR(255),
    LoaiMonAn NVARCHAR(50) NOT NULL, 
    NgayBatDau DATE NOT NULL,     
    NgayKetThuc DATE NOT NULL,    
    GiaEco DECIMAL(15,2) NOT NULL, 
    GiaBus DECIMAL(15,2) NOT NULL,   
    TrangThai INT DEFAULT 0,         
    CONSTRAINT check_date CHECK (NgayKetThuc >= NgayBatDau)
);

CREATE TABLE CHITIETDATCHO_MONAN (
    MaDatCho INT,
    MaHK INT,
    MaMonAn INT,
    SoLuong INT NOT NULL DEFAULT 1,
    PRIMARY KEY (MaDatCho, MaHK, MaMonAn),
    FOREIGN KEY (MaDatCho, MaHK) REFERENCES CHITIETDATCHO(MaDatCho, MaHK) ON DELETE CASCADE,
    FOREIGN KEY (MaMonAn) REFERENCES MONAN(MaMonAn) ON DELETE CASCADE
);

INSERT INTO THETHANHTOAN (SoThe, TenChuThe, NganHang, SoDu) VALUES
('4532789156230147', 'NGUYEN VAN AN', 'Vietcombank', 15000000.00),
('4532789156230148', 'TRAN THI BINH', 'Agribank', 25000000.00), 
('4532789156230149', 'LE VAN CUONG', 'BIDV', 8500000.00),
('4532789156230150', 'PHAM THI DUNG', 'Techcombank', 32000000.00),
('4532789156230151', 'HOANG VAN EM', 'MB Bank', 4500000.00),
('4532789156230152', 'VU THI FA', 'VPBank', 18900000.00),
('4532789156230153', 'DO VAN GIANG', 'ACB', 27500000.00),
('4532789156230154', 'BUI THI HONG', 'Sacombank', 13500000.00),
('4532789156230155', 'NGO VAN INH', 'VIB', 9800000.00),
('4532789156230156', 'DUONG THI KIM', 'TPBank', 42000000.00),
('4532789156230157', 'LY VAN LONG', 'Vietcombank', 5600000.00),
('4532789156230158', 'MAI THI MINH', 'BIDV', 31000000.00),
('4532789156230159', 'TRINH VAN NAM', 'Agribank', 7800000.00),
('4532789156230160', 'PHAN THI OANH', 'Techcombank', 22500000.00),
('4532789156230161', 'DANG VAN PHU', 'MB Bank', 16700000.00),
('4532789156230162', 'TRAN THI QUYEN', 'VPBank', 29000000.00),
('4532789156230163', 'LE VAN RONG', 'ACB', 11200000.00),
('4532789156230164', 'NGUYEN THI SON', 'Sacombank', 38500000.00),
('4532789156230165', 'HOANG VAN TUAN', 'VIB', 14300000.00),
('4532789156230166', 'PHAM THI UYEN', 'TPBank', 20500000.00),
('4532789156230167', 'VU VAN VINH', 'Vietcombank', 33000000.00),
('4532789156230168', 'DO THI XUAN', 'BIDV', 8900000.00),
('4532789156230169', 'BUI VAN YEN', 'Agribank', 27800000.00),
('4532789156230170', 'NGO THI ZUNG', 'MB Bank', 19500000.00),
('4532789156230171', 'DUONG VAN ANH', 'Techcombank', 12400000.00),
('4532789156230172', 'LY THI BICH', 'VPBank', 35000000.00),
('4532789156230173', 'MAI VAN CONG', 'ACB', 6700000.00),
('4532789156230174', 'TRINH THI DAO', 'Sacombank', 28900000.00),
('4532789156230175', 'PHAN VAN EM', 'VIB', 17200000.00),
('4532789156230176', 'DANG THI FUONG', 'TPBank', 23500000.00),
('4532789156230177', 'TRAN VAN GIANG', 'Vietcombank', 9300000.00),
('4532789156230178', 'LE THI HUONG', 'BIDV', 31700000.00),
('4532789156230179', 'NGUYEN VAN ICH', 'Agribank', 14800000.00),
('4532789156230180', 'HOANG THI KHANH', 'Techcombank', 26400000.00),
('4532789156230181', 'PHAM VAN LINH', 'MB Bank', 7900000.00),
('4532789156230182', 'VU THI MAI', 'VPBank', 39200000.00),
('4532789156230183', 'DO VAN NAM', 'ACB', 16500000.00),
('4532789156230184', 'BUI THI OANH', 'Sacombank', 22800000.00),
('4532789156230185', 'NGO VAN PHU', 'VIB', 11600000.00),
('4532789156230186', 'DUONG THI QUYEN', 'TPBank', 33800000.00),
('4532789156230187', 'LY VAN RONG', 'Vietcombank', 18300000.00),
('4532789156230188', 'MAI THI SON', 'BIDV', 27200000.00),
('4532789156230189', 'TRINH VAN TUAN', 'Agribank', 8200000.00),
('4532789156230190', 'PHAN THI UYEN', 'Techcombank', 36500000.00),
('4532789156230191', 'DANG VAN VINH', 'MB Bank', 13900000.00),
('4532789156230192', 'TRAN THI XUAN', 'VPBank', 29700000.00),
('4532789156230193', 'LE VAN YEN', 'ACB', 15400000.00),
('4532789156230194', 'NGUYEN THI ZUNG', 'Sacombank', 21800000.00),
('4532789156230195', 'HOANG VAN AN', 'VIB', 10200000.00),
('4532789156230196', 'PHAM THI BINH', 'TPBank', 34600000.00),
('4532789156230197', 'VU VAN CUONG', 'Vietcombank', 19100000.00);

-- Thêm dữ liệu món chính
INSERT INTO MONAN (TenMonAn, MoTa, LoaiMonAn, NgayBatDau, NgayKetThuc, GiaEco, GiaBus, TrangThai) VALUES
('Cơm gà xối mỡ', 'Cơm gà với da giòn, ăn kèm xà lách và nước mắm', 'Món chính', '2024-01-01', '2024-12-31', 150000, 250000, 0),
('Bò sốt tiêu đen', 'Bò Úc thượng hạng sốt tiêu đen, ăn kèm cơm trắng và rau củ', 'Món chính', '2024-01-01', '2024-12-31', 180000, 300000, 0),
('Cá hồi nướng', 'Cá hồi Na Uy nướng với sốt chanh dây, ăn kèm khoai tây nghiền', 'Món chính', '2024-01-01', '2024-12-31', 200000, 350000, 0),
('Mì Ý sốt bò bằm', 'Mì Ý với sốt bò bằm và phô mai parmesan', 'Món chính', '2024-01-01', '2024-12-31', 150000, 250000, 0),

-- Thêm dữ liệu món chay
('Cơm chiên rau củ', 'Cơm chiên với các loại rau củ tươi và nấm', 'Món chay', '2024-01-01', '2024-12-31', 120000, 200000, 0),
('Đậu hũ sốt nấm', 'Đậu hũ non sốt nấm đông cô, ăn kèm cơm trắng', 'Món chay', '2024-01-01', '2024-12-31', 120000, 200000, 0),

-- Thêm dữ liệu tráng miệng
('Bánh Tiramisu', 'Bánh Tiramisu truyền thống của Ý', 'Tráng miệng', '2024-01-01', '2024-12-31', 80000, 120000, 0),
('Trái cây tổng hợp', 'Đĩa trái cây tươi theo mùa', 'Tráng miệng', '2024-01-01', '2024-12-31', 60000, 100000, 0),
('Pudding xoài', 'Pudding xoài với sốt chanh dây', 'Tráng miệng', '2024-01-01', '2024-12-31', 70000, 110000, 0),

-- Thêm dữ liệu đồ uống
('Nước cam tươi', 'Nước cam ép tươi 100%', 'Đồ uống', '2024-01-01', '2024-12-31', 40000, 60000, 0),
('Cà phê sữa', 'Cà phê phin truyền thống với sữa đặc', 'Đồ uống', '2024-01-01', '2024-12-31', 35000, 50000, 0),
('Trà hoa cúc', 'Trà hoa cúc mật ong', 'Đồ uống', '2024-01-01', '2024-12-31', 30000, 45000, 0),
('Sinh tố bơ', 'Sinh tố bơ đậm đà', 'Đồ uống', '2024-01-01', '2024-12-31', 45000, 65000, 0),

-- Thêm dữ liệu món ăn nhẹ
('Bánh mì kẹp thịt nguội', 'Bánh mì kẹp thịt nguội và rau sống', 'Món ăn nhẹ', '2024-01-01', '2024-12-31', 85000, 120000, 0),
('Mì ly hải sản', 'Mì ăn liền với hải sản', 'Món ăn nhẹ', '2024-01-01', '2024-12-31', 65000, 95000, 0),
('Sandwich gà', 'Sandwich kẹp gà và phô mai', 'Món ăn nhẹ', '2024-01-01', '2024-12-31', 75000, 110000, 0);

-- QUOCGIA
INSERT INTO `QUOCGIA` (`MaQG`, `TenQuocGia`) VALUES ('VN', 'Việt Nam');
INSERT INTO `QUOCGIA` (`MaQG`, `TenQuocGia`) VALUES ('US', 'Hoa Kỳ');
INSERT INTO `QUOCGIA` (`MaQG`, `TenQuocGia`) VALUES ('JP', 'Nhật Bản');
INSERT INTO `QUOCGIA` (`MaQG`, `TenQuocGia`) VALUES ('CN', 'Trung Quốc');

-- HANGHANGKHONG
INSERT INTO `HANGHANGKHONG` (`MaHHK`, `TenHHK`, `MaQG`) VALUES ('VN', 'Vietnam Airlines', 'VN');
INSERT INTO `HANGHANGKHONG` (`MaHHK`, `TenHHK`, `MaQG`) VALUES ('VJ', 'VietJet Air', 'VN');
INSERT INTO `HANGHANGKHONG` (`MaHHK`, `TenHHK`, `MaQG`) VALUES ('QH', 'Bamboo Airways', 'VN');
INSERT INTO `HANGHANGKHONG` (`MaHHK`, `TenHHK`, `MaQG`) VALUES ('AA', 'American Airlines', 'US');
INSERT INTO `HANGHANGKHONG` (`MaHHK`, `TenHHK`, `MaQG`) VALUES ('UA', 'United Airlines', 'US');

-- SANBAY
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('HAN', 'Sân bay Quốc tế Nội Bài', 'Hà Nội', 'VN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('SGN', 'Sân bay Quốc tế Tân Sơn Nhất', 'TP. Hồ Chí Minh', 'VN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('DAD', 'Sân bay Quốc tế Đà Nẵng', 'Đà Nẵng', 'VN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('CXR', 'Sân bay Quốc tế Cam Ranh', 'Khánh Hòa', 'VN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('PQC', 'Sân bay Quốc tế Phú Quốc', 'Kiên Giang', 'VN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('VII', 'Sân bay Quốc tế Vinh', 'Nghệ An', 'VN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('HPH', 'Sân bay Cát Bi', 'Hải Phòng', 'VN', 'Nội địa');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('PEK', 'Sân bay quốc tế Thủ đô Bắc Kinh', 'Bắc Kinh', 'CN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('PVG', 'Sân bay quốc tế Phố Đông Thượng Hải', 'Thượng Hải', 'CN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('CAN', 'Sân bay quốc tế Bạch Vân Quảng Châu', 'Quảng Châu', 'CN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('SHA', 'Sân bay quốc tế Hồng Kiều Thượng Hải', 'Thương Hải', 'CN', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('LAX', 'Sân bay Quốc tế Los Angeles', 'Los Angeles', 'US', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('JFK', 'Sân bay Quốc tế John F. Kennedy', 'New York', 'US', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('ORD', 'Sân bay Quốc tế O\'Hare', 'Chicago', 'US', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('NRT', 'Sân bay quốc tế Narita', 'Tokyo', 'JP', 'Quốc tế');
INSERT INTO `SANBAY` (`MaSanBay`, `TenSanBay`, `ThanhPho`, `MaQG`, `LoaiSB`) VALUES ('KIX', 'Sân bay quốc tế Kansai', 'Osaka', 'JP', 'Quốc tế');

--  MAYBAY
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Airbus A350-900', 'VN', '9', '29', 'Airbus');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Boeing 787-9 Dreamliner', 'VN', '4', '24', 'Boeing');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Airbus A321', 'VN', '6', '26', 'Airbus');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Airbus A320-200', 'VJ', '0', '22', 'Airbus');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Airbus A321neo', 'VJ', '0', '24', 'Airbus');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Boeing 787-9 Dreamliner', 'QH', '6', '26', 'Boeing');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Airbus A321neo', 'QH', '8', '28', 'Airbus');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Embraer 190', 'QH', '6', '26', 'Embraer');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Boeing 777-300ER', 'AA', '6', '26', 'Boeing');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Boeing 737 MAX 8', 'AA', '4', '24', 'Boeing');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Boeing 777-200', 'AA', '8', '28', 'Boeing');
INSERT INTO `MAYBAY` (`TenMayBay`, `MaHHK`, `SoChoNgoiBus`, `SoChoNgoiEco`, `LoaiMB`) VALUES ('Boeing 787-10 Dreamliner', 'UA', '8', '28', 'Boeing');

-- DICHVU
INSERT INTO DICHVU (TenDichVu, MoTa) VALUES
('Hành lý xách tay', 'Khối lượng hành lý xách tay được tính dựa trên số kg.'),
('Hành lý ký gửi', 'Khối lượng hành lý ký gửi được tính dựa trên số kg.'),
('Phí đổi lịch bay', 'Phí thay đổi lịch trình chuyến bay được tính theo phần trăm giá vé chuyến bay.'),
('Hoàn vé', 'Số tiền hoàn lại sẽ được tính theo phần trăm giá trị vé đã mua.'),
('Bảo hiểm du lịch', 'Hành khách có thể lựa chọn mua hoặc không mua bảo hiểm du lịch.');

-- GOIDICHVU
INSERT INTO GOIDICHVU (MaGoi, TenGoi, MoTa, HeSoGia) VALUES
(1, 'Economy Class', 'Gói dịch vụ tiêu chuẩn cho hạng phổ thông', 1.00),
(2, 'Business Class', 'Gói dịch vụ tiêu chuẩn cho hạng thương gia', 1.00),
(3, 'Economy Plus', 'Gói dịch vụ nâng cao cho hạng phổ thông', 1.20),
(4, 'Business Plus', 'Gói dịch vụ cao cấp cho hạng thương gia', 1.20);

-- DICHVUVE
INSERT INTO DICHVUVE (MaDV, MaHHK, MaGoi, LoaiVeApDung, ThamSo) VALUES
(1, 'VJ', 1, 'Economy', 7),   
(2, 'VJ', 1, 'Economy', 0), 

-- Business Class (MaGoi = 2)
(1, 'VJ', 2, 'Business', 12), -- 12kg xách tay
(2, 'VJ', 2, 'Business', 20), -- 30kg ký gửi

-- Economy Plus (MaGoi = 3)
(1, 'VJ', 3, 'Economy', 7),   -- 7kg xách tay
(2, 'VJ', 3, 'Economy', 20),  -- 20kg ký gửi
(3, 'VJ', 3, 'Economy', 40),  -- 40% phí đổi vé
(4, 'VJ', 3, 'Economy', 70),  -- 70% hoàn tiền
(5, 'VJ', 3, 'Economy', 1),   -- Có bảo hiểm

-- Business Plus (MaGoi = 4)
(1, 'VJ', 4, 'Business', 12), -- 12kg xách tay
(2, 'VJ', 4, 'Business', 30), -- 30kg ký gửi
(3, 'VJ', 4, 'Business', 30), -- 30% phí đổi vé
(4, 'VJ', 4, 'Business', 80), -- 80% hoàn tiền
(5, 'VJ', 4, 'Business', 1);  -- Có bảo hiểm

-- Bamboo Airways (QH)
-- Economy Class (MaGoi = 1)
INSERT INTO DICHVUVE (MaDV, MaHHK, MaGoi, LoaiVeApDung, ThamSo) VALUES
(1, 'QH', 1, 'Economy', 10),  -- 10kg xách tay
(2, 'QH', 1, 'Economy', 20),  -- 20kg ký gửi

-- Business Class (MaGoi = 2)
(1, 'QH', 2, 'Business', 15), -- 15kg xách tay
(2, 'QH', 2, 'Business', 30), -- 30kg ký gửi

-- Economy Plus (MaGoi = 3)
(1, 'QH', 3, 'Economy', 10),  -- 10kg xách tay
(2, 'QH', 3, 'Economy', 20),  -- 20kg ký gửi
(3, 'QH', 3, 'Economy', 35),  -- 35% phí đổi vé
(4, 'QH', 3, 'Economy', 75),  -- 75% hoàn tiền
(5, 'QH', 3, 'Economy', 1),   -- Có bảo hiểm

-- Business Plus (MaGoi = 4)
(1, 'QH', 4, 'Business', 15), -- 15kg xách tay
(2, 'QH', 4, 'Business', 30), -- 30kg ký gửi
(3, 'QH', 4, 'Business', 25), -- 25% phí đổi vé
(4, 'QH', 4, 'Business', 85), -- 85% hoàn tiền
(5, 'QH', 4, 'Business', 1);  -- Có bảo hiểm

-- American Airlines (AA)
-- Economy Class (MaGoi = 1)
INSERT INTO DICHVUVE (MaDV, MaHHK, MaGoi, LoaiVeApDung, ThamSo) VALUES
(1, 'AA', 1, 'Economy', 10),  -- 10kg xách tay
(2, 'AA', 1, 'Economy', 23),  -- 23kg ký gửi

-- Business Class (MaGoi = 2)
(1, 'AA', 2, 'Business', 15), -- 15kg xách tay
(2, 'AA', 2, 'Business', 32), -- 32kg ký gửi

-- Economy Plus (MaGoi = 3)
(1, 'AA', 3, 'Economy', 10),  -- 10kg xách tay
(2, 'AA', 3, 'Economy', 23),  -- 23kg ký gửi
(3, 'AA', 3, 'Economy', 30),  -- 30% phí đổi vé
(4, 'AA', 3, 'Economy', 80),  -- 80% hoàn tiền
(5, 'AA', 3, 'Economy', 1),   -- Có bảo hiểm

-- Business Plus (MaGoi = 4)
(1, 'AA', 4, 'Business', 15), -- 15kg xách tay
(2, 'AA', 4, 'Business', 32), -- 32kg ký gửi
(3, 'AA', 4, 'Business', 20), -- 20% phí đổi vé
(4, 'AA', 4, 'Business', 90), -- 90% hoàn tiền
(5, 'AA', 4, 'Business', 1);  -- Có bảo hiểm

-- United Airlines (UA)
-- Economy Class (MaGoi = 1)
INSERT INTO DICHVUVE (MaDV, MaHHK, MaGoi, LoaiVeApDung, ThamSo) VALUES
(1, 'UA', 1, 'Economy', 10),  -- 10kg xách tay
(2, 'UA', 1, 'Economy', 23),  -- 23kg ký gửi

-- Business Class (MaGoi = 2)
(1, 'UA', 2, 'Business', 15), -- 15kg xách tay
(2, 'UA', 2, 'Business', 32), -- 32kg ký gửi

-- Economy Plus (MaGoi = 3)
(1, 'UA', 3, 'Economy', 10),  -- 10kg xách tay
(2, 'UA', 3, 'Economy', 23),  -- 23kg ký gửi
(3, 'UA', 3, 'Economy', 30),  -- 30% phí đổi vé
(4, 'UA', 3, 'Economy', 80),  -- 80% hoàn tiền
(5, 'UA', 3, 'Economy', 1),   -- Có bảo hiểm

-- Business Plus (MaGoi = 4)
(1, 'UA', 4, 'Business', 15), -- 15kg xách tay
(2, 'UA', 4, 'Business', 32), -- 32kg ký gửi
(3, 'UA', 4, 'Business', 20), -- 20% phí đổi vé
(4, 'UA', 4, 'Business', 90), -- 90% hoàn tiền
(5, 'UA', 4, 'Business', 1);  -- Có bảo hiểm

-- VietNam Airlines (VN)
-- Economy Class (MaGoi = 1)
INSERT INTO DICHVUVE (MaDV, MaHHK, MaGoi, LoaiVeApDung, ThamSo) VALUES
(1, 'VN', 1, 'Economy', 12),  
(2, 'VN', 1, 'Economy', 23),  

-- Business Class (MaGoi = 2)
(1, 'VN', 2, 'Business', 15), 
(2, 'VN', 2, 'Business', 30),

-- Economy Plus (MaGoi = 3)
(1, 'VN', 3, 'Economy', 10),  
(2, 'VN', 3, 'Economy', 20), 
(3, 'VN', 3, 'Economy', 35),
(4, 'VN', 3, 'Economy', 75),  
(5, 'VN', 3, 'Economy', 1),

-- Business Plus (MaGoi = 4)
(1, 'VN', 4, 'Business', 15), -- 15kg xách tay
(2, 'VN', 4, 'Business', 30), -- 30kg ký gửi
(3, 'VN', 4, 'Business', 25), -- 25% phí đổi vé
(4, 'VN', 4, 'Business', 85), -- 85% hoàn tiền
(5, 'VN', 4, 'Business', 1);  -- Có bảo hiểm
-- NGUOILIENHE
INSERT INTO NGUOILIENHE (HoNLH, TenNLH, SDT, Email) VALUES ('Nguyễn Hoàng', 'Anh', '0123456789', 'nguyenhoanganh@gmail.com');
INSERT INTO NGUOILIENHE (HoNLH, TenNLH, SDT, Email) VALUES ('Vũ Ngọc', 'Minh', '0323456789', 'vungocminh@gmail.com');
INSERT INTO NGUOILIENHE (HoNLH, TenNLH, SDT, Email) VALUES ('Bùi Ngọc', 'Hà', '0323456789', 'buingocha@gmail.com');
INSERT INTO NGUOILIENHE (HoNLH, TenNLH, SDT, Email) VALUES ('Đặng Quỳnh', 'Anh', '0423456789', 'dangquynhanh@gmail.com');
INSERT INTO NGUOILIENHE (HoNLH, TenNLH, SDT, Email) VALUES ('Lê Bảo', 'Châu', '0783289133', 'lebaochau@gmail.com');
INSERT INTO NGUOILIENHE (HoNLH, TenNLH, SDT, Email) VALUES ('Hoàng Tuấn', 'Khôi', '0523456789', 'hoangtuankhoi@gmail.com');
INSERT INTO NGUOILIENHE (HoNLH, TenNLH, SDT, Email) VALUES ('Phan Anh', 'Thư', '0328742311', 'phananhthu@gmail.com');

-- NHOMNGUOIDUNG
INSERT INTO `NHOMNGUOIDUNG` (`TenNhomNguoiDung`) VALUES ('ADMIN');
INSERT INTO `NHOMNGUOIDUNG` (`TenNhomNguoiDung`) VALUES ('USER');

-- NGUOIDUNG
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('nghoanh', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('trmikhang', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('lebachau', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('phanduy', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('dogihan', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('vungminh', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('hotuanh', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('bungha', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('daquanh', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('phanthu', 'scrypt:32768:8:1$7FinMtuUWGd0l3jG$1cee91eed6781e8eea3e3d51371d974650fc6a7b0f5dd29ea3ae0b41d279fc96419ea000c8d2559de7488898fe26fd5b3deb0a39487205da09f999696ddfb7b8', '2');
INSERT INTO `NGUOIDUNG` (`TenDangNhap`, `MatKhau`, `MaNND`) VALUES ('admin', 'scrypt:32768:8:1$jPPPWkb0FdFLf4iH$c4c43b885fc3ab5cfa28eea15b3663af5c02ae9c0b62a8ed3691fb0dc546fab41c095384110ff1564c1254febee30ef41dccfd75b2de785a17514340ae453865', '1');
-- HANHKHACH
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Nguyễn Hoàng', 'Anh', 'Anh', '123048394313', STR_TO_DATE('10/05/1995', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Trần Minh', 'Khang', 'Anh', '123043549463', STR_TO_DATE('20/07/1993', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Lê Bảo', 'Châu', 'Ông', '123075294345', STR_TO_DATE('05/11/1997', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Phạm Anh', 'Duy', 'Anh', '123075350833', STR_TO_DATE('03/10/1995', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Đỗ Gia', 'Hân', 'Chị', '123078439702', STR_TO_DATE('12/12/1995', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Vũ Ngọc', 'Minh', 'Anh', '123035248761', STR_TO_DATE('18/08/1998', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Hoàng Tuấn', 'Khôi', 'Ông', '123087580495', STR_TO_DATE('09/01/1994', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Bùi Ngọc', 'Hà', 'Chị', '123065384221', STR_TO_DATE('28/07/1998', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Đặng Quỳnh', 'Anh', 'Bà', '123789882011', STR_TO_DATE('26/12/1997', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');
INSERT INTO `HANHKHACH` (`HoHK`, `TenHK`, `DanhXung`, `CCCD`, `NgaySinh`, `QuocTich`, `LoaiHK`) 
VALUES ('Phan Anh', 'Thư', 'Bà', '123089890991', STR_TO_DATE('29/10/1978', '%d/%m/%Y'), 'Việt Nam', 'Người lớn');

-- CHUYENBAY
INSERT INTO `CHUYENBAY` (`MaChuyenBay`, `MaMB`, `MaSanBayDi`, `ThoiGianDi`, `MaSanBayDen`, `ThoiGianDen`, `SLGheBus`, `SLGheEco`, `SLBusConLai`, `SLEcoConLai`, `LoaiChuyenBay`, `GiaVeEco`, `GiaVeBus`, `TrangThaiVe`) 
VALUES ('VN123', '1', 'HAN', STR_TO_DATE('10/10/2024 8:00', '%d/%m/%Y %H:%i'), 'SGN', STR_TO_DATE('10/10/2024 10:30', '%d/%m/%Y %H:%i'), '5', '5', '5', '5', 'Nội Địa', '10000000', '10000000', 0);
INSERT INTO `CHUYENBAY` (`MaChuyenBay`, `MaMB`, `MaSanBayDi`, `ThoiGianDi`, `MaSanBayDen`, `ThoiGianDen`, `SLGheBus`, `SLGheEco`, `SLBusConLai`, `SLEcoConLai`, `LoaiChuyenBay`, `GiaVeEco`, `GiaVeBus`, `TrangThaiVe`) 
VALUES ('VJ456', '4', 'SGN', STR_TO_DATE('11/10/2024 11:15', '%d/%m/%Y %H:%i'), 'DAD', STR_TO_DATE('11/10/2024 13:00', '%d/%m/%Y %H:%i'), '0', '10', '0', '10', 'Nội Địa', '1500000', '3000000', 0);
INSERT INTO `CHUYENBAY` (`MaChuyenBay`, `MaMB`, `MaSanBayDi`, `ThoiGianDi`, `MaSanBayDen`, `ThoiGianDen`, `SLGheBus`, `SLGheEco`, `SLBusConLai`, `SLEcoConLai`, `LoaiChuyenBay`, `GiaVeEco`, `GiaVeBus`, `TrangThaiVe`) 
VALUES ('AA789', '9', 'HAN', STR_TO_DATE('12/10/2024 14:00', '%d/%m/%Y %H:%i'), 'JFK', STR_TO_DATE('13/10/2024 17:15', '%d/%m/%Y %H:%i'), '5', '8', '5', '8', 'Quốc tế', '15000000', '30000000', 0);
INSERT INTO `CHUYENBAY` (`MaChuyenBay`, `MaMB`, `MaSanBayDi`, `ThoiGianDi`, `MaSanBayDen`, `ThoiGianDen`, `SLGheBus`, `SLGheEco`, `SLBusConLai`, `SLEcoConLai`, `LoaiChuyenBay`, `GiaVeEco`, `GiaVeBus`, `TrangThaiVe`) 
VALUES ('UA321', '12', 'SGN', STR_TO_DATE('10/10/2024 7:30', '%d/%m/%Y %H:%i'), 'ORD', STR_TO_DATE('11/11/2024 8:30', '%d/%m/%Y %H:%i'), '8', '10', '8', '10', 'Quốc tế', '20000000', '60000000', 0);

-- DICHVUHANHLY
INSERT INTO `DICHVUHANHLY` (`MaCB`, `SoKy`, `Gia`, `MoTa`) VALUES ('VN123', '10', '200000', 'Gói hành lý ký gửi');
INSERT INTO `DICHVUHANHLY` (`MaCB`, `SoKy`, `Gia`, `MoTa`) VALUES ('VN123', '20', '400000', 'Gói hành lý ký gửi');
INSERT INTO `DICHVUHANHLY` (`MaCB`, `SoKy`, `Gia`, `MoTa`) VALUES ('VN123', '30', '500000', 'Gói hành lý ký gửi');
INSERT INTO `DICHVUHANHLY` (`MaCB`, `SoKy`, `Gia`, `MoTa`) VALUES ('VJ456', '10', '200000', 'Gói hành lý ký gửi');
INSERT INTO `DICHVUHANHLY` (`MaCB`, `SoKy`, `Gia`, `MoTa`) VALUES ('AA789', '10', '500000', 'Gói hành lý ký gửi');
INSERT INTO `DICHVUHANHLY` (`MaCB`, `SoKy`, `Gia`, `MoTa`) VALUES ('UA321', '15', '1000000', 'Gói hành lý ký gửi');

-- DATCHO
INSERT INTO DATCHO (MaCB, MaNLH, SoLuongGheBus, SoLuongGheEco, NgayMua, TrangThai, MaND) 
VALUES ('VN123', '1', '1', '1', STR_TO_DATE('07/08/2024 10:30:45', '%d/%m/%Y %H:%i:%s'), 'Đã thanh toán', '2');
INSERT INTO DATCHO (MaCB, MaNLH, SoLuongGheBus, SoLuongGheEco, NgayMua, TrangThai, MaND) 
VALUES ('VJ456', '3', '0', '1', STR_TO_DATE('03/08/2024 11:15:30', '%d/%m/%Y %H:%i:%s'), 'Đã thanh toán', '9');
INSERT INTO DATCHO (MaCB, MaNLH, SoLuongGheBus, SoLuongGheEco, NgayMua, TrangThai, MaND) 
VALUES ('AA789', '5', '2', '1', STR_TO_DATE('04/10/2024 09:45:20', '%d/%m/%Y %H:%i:%s'), 'Đã thanh toán', '4');
INSERT INTO DATCHO (MaCB, MaNLH, SoLuongGheBus, SoLuongGheEco, NgayMua, TrangThai, MaND) 
VALUES ('UA321', '4', '0', '3', STR_TO_DATE('30/09/2024 14:20:10', '%d/%m/%Y %H:%i:%s'), 'Đã thanh toán', '10');
INSERT INTO DATCHO (MaCB, MaNLH, SoLuongGheBus, SoLuongGheEco, NgayMua, TrangThai, MaND) 
VALUES ('VN123', '2', '0', '1', STR_TO_DATE('01/10/2024 16:05:35', '%d/%m/%Y %H:%i:%s'), 'Đã hủy', '7');
INSERT INTO DATCHO (MaCB, MaNLH, SoLuongGheBus, SoLuongGheEco, NgayMua, TrangThai, MaND) 
VALUES ('VJ456', '6', '0', '2', STR_TO_DATE('05/10/2024 08:10:50', '%d/%m/%Y %H:%i:%s'), 'Đã thanh toán', '3');
INSERT INTO DATCHO (MaCB, MaNLH, SoLuongGheBus, SoLuongGheEco, NgayMua, TrangThai, MaND) 
VALUES ('AA789', '7', '0', '1', STR_TO_DATE('07/10/2024 18:25:15', '%d/%m/%Y %H:%i:%s'), 'Đã thanh toán', '11');

-- CHITIETDATCHO
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('1', '1', NULL);
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('2', '1', NULL);
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('3', '2', NULL);
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('4', '3', '1');
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('5', '3', NULL);
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('6', '4', '5');
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('7', '4', '2');
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('8', '5', '4');
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('9', '6', NULL);
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('10', '7', NULL);
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('1', '4', NULL);
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('2', '3', '2');
INSERT INTO CHITIETDATCHO (MaHK, MaDatCho, MaDichVu) VALUES ('7', '2', NULL);

-- KHUYENMAI
INSERT INTO KHUYENMAI (MaKhuyenMai, TenKhuyenMai, MoTa, LoaiKhuyenMai, GiaTri, NgayBatDau, NgayKetThuc) 
VALUES ('UuDaiT10', 'Ưu đãi tháng 10', '', 'Trực tiếp', '100000', STR_TO_DATE('01/10/2024', '%d/%m/%Y'), STR_TO_DATE('31/10/2024', '%d/%m/%Y'));
INSERT INTO KHUYENMAI (MaKhuyenMai, TenKhuyenMai, MoTa, LoaiKhuyenMai, GiaTri, NgayBatDau, NgayKetThuc) 
VALUES ('UuDaiT11', 'Ưu đãi tháng 11', '', 'Trực tiếp', '50000', STR_TO_DATE('01/11/2024', '%d/%m/%Y'), STR_TO_DATE('30/11/2024', '%d/%m/%Y'));
INSERT INTO KHUYENMAI (MaKhuyenMai, TenKhuyenMai, MoTa, LoaiKhuyenMai, GiaTri, NgayBatDau, NgayKetThuc) 
VALUES ('UuDaiT12', 'Ưu đãi tháng 12', '', 'Phần trăm', '3', STR_TO_DATE('01/12/2024', '%d/%m/%Y'), STR_TO_DATE('31/12/2024', '%d/%m/%Y'));

-- CB_KHUYENMAI
INSERT INTO CB_KHUYENMAI (MaCB, MaKM) VALUES ('VN123', 'UuDaiT10');
INSERT INTO CB_KHUYENMAI (MaCB, MaKM) VALUES ('VJ456', 'UuDaiT10');
INSERT INTO CB_KHUYENMAI (MaCB, MaKM) VALUES ('AA789', 'UuDaiT10');
-- HHK_KHUYENMAI
INSERT INTO HHK_KHUYENMAI (MaHHK, MaKM) VALUES ('VN', 'UuDaiT10');
INSERT INTO HHK_KHUYENMAI (MaHHK, MaKM) VALUES ('VJ', 'UuDaiT10');

-- THANHTOAN
INSERT INTO THANHTOAN (MaThanhToan, MaDatCho, MaKhuyenMai, TienGiam, Thue, SoTien, NgayThanhToan, PhuongThuc) 
VALUES ('1', '1', NULL, '0', '1100000', '1100000', STR_TO_DATE('07/08/2024', '%d/%m/%Y'), 'Chuyển khoản');
INSERT INTO THANHTOAN (MaThanhToan, MaDatCho, MaKhuyenMai, TienGiam, Thue, SoTien, NgayThanhToan, PhuongThuc) 
VALUES ('2', '4', NULL, '0', '770000', '770000', STR_TO_DATE('30/09/2024', '%d/%m/%Y'), 'Chuyển khoản');
INSERT INTO THANHTOAN (MaThanhToan, MaDatCho, MaKhuyenMai, TienGiam, Thue, SoTien, NgayThanhToan, PhuongThuc) 
VALUES ('3', '6', 'UuDaiT10', '840000', '30800000', '29960000', STR_TO_DATE('05/10/2024', '%d/%m/%Y'), 'Chuyển khoản');


SELECT * FROM NGUOIDUNG WHERE TenDangNhap = 'adminn';

