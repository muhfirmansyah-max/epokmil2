# modules/penetapan/routes.py
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, send_from_directory)
from flask_login import login_required, current_user
from core.models import Paket, Peserta, Penetapan
from core.database import db
from core.config import Config
from helpers.document_generator import generate_docx_penetapan
from datetime import datetime

penetapan_bp = Blueprint('penetapan', __name__)


@penetapan_bp.route('/<int:paket_id>', methods=['GET', 'POST'])
@login_required
def kelola(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    penetapan = Penetapan.query.filter_by(paket_id=paket.id).first()
    if not penetapan:
        penetapan = Penetapan(paket_id=paket.id)
        db.session.add(penetapan)
        db.session.commit()

    # Hanya peserta yang lulus seluruh tahap yang dapat ditetapkan
    peserta_lulus = [p for p in paket.peserta if p.lulus_semua]

    if request.method == 'POST':
        if current_user.peran == 'Katim':
            flash('Katim hanya memiliki akses lihat.', 'warning')
            return redirect(url_for('penetapan.kelola', paket_id=paket.id))
        penetapan.nomor_sk = request.form.get('nomor_sk')
        tgl = request.form.get('tanggal_sk')
        penetapan.tanggal_sk = datetime.strptime(tgl, '%Y-%m-%d').date() if tgl else None
        penetapan.pemenang_id = request.form.get('pemenang_id') or None
        penetapan.cadangan_id = request.form.get('cadangan_id') or None
        penetapan.dasar_penetapan = request.form.get('dasar_penetapan')
        paket.status_paket = 'Penetapan'
        db.session.commit()
        flash('Penetapan pemenang disimpan.', 'success')
        return redirect(url_for('penetapan.kelola', paket_id=paket.id))

    return render_template('penetapan/kelola.html', paket=paket,
                           penetapan=penetapan, peserta_lulus=peserta_lulus)


@penetapan_bp.route('/<int:paket_id>/unduh')
@login_required
def unduh(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    penetapan = Penetapan.query.filter_by(paket_id=paket.id).first()
    if not penetapan or not penetapan.pemenang_id:
        flash('Tetapkan pemenang terlebih dahulu.', 'warning')
        return redirect(url_for('penetapan.kelola', paket_id=paket.id))
    ok, hasil = generate_docx_penetapan(paket, penetapan)
    return send_from_directory(Config.UPLOAD_FOLDER, hasil, as_attachment=True)
