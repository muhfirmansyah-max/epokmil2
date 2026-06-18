# core/models.py
from core.database import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    peran = db.Column(db.String(255), default='Anggota Pokmil') # Bisa menyimpan "Admin, Pokmil"
    nama_pokmil = db.Column(db.String(50), nullable=True)
    is_ketua_pokmil = db.Column(db.Boolean, default=False) 
    last_login = db.Column(db.DateTime, nullable=True)

class Paket(db.Model):
    __tablename__ = 'paket'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_paket = db.Column(db.String(255), nullable=False)
    kode_paket = db.Column(db.String(50), unique=True, nullable=True)
    tahun_anggaran = db.Column(db.Integer, default=2026)
    unit_kerja = db.Column(db.String(255), nullable=False)
    nama_ppk = db.Column(db.String(100), nullable=False)
    nilai_hps = db.Column(db.Float, nullable=False)
    sumber_dana = db.Column(db.String(100), nullable=False)
    
    # Karakteristik Utama Paket
    jenis_pengadaan = db.Column(db.String(50), nullable=False)
    metode_pemilihan = db.Column(db.String(50), nullable=False)
    metode_kualifikasi = db.Column(db.String(50), nullable=False)
    
    # Status Alur Kerja & Penugasan
    status_paket = db.Column(db.String(30), default='Draf') 
    assigned_pokmil = db.Column(db.String(50), nullable=True) 
    tanggal_buat = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Audit & Monitoring
    delegated_at = db.Column(db.DateTime, nullable=True)
    deadline_reviu = db.Column(db.DateTime, nullable=True) # Untuk deteksi kendala/keterlambatan

    @property
    def skala_usaha(self):
        if 'konsultan' in self.jenis_pengadaan.lower():
            return 'Kecil' if self.nilai_hps <= 5000000000 else 'Non-Kecil'
        else:
            return 'Kecil' if self.nilai_hps <= 15000000000 else 'Non-Kecil'

    @property
    def is_terlambat(self):
        """Fitur deteksi kendala keterlambatan untuk Katim/Kepala UKPBJ"""
        if self.deadline_reviu and datetime.utcnow() > self.deadline_reviu and self.status_paket == 'Reviu':
            return True
        return False

class MasterUnsurReviu(db.Model):
    __tablename__ = 'master_unsur_reviu'
    id = db.Column(db.Integer, primary_key=True)
    kelompok = db.Column(db.String(50), nullable=False) # KAK, HPS, Rancangan Kontrak, Dokumen Anggaran
    nama_unsur = db.Column(db.String(255), nullable=False)

class ReviuPaket(db.Model):
    __tablename__ = 'reviu_paket'
    
    id = db.Column(db.Integer, primary_key=True)
    paket_id = db.Column(db.Integer, db.ForeignKey('paket.id'), unique=True, nullable=False)
    nomor_ba_reviu = db.Column(db.String(100), nullable=True)
    tanggal_ba = db.Column(db.Date, nullable=True)
    kesimpulan_reviu = db.Column(db.Text, nullable=True) 
    
    catatan_kak = db.Column(db.Text, nullable=True)
    catatan_spesifikasi = db.Column(db.Text, nullable=True) 
    catatan_hps = db.Column(db.Text, nullable=True)
    catatan_kontrak = db.Column(db.Text, nullable=True)
    catatan_anggaran = db.Column(db.Text, nullable=True)     
    catatan_rup = db.Column(db.Text, nullable=True)              
    catatan_pasar = db.Column(db.Text, nullable=True)            
    
    paket = db.relationship('Paket', backref=db.backref('reviu', uselist=False))

class DetailUnsurReviu(db.Model):
    __tablename__ = 'detail_unsur_reviu'
    
    id = db.Column(db.Integer, primary_key=True)
    reviu_id = db.Column(db.Integer, db.ForeignKey('reviu_paket.id'), nullable=False)
    nama_unsur = db.Column(db.String(255), nullable=False)
    kelompok = db.Column(db.String(50), nullable=False)
    kesesuaian = db.Column(db.String(20), default='Sesuai') # Sesuai, Tidak Sesuai, N/A
    catatan_reviu = db.Column(db.Text, nullable=True)

# ============================================================
# TAHAP LANJUTAN ALUR: Evaluasi (c), Penetapan (d), Laporan (e)
# ============================================================

class Peserta(db.Model):
    """Penyedia yang memasukkan penawaran untuk satu paket (dasar kertas kerja)."""
    __tablename__ = 'peserta'

    id = db.Column(db.Integer, primary_key=True)
    paket_id = db.Column(db.Integer, db.ForeignKey('paket.id'), nullable=False)
    nama_penyedia = db.Column(db.String(255), nullable=False)
    npwp = db.Column(db.String(50), nullable=True)
    harga_penawaran = db.Column(db.Float, default=0)
    harga_terkoreksi = db.Column(db.Float, default=0)

    # Hasil evaluasi (Sistem Gugur: Lulus/Gugur; Sistem Nilai pakai nilai_teknis)
    eval_administrasi = db.Column(db.String(20), default='Belum')
    eval_teknis = db.Column(db.String(20), default='Belum')
    eval_kualifikasi = db.Column(db.String(20), default='Belum')
    nilai_teknis = db.Column(db.Float, default=0)
    catatan = db.Column(db.Text, nullable=True)
    urutan = db.Column(db.Integer, default=0)

    paket = db.relationship('Paket', backref=db.backref('peserta', cascade='all, delete-orphan'))

    @property
    def lulus_semua(self):
        return (self.eval_administrasi == 'Lulus'
                and self.eval_teknis == 'Lulus'
                and self.eval_kualifikasi == 'Lulus')


