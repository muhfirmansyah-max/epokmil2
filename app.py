# app.py
import os
from flask import Flask, render_template, redirect, url_for, abort
from functools import wraps
from core.config import Config
from core.database import db
from flask_login import LoginManager, login_required, current_user
from core.models import User, Paket

def role_required(role_list):
    """
    Decorator untuk membatasi akses rute berdasarkan peran.
    Penggunaan: @role_required(['Admin', 'Katim'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.peran not in role_list:
                abort(403) # Forbidden: User terotentikasi tapi tidak punya izin
            return f(*args, **kwargs)
        return decorated_function
    return decorator

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi Database
db.init_app(app)

# Inisialisasi Sesi Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Registrasi Peta Tahapan (Blueprints)
from modules.auth.routes import auth_bp
from modules.paket.routes import paket_bp
from modules.reviu_dokpil.routes import reviu_bp
from modules.admin.routes import admin_bp
from modules.evaluasi.routes import evaluasi_bp
from modules.penetapan.routes import penetapan_bp
from modules.laporan.routes import laporan_bp
from modules.template_dokpil.routes import template_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(paket_bp, url_prefix='/paket')
app.register_blueprint(reviu_bp, url_prefix='/reviu')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(evaluasi_bp, url_prefix='/evaluasi')
app.register_blueprint(penetapan_bp, url_prefix='/penetapan')
app.register_blueprint(laporan_bp, url_prefix='/laporan')
app.register_blueprint(template_bp, url_prefix='/template')

# Buat tabel yang belum ada secara otomatis (aman/idempoten; tidak menghapus data).
# Mencegah error "no such table" saat ada model baru tanpa menjalankan init_db.
with app.app_context():
    db.create_all()

# Route Root Aplikasi
@app.route('/')
@login_required
def beranda():
    # Menghitung statistik sederhana untuk dashboard monitoring utama
    total_paket = Paket.query.count() if current_user.peran in ['Admin', 'Katim'] else Paket.query.filter_by(assigned_pokmil=current_user.nama_pokmil).count()
    return render_template('beranda.html', total_paket=total_paket)

if __name__ == '__main__':
    os.makedirs(os.path.join(app.config['BASE_DIR'], 'data'), exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)