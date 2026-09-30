import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# 1. DEFINISI FUNGSI KEANGGOTAAN LINGUISTIK
#    VARIABEL: PENGGUNAAN CPU SERVER
#    DOMAIN: 0 - 100 %
# ==========================================================

# ----------------------------------------------------------
# RENDAH
# Bentuk bahu kiri
# Penuh pada <= 20
# Turun sampai 0 pada 40
# ----------------------------------------------------------
def mf_rendah(x):
    kondisi = [
        x <= 20,
        (x > 20) & (x < 40),
        x >= 40
    ]

    pilihan = [
        1.0,
        (40.0 - x) / (40.0 - 20.0),
        0.0
    ]

    return np.select(kondisi, pilihan)


# ----------------------------------------------------------
# NORMAL
# Bentuk segitiga
# Mulai pada 30
# Puncak pada 50
# Berakhir pada 70
# ----------------------------------------------------------
def mf_normal(x):
    kondisi = [
        x <= 30,
        (x > 30) & (x <= 50),
        (x > 50) & (x < 70),
        x >= 70
    ]

    pilihan = [
        0.0,
        (x - 30.0) / (50.0 - 30.0),
        (70.0 - x) / (70.0 - 50.0),
        0.0
    ]

    return np.select(kondisi, pilihan)


# ----------------------------------------------------------
# TINGGI
# Bentuk bahu kanan
# Mulai naik pada 60
# Penuh pada >= 80
# ----------------------------------------------------------
def mf_tinggi(x):
    kondisi = [
        x <= 60,
        (x > 60) & (x < 80),
        x >= 80
    ]

    pilihan = [
        0.0,
        (x - 60.0) / (80.0 - 60.0),
        1.0
    ]

    return np.select(kondisi, pilihan)


# ==========================================================
# 2. DEFINISI STRUKTUR VARIABEL LINGUISTIK
# ==========================================================

variabel_cpu = {
    "nama": "Penggunaan CPU Server",
    "satuan": "%",
    "semesta": (0.0, 100.0),

    "label": {
        "Rendah": mf_rendah,
        "Normal": mf_normal,
        "Tinggi": mf_tinggi
    }
}


# ==========================================================
# 3. FUNGSI FUZZIFIKASI INPUT TUNGGAL
# ==========================================================

def fuzzifikasi(nilai_crisp, variabel):
    """
    Memetakan nilai crisp ke semua derajat
    keanggotaan linguistik.
    """

    hasil = {}

    u_min, u_max = variabel["semesta"]

    # Cek apakah input berada dalam domain
    if not (u_min <= nilai_crisp <= u_max):
        raise ValueError(
            f"Input {nilai_crisp} di luar semesta "
            f"[{u_min}, {u_max}]"
        )

    # Hitung derajat keanggotaan setiap label
    for nama_label, fungsi_mf in variabel["label"].items():

        derajat = float(
            fungsi_mf(np.array([nilai_crisp]))[0]
        )

        hasil[nama_label] = round(derajat, 4)

    return hasil


# ==========================================================
# 4. MEMBUAT DOMAIN CPU
# ==========================================================

x_semesta = np.linspace(0.0, 100.0, 500)

y_rendah = mf_rendah(x_semesta)
y_normal = mf_normal(x_semesta)
y_tinggi = mf_tinggi(x_semesta)


# ==========================================================
# 5. PLOT KETIGA FUNGSI KEANGGOTAAN
# ==========================================================

plt.figure(figsize=(10, 5.5))

plt.plot(
    x_semesta,
    y_rendah,
    label="Rendah",
    color="#2ca02c",
    linewidth=2.5
)

plt.plot(
    x_semesta,
    y_normal,
    label="Normal",
    color="#ff7f0e",
    linewidth=2.5
)

plt.plot(
    x_semesta,
    y_tinggi,
    label="Tinggi",
    color="#d62728",
    linewidth=2.5
)


# ==========================================================
# 6. PENGUJIAN FUZZIFIKASI
#    INPUT CPU = 10%
# ==========================================================

x_uji = 10

derajat_uji = fuzzifikasi(
    x_uji,
    variabel_cpu
)


# Garis vertikal input x = 10
plt.axvline(
    x=x_uji,
    color="purple",
    linestyle="--",
    linewidth=1.8,
    label=f"Input x = {x_uji}%"
)


# Titik hasil fuzzifikasi
for label, derajat in derajat_uji.items():

    if derajat > 0:

        plt.scatter(
            x_uji,
            derajat,
            color="purple",
            s=70,
            zorder=5
        )


# ==========================================================
# 7. PENGATURAN GRAFIK
# ==========================================================

plt.title(
    "Variabel Linguistik: Penggunaan CPU Server",
    fontsize=13,
    fontweight="bold"
)

plt.xlabel(
    "Penggunaan CPU (%)",
    fontsize=11
)

plt.ylabel(
    "Derajat Keanggotaan μ(x)",
    fontsize=11
)

plt.xlim(0, 100)
plt.ylim(-0.05, 1.1)

plt.xticks(
    np.arange(0, 101, 10)
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
    loc="center right",
    fontsize=10
)

plt.tight_layout()


# ==========================================================
# 8. SIMPAN HASIL GRAFIK
# ==========================================================

plt.savefig(
    "variabel_linguistik_cpu_server.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================================
# 9. TABEL HASIL FUZZIFIKASI
# ==========================================================

print()
print("=" * 55)
print(f"HASIL FUZZIFIKASI CPU = {x_uji}%")
print("=" * 55)

print(
    f"{'Label':<15} | {'Derajat Keanggotaan μ(x)':>25}"
)

print("-" * 55)

for label, derajat in derajat_uji.items():

    print(
        f"{label:<15} | {derajat:>25.4f}"
    )

print("=" * 55)
