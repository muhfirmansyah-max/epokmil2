# modules/laporan/routes.py
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, send_from_directory)
from flask_login import login_required, current_user
from core.models import Paket, Peserta, Penetapan, LaporanTender
from core.database import db
from core.config import Config
from helpers.document_generator import generate_docx_laporan
from datetime import datetime

laporan_bp = Blueprint('laporan', __name__)


@laporan_bp.route('/<int:paket_id>', methods=['GET', 'POST'])
@login_required
def kelola(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    laporan = LaporanTender.query.filter_by(paket_id=paket.id).first()
    if not laporan:
        laporan = LaporanTender(paket_id=paket.id)
        db.session.add(laporan)
        db.session.commit()

    if request.method == 'POST':
        if current_user.peran == 'Katim':
            flash('Katim hanya memiliki akses lihat.', 'warning')
            return redirect(url_for('laporan.kelola', paket_id=paket.id))
        laporan.nomor_laporan = request.form.get('nomor_laporan')
        tgl = request.form.get('tanggal')
        laporan.tanggal = datetime.strptime(tgl, '%Y-%m-%d').date() if tgl else None
        laporan.ringkasan = request.form.get('ringkasan')
        paket.status_paket = 'Selesai'
        db.session.commit()
        flash('Laporan hasil tender disimpan. Paket selesai.', 'success')
        return redirect(url_for('laporan.kelola', paket_id=paket.id))

    return render_template('laporan/kelola.html', paket=paket, laporan=laporan)


@laporan_bp.route('/<int:paket_id>/unduh')
@login_required
def unduh(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    laporan = LaporanTender.query.filter_by(paket_id=paket.id).first()
    peserta = Peserta.query.filter_by(paket_id=paket.id).order_by(Peserta.id).all()
    penetapan = Penetapan.query.filter_by(paket_id=paket.id).first()
    if not laporan:
        flash('Isi laporan terlebih dahulu.', 'warning')
        return redirect(url_for('laporan.kelola', paket_id=paket.id))
    ok, hasil = generate_docx_laporan(paket, laporan, peserta, penetapan)
    return send_from_directory(Config.UPLOAD_FOLDER, hasil, as_attachment=True)
