# Cara Menandai Template Sebelum Impor (paling akurat)

Tandai langsung di Word dengan token docxtpl: tulis {{ nama_field }} di tiap titik isian.

## Aturan nama field
- huruf kecil, angka, garis bawah; TANPA spasi; diawali huruf.
- Beri awalan ldp_ atau ldk_ agar dikelompokkan otomatis di form.

## Contoh penandaan di dokumen
- Masa berlaku penawaran: {{ ldp_masa_berlaku_penawaran }} hari kalender
- Nama paket: {{ ldp_nama_paket_pengadaan }}
- Jenis kontrak: {{ ldp_jenis_kontrak }}
- Kualifikasi usaha: {{ ldk_kualifikasi_usaha }}
- Persyaratan pengalaman: {{ ldk_syarat_pengalaman }}

## Langkah
1. Buka dokumen di Word, ganti tiap titik isian dengan {{ ... }} sesuai di atas.
2. Simpan sebagai .docx.
3. Menu Template -> Impor -> pilih mode "Sudah saya tandai" -> Impor.
4. Aplikasi membaca semua token, membuat form isian otomatis (label diramahkan,
   dikelompokkan LDP/LDK). Isi -> Generate & Unduh.

## Catatan
- Bila dokumen sudah memuat {{ }}, aplikasi otomatis memakainya walau Anda memilih
  mode deteksi otomatis (token manual diprioritaskan & disimpan apa adanya).
- Ketik token sekaligus (hindari autocorrect memecah tanda kurung). Jika perlu,
  matikan AutoCorrect saat mengetik token.
- Nama field = nama yang muncul jadi label form (mis. ldp_masa_berlaku_penawaran
  -> grup "LDP", label "Masa berlaku penawaran").
