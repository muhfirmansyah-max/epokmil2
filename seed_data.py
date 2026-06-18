# seed_data.py
from app import app
from core.database import db
from core.models import User, MasterUnsurReviu
from werkzeug.security import generate_password_hash

with app.app_context():
    # Membuat tabel baru di database jika belum ada
    db.create_all()
    
    # Suntik User Katim default jika belum terdaftar
    if not User.query.filter_by(username='katim_pusat').first():
        katim = User(
            username='katim_pusat',
            password_hash=generate_password_hash('katim123'),
            nama_lengkap='Kepala Tim UKPBJ',
            peran='Katim'
        )
        db.session.add(katim)
        
    # Suntik User Pokja default jika belum terdaftar
    if not User.query.filter_by(username='pokmil3_user').first():
        pokja = User(
            username='pokmil3_user',
            password_hash=generate_password_hash('pokja123'),
            nama_lengkap='Muhamad Firmansyah',
            peran='Ketua Pokja',
            nama_pokmil='Pokmil 3'
        )
        db.session.add(pokja)
        
    # REVISI: Suntik Bank Unsur Reviu Dokumen Persiapan Lengkap
    # Menghapus data lama agar tidak terjadi penumpukan/duplikasi saat seeding ulang
    db.session.query(MasterUnsurReviu).delete()
    
    unsur_list = [
        # 1. Kelompok KAK
        MasterUnsurReviu(kelompok='KAK', nama_unsur='Kesesuaian uraian pekerjaan dengan sasaran yang diinginkan'),
        MasterUnsurReviu(kelompok='KAK', nama_unsur='Kejelasan ruang lingkup, lokasi pekerjaan, dan fasilitas penunjang'),
        
        # 2. Kelompok Spesifikasi Teknis (6 Aspek Penting)
        MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Mutu (Merek, standar produk, komposisi bahan, kinerja/fungsi)'),
        MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Kuantitas (Volume pekerjaan, jumlah barang/satuan ukuran)'),
        MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Biaya (Kesesuaian dengan anggaran, efisiensi komponen biaya)'),
        MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Lokasi (Tempat penyerahan barang/pelaksanaan pekerjaan)'),
        MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Waktu (Masa penyerahan, jadwal pelaksanaan, durasi pemeliharaan)'),
        MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Layanan (Instalasi, uji coba, pelatihan, garansi purnajual)'),
        
        # 3. Kelompok HPS
        MasterUnsurReviu(kelompok='HPS', nama_unsur='Kesesuaian kebutuhan telah tercakup seluruhnya dalam HPS'),
        MasterUnsurReviu(kelompok='HPS', nama_unsur='Tanggal penyusunan HPS sesuai ketentuan (paling lama 28 hari kerja sebelum batas akhir pemasukan penawaran)'),
        MasterUnsurReviu(kelompok='HPS', nama_unsur='Metode survei pasar yang digunakan (RFI, survei online, distributor, pabrikan, dll)'),
        MasterUnsurReviu(kelompok='HPS', nama_unsur='Ketepatan perhitungan pajak (PPN/PPh) dalam HPS'),
        MasterUnsurReviu(kelompok='HPS', nama_unsur='Kelengkapan dokumentasi penyusunan HPS'),
        
        # 4. Kelompok Rancangan Kontrak
        MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Telah mengakomodir mitigasi risiko (asuransi, denda, ganti rugi, tanggung jawab audit)'),
        MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Kejelasan jangka waktu pelaksanaan'),
        MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Kesesuaian spesifikasi/KAK dengan rancangan kontrak'),
        MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Ketentuan jaminan mutu/garansi'),
        MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Kesesuaian dengan ketentuan peraturan yang berlaku'),
        MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Ketentuan uang muka'),
        MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Ketentuan cara pembayaran'),
        
        # 5. Kelompok Anggaran
        MasterUnsurReviu(kelompok='Anggaran', nama_unsur='Ketersediaan plafon anggaran dalam DIPA/DPAL dan kesesuaian akun belanja'),
        
        # 6. Kelompok RUP
        MasterUnsurReviu(kelompok='RUP', nama_unsur='Kesesuaian paket dengan yang diumumkan di SiRUP'),
        MasterUnsurReviu(kelompok='RUP', nama_unsur='Kesesuaian kualifikasi usaha (kecil/non-kecil)'),
        MasterUnsurReviu(kelompok='RUP', nama_unsur='Kesesuaian metode pemilihan'),
        MasterUnsurReviu(kelompok='RUP', nama_unsur='Kesesuaian nilai pagu anggaran'),
        
        # 7. Kelompok Survei Pasar
        MasterUnsurReviu(kelompok='Survei Pasar', nama_unsur='Analisis ketersediaan barang/jasa dan jumlah penyedia potensial di pasar')
    ]
    
    db.session.bulk_save_objects(unsur_list)
    db.session.commit()
    print("Database Berhasil Di-Seeding dengan Unsur Reviu yang Baru!")