import numpy as np
import matplotlib.pyplot as plt


# ==========================================================
# SISTEM PRIORITAS TIKET HELPDESK TI
# ==========================================================
#
# Semesta pembicaraan : 0 <= x <= 24 jam
#
# CRISP:
#   x < 8  -> 0 (Tidak Kritis)
#   x >= 8 -> 1 (Kritis)
#
# FUZZY LINEAR NAIK:
#   x < 4       -> 0
#   4 <= x <= 12 -> (x - 4) / (12 - 4)
#   x > 12      -> 1
#
# ==========================================================


# ==========================================================
# 1. FUNGSI CRISP
# ==========================================================

def crisp_kritis(waktu, threshold=8.0):
    """
    Fungsi Crisp.

    Jika waktu tunggu >= 8 jam:
        nilai = 1 (Kritis)

    Jika waktu tunggu < 8 jam:
        nilai = 0 (Tidak Kritis)
    """

    return np.where(
        waktu >= threshold,
        1.0,
        0.0
    )


# ==========================================================
# 2. FUNGSI FUZZY LINEAR NAIK
# ==========================================================

def fuzzy_kritis(waktu, a=4.0, b=12.0):
    """
    Fungsi keanggotaan Fuzzy Linear Naik.

    Jika waktu < 4 jam:
        μ(x) = 0

    Jika 4 <= waktu <= 12 jam:
        μ(x) = (x - 4) / (12 - 4)

    Jika waktu > 12 jam:
        μ(x) = 1
    """

    derajat = (waktu - a) / (b - a)

    # Membatasi nilai antara 0 dan 1
    return np.clip(
        derajat,
        0.0,
        1.0
    )


# ==========================================================
# 3. DATA PENGUJIAN
# ==========================================================

data_uji = [
    2,
    4,
    6,
    7.9,
    8.0,
    8.1,
    10,
    12,
    16,
    24
]


# ==========================================================
# 4. MENAMPILKAN TABEL PERBANDINGAN
# ==========================================================

print("=" * 80)
print("       SISTEM PRIORITAS TIKET HELPDESK TI")
print("       PERBANDINGAN CRISP DAN FUZZY")
print("=" * 80)

print(
    f"{'Waktu (Jam)':<15} | "
    f"{'Crisp':<10} | "
    f"{'Fuzzy μ(x)':<12} | "
    f"{'Interpretasi'}"
)

print("-" * 80)


for waktu in data_uji:

    # Menghitung nilai Crisp
    crisp = float(
        crisp_kritis(
            waktu,
            threshold=8.0
        )
    )

    # Menghitung nilai Fuzzy
    fuzzy = float(
        fuzzy_kritis(
            waktu,
            a=4.0,
            b=12.0
        )
    )

    # Interpretasi nilai fuzzy
    if fuzzy == 0:
        interpretasi = "Tidak kritis"

    elif fuzzy == 1:
        interpretasi = "Sangat kritis"

    else:
        interpretasi = (
            f"Tingkat kritis {fuzzy * 100:.1f}%"
        )

    print(
        f"{waktu:<15.1f} | "
        f"{crisp:<10.1f} | "
        f"{fuzzy:<12.3f} | "
        f"{interpretasi}"
    )


# ==========================================================
# 5. PERHITUNGAN MANUAL BEBERAPA DATA
# ==========================================================

print("\n")
print("=" * 80)
print("       CONTOH PERHITUNGAN FUZZY")
print("=" * 80)

contoh = [4, 6, 8, 10, 12]

for x in contoh:

    fuzzy = float(
        fuzzy_kritis(
            x,
            a=4.0,
            b=12.0
        )
    )

    print(
        f"x = {x:>2} jam"
        f"  ->  μ(x) = {fuzzy:.3f}"
    )


# ==========================================================
# 6. MEMBUAT DOMAIN UNTUK GRAFIK
# ==========================================================

# Domain waktu tunggu dari 0 sampai 24 jam
waktu = np.linspace(
    0,
    24,
    500
)


# ==========================================================
# 7. MENGHITUNG NILAI CRISP DAN FUZZY UNTUK GRAFIK
# ==========================================================

y_crisp = crisp_kritis(
    waktu,
    threshold=8.0
)

y_fuzzy = fuzzy_kritis(
    waktu,
    a=4.0,
    b=12.0
)


# ==========================================================
# 8. MEMBUAT GRAFIK
# ==========================================================

plt.figure(
    figsize=(11, 6)
)


# ----------------------------------------------------------
# Grafik Crisp
# ----------------------------------------------------------

plt.step(
    waktu,
    y_crisp,
    where="post",
    linewidth=2.5,
    label="Crisp (Threshold = 8 jam)"
)


# ----------------------------------------------------------
# Grafik Fuzzy Linear Naik
# ----------------------------------------------------------

plt.plot(
    waktu,
    y_fuzzy,
    linewidth=2.5,
    label="Fuzzy Linear Naik (4 - 12 jam)"
)


# ==========================================================
# 9. PENANDA BATAS CRISP
# ==========================================================

plt.axvline(
    x=8,
    linestyle="--",
    alpha=0.6,
    label="Batas Crisp = 8 jam"
)


# ==========================================================
# 10. PENANDA BATAS FUZZY
# ==========================================================

# Awal kenaikan fuzzy
plt.axvline(
    x=4,
    linestyle=":",
    alpha=0.6,
    label="Awal Fuzzy = 4 jam"
)

# Akhir kenaikan fuzzy
plt.axvline(
    x=12,
    linestyle=":",
    alpha=0.6,
    label="Akhir Fuzzy = 12 jam"
)


# ==========================================================
# 11. JUDUL GRAFIK
# ==========================================================

plt.title(
    "Perbandingan Logika Crisp dan Fuzzy\n"
    "Sistem Prioritas Tiket Helpdesk TI",
    fontsize=14,
    fontweight="bold"
)


# ==========================================================
# 12. LABEL SUMBU
# ==========================================================

plt.xlabel(
    "Waktu Tunggu Penyelesaian Tiket (Jam)",
    fontsize=11
)

plt.ylabel(
    "Derajat Keanggotaan / Nilai Kebenaran",
    fontsize=11
)


# ==========================================================
# 13. PENGATURAN SUMBU
# ==========================================================

plt.xlim(
    0,
    24
)

plt.ylim(
    -0.05,
    1.1
)

plt.xticks(
    np.arange(
        0,
        25,
        2
    )
)

plt.yticks(
    np.arange(
        0,
        1.1,
        0.1
    )
)


# ==========================================================
# 14. GRID
# ==========================================================

plt.grid(
    True,
    linestyle=":",
    alpha=0.6
)


# ==========================================================
# 15. LEGEND
# ==========================================================

plt.legend(
    loc="upper left",
    fontsize=9
)


# ==========================================================
# 16. MERAPIKAN GRAFIK
# ==========================================================

plt.tight_layout()


# ==========================================================
# 17. SIMPAN GRAFIK DALAM FORMAT PNG
# ==========================================================

nama_file = "grafik_komparasi_crisp_fuzzy_helpdesk.png"

plt.savefig(
    nama_file,
    format="png",
    dpi=300,
    bbox_inches="tight"
)


# ==========================================================
# 18. TAMPILKAN GRAFIK
# ==========================================================

plt.show()
