@echo off
title Menjalankan Aplikasi Kertas Kerja Pokja - Lokal
echo Menyegarkan dan memastikan database siap...
python seed_data.py
echo Memulai Server via Python Flask pada port 5000...
start http://127.0.0.1:5000
python app.py
pause