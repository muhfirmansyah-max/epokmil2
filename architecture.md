1. Overview
Aplikasi Epokmil2 adalah sistem kertas kerja pokmil yang dibangun menggunakan Python Flask. Aplikasi ini dirancang untuk memproses data pokmil secara efisien, dengan fokus pada kemudahan input data dan pengelolaan kertas kerja berbasis web.

2. Struktur Proyek
app.py: File entry point utama untuk menjalankan server Flask.

templates/: Berisi file HTML (Jinja2) untuk tampilan antarmuka (UI).

static/: Berisi file statis seperti CSS, JavaScript, dan gambar.

models/: (Jika ada) Berisi skema database atau definisi data.

data/ atau database/: (Jika ada) Tempat penyimpanan file data (misal: SQLite atau file CSV).

3. Tech Stack
Backend: Python, Flask framework.

Templating: Jinja2 (HTML templates).

Data Handling: [Sebutkan: SQLite / SQLAlchemy / File CSV / Pandas].

Styling: [Sebutkan: CSS murni / Bootstrap / Tailwind].

4. Alur Kerja (Workflows)
Request Handling: User mengakses route melalui browser, Flask memproses logika di app.py.

Rendering: Data yang diproses dikirim ke file HTML di folder templates/ menggunakan engine Jinja2.

Data Processing: Aplikasi menerima input dari form HTML, memprosesnya dengan Python, dan menyimpannya ke [sebutkan tempat penyimpanan data].

5. Instruksi untuk AI (Claude)
Saat membantu pengembangan aplikasi ini:

Flask Best Practices: Selalu gunakan pola route dan controller yang rapi.

Jinja2: Jika mengubah tampilan, pastikan sintaks Jinja2 ({{ }} atau {% %}) sudah benar.

Data Integrity: Jika ada perubahan pada struktur penyimpanan data, beri peringatan agar tidak merusak data yang sudah ada.

Vibe Coding: Fokus pada kode yang pythonic (bersih dan sesuai standar Python).

Konteks: Selalu merujuk pada app.py saat memberikan saran logika backend.