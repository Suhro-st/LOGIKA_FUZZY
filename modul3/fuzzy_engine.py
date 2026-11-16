import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Pastikan folder modul dapat diimpor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import fuzzy_logic as fl

DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
KOLOM_DATASET = ["ID_Karyawan", "Nama_Karyawan", "Masa_Kerja", "Nilai_Kinerja", "Pendidikan",
                 "Gaji_Aktual", "Gaji_Prediksi_Fuzzy"]
WARNA_KATEGORI = {"Rendah": "#C8553D", "Sedang": "#F2A541", "Tinggi": "#0B5563"}
WARNA_MF = ["#0B5563", "#F2A541", "#C8553D", "#5B8E7D", "#7A5C99"]

# Penyimpanan riwayat perhitungan selama sesi berjalan
RIWAYAT_SESI = []


def muat_dataset():
    """Membaca file dataset.csv."""
    try:
        df = pd.read_csv(DATASET_PATH)
        return df, None
    except FileNotFoundError:
        return pd.DataFrame(columns=KOLOM_DATASET), "File dataset.csv tidak ditemukan di folder modul3."
    except Exception as e:
        return pd.DataFrame(columns=KOLOM_DATASET), f"Gagal membaca dataset: {e}"


def garis(panjang=68, karakter="="):
    print(karakter * panjang)


# ---------------------------------------------------------------------------
# 1. MENU DASHBOARD
# ---------------------------------------------------------------------------
def menu_dashboard():
    garis(68, "=")
    print("                    🏠 DASHBOARD SISTEM GAJI")
    garis(68, "=")

    df, err = muat_dataset()
    if err:
        print(f"[!] {err}")
        return

    aktual = df["Gaji_Aktual"].tolist()
    prediksi = df["Gaji_Prediksi_Fuzzy"].tolist()
    ev = fl.evaluasi(aktual, prediksi)

    print(f" • Jumlah Data Karyawan  : {len(df)} orang")
    print(f" • Rata-rata Gaji Aktual : {fl.format_rupiah(df['Gaji_Aktual'].mean())}")
    print(f" • Rata-rata Prediksi    : {fl.format_rupiah(df['Gaji_Prediksi_Fuzzy'].mean())}")
    print(f" • MAE (Mean Abs Error)  : {fl.format_rupiah(ev['MAE'])}")
    print(f" • RMSE                  : {fl.format_rupiah(ev['RMSE'])}")
    print(f" • MAPE                  : {ev['MAPE']:.2f}%")
    print(f" • R-Squared (R²)        : {ev['R2']:.4f}")
    garis(68, "-")

    tanya = input("Tampilkan grafik visualisasi (Scatter Plot & Sebaran)? (y/n, default n): ").strip().lower()
    if tanya == "y":
        tampilkan_grafik_dashboard(df)