class Penetapan(db.Model):
    """Penetapan Pemenang oleh Pokmil (dokumen d)."""
    __tablename__ = 'penetapan'

    id = db.Column(db.Integer, primary_key=True)
    paket_id = db.Column(db.Integer, db.ForeignKey('paket.id'), unique=True, nullable=False)
    nomor_sk = db.Column(db.String(100), nullable=True)
    tanggal_sk = db.Column(db.Date, nullable=True)
    pemenang_id = db.Column(db.Integer, db.ForeignKey('peserta.id'), nullable=True)
    cadangan_id = db.Column(db.Integer, db.ForeignKey('peserta.id'), nullable=True)
    dasar_penetapan = db.Column(db.Text, nullable=True)

    paket = db.relationship('Paket', backref=db.backref('penetapan', uselist=False, cascade='all, delete-orphan'))
    pemenang = db.relationship('Peserta', foreign_keys=[pemenang_id])
    cadangan = db.relationship('Peserta', foreign_keys=[cadangan_id])


class LaporanTender(db.Model):
    """Laporan Hasil Tender oleh Pokmil (dokumen e)."""
    __tablename__ = 'laporan_tender'

    id = db.Column(db.Integer, primary_key=True)
    paket_id = db.Column(db.Integer, db.ForeignKey('paket.id'), unique=True, nullable=False)
    nomor_laporan = db.Column(db.String(100), nullable=True)
    tanggal = db.Column(db.Date, nullable=True)
    ringkasan = db.Column(db.Text, nullable=True)

    paket = db.relationship('Paket', backref=db.backref('laporan', uselist=False, cascade='all, delete-orphan'))


class KriteriaEvaluasi(db.Model):
    """Kriteria penyusun Kertas Kerja Evaluasi (c).
    - kelompok 'Teknis'      : diambil dari LKE (Lembar Kriteria Evaluasi) pada LDP.
    - kelompok 'Kualifikasi' : diambil dari persyaratan pada LDK.
    - kelompok 'Administrasi': kelengkapan administrasi penawaran.
    bobot & ambang_batas dipakai untuk metode Sistem Nilai; untuk Sistem Gugur
    cukup pass/fail (bobot boleh 0)."""
    __tablename__ = 'kriteria_evaluasi'

    id = db.Column(db.Integer, primary_key=True)
    paket_id = db.Column(db.Integer, db.ForeignKey('paket.id'), nullable=False)
    kelompok = db.Column(db.String(20), nullable=False, default='Teknis')  # Administrasi/Teknis/Kualifikasi
    sumber = db.Column(db.String(10))                # 'LKE' / 'LDK'
    nama_kriteria = db.Column(db.String(400), nullable=False)
    bobot = db.Column(db.Float, default=0)           # persen, untuk Sistem Nilai
    ambang_batas = db.Column(db.Float, default=0)    # nilai minimal lulus
    urutan = db.Column(db.Integer, default=0)

    paket = db.relationship('Paket', backref=db.backref('kriteria', cascade='all, delete-orphan'))


class DokpilData(db.Model):
    """Nilai isian Dokpil per paket (sumber data mail-merge LDP/LDK).
    Disimpan sebagai pasangan kunci-nilai agar fleksibel mengikuti jenis/metode."""
    __tablename__ = 'dokpil_data'

    id = db.Column(db.Integer, primary_key=True)
    paket_id = db.Column(db.Integer, db.ForeignKey('paket.id'), nullable=False)
    field_key = db.Column(db.String(80), nullable=False)
    field_value = db.Column(db.Text)

    paket = db.relationship('Paket', backref=db.backref('dokpil_data', cascade='all, delete-orphan'))
    __table_args__ = (db.UniqueConstraint('paket_id', 'field_key', name='uq_dokpil_paket_field'),)


class TemplateDokpil(db.Model):
    """Template hasil impor (Manajemen Template). File .docx sudah bertoken {{ }}
    dan daftar field-nya disimpan untuk membangun form isian otomatis."""
    __tablename__ = 'template_dokpil'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    kategori = db.Column(db.String(40), default='Dokpil')  # Dokpil / Dokumen Kualifikasi
    file_template = db.Column(db.String(300), nullable=False)   # nama file .docx bertoken
    original_filename = db.Column(db.String(300))
    fields_json = db.Column(db.Text)                           # JSON daftar key
    jumlah_field = db.Column(db.Integer, default=0)
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)


class TemplateKriteria(db.Model):
    """Set kriteria evaluasi (LKE/LDK) yang bisa dipakai ulang untuk Setting
    Kertas Kerja paket lain. data_json = daftar {kelompok,nama,bobot,ambang,sumber}."""
    __tablename__ = 'template_kriteria'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    jenis_pengadaan = db.Column(db.String(60))
    data_json = db.Column(db.Text)
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)
