from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from core.models import Paket, User
from core.database import db

paket_bp = Blueprint('paket', __name__)


def _daftar_pokmil():
    """Daftar nama Pokmil unik (untuk dropdown penugasan)."""
    return db.session.query(User.nama_pokmil).filter(
        User.nama_pokmil != None, User.nama_pokmil != ''
    ).distinct().all()


@paket_bp.route('/')
@login_required
def daftar_paket():
    if current_user.peran in ['Admin', 'Katim']:
        daftar = Paket.query.all()
    else:
        daftar = Paket.query.filter_by(assigned_pokmil=current_user.nama_pokmil).all()
    return render_template('paket/index.html', daftar_paket=daftar)


@paket_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
def tambah_paket():
    if current_user.peran not in ['Admin', 'Katim']:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    if request.method == 'POST':
        assigned = request.form.get('assigned_pokmil')
        paket_baru = Paket(
            nama_paket=request.form.get('nama_paket'),
            kode_paket=request.form.get('kode_paket'),
            tahun_anggaran=int(request.form.get('tahun_anggaran') or 2026),
            unit_kerja=request.form.get('unit_kerja'),
            nama_ppk=request.form.get('nama_ppk'),
            nilai_hps=float(request.form.get('nilai_hps') or 0),
            sumber_dana=request.form.get('sumber_dana'),
            jenis_pengadaan=request.form.get('jenis_pengadaan'),
            metode_pemilihan=request.form.get('metode_pemilihan'),
            metode_kualifikasi=request.form.get('metode_kualifikasi'),
            assigned_pokmil=assigned or None,
            status_paket='Reviu' if assigned else 'Draf',
        )
        db.session.add(paket_baru)
        db.session.commit()
        flash('Paket pengadaan berhasil direkam ke sistem!', 'success')
        return redirect(url_for('paket.daftar_paket'))

    # GET: kirim daftar Pokmil agar dropdown penugasan terisi
    return render_template('paket/tambah.html', daftar_pokmil=_daftar_pokmil())


@paket_bp.route('/edit/<int:paket_id>', methods=['GET', 'POST'])
@login_required
def edit_paket(paket_id):
    paket = Paket.query.get_or_404(paket_id)

    if current_user.peran not in ['Admin', 'Katim']:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    if request.method == 'POST':
        paket.nama_paket = request.form.get('nama_paket')
        paket.kode_paket = request.form.get('kode_paket')
        paket.unit_kerja = request.form.get('unit_kerja')
        paket.nama_ppk = request.form.get('nama_ppk')
        paket.nilai_hps = float(request.form.get('nilai_hps') or 0)
        paket.sumber_dana = request.form.get('sumber_dana')
        paket.jenis_pengadaan = request.form.get('jenis_pengadaan')
        paket.metode_pemilihan = request.form.get('metode_pemilihan')
        paket.metode_kualifikasi = request.form.get('metode_kualifikasi')
        paket.assigned_pokmil = request.form.get('assigned_pokmil')
        db.session.commit()
        flash('Data paket berhasil diperbarui!', 'success')
        return redirect(url_for('paket.daftar_paket'))

    return render_template('paket/edit_paket.html', paket=paket, daftar_pokmil=_daftar_pokmil())
