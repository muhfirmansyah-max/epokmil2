# Panduan Instalasi & Penggunaan Sistem Kertas Kerja Digital Pokja Pemilihan

Sistem ini didesain ringan untuk membantu administrasi kertas kerja Pokja Pemilihan tanpa memerlukan instalasi server database yang rumit.

## Persyaratan Awal
* Pastikan komputer Anda sudah terinstal **Python versi 3.10** ke atas.
* Saat instalasi Python di Windows, pastikan mencentang pilihan **"Add Python to PATH"**.

## Langkah Instalasi Pertama Kali
1. Ekstrak seluruh isi folder aplikasi ini.
2. Klik dua kali pada file **`install.bat`**.
3. Tunggu hingga proses instalasi library dan pembuatan database selesai. Jendela terminal akan tertutup otomatis atau meminta Anda menekan tombol sembarang jika selesai.

## Cara Menjalankan Aplikasi

### A. Penggunaan Mandiri (Hanya di Laptop Sendiri)
1. Klik dua kali file **`run_local.bat`**.
2. Browser utama komputer Anda akan otomatis terbuka ke alamat `http://127.0.0.1:5000`.
3. Gunakan akun default berikut untuk masuk:
   * **Username:** `admin`
   * **Password:** `Admin@12345`

### B. Penggunaan Bersama (Berbagi Pakai Lewat Jaringan LAN/Wi-Fi Kantor)
1. Sambungkan laptop Anda dan laptop anggota Pokja lain ke Wi-Fi atau jaringan lokal router yang sama.
2. Klik dua kali file **`run_lan.bat`**.
3. Cek IP lokal laptop Anda melalui `cmd` dengan mengetik perintah `ipconfig` (misal ketemu IP: `192.168.1.25`).
4. Anggota pokja lain dapat membuka sistem melalui browser mereka dengan mengetik alamat: `http://192.168.1.25:5000`.

> **Catatan Kendala LAN:** Jika komputer rekan Anda tidak bisa membuka halaman web tersebut, silakan buka menu *Windows Defender Firewall* di laptop Anda, pilih *Advanced Settings*, dan buat aturan masuk (*Inbound Rules*) baru untuk mengizinkan lalu lintas data melalui **Port 5000**.