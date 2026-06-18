# Fitur Mail-Merge Dokumen Pemilihan (Dokpil)

## Apa yang sudah jadi
1. **Pemilih template otomatis** — `helpers/mapping_dokpil.py` memilih 1 dari 27
   MDP LKPP berdasarkan metode pemilihan, jenis pengadaan, kualifikasi, dan HPS.
2. **Generator** — `helpers/document_generator.py > generate_docx_dokpil(paket)`
   mengisi template dengan docxtpl. Token yang belum ada datanya dibiarkan
   kosong (tidak error).
3. **Konverter MDP → template** — `tools/templatize_mdp.py`. Mengubah file MDP
   resmi menjadi template mail-merge: setiap titik isian (garis bawah `____` /
   instruksi `[diisi ...]`) di tabel (LDP, LDK, SSKK, SSUK, Surat Perjanjian)
   diganti token `{{ field }}`.
4. **Contoh jadi** — `templates_dokumen/IV.1 - TEMPLATE Tender Pascakualifikasi
   Barang.docx` (182 field) + daftar field-nya.

## Cara mengonversi MDP lain menjadi template
```
pip install python-docx docxtpl
python tools/templatize_mdp.py "MDP/IV.4 - ... Jasa Lainnya.docx" "templates_dokumen/IV.4 - TEMPLATE ....docx"
```
Setiap konversi menghasilkan juga file `*.fields.txt` berisi daftar token.

## CATATAN PENTING (dibaca dulu)
- **Penamaan field bersifat mekanis** (mis. `f_sumber_dana`, `f_jenis_kontrak_2`)
  karena diturunkan otomatis dari label baris. Template-nya valid dan bisa diisi,
  tetapi belum "ramah". Agar aplikasi mengisi otomatis dari data paket, token di
  template harus disamakan dengan nama field yang dikirim generator
  (`nama_paket`, `nilai_hps`, dst.) — ini perlu pemetaan kuratif per dokumen.
- **Belum diuji render** di lingkungan ini karena `docxtpl` tidak terpasang dan
  tanpa internet. Konverter sudah diuji menghasilkan .docx valid dengan token
  Jinja yang sah; render akhir harus dicoba di komputer Anda (`docxtpl` terpasang).
- File MDP berformat lama `.doc` (Penunjukan/PL tertentu) harus dikonversi ke
  `.docx` lebih dulu (mis. via LibreOffice/Word) sebelum di-templatize.

## Dua pilihan agar benar-benar "siap pakai"
A. **Form dinamis dari daftar field** — aplikasi membaca `*.fields.txt`, membuat
   form isian otomatis, lalu merge. Skalabel untuk semua 27, tapi field banyak.
B. **Pemetaan kuratif (~25 field inti)** — saya tandai titik-titik penting LDP/
   LDK/SSKK dengan nama field standar (nama_paket, sumber_dana, jenis_kontrak,
   masa_pelaksanaan, masa_pemeliharaan, jaminan, dst.) yang otomatis terisi dari
   data paket + hasil reviu. Lebih ramah, dikerjakan per template.
