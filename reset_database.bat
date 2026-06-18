@echo off
echo WARNING: Proses ini akan menghapus semua data paket pengadaan Anda!
echo.
set /p konfirmasi="Apakah Anda yakin ingin melakukan reset database? (Y/N): "
if /i "%konfirmasi%" neq "Y" goto batal

if exist data\pokja.db (
    echo Menghapus database lama...
    del /f /q data\pokja.db
)
echo Membuat ulang struktur tabel dan data master...
call .venv\Scripts\activate
python seed_data.py
echo Reset database selesai!
pause
exit

:batal
echo Proses dibatalkan. Data Anda aman.
pause