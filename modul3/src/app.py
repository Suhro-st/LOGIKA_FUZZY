# -*- coding: utf-8 -*-
"""
app.py - Lapisan tampilan (Streamlit) "Sistem Penerapan Gaji Karyawan Berbasis Logika Fuzzy".
 
Seluruh perhitungan fuzzy (validasi, fuzzifikasi, inferensi Mamdani, centroid) berada di
fuzzy_logic.py. File ini hanya mengurus antarmuka, grafik, dan penyimpanan riwayat.
 
Jalankan dengan:  streamlit run app.py
"""
import os
import sys
from datetime import datetime

import streamlit as st

# Otomatis beralih ke 'streamlit run' jika dijalankan langsung (misal tombol Play di VS Code)
if __name__ == "__main__" and not st.runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", os.path.abspath(__file__)]
    sys.exit(stcli.main())

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import fuzzy_logic as fl
 
# ---------------------------------------------------------------------------
# Konfigurasi halaman & gaya
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Gaji Karyawan Fuzzy", page_icon="💼", layout="wide")
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
KOLOM_DATASET = ["ID_Karyawan", "Nama_Karyawan", "Masa_Kerja", "Nilai_Kinerja", "Pendidikan",
                 "Gaji_Aktual", "Gaji_Prediksi_Fuzzy"]
