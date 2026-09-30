import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# 1. DEFINISI FUNGSI KEANGGOTAAN LINGUISTIK
#    VARIABEL: USIA
#    DOMAIN: 0 - 150 TAHUN
# ==========================================================

# ----------------------------------------------------------
# BAYI / ANAK USIA DINI
# a = 0, b = 0, c = 5, d = 6
# ----------------------------------------------------------
def mf_bayi(x):
    kondisi = [
        x <= 5,
        (x > 5) & (x < 6),
        x >= 6
    ]

    pilihan = [
        1.0,
        (6.0 - x) / (6.0 - 5.0),
        0.0
    ]

    return np.select(kondisi, pilihan)


# ----------------------------------------------------------
# ANAK-ANAK
# a = 5, b = 6, c = 11, d = 12
# ----------------------------------------------------------
def mf_anak(x):
    kondisi = [
        x <= 5,
        (x > 5) & (x < 6),
        (x >= 6) & (x <= 11),
        (x > 11) & (x < 12),
        x >= 12
    ]

    pilihan = [
        0.0,
        (x - 5.0) / (6.0 - 5.0),
        1.0,
        (12.0 - x) / (12.0 - 11.0),
        0.0
    ]

    return np.select(kondisi, pilihan)


# ----------------------------------------------------------
# REMAJA
# a = 9, b = 10, c = 19, d = 20
# ----------------------------------------------------------
def mf_remaja(x):
    kondisi = [
        x <= 9,
        (x > 9) & (x < 10),
        (x >= 10) & (x <= 19),
        (x > 19) & (x < 20),
        x >= 20
    ]

    pilihan = [
        0.0,
        (x - 9.0) / (10.0 - 9.0),
        1.0,
        (20.0 - x) / (20.0 - 19.0),
        0.0
    ]

    return np.select(kondisi, pilihan)


# ----------------------------------------------------------
# PEMUDA
# a = 14, b = 15, c = 24, d = 25
# ----------------------------------------------------------
def mf_pemuda(x):
    kondisi = [
        x <= 14,
        (x > 14) & (x < 15),
        (x >= 15) & (x <= 24),
        (x > 24) & (x < 25),
        x >= 25
    ]

    pilihan = [
        0.0,
        (x - 14.0) / (15.0 - 14.0),
        1.0,
        (25.0 - x) / (25.0 - 24.0),
        0.0
    ]

    return np.select(kondisi, pilihan)


# ----------------------------------------------------------
# DEWASA
# a = 19, b = 20, c = 65, d = 66
# ----------------------------------------------------------
def mf_dewasa(x):
    kondisi = [
        x <= 19,
        (x > 19) & (x < 20),
        (x >= 20) & (x <= 65),
        (x > 65) & (x < 66),
        x >= 66
    ]

    pilihan = [
        0.0,
        (x - 19.0) / (20.0 - 19.0),
        1.0,
        (66.0 - x) / (66.0 - 65.0),
        0.0
    ]

    return np.select(kondisi, pilihan)


# ----------------------------------------------------------
# LANSIA
# a = 64, b = 65, c = 150, d = 150
# Domain berakhir pada 150
# ----------------------------------------------------------
def mf_lansia(x):
    kondisi = [
        x <= 64,
        (x > 64) & (x < 65),
        (x >= 65) & (x <= 150)
    ]

    pilihan = [
        0.0,
        (x - 64.0) / (65.0 - 64.0),
        1.0
    ]

    return np.select(kondisi, pilihan)


# ==========================================================
# 2. STRUKTUR VARIABEL LINGUISTIK
# ==========================================================

variabel_usia = {
    "nama": "Usia",
    "satuan": "tahun",
    "semesta": (0.0, 150.0),

    "label": {
        "Bayi / Anak Usia Dini": mf_bayi,
        "Anak-anak": mf_anak,
        "Remaja": mf_remaja,
        "Pemuda": mf_pemuda,
        "Dewasa": mf_dewasa,
        "Lansia": mf_lansia
    }
}


