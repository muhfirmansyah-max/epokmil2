# modules/template_dokpil/routes.py
import os
import json
import time
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, send_from_directory)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from core.models import TemplateDokpil
from core.database import db
from core.config import Config
from helpers.templatizer import templatize_docx, label_dari_key

template_bp = Blueprint('template_dokpil', __name__)


def _folder():
    os.makedirs(Config.TEMPLATE_DOC_FOLDER, exist_ok=True)
    return Config.TEMPLATE_DOC_FOLDER


def _admin_katim():
    return current_user.peran in ['Admin', 'Katim']


@template_bp.route('/')
@login_required
def daftar():
    templates = TemplateDokpil.query.order_by(TemplateDokpil.dibuat_pada.desc()).all()
    return render_template('template/daftar.html', templates=templates,
                           boleh_kelola=_admin_katim())


@template_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if not _admin_katim():
        flash('Hanya Admin/Katim yang dapat mengunggah template.', 'danger')
        return redirect(url_for('template_dokpil.daftar'))

    file = request.files.get('file')
    if not file or not file.filename:
        flash('Pilih berkas .docx terlebih dahulu.', 'warning')
        return redirect(url_for('template_dokpil.daftar'))
    if not file.filename.lower().endswith('.docx'):
        flash('Hanya berkas .docx yang didukung (file .doc lama harap Save As .docx dulu).', 'warning')
        return redirect(url_for('template_dokpil.daftar'))

    nama = request.form.get('nama', '').strip() or os.path.splitext(file.filename)[0]
    kategori = request.form.get('kategori', 'Dokpil')
    lingkup = request.form.get('lingkup', 'ldp_ldk')

    aman = secure_filename(file.filename)
    stamp = str(int(time.time()))
    src_path = os.path.join(_folder(), f"_asli_{stamp}_{aman}")
    dst_name = f"tpl_{stamp}_{aman}"
    dst_path = os.path.join(_folder(), dst_name)
    file.save(src_path)

    fallback = False
    try:
        fields = templatize_docx(src_path, dst_path, lingkup=lingkup)
        if not fields and lingkup == 'ldp_ldk':
            # LDP/LDK tak terdeteksi -> coba pindai semua bagian otomatis
            fields = templatize_docx(src_path, dst_path, lingkup='semua')
            fallback = bool(fields)
    except Exception as e:
        flash(f'Gagal memproses dokumen: {e}', 'danger')
        if os.path.exists(src_path):
            os.remove(src_path)
        return redirect(url_for('template_dokpil.daftar'))
    finally:
        if os.path.exists(src_path):
            os.remove(src_path)

    if not fields:
        flash('0 field terdeteksi. Pastikan dokumen memuat titik isian berupa '
              'garis bawah "____" atau instruksi "[diisi ...]". Coba pilih lingkup '
              '"Semua bagian ber-isian", atau kirim contoh dokumennya untuk dicek.', 'warning')

    db.session.add(TemplateDokpil(
        nama=nama, kategori=kategori, file_template=dst_name,
        original_filename=file.filename, fields_json=json.dumps(fields),
        jumlah_field=len(fields)))
    db.session.commit()
    pesan = f'Template "{nama}" dibuat dari {file.filename} — {len(fields)} field terdeteksi.'
    if fallback:
        pesan += ' (LDP/LDK tidak terdeteksi, dipindai dari semua bagian ber-isian.)'
    flash(pesan, 'success' if fields else 'warning')
    return redirect(url_for('template_dokpil.daftar'))


@template_bp.route('/<int:template_id>/isi', methods=['GET', 'POST'])
@login_required
def isi(template_id):
    t = TemplateDokpil.query.get_or_404(template_id)
    keys = json.loads(t.fields_json or '[]')
    # kelompokkan field untuk form
    grup = {}
    for k in keys:
        g, lbl = label_dari_key(k)
        grup.setdefault(g, []).append({'key': k, 'label': lbl})

    if request.method == 'POST':
        try:
            from docxtpl import DocxTemplate
            from jinja2 import Environment, Undefined
        except ImportError:
            flash("Pustaka 'docxtpl' belum terpasang di server. Jalankan: pip install docxtpl", 'danger')
            return redirect(url_for('template_dokpil.isi', template_id=t.id))

        class _Kosong(Undefined):
            def __str__(self):
                return ""

        values = {k: request.form.get(k, '') for k in keys}
        doc = DocxTemplate(os.path.join(_folder(), t.file_template))
        doc.render(values, jinja_env=Environment(undefined=_Kosong))
        out_name = f"Isi_{secure_filename(t.nama)}_{int(time.time())}.docx"
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        doc.save(os.path.join(Config.UPLOAD_FOLDER, out_name))
        return send_from_directory(Config.UPLOAD_FOLDER, out_name, as_attachment=True)

    return render_template('template/isi.html', t=t, grup=grup, jumlah=len(keys))


@template_bp.route('/<int:template_id>/hapus', methods=['POST'])
@login_required
def hapus(template_id):
    if not _admin_katim():
        flash('Hanya Admin/Katim yang dapat menghapus template.', 'danger')
        return redirect(url_for('template_dokpil.daftar'))
    t = TemplateDokpil.query.get_or_404(template_id)
    path = os.path.join(_folder(), t.file_template)
    if os.path.exists(path):
        os.remove(path)
    db.session.delete(t)
    db.session.commit()
    flash('Template dihapus.', 'success')
    return redirect(url_for('template_dokpil.daftar'))
