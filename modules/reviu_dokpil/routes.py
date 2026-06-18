# modules/reviu_dokpil/routes.py
import os
import json
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, send_from_directory)
from flask_login import login_required, current_user
from core.models import (Paket, ReviuPaket, DetailUnsurReviu, MasterUnsurReviu,
                         DokpilData, TemplateDokpil)
from core.database import db
from core.config import Config
from helpers.mapping_dokpil import tentukan_master_dokpil
from helpers.dokpil_fields import field_dokpil
from helpers.templatizer import label_dari_key
from helpers.document_generator import generate_docx_ba_reviu, generate_docx_dokpil
from datetime import datetime

reviu_bp = Blueprint('reviu_dokpil', __name__)

TEMPLATE_KEY = '__template_id__'   # kunci khusus penyimpan pilihan template di DokpilData


def _template_terpilih(paket_id):
    row = DokpilData.query.filter_by(paket_id=paket_id, field_key=TEMPLATE_KEY).first()
    if row and row.field_value:
        return TemplateDokpil.query.get(int(row.field_value))
    return None


def _muat_reviu(paket):
    """Mengambil/membuat ReviuPaket + DetailUnsurReviu dari bank unsur."""
    reviu = ReviuPaket.query.filter_by(paket_id=paket.id).first()
    if not reviu:
        reviu = ReviuPaket(paket_id=paket.id)
        db.session.add(reviu)
        db.session.commit()

    detail = DetailUnsurReviu.query.filter_by(reviu_id=reviu.id).all()
    # Sinkronkan: tambahkan unsur master yang belum ada (tanpa menghapus isian lama).
    sudah_ada = {(d.kelompok, d.nama_unsur) for d in detail}
    baru = 0
    for mu in MasterUnsurReviu.query.all():
        if (mu.kelompok, mu.nama_unsur) not in sudah_ada:
            db.session.add(DetailUnsurReviu(
                reviu_id=reviu.id, nama_unsur=mu.nama_unsur,
                kelompok=mu.kelompok, kesesuaian='Belum Diisi'))
            baru += 1
    if baru:
        db.session.commit()
        detail = DetailUnsurReviu.query.filter_by(reviu_id=reviu.id).all()
    return reviu, detail


@reviu_bp.route('/<int:paket_id>', methods=['GET', 'POST'])
@login_required
def kelola_reviu(paket_id):
    paket = Paket.query.get_or_404(paket_id)

    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak! Anda tidak ditugaskan untuk paket ini.', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    reviu, detail_unsur = _muat_reviu(paket)

    if request.method == 'POST':
        if current_user.peran == 'Katim':
            flash('Katim hanya memiliki akses lihat (Monitoring).', 'warning')
            return redirect(url_for('reviu_dokpil.kelola_reviu', paket_id=paket.id))

        reviu.nomor_ba_reviu = request.form.get('nomor_ba_reviu')
        tgl = request.form.get('tanggal_ba')
        reviu.tanggal_ba = datetime.strptime(tgl, '%Y-%m-%d').date() if tgl else None
        # PERBAIKAN: gunakan nama field model yang benar (sebelumnya 'kessummary_reviu')
        reviu.kesimpulan_reviu = request.form.get('kesimpulan_reviu')
        reviu.catatan_kak = request.form.get('catatan_kak')
        reviu.catatan_spesifikasi = request.form.get('catatan_spesifikasi')
        reviu.catatan_hps = request.form.get('catatan_hps')
        reviu.catatan_kontrak = request.form.get('catatan_kontrak')
        reviu.catatan_anggaran = request.form.get('catatan_anggaran')
        reviu.catatan_rup = request.form.get('catatan_rup')
        reviu.catatan_pasar = request.form.get('catatan_pasar')

        for det in detail_unsur:
            det.kesesuaian = request.form.get(f'status_{det.id}', det.kesesuaian)
            det.catatan_reviu = request.form.get(f'catatan_{det.id}')

        paket.status_paket = 'Dokpil'
        db.session.commit()
        flash('Kertas kerja reviu berhasil disimpan.', 'success')
        return redirect(url_for('reviu_dokpil.kelola_reviu', paket_id=paket.id))

    total = len(detail_unsur)
    selesai = len([d for d in detail_unsur if d.kesesuaian not in ('Belum Diisi', None, '')])
    progress = int((selesai / total) * 100) if total else 0
    rekomendasi_mdp = tentukan_master_dokpil(paket)

    return render_template('reviu/kelola.html', paket=paket, reviu=reviu,
                           detail_unsur=detail_unsur, rekomendasi_mdp=rekomendasi_mdp,
                           progress=progress)


