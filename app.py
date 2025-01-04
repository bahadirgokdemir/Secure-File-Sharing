import traceback

from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import json
from cryptography.fernet import Fernet
from werkzeug.utils import secure_filename

# Flask uygulamasini olustur
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/encrypted/'
app.config['DECRYPT_FOLDER'] = 'uploads/decrypted/'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# JSON dosya yolu
KEYS_FILE = 'keys.json'

# Klasörleri olustur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DECRYPT_FOLDER'], exist_ok=True)

# JSON dosyasini baslat
if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, 'w') as f:
        json.dump({}, f)

# Key ekleme
def save_key(filename, key):
    try:
        filename = normalize_filename(filename)  # Normalize filename
        with open(KEYS_FILE, 'r') as f:
            keys = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        keys = {}

    keys[filename] = key
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f)

# Key alma
def get_key(filename):
    try:
        filename = normalize_filename(filename)  # Normalize filename
        with open(KEYS_FILE, 'r') as f:
            keys = json.load(f)
        return keys.get(filename)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

# AES anahtar olusturma
def generate_key():
    return Fernet.generate_key().decode()

# Dosya sifreleme
def encrypt_file(file_path, key):
    cipher = Fernet(key.encode())
    with open(file_path, 'rb') as f:
        encrypted_data = cipher.encrypt(f.read())
    # Şifrelenmiş veriyi aynı dosyanın içine yazıyoruz
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)
    return file_path

# Dosya sifresini cözme
def decrypt_file(file_path, key):
    cipher = Fernet(key.encode())
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()  # Dosyayı oku
    decrypted_data = cipher.decrypt(encrypted_data)  # Şifreyi çöz

    # Çözülmüş dosyayı geçici olarak oluştur
    decrypted_path = os.path.join(app.config['DECRYPT_FOLDER'], os.path.basename(file_path))
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_data)

    return decrypted_path

# Dosya adlarını normalize etme
def normalize_filename(filename):
    return filename.replace(' ', '_').lower()

# Uzantı kontrolü
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Ana sayfa
@app.route('/')
def home():
    return render_template('index.html')

# Dosya yükleme
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya bulunamadi!'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Dosya secilmedi!'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'İzin verilmeyen dosya türü!'}), 400

    filename = normalize_filename(secure_filename(file.filename))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # sifreleme ve anahtar olusturma
    key = generate_key()
    encrypt_file(file_path, key)
    save_key(filename, key)  # JSON'a kaydet

    # Basari mesaji dön
    return jsonify({'message': 'Dosya basariyla yuklendi!', 'key': key, 'filename': filename})

# Dosya indirme
@app.route('/download', methods=['POST'])
def download_file():
    data = request.get_json()
    filename = data.get('filename')
    key = data.get('key')
    print("DATA",data)
    # JSON'dan anahtarı al
    stored_key = get_key(filename)
    if not stored_key or stored_key != key:
        return jsonify({'error': 'Geçersiz anahtar veya dosya bulunamadı!'}), 403

    # Dosya yolunu kontrol et
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(file_path)

    if not os.path.exists(file_path):
        return jsonify({'error': 'Dosya bulunamadı!'}), 404

    try:
        # Şifre çözme işlemi
        decrypted_path = decrypt_file(file_path, key)  # Çözülmüş dosyanın yolunu al
        return send_from_directory(app.config['DECRYPT_FOLDER'], os.path.basename(decrypted_path), as_attachment=True)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Dosya indirilemedi!'}), 500

if __name__ == '__main__':
    app.run(debug=True)
