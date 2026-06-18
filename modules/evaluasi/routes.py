# modules/evaluasi/routes.py
import json
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, send_from_directory)
from flask_login import login_required, current_user
from core.models import Paket, Peserta, KriteriaEvaluasi, TemplateKriteria
from core.database import db
from core.config import Config
from helpers.document_generator import generate_docx_kertas_kerja
from helpers.excel_generator import generate_xlsx_kertas_kerja

evaluasi_bp = Blueprint('evaluasi', __name__)

PILIHAN = ['Belum', 'Lulus', 'Gugur']


def _boleh_ubah(paket):
    if current_user.peran == 'Admin':
        return True
    return (current_user.peran in ['Pokmil', 'Ketua Pokja']
            and paket.assigned_pokmil == current_user.nama_pokmil)


def _kriteria(paket_id):
    return KriteriaEvaluasi.query.filter_by(paket_id=paket_id)\
        .order_by(KriteriaEvaluasi.kelompok, KriteriaEvaluasi.urutan, KriteriaEvaluasi.id).all()


@evaluasi_bp.route('/<int:paket_id>', methods=['GET', 'POST'])
@login_required
def kelola(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    if request.method == 'POST':
        if not _boleh_ubah(paket):
            flash('Hanya Pokmil bertugas yang dapat mengubah data.', 'warning')
            return redirect(url_for('evaluasi.kelola', paket_id=paket.id))

        aksi = request.form.get('aksi')
        if aksi == 'tambah':
            nama = request.form.get('nama_penyedia', '').strip()
            if nama:
                db.session.add(Peserta(
                    paket_id=paket.id, nama_penyedia=nama,
                    npwp=request.form.get('npwp', '').strip(),
                    harga_penawaran=float(request.form.get('harga_penawaran') or 0)))
                db.session.commit()
                flash('Peserta ditambahkan.', 'success')

        elif aksi == 'hapus':
            ps = Peserta.query.get(request.form.get('peserta_id'))
            if ps and ps.paket_id == paket.id:
                db.session.delete(ps)
                db.session.commit()
                flash('Peserta dihapus.', 'success')

        elif aksi == 'simpan':
            for ps in paket.peserta:
                ps.harga_penawaran = float(request.form.get(f'penawaran_{ps.id}') or 0)
                ps.harga_terkoreksi = float(request.form.get(f'terkoreksi_{ps.id}') or 0)
                ps.eval_administrasi = request.form.get(f'adm_{ps.id}', 'Belum')
                ps.eval_teknis = request.form.get(f'teknis_{ps.id}', 'Belum')
                ps.eval_kualifikasi = request.form.get(f'kual_{ps.id}', 'Belum')
                ps.catatan = request.form.get(f'catatan_{ps.id}')
            paket.status_paket = 'Evaluasi'
            db.session.commit()
            flash('Hasil evaluasi disimpan.', 'success')

        return redirect(url_for('evaluasi.kelola', paket_id=paket.id))

    peserta = Peserta.query.filter_by(paket_id=paket.id).order_by(Peserta.id).all()
    kriteria = _kriteria(paket.id)
    return render_template('evaluasi/kelola.html', paket=paket, peserta=peserta,
                           pilihan=PILIHAN, boleh_ubah=_boleh_ubah(paket),
                           jml_teknis=len([k for k in kriteria if k.kelompok == 'Teknis']),
                           jml_kualifikasi=len([k for k in kriteria if k.kelompok == 'Kualifikasi']))


# ---------- Setting Kriteria (Teknis dari LKE, Kualifikasi dari LDK) ----------
@evaluasi_bp.route('/<int:paket_id>/kriteria', methods=['GET', 'POST'])
@login_required
def kelola_kriteria(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    if request.method == 'POST':
        if not _boleh_ubah(paket):
            flash('Hanya Pokmil bertugas yang dapat mengubah kriteria.', 'warning')
            return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))

        aksi = request.form.get('aksi')
        if aksi == 'tambah':
            nama = request.form.get('nama_kriteria', '').strip()
            kelompok = request.form.get('kelompok', 'Teknis')
            if nama:
                db.session.add(KriteriaEvaluasi(
                    paket_id=paket.id, kelompok=kelompok,
                    sumber='LKE' if kelompok == 'Teknis' else 'LDK',
                    nama_kriteria=nama,
                    bobot=float(request.form.get('bobot') or 0),
                    ambang_batas=float(request.form.get('ambang_batas') or 0),
                    urutan=int(request.form.get('urutan') or 0)))
                db.session.commit()
                flash('Kriteria ditambahkan.', 'success')
        elif aksi == 'hapus':
            k = KriteriaEvaluasi.query.get(request.form.get('kriteria_id'))
            if k and k.paket_id == paket.id:
                db.session.delete(k)
                db.session.commit()
                flash('Kriteria dihapus.', 'success')
        elif aksi == 'simpan':
            for k in _kriteria(paket.id):
                nm = request.form.get(f'nama_{k.id}')
                if nm is not None and nm.strip():
                    k.nama_kriteria = nm.strip()
                if k.kelompok == 'Teknis':
                    k.bobot = float(request.form.get(f'bobot_{k.id}') or 0)
                    k.ambang_batas = float(request.form.get(f'ambang_{k.id}') or 0)
            db.session.commit()
            flash('Perubahan kriteria disimpan.', 'success')
        return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))

    kriteria = _kriteria(paket.id)
    teknis = [k for k in kriteria if k.kelompok == 'Teknis']
    kualifikasi = [k for k in kriteria if k.kelompok == 'Kualifikasi']
    total_bobot = sum(k.bobot or 0 for k in teknis)
    templates = TemplateKriteria.query.order_by(TemplateKriteria.dibuat_pada.desc()).all()
    return render_template('evaluasi/kriteria.html', paket=paket, teknis=teknis,
                           kualifikasi=kualifikasi, total_bobot=total_bobot,
                           templates=templates, boleh_ubah=_boleh_ubah(paket))


