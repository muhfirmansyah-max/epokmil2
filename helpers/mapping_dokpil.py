# helpers/mapping_dokpil.py
"""Memilih file template MDP (Perlem LKPP 12/2021) sesuai karakteristik paket.

Mengembalikan nama file template (relatif terhadap folder templates_dokumen/).
Letakkan hasil templatize (lihat templatize_mdp.py) dengan nama yang sama.
"""

# Ambang nilai (Perlem 12/2021): batas usaha kecil
BATAS_KECIL_KONSTRUKSI = 15_000_000_000   # Pekerjaan Konstruksi & Barang/JL
BATAS_KECIL_KONSULTAN = 1_000_000_000     # Jasa Konsultansi


def _norm(s):
    return (s or "").lower()


def tentukan_master_dokpil(paket):
    metode = _norm(paket.metode_pemilihan)
    jenis = _norm(paket.jenis_pengadaan)
    kual = _norm(getattr(paket, "metode_kualifikasi", ""))
    konsultan = "konsultan" in jenis
    konstruksi = "konstruksi" in jenis
    jasa_lain = "jasa lainnya" in jenis or ("jasa" in jenis and not konsultan and not konstruksi)
    perorangan = "perorangan" in jenis

    # ---- Pengadaan Langsung ----
    if "pengadaan langsung" in metode:
        if konsultan:
            return "IV.16 - MDP Pengadaan Langsung Pengadaan Jasa Konsultansi Perorangan.docx" if perorangan \
                else "IV.15 MDP - Pengadaan Langsung Pengadaan Jasa Konsultansi Badan Usaha.docx"
        if jasa_lain:
            return "IV.14 - MDP Pengadaan Langsung Pengadaan Jasa Lainnya.docx"
        return "IV.13 - MDP Pengadan Langsung Barang.docx"

    # ---- Penunjukan Langsung (B = Dokumen Penunjukan Langsung) ----
    if "penunjukan langsung" in metode:
        if konsultan:
            return "IV.12.B - MDP Penunjukan Langsung Jasa Konsultansi Perorangan (Dokumen Penunjukan Langsung).docx" if perorangan \
                else "IV.11.B -  MDP Penunjukan Langsung Pengadaan Jasa Konsultansi Badan Usaha(Dokumen Penunjukan Langsung).docx"
        if jasa_lain:
            return "IV.10.B - MDP Penunjukan Langsung Jasa Lainnya (Dokumen Penunjukan Langsung).doc"
        return "IV.9.B - MDP Penunjukan Langsung Pengadaan Barang (Dokumen Penunjukan Langsung).doc"

    # ---- Seleksi (Jasa Konsultansi) ----
    if "seleksi" in metode:
        return "IV.8 - MDP Seleksi Pengadaan Jasa Konsultansi Perorangan.docx" if perorangan \
            else "IV.7.B - MDP Seleksi Pengadaan Jasa Konsultansi Badan Usaha (Dok. Seleksi).docx"

    # ---- Tender Cepat ----
    if "tender cepat" in metode:
        return "IV.6 - MDP Tender Cepat Pengadaan Jasa Lainnya.docx" if jasa_lain \
            else "IV.3 - MDP Tender Cepat Pengadaan Barang.docx"

    # ---- Tender ----
    if "tender" in metode:
        prakualifikasi = "pra" in kual
        if jasa_lain:
            return "IV.5.B - MDP Tender Prakualifikasi Pengadaan Jasa Lainnya (Dok. Tender).docx" if prakualifikasi \
                else "IV.4 - MDP Tender Pascakualifikasi Pengadaan Jasa Lainnya.docx"
        # Barang
        return "IV.2.B - MDP Tender Prakualifikasi Pengadaan Barang (Dok. Tender).docx" if prakualifikasi \
            else "IV.1 - MDP Tender Pascakualifikasi Pengadaan Barang.docx"

    return "IV.1 - MDP Tender Pascakualifikasi Pengadaan Barang.docx"