# ==========================================================
# 3. FUNGSI FUZZIFIKASI
# ==========================================================

def fuzzifikasi(nilai_crisp, variabel):
    """
    Mengubah nilai crisp menjadi derajat keanggotaan
    pada setiap kategori usia.
    """

    hasil = {}

    u_min, u_max = variabel["semesta"]

    if not (u_min <= nilai_crisp <= u_max):
        raise ValueError(
            f"Input {nilai_crisp} di luar domain "
            f"[{u_min}, {u_max}]"
        )

    for nama_label, fungsi_mf in variabel["label"].items():

        derajat = float(
            fungsi_mf(np.array([nilai_crisp]))[0]
        )

        hasil[nama_label] = round(derajat, 4)

    return hasil


# ==========================================================
# 4. MEMBUAT DOMAIN USIA
# ==========================================================

x_semesta = np.linspace(0.0, 150.0, 1000)

y_bayi = mf_bayi(x_semesta)
y_anak = mf_anak(x_semesta)
y_remaja = mf_remaja(x_semesta)
y_pemuda = mf_pemuda(x_semesta)
y_dewasa = mf_dewasa(x_semesta)
y_lansia = mf_lansia(x_semesta)


# ==========================================================
# 5. VISUALISASI SEMUA FUNGSI KEANGGOTAAN
# ==========================================================

plt.figure(figsize=(14, 7))

plt.plot(
    x_semesta,
    y_bayi,
    label="Bayi / Anak Usia Dini",
    linewidth=2.5
)

plt.plot(
    x_semesta,
    y_anak,
    label="Anak-anak",
    linewidth=2.5
)

plt.plot(
    x_semesta,
    y_remaja,
    label="Remaja",
    linewidth=2.5
)

plt.plot(
    x_semesta,
    y_pemuda,
    label="Pemuda",
    linewidth=2.5
)

plt.plot(
    x_semesta,
    y_dewasa,
    label="Dewasa",
    linewidth=2.5
)

plt.plot(
    x_semesta,
    y_lansia,
    label="Lansia",
    linewidth=2.5
)


# ==========================================================
# 6. CONTOH INPUT CRISP
# ==========================================================

x_uji = 18

derajat_uji = fuzzifikasi(
    x_uji,
    variabel_usia
)


# Garis vertikal untuk menunjukkan posisi input
plt.axvline(
    x=x_uji,
    linestyle="--",
    linewidth=1.8,
    label=f"Input x = {x_uji} tahun"
)


# Menampilkan titik pada fungsi yang mempunyai
# derajat keanggotaan lebih dari 0
for label, derajat in derajat_uji.items():

    if derajat > 0:

        plt.scatter(
            x_uji,
            derajat,
            s=70,
            zorder=5
        )


# ==========================================================
# 7. PENGATURAN GRAFIK
# ==========================================================

plt.title(
    "Fungsi Keanggotaan Linguistik Variabel Usia",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel(
    "Usia (tahun)",
    fontsize=11
)

plt.ylabel(
    "Derajat Keanggotaan μ(x)",
    fontsize=11
)

plt.xlim(0, 150)
plt.ylim(-0.05, 1.1)

plt.xticks(
    np.arange(0, 151, 10)
)

plt.yticks(
    np.arange(0, 1.1, 0.1)
)

plt.grid(
    True,
    linestyle=":",
    alpha=0.6
)

plt.legend(
    loc="center left",
    bbox_to_anchor=(1, 0.5)
)

plt.tight_layout()


# ==========================================================
# 8. SIMPAN GRAFIK
# ==========================================================

plt.savefig(
    "fungsi_keanggotaan_usia.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================================
# 9. HASIL FUZZIFIKASI
# ==========================================================

print("=" * 60)
print(
    f"HASIL FUZZIFIKASI USIA = "
    f"{x_uji} {variabel_usia['satuan']}"
)
print("=" * 60)

for label, derajat in derajat_uji.items():

    print(
        f"{label:<25} : μ = {derajat}"
    )