@evaluasi_bp.route('/<int:paket_id>/kriteria/simpan-template', methods=['POST'])
@login_required
def simpan_template_kriteria(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if not _boleh_ubah(paket):
        flash('Akses ditolak.', 'warning')
        return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))
    nama = (request.form.get('nama_template') or '').strip() or f"Template {paket.jenis_pengadaan}"
    data = [{"kelompok": k.kelompok, "nama": k.nama_kriteria, "bobot": k.bobot or 0,
             "ambang": k.ambang_batas or 0, "sumber": k.sumber} for k in _kriteria(paket.id)]
    if not data:
        flash('Belum ada kriteria untuk disimpan.', 'warning')
        return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))
    db.session.add(TemplateKriteria(nama=nama, jenis_pengadaan=paket.jenis_pengadaan,
                                    data_json=json.dumps(data)))
    db.session.commit()
    flash(f'Kriteria disimpan sebagai template "{nama}" ({len(data)} kriteria).', 'success')
    return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))


@evaluasi_bp.route('/<int:paket_id>/kriteria/terapkan-template', methods=['POST'])
@login_required
def terapkan_template_kriteria(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if not _boleh_ubah(paket):
        flash('Akses ditolak.', 'warning')
        return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))
    t = TemplateKriteria.query.get(request.form.get('template_id'))
    if not t:
        flash('Template tidak ditemukan.', 'warning')
        return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))
    ada = {(k.kelompok, k.nama_kriteria) for k in _kriteria(paket.id)}
    n = 0
    for i, d in enumerate(json.loads(t.data_json or '[]')):
        if (d['kelompok'], d['nama']) in ada:
            continue
        db.session.add(KriteriaEvaluasi(
            paket_id=paket.id, kelompok=d['kelompok'],
            sumber=d.get('sumber') or ('LKE' if d['kelompok'] == 'Teknis' else 'LDK'),
            nama_kriteria=d['nama'], bobot=d.get('bobot') or 0,
            ambang_batas=d.get('ambang') or 0, urutan=i))
        n += 1
    db.session.commit()
    flash(f'{n} kriteria dari template "{t.nama}" diterapkan.', 'success')
    return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))


@evaluasi_bp.route('/kriteria/template/<int:template_id>/hapus', methods=['POST'])
@login_required
def hapus_template_kriteria(template_id):
    if current_user.peran not in ['Admin', 'Katim', 'Pokmil', 'Ketua Pokja']:
        flash('Akses ditolak.', 'warning')
        return redirect(url_for('paket.daftar_paket'))
    t = TemplateKriteria.query.get_or_404(template_id)
    paket_id = request.form.get('paket_id')
    db.session.delete(t)
    db.session.commit()
    flash('Template kriteria dihapus.', 'success')
    return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket_id) if paket_id
                    else url_for('paket.daftar_paket'))


@evaluasi_bp.route('/<int:paket_id>/kriteria/otomatis', methods=['POST'])
@login_required
def isi_otomatis(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if not _boleh_ubah(paket):
        flash('Hanya Pokmil bertugas yang dapat mengisi kriteria.', 'warning')
        return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))

    from helpers.kriteria_standar import kriteria_standar
    std = kriteria_standar(paket)
    ada = _kriteria(paket.id)
    ada_teknis = any(k.kelompok == 'Teknis' for k in ada)
    ada_kual = any(k.kelompok == 'Kualifikasi' for k in ada)

    n = 0
    if not ada_teknis:
        for i, (nama, bobot, ambang) in enumerate(std['teknis']):
            db.session.add(KriteriaEvaluasi(
                paket_id=paket.id, kelompok='Teknis', sumber='LKE',
                nama_kriteria=nama, bobot=bobot, ambang_batas=ambang, urutan=i))
            n += 1
    if not ada_kual:
        for i, nama in enumerate(std['kualifikasi']):
            db.session.add(KriteriaEvaluasi(
                paket_id=paket.id, kelompok='Kualifikasi', sumber='LDK',
                nama_kriteria=nama, urutan=i))
            n += 1
    db.session.commit()

    if n:
        flash(f'{n} kriteria standar ditambahkan. Silakan sesuaikan bobot/ambang & '
              f'persyaratan sesuai LKE dan LDK paket ini.', 'success')
    else:
        flash('Kriteria sudah ada. Hapus dulu bila ingin mengisi ulang dari standar.', 'info')
    return redirect(url_for('evaluasi.kelola_kriteria', paket_id=paket.id))


@evaluasi_bp.route('/<int:paket_id>/unduh-excel')
@login_required
def unduh_excel(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    peserta = Peserta.query.filter_by(paket_id=paket.id).order_by(Peserta.id).all()
    if not peserta:
        flash('Belum ada peserta untuk dievaluasi.', 'warning')
        return redirect(url_for('evaluasi.kelola', paket_id=paket.id))
    ok, hasil = generate_xlsx_kertas_kerja(paket, peserta, _kriteria(paket.id))
    return send_from_directory(Config.UPLOAD_FOLDER, hasil, as_attachment=True)


@evaluasi_bp.route('/<int:paket_id>/unduh-word')
@login_required
def unduh_word(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    peserta = Peserta.query.filter_by(paket_id=paket.id).order_by(Peserta.id).all()
    ok, hasil = generate_docx_kertas_kerja(paket, peserta, _kriteria(paket.id))
    return send_from_directory(Config.UPLOAD_FOLDER, hasil, as_attachment=True)
