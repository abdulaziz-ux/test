from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from collections import defaultdict
import time

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Dictionary untuk menyimpan jumlah permintaan dari setiap IP dalam rentang waktu
request_counts = defaultdict(int)

# Threshold untuk jumlah maksimal permintaan dalam rentang waktu tertentu
REQUEST_THRESHOLD = 100

# Rentang waktu (dalam detik) untuk menghitung jumlah permintaan
TIME_WINDOW = 60  # Contoh: 60 detik (1 menit)

@app.route('/protected-resource')
@limiter.limit("100 per minute")
def protected_resource():
    # Dapatkan alamat IP pengirim permintaan saat ini
    ip_address = request.remote_addr
    
    # Dapatkan waktu saat ini
    current_time = int(time.time())
    
    # Bersihkan catatan lama dari request_counts
    for ip in list(request_counts):
        if current_time - request_counts[ip]['time'] > TIME_WINDOW:
            del request_counts[ip]
    
    # Tambahkan permintaan baru ke dictionary
    request_counts[ip_address] = {
        'count': request_counts[ip_address]['count'] + 1,
        'time': current_time
    }

    # Cek apakah jumlah permintaan dari IP ini melebihi threshold
    if request_counts[ip_address]['count'] > REQUEST_THRESHOLD:
        return jsonify({'error': 'Too many requests. Please try again later.'}), 429  # HTTP 429 Too Many Requests

    # Jika tidak ada masalah, kembalikan sumber daya yang dilindungi
    return "This is a protected resource."

if __name__ == '__main__':
    app.run(debug=True)
