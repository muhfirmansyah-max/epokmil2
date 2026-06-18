@echo off
echo =======================================================
echo     MENJALANKAN APLIKASI UNTUK JARINGAN LOKAL (LAN)    
echo =======================================================
echo.
echo Petunjuk Akses Pengguna Lain:
echo 1. Cari Tahu IP Address Komputer Ini via Command Prompt (Ketik ipconfig).
echo 2. Berikan alamat tersebut ke rekan pokja Anda, contoh: http://192.168.1.X:5000
echo 3. Pastikan Windows Firewall mengizinkan Port 5000 untuk masuk.
echo.
call .venv\Scripts\activate
python app.py lan
pause