@reviu_bp.route('/<int:paket_id>/unduh-ba')
@login_required
def unduh_ba_reviu(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    reviu, detail_unsur = _muat_reviu(paket)
    ok, hasil = generate_docx_ba_reviu(paket, reviu, detail_unsur)
    if not ok:
        flash(hasil, 'danger')
        return redirect(url_for('reviu_dokpil.kelola_reviu', paket_id=paket.id))
    return send_from_directory(Config.UPLOAD_FOLDER, hasil, as_attachment=True)


@reviu_bp.route('/<int:paket_id>/dokpil', methods=['GET', 'POST'])
@login_required
def dokpil(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    if request.method == 'POST':
        if current_user.peran == 'Katim':
            flash('Katim hanya memiliki akses lihat.', 'warning')
            return redirect(url_for('reviu_dokpil.dokpil', paket_id=paket.id))
        tid = request.form.get('template_id', '').strip()
        row = DokpilData.query.filter_by(paket_id=paket.id, field_key=TEMPLATE_KEY).first()
        if tid:
            if row:
                row.field_value = tid
            else:
                db.session.add(DokpilData(paket_id=paket.id, field_key=TEMPLATE_KEY, field_value=tid))
            flash('Template Dokpil dipilih.', 'success')
        elif row:
            db.session.delete(row)
            flash('Pilihan template dilepas (kembali ke pemilihan otomatis).', 'info')
        db.session.commit()
        return redirect(url_for('reviu_dokpil.dokpil', paket_id=paket.id))

    templates = TemplateDokpil.query.filter(
        TemplateDokpil.kategori.in_(['Dokpil', 'Dokumen Kualifikasi'])
    ).order_by(TemplateDokpil.dibuat_pada.desc()).all()
    terpilih = _template_terpilih(paket.id)

    auto_file = tentukan_master_dokpil(paket)
    auto_tersedia = os.path.exists(os.path.join(Config.TEMPLATE_DOC_FOLDER, auto_file))
    tersedia = bool(terpilih) or auto_tersedia

    auto_fields = [
        ("Kode RUP", paket.kode_paket or '-'),
        ("Nama Paket", paket.nama_paket),
        ("Uraian Singkat Paket", paket.nama_paket),
        ("Satuan Kerja / OPD", paket.unit_kerja or '-'),
        ("Sumber Dana", paket.sumber_dana or '-'),
        ("Tahun Anggaran", paket.tahun_anggaran or '-'),
        ("Nilai HPS", f"Rp {paket.nilai_hps:,.0f}".replace(',', '.') if paket.nilai_hps else '-'),
        ("PPK", paket.nama_ppk or '-'),
    ]
    manual_fields = [
        "Alamat & website Pokja/SPSE", "Jadwal & jangka waktu pelaksanaan",
        "Metode & ambang batas evaluasi teknis", "Masa berlaku penawaran",
        "Garansi / layanan purna jual", "Jaminan pelaksanaan",
        "Persyaratan kualifikasi (LDK)",
    ]
    return render_template('reviu/dokpil.html', paket=paket,
                           templates=templates, terpilih=terpilih,
                           auto_file=auto_file, auto_tersedia=auto_tersedia,
                           tersedia=tersedia, auto_fields=auto_fields,
                           manual_fields=manual_fields)


@reviu_bp.route('/<int:paket_id>/isian', methods=['GET', 'POST'])
@login_required
def isian_dokpil(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))

    terpilih = _template_terpilih(paket.id)
    if terpilih:
        # Form dibangun dari field template terpilih (token cocok saat merge)
        grup_map = {}
        for k in json.loads(terpilih.fields_json or '[]'):
            g, lbl = label_dari_key(k)
            grup_map.setdefault(g, []).append({'key': k, 'label': lbl})
        grup = [{'judul': f"{terpilih.nama} — {g}", 'fields': fs} for g, fs in grup_map.items()]
        sumber = f'Template terkelola: {terpilih.nama}'
    else:
        grup = field_dokpil(paket)
        sumber = 'Daftar standar (belum memilih template di halaman Dokpil)'

    if request.method == 'POST':
        if current_user.peran == 'Katim':
            flash('Katim hanya memiliki akses lihat.', 'warning')
            return redirect(url_for('reviu_dokpil.isian_dokpil', paket_id=paket.id))
        for g in grup:
            for f in g['fields']:
                val = request.form.get(f['key'], '')
                row = DokpilData.query.filter_by(paket_id=paket.id, field_key=f['key']).first()
                if row:
                    row.field_value = val
                else:
                    db.session.add(DokpilData(paket_id=paket.id, field_key=f['key'], field_value=val))
        db.session.commit()
        flash('Isian Dokpil disimpan.', 'success')
        return redirect(url_for('reviu_dokpil.isian_dokpil', paket_id=paket.id))

    nilai = {d.field_key: d.field_value for d in
             DokpilData.query.filter_by(paket_id=paket.id).all() if d.field_key != TEMPLATE_KEY}
    return render_template('reviu/isian_dokpil.html', paket=paket, grup=grup,
                           nilai=nilai, sumber=sumber)


@reviu_bp.route('/<int:paket_id>/unduh-dokpil')
@login_required
def unduh_dokpil(paket_id):
    paket = Paket.query.get_or_404(paket_id)
    if current_user.peran not in ['Admin', 'Katim'] and paket.assigned_pokmil != current_user.nama_pokmil:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('paket.daftar_paket'))
    isian = {d.field_key: d.field_value for d in
             DokpilData.query.filter_by(paket_id=paket.id).all() if d.field_key != TEMPLATE_KEY}
    terpilih = _template_terpilih(paket.id)
    tpl_path = (os.path.join(Config.TEMPLATE_DOC_FOLDER, terpilih.file_template)
                if terpilih else None)
    ok, hasil = generate_docx_dokpil(paket, isian=isian, template_path=tpl_path)
    if not ok:
        flash(hasil, 'warning')
        return redirect(url_for('reviu_dokpil.dokpil', paket_id=paket.id))
    if paket.status_paket == 'Dokpil':
        paket.status_paket = 'Evaluasi'
        db.session.commit()
    return send_from_directory(Config.UPLOAD_FOLDER, hasil, as_attachment=True)
