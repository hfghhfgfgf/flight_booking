 
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cấu hình định tuyến đến từng service
COMMON_ROUTES = [
    'admin', 'auth', 'login', 'report', 'airlines', 'airports', 
    'aircrafts', 'flight', 'hang-hang-khong', 'quoc-gia', 'dich-vu',"hanh-khach","khuyen-mai","may-bay","nguoi-lien-he","san-bay"
]

ROUTES = {service: 'http://localhost:5001' for service in COMMON_ROUTES}
ROUTES.update({
    'booking': 'http://localhost:5003',
    'bookings': 'http://localhost:5003',
    'lydohuy': 'http://localhost:5003',
    "promotions": 'http://localhost:5003',
    'flights': 'http://localhost:5002',
    'flights': 'http://localhost:5002',
    'packages': 'http://localhost:5002',
    "banks" : 'http://localhost:5002',
    "meals" : 'http://localhost:5002',
    "sanbay" : 'http://localhost:5002',
})

@app.route('/api/<service>', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(service, path):
    print(f"Received request for service: {service}, path: {path}")
    if service not in ROUTES:
        return jsonify({'error': 'Service not found'}), 404

    if path:
        # Nếu có path, thêm vào URL
        target_url = f"{ROUTES[service]}/api/{service}/{path}"
    else:
        target_url = f"{ROUTES[service]}/api/{service}"
    print(target_url)
    # Lấy URL của service backend
 
    # Forward request với method, headers, data, params, etc.
    response = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    # Trả response về cho client
    return (response.content, response.status_code, response.headers.items())

if __name__ == '__main__':
    app.run(port=5000, debug=True)