WARNA = ["#0B5563", "#F2A541", "#C8553D", "#5B8E7D", "#7A5C99"]
WARNA_KATEGORI = {"Rendah": "#C8553D", "Sedang": "#F2A541", "Tinggi": "#0B5563"}
DISCLAIMER = ("Hasil yang ditampilkan merupakan **rekomendasi sistem** berdasarkan **data simulasi**, "
              "bukan keputusan penggajian resmi.")
 
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem; max-width: 1250px;}
    .hero {background: linear-gradient(120deg, #12343B 0%, #0B5563 100%); color: #fff;
           padding: 1.4rem 1.6rem; border-radius: 16px; margin-bottom: 1.2rem;}
    .hero h1 {margin: 0; font-size: 1.7rem; color: #fff;}
    .hero p {margin: .35rem 0 0 0; color: #CFE6EA;}
    .kartu {background: #ffffff; border: 1px solid #DCE5E7; border-radius: 14px; padding: 1rem 1.2rem;
            box-shadow: 0 2px 8px rgba(18,52,59,.07);}
    .kartu .label {color: #5C7A80; font-size: .85rem;}
    .kartu .nilai {color: #12343B; font-size: 1.7rem; font-weight: 700;}
    .hasil {background: linear-gradient(120deg, #0B5563, #12343B); color: #fff; border-radius: 16px;
            padding: 1.3rem 1.5rem; text-align: center;}
    .hasil .label {color: #CFE6EA; font-size: .95rem;}
    .hasil .nilai {font-size: 2.2rem; font-weight: 800; letter-spacing: .5px;}
    .badge {display: inline-block; padding: .2rem .9rem; border-radius: 999px; color: #fff;
            font-weight: 700; margin-top: .4rem;}
    @media (max-width: 640px) {.hero h1 {font-size: 1.3rem;} .hasil .nilai {font-size: 1.7rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)
 
 
# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data
def muat_dataset():
    """Baca dataset.csv. Mengembalikan (DataFrame, pesan_error | None)."""
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        return pd.DataFrame(columns=KOLOM_DATASET), "File dataset.csv tidak ditemukan di folder aplikasi."
    except Exception as e:  # file rusak, encoding salah, dll.
        return pd.DataFrame(columns=KOLOM_DATASET), f"Dataset gagal dibaca: {e}"
    hilang = [k for k in KOLOM_DATASET if k not in df.columns]
    if hilang:
        return pd.DataFrame(columns=KOLOM_DATASET), "Kolom dataset tidak lengkap: " + ", ".join(hilang)
    return df, None
 
 
def rp(nilai):
    return fl.format_rupiah(nilai)
 
 
# ---------------------------------------------------------------------------
# Visualisasi (matplotlib)
# ---------------------------------------------------------------------------
JUDUL_VAR = {"masa_kerja": "Masa Kerja (tahun)", "kinerja": "Nilai Kinerja (0-100)",
             "pendidikan": "Pendidikan (skor ordinal)", "gaji": "Rekomendasi Gaji (juta Rp)"}
 
 
def gambar_mf(nama, nilai=None):
    """Fungsi keanggotaan satu variabel; garis putus-putus menandai nilai input."""
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    x = fl.universe(nama)
    for warna, (label, spec) in zip(WARNA, fl.VARIABEL[nama]["mf"].items()):
        ax.plot(x, fl.mf(x, spec), lw=2.2, color=warna, label=label)
        if nilai is not None:
            d = float(fl.mf(nilai, spec))
            if d > 0:
                ax.plot([nilai], [d], "o", color=warna, ms=6)
    if nilai is not None:
        ax.axvline(nilai, color="#8A9BA0", ls=":")
    if nama == "pendidikan":
        ax.set_xticks([1, 2, 3, 4])
        ax.set_xticklabels(["1\nSMA", "2\nD3", "3\nS1", "4\nS2"])
    ax.set_ylim(-0.02, 1.08)
    ax.set_title(JUDUL_VAR[nama], fontweight="bold", fontsize=10)
    ax.set_ylabel("Derajat keanggotaan", fontsize=8)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
    fig.tight_layout()
    return fig
 
 
def gambar_inferensi(hasil):
    """Hasil agregasi (max) seluruh aturan dan titik centroid."""
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    x = hasil.x_gaji
    for warna, (label, spec) in zip(WARNA, fl.MF_GAJI.items()):
        ax.plot(x, fl.mf(x, spec), color=warna, lw=1, alpha=0.5)
        a = hasil.kekuatan_output[label]
        if a > 0:
            ax.fill_between(x, np.fmin(a, fl.mf(x, spec)), color=warna, alpha=0.3, label=f"{label} (α={a:.3f})")
    ax.plot(x, hasil.agregasi, color="#12343B", lw=2.2, label="Agregasi (max)")
    ax.axvline(hasil.gaji_juta, color="#C8553D", ls="--", lw=2, label=f"Centroid = {hasil.gaji_juta:.3f} juta")
    ax.set_xlabel("Rekomendasi gaji (juta Rp)")
    ax.set_ylabel("Derajat keanggotaan")
    ax.set_title(f"Hasil Inferensi Mamdani \u2192 {hasil.gaji_format} ({hasil.kategori})", fontweight="bold", fontsize=11)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    return fig
 
 
def gambar_aktual_vs_prediksi(df):
    fig, ax = plt.subplots(figsize=(5.2, 4))
    a, p = df["Gaji_Aktual"] / 1e6, df["Prediksi_Dihitung"] / 1e6
    ax.scatter(a, p, color="#0B5563", s=36, alpha=0.85, edgecolor="white")
    lim = [min(a.min(), p.min()) - 0.5, max(a.max(), p.max()) + 0.5]
    ax.plot(lim, lim, "--", color="#C8553D", label="Prediksi = Aktual")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("Gaji aktual (juta Rp)")
    ax.set_ylabel("Gaji prediksi fuzzy (juta Rp)")
    ax.set_title("Gaji Aktual vs Prediksi", fontweight="bold", fontsize=10)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig
 
 
def gambar_kategori(df):
    urut = ["Rendah", "Sedang", "Tinggi"]
    hitung = df["Kategori_Prediksi"].value_counts().reindex(urut).fillna(0)
    fig, ax = plt.subplots(figsize=(5.2, 4))
    batang = ax.bar(urut, hitung.values, color=[WARNA_KATEGORI[k] for k in urut])
    for b, v in zip(batang, hitung.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.2, f"{int(v)}", ha="center", fontsize=9)
    ax.set_ylabel("Jumlah karyawan")
    ax.set_title("Sebaran Kategori Gaji Prediksi", fontweight="bold", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig
 
 
def tampilkan(fig):
    st.pyplot(fig)
    plt.close(fig)
 
 
# ---------------------------------------------------------------------------
# Komponen UI
# ---------------------------------------------------------------------------
def kartu(label, nilai):
    st.markdown(f'<div class="kartu"><div class="label">{label}</div><div class="nilai">{nilai}</div></div>',
                unsafe_allow_html=True)
 
 
def hero(judul, subjudul):
    st.markdown(f'<div class="hero"><h1>{judul}</h1><p>{subjudul}</p></div>', unsafe_allow_html=True)
 
 
def tabel_aturan_df():
    return pd.DataFrame([{"No": r.nomor, "Masa Kerja": r.masa, "Kinerja": r.kinerja,
                          "Pendidikan": r.pendidikan, "Gaji": r.gaji} for r in fl.RULES])
 
 
def csv_bytes(df, sep=";"):
    return df.to_csv(index=False, sep=sep).encode("utf-8-sig")
 
 
# ---------------------------------------------------------------------------
# Halaman
# ---------------------------------------------------------------------------
def halaman_dashboard():
    hero("Sistem Penerapan Gaji Karyawan Berbasis Logika Fuzzy",
         "Rekomendasi gaji dengan metode Fuzzy Mamdani dan defuzzifikasi Centroid")
    df, galat = muat_dataset()
    if galat:
        st.error(galat)
        return
    df = df.copy()
    try:
        df["Prediksi_Dihitung"] = fl.prediksi_dataset(df)
    except Exception as e:
        st.error(f"Dataset memuat data yang tidak valid: {e}")
        return
    df["Kategori_Prediksi"] = df["Prediksi_Dihitung"].apply(fl.kategori_gaji)
    ev = fl.evaluasi(df["Gaji_Aktual"], df["Prediksi_Dihitung"])
 
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kartu("Jumlah karyawan (dataset)", f"{len(df)}")
    with c2:
        kartu("Rata-rata gaji aktual", rp(df["Gaji_Aktual"].mean()))
    with c3:
        kartu("MAE", rp(ev["MAE"]))
    with c4:
        kartu("RMSE", rp(ev["RMSE"]))
    st.write("")
    k1, k2 = st.columns(2)
    with k1:
        tampilkan(gambar_aktual_vs_prediksi(df))
    with k2:
        tampilkan(gambar_kategori(df))
    st.info(DISCLAIMER)
 
 
def halaman_hitung():
    hero("Hitung Rekomendasi Gaji", "Masukkan data karyawan, lalu sistem menghitung rekomendasi gaji secara fuzzy")
    with st.form("form_karyawan"):
        nama = st.text_input("Nama karyawan", placeholder="Masukkan nama karyawan (contoh: Budi Santoso)")
        c1, c2, c3 = st.columns(3)
        masa = c1.number_input("Masa kerja (tahun)", min_value=-100.0, max_value=100.0, value=8.0, step=0.5,
                               help="Rentang valid 0-30 tahun.")
        kinerja = c2.number_input("Nilai kinerja", min_value=-1000.0, max_value=1000.0, value=78.0, step=1.0,
                                  help="Rentang valid 0-100.")
        pend = c3.selectbox("Pendidikan terakhir", list(fl.PENDIDIKAN_VALID), index=2)
        kirim = st.form_submit_button("Hitung Rekomendasi Gaji")
 
    if kirim:
        hasil = fl.proses_input(masa, kinerja, pend)       # validasi + error handling ada di fuzzy_logic
        if not hasil["valid"]:
            st.error("Input tidak valid: " + hasil["pesan"])
            st.session_state.pop("hasil_terakhir", None)
            st.session_state.pop("nama_terakhir", None)
        else:
            h = hasil["hasil"]
            nama_clean = nama.strip() if nama.strip() else "Tanpa Nama"
            st.session_state["hasil_terakhir"] = h
            st.session_state["nama_terakhir"] = nama_clean
            st.session_state.setdefault("riwayat", []).append({
                "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nama_Karyawan": nama_clean,
                "Masa_Kerja": h.masa_kerja, "Nilai_Kinerja": h.kinerja, "Pendidikan": h.pendidikan,
                "Gaji_Rekomendasi": int(round(h.gaji_rp)), "Gaji_Format": h.gaji_format, "Kategori": h.kategori})
            st.success("Perhitungan berhasil dan disimpan ke riwayat.")
 
    h = st.session_state.get("hasil_terakhir")
    nama_terakhir = st.session_state.get("nama_terakhir")
    if h is None:
        st.caption("Isi form di atas lalu tekan tombol untuk melihat hasil.")
        st.warning(DISCLAIMER)
        return
 
    warna = WARNA_KATEGORI[h.kategori]
    kiri, kanan = st.columns([1, 1.4])
    with kiri:
        st.markdown(
            f'<div class="hasil"><div class="label">Rekomendasi Gaji</div><div class="nilai">{h.gaji_format}</div>'
            f'<span class="badge" style="background:{warna}">Kategori: {h.kategori}</span></div>',
            unsafe_allow_html=True)
        st.write("")
        if nama_terakhir and nama_terakhir != "Tanpa Nama":
            st.markdown(f"**Nama Karyawan:** {nama_terakhir}")
        st.markdown(f"**Input:** masa kerja {h.masa_kerja:g} tahun · kinerja {h.kinerja:g} · pendidikan {h.pendidikan}")
        derajat = pd.DataFrame(
            [("Masa Kerja", k, v) for k, v in h.derajat_masa.items()]
            + [("Kinerja", k, v) for k, v in h.derajat_kinerja.items()]
            + [("Pendidikan", k, v) for k, v in h.derajat_pendidikan.items()],
            columns=["Variabel", "Himpunan", "Derajat keanggotaan"])
        derajat["Derajat keanggotaan"] = derajat["Derajat keanggotaan"].round(4)
        st.dataframe(derajat[derajat["Derajat keanggotaan"] > 0], hide_index=True)
    with kanan:
        tampilkan(gambar_inferensi(h))
 
    tab1, tab2 = st.tabs(["Fungsi keanggotaan", "Aturan yang aktif"])
    with tab1:
        a, b, c = st.columns(3)
        with a:
            tampilkan(gambar_mf("masa_kerja", h.masa_kerja))
        with b:
            tampilkan(gambar_mf("kinerja", h.kinerja))
        with c:
            tampilkan(gambar_mf("pendidikan", h.skor_pendidikan))
    with tab2:
        akt = pd.DataFrame([{"No": r.nomor, "Aturan": r.teks(), "Kekuatan (α)": round(al, 4)} for r, al in h.aturan_aktif])
        st.dataframe(akt, hide_index=True)
    st.warning(DISCLAIMER)
 
 
def halaman_dataset():
    hero("Dataset Karyawan", "Dataset simulasi 40 karyawan beserta gaji aktual dan gaji prediksi fuzzy")
    df, galat = muat_dataset()
    if galat:
        st.error(galat)
        return
    c1, c2 = st.columns([2, 1])
    pilih = c1.multiselect("Filter pendidikan", list(fl.PENDIDIKAN_VALID), default=list(fl.PENDIDIKAN_VALID))
    cari = c2.text_input("Cari nama karyawan")
    tampil = df[df["Pendidikan"].isin(pilih)]
    if cari.strip():
        tampil = tampil[tampil["Nama_Karyawan"].str.contains(cari.strip(), case=False, na=False, regex=False)]
    st.caption(f"Menampilkan {len(tampil)} dari {len(df)} karyawan.")
    st.dataframe(tampil, hide_index=True)
    st.download_button("Unduh data (CSV)", data=csv_bytes(tampil), file_name="dataset_karyawan.csv", mime="text/csv")
    with st.expander("Statistik deskriptif"):
        st.dataframe(df[["Masa_Kerja", "Nilai_Kinerja", "Gaji_Aktual", "Gaji_Prediksi_Fuzzy"]].describe().round(1))
    st.info(DISCLAIMER)
 
 
def halaman_riwayat():
    hero("Riwayat Perhitungan", "Seluruh perhitungan pada sesi ini; dapat diekspor ke CSV")
    riwayat = st.session_state.get("riwayat", [])
    if not riwayat:
        st.info("Belum ada riwayat. Lakukan perhitungan pada menu 'Hitung Rekomendasi'.")
        return
    df = pd.DataFrame(riwayat)
    st.dataframe(df, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Ekspor riwayat (CSV)", data=csv_bytes(df), file_name="riwayat_perhitungan.csv", mime="text/csv")
    with c2:
        if st.button("Hapus semua riwayat"):
            st.session_state["riwayat"] = []
            st.session_state.pop("hasil_terakhir", None)
            st.rerun()
 
 
def halaman_tentang():
    hero("Tentang Sistem", "Variabel, himpunan fuzzy, dan basis aturan")
    st.markdown(
        "**Metode:** Fuzzy Mamdani (AND = min, implikasi = min, agregasi = max) dengan defuzzifikasi **Centroid**.\n\n"
        "**Input:** masa kerja 0–30 tahun, nilai kinerja 0–100, pendidikan terakhir (SMA, D3, S1, S2).\n\n"
        "**Output:** rekomendasi gaji Rp2.000.000–Rp20.000.000, dikategorikan Rendah (< Rp6 juta), "
        "Sedang (Rp6–<11 juta), dan Tinggi (≥ Rp11 juta).")
    a, b = st.columns(2)
    with a:
        tampilkan(gambar_mf("masa_kerja"))
        tampilkan(gambar_mf("pendidikan"))
    with b:
        tampilkan(gambar_mf("kinerja"))
        tampilkan(gambar_mf("gaji"))
    st.subheader("Basis aturan (27 aturan)")
    st.dataframe(tabel_aturan_df(), hide_index=True)
    st.warning(DISCLAIMER)
 
 
MENU = {
    "🏠 Dashboard": halaman_dashboard,
    "🧮 Hitung Rekomendasi": halaman_hitung,
    "📋 Dataset Karyawan": halaman_dataset,
    "🕘 Riwayat & Ekspor": halaman_riwayat,
    "ℹ️ Tentang Sistem": halaman_tentang,
}
 
 
def main():
    st.sidebar.title("💼Gaji Karyawan")
    st.sidebar.caption("Final Project Logika Fuzzy")
    pilihan = st.sidebar.radio("MENU:", list(MENU))
    MENU[pilihan]()
    st.sidebar.markdown("---")
    st.sidebar.caption("ini cuma simulasi aja yaa teman-temanku yang sholeh & sholehah , bukan keputusan penggajian resmi")
 
 
main()
