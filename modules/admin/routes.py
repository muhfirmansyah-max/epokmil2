from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from core.models import db, User
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

PERAN_OPSI = ['Admin', 'Katim', 'Kepala UKPBJ', 'Ketua Pokja', 'Pokmil']


def _hanya_admin():
    return 'Admin' in (current_user.peran or '')


@admin_bp.route('/users')
@login_required
def manajemen_user():
    # Admin & Katim boleh melihat daftar
    if 'Admin' not in current_user.peran and 'Katim' not in current_user.peran:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('beranda'))
    users = User.query.order_by(User.peran, User.nama_lengkap).all()
    return render_template('admin/manajemen_user.html', users=users)


@admin_bp.route('/tambah-akun', methods=['GET', 'POST'])
@login_required
def tambah_akun():
    if not _hanya_admin():
        flash('Hanya Admin yang diizinkan menambah akun!', 'danger')
        return redirect(url_for('admin.manajemen_user'))

    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar!', 'warning')
            return redirect(url_for('admin.tambah_akun'))
        new_user = User(
            username=username,
            password_hash=generate_password_hash(request.form.get('password')),
            nama_lengkap=request.form.get('nama_lengkap'),
            peran=request.form.get('peran'),
            nama_pokmil=request.form.get('nama_pokmil') or None,
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Akun berhasil dibuat.', 'success')
        return redirect(url_for('admin.manajemen_user'))
    return render_template('admin/tambah_akun.html')


# ------------------- BARU: Edit Akun -------------------
@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not _hanya_admin():
        flash('Hanya Admin yang dapat mengubah akun!', 'danger')
        return redirect(url_for('admin.manajemen_user'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.nama_lengkap = request.form.get('nama_lengkap')
        user.peran = request.form.get('peran')
        user.nama_pokmil = request.form.get('nama_pokmil') or None
        user.is_ketua_pokmil = (request.form.get('is_ketua_pokmil') == 'on')
        # Ganti password hanya bila diisi
        pwd = request.form.get('password')
        if pwd:
            user.password_hash = generate_password_hash(pwd)
        db.session.commit()
        flash(f'Akun {user.username} berhasil diperbarui.', 'success')
        return redirect(url_for('admin.manajemen_user'))

    return render_template('admin/edit_user.html', user=user, peran_opsi=PERAN_OPSI)


# ------------------- BARU: Hapus Akun -------------------
@admin_bp.route('/users/<int:user_id>/hapus', methods=['POST'])
@login_required
def hapus_user(user_id):
    if not _hanya_admin():
        flash('Hanya Admin yang dapat menghapus akun!', 'danger')
        return redirect(url_for('admin.manajemen_user'))
    if user_id == current_user.id:
        flash('Anda tidak dapat menghapus akun Anda sendiri.', 'warning')
        return redirect(url_for('admin.manajemen_user'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'Akun {user.username} telah dihapus.', 'success')
    return redirect(url_for('admin.manajemen_user'))
