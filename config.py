import os

# Dosya yolları ve izinler
UPLOAD_FOLDER = 'uploads/encrypted/'
DECRYPT_FOLDER = 'uploads/decrypted/'
SECRET_KEY = 'supersecretkey'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Klasörlerin kontrolü
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DECRYPT_FOLDER, exist_ok=True)

