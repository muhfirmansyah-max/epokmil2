# Kelanjutan Alur EPOKMIL (a–e)

Dokumen ini merangkum penambahan untuk melengkapi alur dari tahap 4 s.d. 12.

## Cara menjalankan (Windows / lokal)

1. Pasang dependensi (sekali):
   ```
   pip install flask flask_sqlalchemy flask_login python-docx openpyxl docxtpl
   ```
2. **Buat tabel baru** (peserta, penetapan, laporan) — aman, tidak menghapus data lama:
   ```
   python init_db.py
   ```
3. Jalankan:
   ```
   python app.py
   ```

## Yang diperbaiki (yang membuat alur macet)

- `reviu_dokpil`: bug `kessummary_reviu` → diganti ke field model `kesimpulan_reviu`
  (kesimpulan reviu kini tersimpan). Route `unduh-ba` yang sebelumnya hanya stub
  kini benar-benar membuat file BA.
- `paket.edit_paket`: dulu merender template yang tidak ada + ada kode mati.
  Kini memuat daftar Pokmil, memperbarui seluruh field, dan punya `edit_paket.html`.
- `templates/paket/index.html`: `url_for('reviu_dokpil.monitoring_progress')`
  menunjuk endpoint yang tidak ada (menyebabkan crash). Diganti menu "Proses"
  berisi tautan ke seluruh tahap a–e.
- `reviu/kelola.html`: nama kelompok unsur diselaraskan dengan data master
  (Anggaran & Survei Pasar kini ikut tampil).

## Dokumen yang dihasilkan

| Kode | Dokumen | Modul | Format |
|------|---------|-------|--------|
| a | Berita Acara Reviu | reviu_dokpil | Word (python-docx, tanpa file template) |
| b | Dokumen Pemilihan (MDP) | reviu_dokpil | Word (docxtpl, isi template resmi) |
| c | Kertas Kerja Evaluasi | evaluasi | Word **dan** Excel berformula |
| d | Penetapan Pemenang | penetapan | Word |
| e | Laporan Hasil Tender | laporan | Word |

### Catatan Dokumen Pemilihan (b)
Generator mengisi template MDP resmi sesuai metode (lihat `helpers/mapping_dokpil.py`).
Letakkan file `.docx` MDP di folder `templates_dokumen/` dengan path sesuai mapping,
mis. `templates_dokumen/tender/mdp_tender_konstruksi_kecil.docx`. Gunakan token
docxtpl seperti `{{ nama_paket }}`, `{{ nilai_hps }}`, dst. Bila template belum ada,
sistem menampilkan pesan ramah, bukan error.

### Catatan Kertas Kerja Excel (c)
File Excel berisi 3 sheet: **Peserta**, **Evaluasi**, **Rekapitulasi**. Sheet
Rekapitulasi MENGAMBIL data dari dua sheet lain via rumus (link otomatis),
menghitung LULUS/GUGUR, peringkat harga di antara yang lulus (SUMPRODUCT), dan
usulan pemenang (INDEX/MATCH). Mengubah angka di sheet sumber otomatis memperbarui
rekapitulasi saat dibuka di Excel.

## Status paket sepanjang alur
Draf → Reviu → Dokpil → Evaluasi → Penetapan → Selesai
