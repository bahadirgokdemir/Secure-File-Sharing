// Sekme Geçişi
//Routing yapısına hakim olunmadığından script içersinde yönlenmeler gerçekleştirildi
// Sekme Geçişi
function showSection(section) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(sec => (sec.style.display = 'none'));
    const activeSection = document.getElementById(`${section}-section`);
    if (activeSection) {
        activeSection.style.display = 'block';
    }
}


// Şifre Doğrulama
// Şifreyi kontrol ederek dosyayı indir
function verifyPassword() {
    const key = document.getElementById('download-password').value;
    const filename = document.getElementById('download-filename').value;

    fetch('/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename, key })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Anahtar yanlış veya dosya bulunamadı.');
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
    })
    .catch(() => {
        const errorMessage = document.getElementById('error-message');
        errorMessage.style.display = 'block';
    });
}

// Sürükle ve Bırak İşlemleri (Upload Sekmesi)
const dropZone = document.getElementById('drop-zone');
dropZone.addEventListener('dragover', (event) => {
    event.preventDefault();
    dropZone.classList.add('dragging');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragging');
});

dropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropZone.classList.remove('dragging');
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const fileName = files[0].name;
        showPopup(generatePassword(), fileName);
    }
});

// "Dosya Seçin" butonunu tetikleme
// Dosya Seçme ve Yükleme
function triggerFileInput() {
    const fileInput = document.getElementById('file-input');
    fileInput.click();
    fileInput.addEventListener('change', () => {
        const files = fileInput.files;
        if (files.length > 0) {
            uploadFile(files[0]); // API'ye dosyayı gönder
        }
    });
}

// Sürükle ve Bırak ile Dosya Yükleme
dropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropZone.classList.remove('dragging');
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]); // API'ye dosyayı gönder
    }
});

// Şifre Üretme
//TODO: Back-End entegrasyonu sırasında JWT-Token ile bağlanacak
function generatePassword() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let password = '';
    for (let i = 0; i < 8; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
}

// Pop-up Gösterme
function showPopup(password, fileName) {
    const popup = document.getElementById('popup');
    const passwordElement = document.getElementById('generated-password');
    const fileNameElement = document.getElementById('file-name');
    passwordElement.textContent = password;
    fileNameElement.textContent = fileName;
    popup.style.display = 'flex';
}

// Sayfa yüklendiğinde Welcome Page'i göster
document.addEventListener('DOMContentLoaded', () => {
    showSection('welcome');
});


// Pop-up Kapatma
function closePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}

// Sayfa yüklendiğinde Welcome Page'i göster
document.addEventListener('DOMContentLoaded', () => {
    showSection('welcome');
});


// Dosya yükleme işlemi
function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showPopup(data.key, fileInput.files[0].name);
        } else {
            alert("Dosya yüklenemedi: " + data.error);
        }
    })
    .catch(error => {
        alert("Bir hata oluştu: " + error);
    });
}



