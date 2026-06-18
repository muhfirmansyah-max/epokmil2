# helpers/kriteria_standar.py
"""Kriteria standar (rujukan LKPP) untuk menyemai Kertas Kerja Evaluasi.
Teknis -> mengikuti pola LKE; Kualifikasi -> persyaratan umum LDK.
Semua bersifat DEFAULT yang dapat disesuaikan Pokja."""

# Persyaratan kualifikasi umum (LDK) untuk Barang/Jasa Lainnya, pascakualifikasi
_KUALIFIKASI_UMUM = [
    "Memiliki izin usaha sesuai bidang (NIB/izin usaha terkait)",
    "Memiliki NPWP dan telah memenuhi kewajiban perpajakan (SPT Tahunan terakhir)",
    "Mempunyai status valid keterangan Wajib Pajak",
    "Tidak masuk dalam Daftar Hitam",
    "Tidak dalam pengawasan pengadilan, tidak pailit, dan kegiatan usahanya tidak sedang dihentikan",
    "Yang bersangkutan dan manajemennya tidak sedang menjalani sanksi pidana",
    "Menyampaikan akta pendirian/perubahan perusahaan (bagi badan usaha)",
]
_KUALIFIKASI_PENGALAMAN = [
    "Memiliki pengalaman menyediakan barang/jasa sejenis (sesuai ketentuan kualifikasi)",
]
_KUALIFIKASI_KONSULTAN = [
    "Memiliki izin usaha jasa konsultansi / SBU sesuai bidang",
    "Memiliki Tenaga Ahli tetap sesuai bidang layanan",
]
_KUALIFIKASI_KONSTRUKSI = [
    "Memiliki Sertifikat Badan Usaha (SBU) Jasa Konstruksi yang masih berlaku",
    "Memiliki Sisa Kemampuan Paket (SKP) yang cukup",
    "Memiliki kemampuan menyediakan peralatan utama",
    "Memiliki personel manajerial sesuai persyaratan",
]

# Teknis (LKE): daftar (nama_unsur, bobot%, ambang). Bobot 0 = sistem gugur.
_TEKNIS_BARANG = [
    ("Spesifikasi teknis barang yang ditawarkan", 0, 0),
    ("Identitas barang (jenis, tipe, merek) sesuai", 0, 0),
    ("Jadwal/waktu penyerahan barang", 0, 0),
    ("Layanan purna jual dan garansi", 0, 0),
]
_TEKNIS_JASA_LAINNYA = [
    ("Metode pelaksanaan pekerjaan", 0, 0),
    ("Jadwal waktu pelaksanaan pekerjaan", 0, 0),
    ("Peralatan dan/atau personel yang digunakan", 0, 0),
    ("Spesifikasi teknis pekerjaan", 0, 0),
]
_TEKNIS_KONSTRUKSI = [
    ("Metode pelaksanaan pekerjaan", 0, 0),
    ("Jangka waktu pelaksanaan", 0, 0),
    ("Peralatan utama", 0, 0),
    ("Personel manajerial", 0, 0),
    ("Rencana Keselamatan Konstruksi (RKK)", 0, 0),
]
# Konsultansi memakai Sistem Nilai (berbobot) — bobot default LKPP yang lazim
_TEKNIS_KONSULTAN = [
    ("Pengalaman Perusahaan", 10, 0),
    ("Pendekatan dan Metodologi", 30, 0),
    ("Kualifikasi Tenaga Ahli", 60, 0),
]


def kriteria_standar(paket):
    jenis = (paket.jenis_pengadaan or "").lower()
    konsultan = "konsultan" in jenis
    konstruksi = "konstruksi" in jenis
    jasa_lain = "jasa lainnya" in jenis

    if konsultan:
        teknis = _TEKNIS_KONSULTAN
        kualifikasi = _KUALIFIKASI_UMUM + _KUALIFIKASI_KONSULTAN + _KUALIFIKASI_PENGALAMAN
    elif konstruksi:
        teknis = _TEKNIS_KONSTRUKSI
        kualifikasi = _KUALIFIKASI_UMUM + _KUALIFIKASI_KONSTRUKSI + _KUALIFIKASI_PENGALAMAN
    elif jasa_lain:
        teknis = _TEKNIS_JASA_LAINNYA
        kualifikasi = _KUALIFIKASI_UMUM + _KUALIFIKASI_PENGALAMAN
    else:  # Barang
        teknis = _TEKNIS_BARANG
        kualifikasi = _KUALIFIKASI_UMUM + _KUALIFIKASI_PENGALAMAN

    return {"teknis": list(teknis), "kualifikasi": list(kualifikasi)}
