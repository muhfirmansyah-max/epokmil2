# migrate_db.py
from app import app
from core.database import db
from sqlalchemy import text

with app.app_context():
    print("Memulai proses modifikasi (migrasi) kolom tabel reviu_paket...")
    
    # Daftar kolom baru yang ingin ditambahkan
    kolom_baru = [
        ("catatan_spesifikasi", "TEXT"),
        ("catatan_anggaran", "TEXT"),
        ("catatan_rup", "TEXT"),
        ("catatan_pasar", "TEXT")
    ]
    
    for nama_kolom, tipe_data in kolom_baru:
        try:
            # Menjalankan perintah ALTER TABLE secara aman
            query = text(f"ALTER TABLE reviu_paket ADD COLUMN {nama_kolom} {tipe_data};")
            db.session.execute(query)
            db.session.commit()
            print(f" [+] Kolom '{nama_kolom}' berhasil ditambahkan.")
        except Exception as e:
            # Jika kolom sudah ada, SQLite akan melempar error, kita tangkap agar tidak stop
            db.session.rollback()
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print(f" [!] Kolom '{nama_kolom}' sudah ada di database, melewati...")
            else:
                print(f" [X] Gagal menambahkan '{nama_kolom}': {e}")

    print("\nProses migrasi selesai! Menjalankan ulang seed data untuk memperbarui master unsur...")
    
    # Jalankan ulang pengisian master unsur reviu agar bank soalnya terperbarui
    from core.models import MasterUnsurReviu
    try:
        db.session.query(MasterUnsurReviu).delete()
        
        unsur_list = [
            # KAK
            MasterUnsurReviu(kelompok='KAK', nama_unsur='Kesesuaian uraian pekerjaan dengan sasaran yang diinginkan'),
            MasterUnsurReviu(kelompok='KAK', nama_unsur='Kejelasan ruang lingkup, lokasi pekerjaan, dan fasilitas penunjang'),
            # Spesifikasi Teknis (6 Aspek)
            MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Mutu (Merek, standar produk, komposisi bahan, kinerja/fungsi)'),
            MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Kuantitas (Volume pekerjaan, jumlah barang/satuan ukuran)'),
            MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Biaya (Kesesuaian dengan anggaran, efisiensi komponen biaya)'),
            MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Lokasi (Tempat penyerahan barang/pelaksanaan pekerjaan)'),
            MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Waktu (Masa penyerahan, jadwal pelaksanaan, durasi pemeliharaan)'),
            MasterUnsurReviu(kelompok='Spesifikasi Teknis', nama_unsur='Aspek Layanan (Instalasi, uji coba, pelatihan, garansi purnajual)'),
            # HPS
            MasterUnsurReviu(kelompok='HPS', nama_unsur='Kesesuaian kalkulasi, keahlian penyusun, dan masa berlaku riwayat harga pasar HPS'),
            MasterUnsurReviu(kelompok='HPS', nama_unsur='Kelebihan biaya (overpricing) atau ketidakwajaran rincian harga satuan'),
            # Rancangan Kontrak
            MasterUnrev(kelompok='Rancangan Kontrak', nama_unsur='Ketepatan jenis kontrak yang dipilih (Lump Sum, Harga Satuan, dll)'),
            MasterUnsurReviu(kelompok='Rancangan Kontrak', nama_unsur='Ketentuan sanksi, denda keterlambatan, keadaan kahar, dan penyelesaian perselisihan'),
            # Anggaran
            MasterUnsurReviu(kelompok='Anggaran', nama_unsur='Ketersediaan plafon anggaran dalam DIPA/DPAL dan kesesuaian akun belanja'),
            # RUP
            MasterUnsurReviu(kelompok='RUP', nama_unsur='Kesesuaian paket yang diumumkan di SiRUP (Kode RUP, nama paket, pemaketan)'),
            # Survei Pasar
            MasterUnsurReviu(kelompok='Survei Pasar', nama_unsur='Analisis ketersediaan barang/jasa dan jumlah penyedia potensial di pasar')
        ]
        db.session.bulk_save_objects(unsur_list)
        db.session.commit()
        print(" [+] Bank data Master Unsur Reviu berhasil diperbarui!")
    except Exception as e:
        db.session.rollback()
        print(f" [X] Gagal memperbarui Master Unsur: {e}")
        
    print("\nSemua beres! Silakan jalankan aplikasi Anda kembali.")