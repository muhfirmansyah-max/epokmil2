# create_admin.py
from app import app, db
from core.models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Cek apakah admin sudah ada agar tidak duplikat
        admin_exists = User.query.filter_by(username='admin').first()
        
        if not admin_exists:
            new_admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'), # Password default
                nama_lengkap='Administrator Utama',
                peran='Admin'
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Akun admin berhasil dibuat!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Akun admin sudah ada di database.")

if __name__ == '__main__':
    create_admin()