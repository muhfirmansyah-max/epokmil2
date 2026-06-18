# File: D:\project\epokmil\init_db.py
from app import app
from core.database import db
from core.models import (User, Paket, ReviuPaket, DetailUnsurReviu,
                         MasterUnsurReviu, Peserta, Penetapan, LaporanTender,
                         KriteriaEvaluasi, DokpilData, TemplateDokpil, TemplateKriteria)

def create_tables():
    with app.app_context():
        # Menghapus tabel lama jika ingin benar-benar fresh (opsional)
        # db.drop_all() 
        
        # Membuat tabel baru sesuai dengan models.py saat ini
        db.create_all()
        print("Database dan tabel berhasil dibuat/diperbarui!")

if __name__ == '__main__':
    create_tables()