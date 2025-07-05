

# Phần mềm đặt vé máy bay

## Giới thiệu

* Đây là ứng dụng được sử dụng cho môn Phân tích phần mềm hướng dịch vụ.
* Ứng dụng được xây dựng bằng Flask framework, giao diện sử dụng thư viện Bootstrap5 và database viết bằng MySQL. 

# Tính năng
## Tính năng cho người dùng
1. Tìm kiếm chuyến bay.
2. Xem danh sách đặt chỗ đã đặt.
3. Tra cứu đặt chỗ.
4. Xem thông tin khuyến mãi.
5. Đặt vé kèm các dịch vụ hành lý, đồ ăn kèm cho chuyến bay.
6. In vé máy bay
7. Yêu cầu hủy đặt chỗ
   
## Tính năng cho admin
1. Dashboard
2. Quản lý sân bay, hãng hàng không, máy bay.
3. Xem và sửa danh sách hành khách và người liên hệ.
4. Quản lý chuyến bay và khuyến mãi.
5. Xem danh sách đặt chỗ.
6. Duyệt/từ chối đặt chỗ theo yêu câu của người dùng.

## Setup
### Yêu cầu
- Python 3.11.9

### Cài đặt
```bash
$ pip install -r client_app/requirements.txt
$ pip install -r webservice/requirements.txt
```

## Chạy
### web service
```bash
$ cd webservice
$ pip install mysql-connector-python
$ python run.py
```

### client app
```bash
$ cd client_app
$ pip install reportlab
$ python run.py
```


### GOOGLE_CLIENT

Authorized JavaScript origins:
      http://localhost:3000

Authorized redirect URIs:
      http://localhost:3000/api/login/google/callback
      http://127.0.0.1:3000/api/login/google/callback