def tampilkan_grafik_dashboard(df):
    """Menampilkan grafik dashboard menggunakan Matplotlib."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Grafik 1: Scatter aktual vs prediksi
    akt_juta = df["Gaji_Aktual"] / 1_000_000.0
    pred_juta = df["Gaji_Prediksi_Fuzzy"] / 1_000_000.0
    mn = min(akt_juta.min(), pred_juta.min()) - 0.5
    mx = max(akt_juta.max(), pred_juta.max()) + 0.5

    ax1.plot([mn, mx], [mn, mx], "--", color="#C8553D", lw=1.5, label="Prediksi = Aktual")
    ax1.scatter(akt_juta, pred_juta, color="#0B5563", edgecolors="#fff", s=50, alpha=0.85)
    ax1.set_xlabel("Gaji Aktual (juta Rp)")
    ax1.set_ylabel("Gaji Prediksi Fuzzy (juta Rp)")
    ax1.set_title("Gaji Aktual vs Prediksi", fontweight="bold")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Grafik 2: Sebaran kategori
    kat = [fl.kategori_gaji(g / 1_000_000.0) for g in df["Gaji_Prediksi_Fuzzy"]]
    hitung = pd.Series(kat).value_counts()
    urut = [k for k in ["Rendah", "Sedang", "Tinggi"] if k in hitung]
    nilai = [hitung[k] for k in urut]
    warna = [WARNA_KATEGORI[k] for k in urut]

    batang = ax2.bar(urut, nilai, color=warna)
    for b, v in zip(batang, nilai):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v), ha="center", fontweight="bold")
    ax2.set_ylabel("Jumlah Karyawan")
    ax2.set_title("Sebaran Kategori Gaji Prediksi", fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    print("Menampilkan jendela grafik... (Tutup jendela grafik untuk kembali ke menu)")
    plt.show()


# ---------------------------------------------------------------------------
# 2. MENU HITUNG REKOMENDASI GAJI
# ---------------------------------------------------------------------------
def menu_hitung():
    garis(68, "=")
    print("               🧮 HITUNG REKOMENDASI GAJI (FUZZY MAMDANI)")
    garis(68, "=")

    nama = input("Masukkan Nama Karyawan (contoh: Budi Santoso) [opsional]: ").strip()
    if not nama:
        nama = "Tanpa Nama"

    # Input Masa Kerja
    while True:
        try:
            raw = input("Masukkan Masa Kerja (0 - 30 tahun) [contoh 8]: ").strip()
            masa = float(raw)
            if 0 <= masa <= 30:
                break
            print("[!] Masa kerja harus dalam rentang 0 s.d. 30 tahun.")
        except ValueError:
            print("[!] Harap masukkan angka yang valid.")

    # Input Kinerja
    while True:
        try:
            raw = input("Masukkan Nilai Kinerja (0 - 100) [contoh 78]: ").strip()
            kinerja = float(raw)
            if 0 <= kinerja <= 100:
                break
            print("[!] Nilai kinerja harus dalam rentang 0 s.d. 100.")
        except ValueError:
            print("[!] Harap masukkan angka yang valid.")

    # Input Pendidikan
    while True:
        pend = input("Pendidikan Terakhir (SMA / D3 / S1 / S2) [contoh S1]: ").strip().upper()
        if pend in fl.PENDIDIKAN_VALID:
            break
        print(f"[!] Pilihan tidak valid. Pilih salah satu: {', '.join(fl.PENDIDIKAN_VALID)}")

    # Proses logika fuzzy
    hasil = fl.proses_input(masa, kinerja, pend)
    if not hasil["valid"]:
        print(f"\n[!] Galat perhitungan: {hasil['pesan']}")
        return

    h = hasil["hasil"]

    # Simpan ke riwayat sesi
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    RIWAYAT_SESI.append({
        "Waktu": waktu_sekarang,
        "Nama_Karyawan": nama,
        "Masa_Kerja": h.masa_kerja,
        "Nilai_Kinerja": h.kinerja,
        "Pendidikan": h.pendidikan,
        "Gaji_Rekomendasi": int(round(h.gaji_rp)),
        "Gaji_Format": h.gaji_format,
        "Kategori": h.kategori
    })

    # Tampilkan hasil perhitungan
    garis(68, "=")
    print("                      HASIL REKOMENDASI GAJI")
    garis(68, "=")
    print(f" Karyawan          : {nama}")
    print(f" Input             : Masa Kerja {h.masa_kerja:g} th | Kinerja {h.kinerja:g} | Pendidikan {h.pendidikan}")
    print(f" Rekomendasi Gaji  : {h.gaji_format}")
    print(f" Kategori Gaji     : {h.kategori}")
    print(f" Titik Centroid    : {h.gaji_juta:.4f} juta")
    garis(68, "-")

    print("\n1. Derajat Keanggotaan (Fuzzifikasi):")
    print(f"   • Masa Kerja ({h.masa_kerja:g} th) : " +
          ", ".join([f"{k} = {v:.4f}" for k, v in h.derajat_masa.items() if v > 0]))
    print(f"   • Kinerja ({h.kinerja:g})     : " +
          ", ".join([f"{k} = {v:.4f}" for k, v in h.derajat_kinerja.items() if v > 0]))
    print(f"   • Pendidikan ({h.pendidikan})  : " +
          ", ".join([f"{k} = {v:.4f}" for k, v in h.derajat_pendidikan.items() if v > 0]))

    print(f"\n2. Aturan yang Aktif ({len(h.aturan_aktif)} aturan terpicu):")
    for r, al in h.aturan_aktif:
        print(f"   [R{r.nomor:02d}] {r.teks()}  --> alpha (α) = {al:.4f}")

    garis(68, "=")
    print("[✓] Hasil berhasil disimpan ke riwayat sesi.")

    tanya = input("\nTampilkan grafik inferensi & fungsi keanggotaan? (y/n, default n): ").strip().lower()
    if tanya == "y":
        tampilkan_grafik_inferensi(h)


def tampilkan_grafik_inferensi(h):
    """Menampilkan visualisasi kurva inferensi Mamdani & centroid."""
    fig, ax = plt.subplots(figsize=(8, 4))
    x = h.x_gaji
    for warna, (label, spec) in zip(WARNA_MF, fl.MF_GAJI.items()):
        ax.plot(x, fl.mf(x, spec), color=warna, lw=1.2, alpha=0.5, label=f"MF {label}")
        a = h.kekuatan_output[label]
        if a > 0:
            ax.fill_between(x, np.fmin(a, fl.mf(x, spec)), color=warna, alpha=0.3, label=f"{label} (α={a:.3f})")

    ax.plot(x, h.agregasi, color="#12343B", lw=2.2, label="Agregasi Max")
    ax.axvline(h.gaji_juta, color="#C8553D", ls="--", lw=2, label=f"Centroid = {h.gaji_juta:.3f} jt")
    ax.set_title(f"Inferensi Fuzzy Mamdani - Rekomendasi: {h.gaji_format} ({h.kategori})", fontweight="bold")
    ax.set_xlabel("Gaji (Juta Rupiah)")
    ax.set_ylabel("Derajat Keanggotaan")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    plt.tight_layout()
    print("Menampilkan kurva inferensi... (Tutup jendela grafik untuk kembali)")
    plt.show()


# ---------------------------------------------------------------------------
# 3. MENU DATASET KARYAWAN
# ---------------------------------------------------------------------------
def menu_dataset():
    garis(68, "=")
    print("                    📋 DATASET KARYAWAN (SIMULASI)")
    garis(68, "=")

    df, err = muat_dataset()
    if err:
        print(f"[!] {err}")
        return

    print(f"Total data: {len(df)} karyawan")
    print("[1] Tampilkan Seluruh Data")
    print("[2] Cari Berdasarkan Nama Karyawan")
    print("[3] Filter Berdasarkan Pendidikan")
    print("[4] Tampilkan Statistik Deskriptif")
    sub = input("Pilih menu dataset (1-4, Enter untuk kembali): ").strip()

    if sub == "1":
        garis(68, "-")
        print(df.to_string(index=False))
    elif sub == "2":
        keyword = input("Masukkan nama karyawan yang dicari: ").strip().lower()
        hasil = df[df["Nama_Karyawan"].str.lower().str.contains(keyword, na=False)]
        print(f"\nDitemukan {len(hasil)} data:")
        if not hasil.empty:
            print(hasil.to_string(index=False))
        else:
            print("Tidak ada data yang cocok.")
    elif sub == "3":
        print(f"Pilihan pendidikan: {', '.join(fl.PENDIDIKAN_VALID)}")
        pend = input("Masukkan pendidikan: ").strip().upper()
        if pend in fl.PENDIDIKAN_VALID:
            hasil = df[df["Pendidikan"] == pend]
            print(f"\nDitemukan {len(hasil)} karyawan dengan pendidikan {pend}:")
            print(hasil.to_string(index=False))
        else:
            print("[!] Pendidikan tidak valid.")
    elif sub == "4":
        garis(68, "-")
        stat = df[["Masa_Kerja", "Nilai_Kinerja", "Gaji_Aktual", "Gaji_Prediksi_Fuzzy"]].describe().round(1)
        print(stat)


# ---------------------------------------------------------------------------
# 4. MENU RIWAYAT & EKSPOR
# ---------------------------------------------------------------------------
def menu_riwayat():
    garis(68, "=")
    print("                    🕘 RIWAYAT PERHITUNGAN SESI")
    garis(68, "=")

    if not RIWAYAT_SESI:
        print("Belum ada riwayat perhitungan pada sesi ini.")
        print("Gunakan menu [2] untuk melakukan perhitungan terlebih dahulu.")
        return

    df_riwayat = pd.DataFrame(RIWAYAT_SESI)
    print(df_riwayat.to_string(index=False))
    garis(68, "-")

    print("[1] Ekspor Riwayat ke File CSV (format rapi untuk Excel / WPS)")
    print("[2] Hapus Semua Riwayat Sesi Ini")
    print("[0] Kembali")
    pilih = input("Pilih aksi (0-2): ").strip()

    if pilih == "1":
        nama_file = os.path.join(BASE_DIR, "riwayat_perhitungan.csv")
        # Ekspor dengan pemisah titik koma ';' agar otomatis rapi di WPS/Excel Indonesia
        df_riwayat.to_csv(nama_file, sep=";", index=False, encoding="utf-8-sig")
        print(f"[✓] Berhasil diekspor ke: {nama_file}")
    elif pilih == "2":
        konfirmasi = input("Yakin ingin menghapus seluruh riwayat sesi? (y/n): ").strip().lower()
        if konfirmasi == "y":
            RIWAYAT_SESI.clear()
            print("[✓] Riwayat berhasil dikosongkan.")


# ---------------------------------------------------------------------------
# 5. MENU TENTANG SISTEM & 27 BASIS ATURAN
# ---------------------------------------------------------------------------
def menu_tentang():
    garis(68, "=")
    print("                   ℹ️ TENTANG SISTEM FUZZY")
    garis(68, "=")
    print("Metode      : Fuzzy Mamdani (AND=min, implikasi=min, agregasi=max)")
    print("Defuzzifikasi: Centroid (Center of Gravity)")
    print("Domain Input:")
    print("  1. Masa Kerja  : 0 - 30 tahun   (Himpunan: Baru, Sedang, Lama)")
    print("  2. Kinerja     : 0 - 100 skor   (Himpunan: Buruk, Cukup, Baik)")
    print("  3. Pendidikan  : SMA, D3, S1, S2 (Himpunan: Rendah, Menengah, Tinggi)")
    print("Domain Output:")
    print("  • Rekomendasi Gaji : Rp2.000.000 s.d. Rp20.000.000")
    print("    - Rendah : < Rp6.000.000")
    print("    - Sedang : Rp6.000.000 s.d. < Rp11.000.000")
    print("    - Tinggi : >= Rp11.000.000")
    garis(68, "-")

    tanya = input("Tampilkan seluruh 27 Basis Aturan Fuzzy? (y/n, default y): ").strip().lower()
    if tanya != "n":
        print("\nBASIS ATURAN (27 ATURAN FUZZY):")
        for r in fl.RULES:
            print(f" [R{r.nomor:02d}] IF Masa Kerja {r.masa:<6} AND Kinerja {r.kinerja:<5} AND Pendidikan {r.pendidikan:<8} THEN Gaji {r.gaji}")


# ---------------------------------------------------------------------------
# PROGRAM UTAMA (LOOP MENU)
# ---------------------------------------------------------------------------
def main():
    while True:
        print("\n" + "=" * 68)
        print("          💼 SISTEM PENERAPAN GAJI KARYAWAN (LOGIKA FUZZY)")
        print("                  Mode Konsol / Terminal Python")
        print("=" * 68)
        print(" [1] 🏠 Dashboard & Statistik Model")
        print(" [2] 🧮 Hitung Rekomendasi Gaji Karyawan")
        print(" [3] 📋 Dataset Karyawan (Tabel & Pencarian)")
        print(" [4] 🕘 Riwayat Perhitungan & Ekspor CSV")
        print(" [5] ℹ️ Tentang Sistem & 27 Basis Aturan")
        print(" [0] 🚪 Keluar")
        print("-" * 68)
        print(" * Catatan: Hasil adalah rekomendasi sistem berdasarkan data simulasi.")
        print("=" * 68)

        pilihan = input("Pilih menu (0-5): ").strip()

        if pilihan == "1":
            menu_dashboard()
        elif pilihan == "2":
            menu_hitung()
        elif pilihan == "3":
            menu_dataset()
        elif pilihan == "4":
            menu_riwayat()
        elif pilihan == "5":
            menu_tentang()
        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan sistem ini. Sampai jumpa!")
            break
        else:
            print("\n[!] Pilihan tidak valid, silakan masukkan angka 0 sampai 5.")

        input("\nTekan [Enter] untuk kembali ke menu utama...")


if __name__ == "__main__":
    main()

