# modules/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from core.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('beranda'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('beranda'))
            
        flash('Username atau password salah!', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda berhasil keluar sistem.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/tambah-user', methods=['GET', 'POST'])
@login_required
def tambah_user():
    # Perbaikan: Admin DAN Katim bisa mengakses untuk manajemen personil
    if current_user.peran not in ['Admin', 'Katim']:
        flash('Akses ditolak! Anda tidak memiliki wewenang.', 'danger')
        return redirect(url_for('beranda'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nama = request.form.get('nama_lengkap')
        peran = request.form.get('peran')
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar!', 'danger')
            return redirect(url_for('auth.tambah_user'))

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            nama_lengkap=nama,
            peran=peran
            # nama_pokmil akan diisi melalui rute tambah_pokmil
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Akun {nama} berhasil dibuat!', 'success')
        return redirect(url_for('beranda'))

    return render_template('tambah_user.html')

@auth_bp.route('/tambah-pokmil', methods=['GET', 'POST'])
@login_required
def tambah_pokmil():
    # Proteksi: Hanya Katim yang bisa membentuk Pokmil
    if current_user.peran != 'Katim':
        flash('Hanya Katim yang dapat membentuk Pokmil!', 'danger')
        return redirect(url_for('beranda'))
    
    # Hanya ambil user yang perannya Pokmil dan belum masuk kelompok mana pun
    calon_anggota = User.query.filter_by(peran='Pokmil', nama_pokmil=None).all()
    
    if request.method == 'POST':
        nama_pokmil = request.form.get('nama_pokmil')
        anggota_terpilih = request.form.getlist('anggota') # List ID user dari checkbox
        
        if not nama_pokmil or not anggota_terpilih:
            flash('Harap isi nama Pokmil dan pilih anggota!', 'warning')
            return redirect(url_for('auth.tambah_pokmil'))

        for user_id in anggota_terpilih:
            user = User.query.get(user_id)
            if user:
                user.nama_pokmil = nama_pokmil
            
        db.session.commit()
        flash(f'Pokmil {nama_pokmil} berhasil dibentuk!', 'success')
        return redirect(url_for('beranda'))
        
    return render_template('auth/tambah_pokmil.html', calon_anggota=calon_anggota)