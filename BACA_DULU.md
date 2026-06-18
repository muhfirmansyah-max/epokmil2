# Isi Otomatis Kriteria (Teknis LKE / Kualifikasi LDK)

## File (timpa/menambah di folder epokmil/)
- `helpers/kriteria_standar.py`        : (BARU) daftar kriteria standar LKPP per jenis pengadaan.
- `modules/evaluasi/routes.py`         : (timpa) + route `isi_otomatis`.
- `templates/evaluasi/kriteria.html`   : (timpa) + tombol "⚡ Isi Otomatis dari Standar".

Tidak perlu init_db lagi (tidak ada tabel baru).

## Cara pakai
Paket -> c. Evaluasi -> Setting Kriteria -> klik **⚡ Isi Otomatis dari Standar (LKE/LDK)**.
- Sistem menyemai kriteria standar sesuai `jenis_pengadaan` paket:
  Barang / Jasa Lainnya / Pekerjaan Konstruksi / Jasa Konsultansi.
  (Konsultansi memakai Sistem Nilai berbobot default 10/30/60.)
- Hanya mengisi kelompok yang masih KOSONG (tidak menggandakan bila sudah ada).
- Pokja tinggal menyesuaikan bobot, ambang batas, dan redaksi persyaratan sesuai
  LKE dan LDK paket yang sebenarnya.

## Catatan jujur
MDP kosong belum memuat kriteria LKE/LDK yang riil (itu keputusan Pokja), jadi
"otomatis" di sini = menyemai DEFAULT standar yang lazim, bukan menyalin dari
template. Tujuannya: Pokja mulai dari matriks siap-sesuaikan, bukan halaman kosong.
