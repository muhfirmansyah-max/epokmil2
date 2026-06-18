# helpers/dokpil_fields.py
"""Definisi field isian Dokpil (LDP/LDK) yang menyesuaikan metode pemilihan,
sistem evaluasi, dan jenis pengadaan. Dipakai halaman isian (mail-merge)."""


def _f(key, label, tipe="text", opsi=None, ket=""):
    return {"key": key, "label": label, "tipe": tipe, "opsi": opsi or [], "ket": ket}


def field_dokpil(paket):
    jenis = (paket.jenis_pengadaan or "").lower()
    metode = (paket.metode_pemilihan or "").lower()
    konsultan = "konsultan" in jenis
    konstruksi = "konstruksi" in jenis
    jasa_lain = "jasa lainnya" in jenis
    barang = not (konsultan or konstruksi or jasa_lain)
    sistem_nilai = konsultan  # konsultansi memakai sistem nilai/kualitas

    grup = []

    # ---- LDP: Informasi & Jadwal ----
    info = [
        _f("ldp_masa_berlaku_penawaran", "Masa berlaku penawaran (hari kalender)", "number"),
        _f("ldp_jangka_waktu_pelaksanaan", "Jangka waktu pelaksanaan (hari kalender)", "number"),
        _f("ldp_alamat_pokja", "Alamat Pokja Pemilihan", "text"),
        _f("ldp_website_spse", "Alamat website LPSE/SPSE", "text"),
        _f("ldp_jadwal_pemberian_penjelasan", "Tanggal pemberian penjelasan (aanwijzing)", "date"),
        _f("ldp_jadwal_pemasukan_penawaran", "Batas akhir pemasukan penawaran", "date"),
    ]
    grup.append({"judul": "LDP — Informasi & Jadwal", "fields": info})

    # ---- LDP: Kontrak & Pembayaran ----
    kontrak = [
        _f("ldp_jenis_kontrak", "Jenis kontrak", "select",
           ["Lumsum", "Harga Satuan", "Gabungan Lumsum dan Harga Satuan", "Terima Jadi (Turnkey)"]),
        _f("ldp_cara_pembayaran", "Cara pembayaran", "select",
           ["Sekaligus", "Termin", "Bulanan"]),
        _f("ldp_uang_muka", "Uang muka", "select", ["Tidak diberikan", "Diberikan"]),
        _f("ldp_besaran_uang_muka", "Besaran uang muka (%) bila diberikan", "number"),
        _f("ldp_jaminan_pelaksanaan", "Jaminan pelaksanaan", "select",
           ["Diperlukan", "Tidak diperlukan"]),
    ]
    grup.append({"judul": "LDP — Kontrak & Pembayaran", "fields": kontrak})

    # ---- LDP: Evaluasi (menyesuaikan sistem) ----
    evaluasi = [
        _f("ldp_metode_evaluasi", "Metode evaluasi penawaran", "select",
           (["Sistem Nilai (merit point)", "Kualitas dan Biaya"] if sistem_nilai
            else ["Sistem Gugur", "Sistem Nilai", "Penilaian Biaya Selama Umur Ekonomis"])),
    ]
    if sistem_nilai:
        evaluasi += [
            _f("ldp_bobot_teknis", "Bobot teknis (%)", "number"),
            _f("ldp_bobot_biaya", "Bobot biaya (%)", "number"),
            _f("ldp_ambang_batas_teknis", "Ambang batas nilai teknis", "number"),
        ]
    else:
        evaluasi += [
            _f("ldp_ambang_batas_teknis", "Ambang batas teknis (bila Sistem Nilai)", "number", ket="opsional"),
        ]
    grup.append({"judul": "LDP — Metode Evaluasi", "fields": evaluasi})

    # ---- LDP: spesifik per jenis ----
    spesifik = []
    if barang:
        spesifik += [
            _f("ldp_masa_garansi", "Masa garansi / layanan purna jual", "text"),
            _f("ldp_tempat_penyerahan", "Tempat penyerahan barang", "text"),
        ]
    if konstruksi or jasa_lain:
        spesifik += [_f("ldp_masa_pemeliharaan", "Masa pemeliharaan", "text")]
    if konstruksi:
        spesifik += [_f("ldp_tingkat_risiko_rkk", "Tingkat risiko Keselamatan Konstruksi (RKK)", "select",
                        ["Kecil", "Sedang", "Besar"])]
    if konsultan:
        spesifik += [_f("ldp_jumlah_tenaga_ahli", "Jumlah tenaga ahli yang dibutuhkan", "number")]
    if spesifik:
        grup.append({"judul": "LDP — Ketentuan Khusus", "fields": spesifik})

    # ---- LDK: Kualifikasi ----
    ldk = [
        _f("ldk_kualifikasi_usaha", "Kualifikasi usaha", "select", ["Usaha Kecil", "Non-Kecil"]),
        _f("ldk_syarat_pengalaman", "Persyaratan pengalaman", "textarea"),
    ]
    if konstruksi:
        ldk += [_f("ldk_klasifikasi_sbu", "Klasifikasi/subklasifikasi SBU yang disyaratkan", "text")]
    if konsultan:
        ldk += [_f("ldk_sbu_konsultansi", "SBU/izin jasa konsultansi yang disyaratkan", "text")]
    grup.append({"judul": "LDK — Persyaratan Kualifikasi", "fields": ldk})

    return grup
