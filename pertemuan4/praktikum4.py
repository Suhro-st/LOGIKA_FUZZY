"""
Praktikum 4 - Operasi Himpunan Fuzzy (T-norm, T-conorm, Complement)
  Bagian A : verifikasi contoh manual (0.80 / 0.60) dan tabel skenario modul
  Bagian B : TUGAS - Bandwidth Jaringan Kampus (A segitiga [30,60,90], B trapesium [40,55,75,95])
  Bagian C : Verifikasi numerik urutan operator dan De Morgan
Library: hanya NumPy dan Matplotlib.
"""
import numpy as np
import matplotlib.pyplot as plt


# ---------- T-NORM (AND) ----------
def tnorm_min(a, b):
    return np.minimum(a, b)


def tnorm_product(a, b):
    return a * b


def tnorm_bounded_diff(a, b):
    return np.maximum(0.0, a + b - 1.0)


# ---------- T-CONORM (OR) ----------
def tconorm_max(a, b):
    return np.maximum(a, b)


def tconorm_algebraic_sum(a, b):
    return a + b - (a * b)


def tconorm_bounded_sum(a, b):
    return np.minimum(1.0, a + b)


# ---------- NOT ----------
def fuzzy_not(mu):
    return 1.0 - mu


# ---------- Fungsi keanggotaan ----------
def mf_segitiga(x, a, b, c):
    x = np.asarray(x, dtype=float)
    return np.maximum(0.0, np.minimum((x - a) / (b - a), (c - x) / (c - b)))


def mf_trapesium(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    return np.maximum(0.0, np.minimum(np.minimum((x - a) / (b - a), 1.0), (d - x) / (d - c)))


# ==========================================================
# BAGIAN A - VERIFIKASI MODUL
# ==========================================================
print("=" * 78)
print("BAGIAN A1 - CONTOH MANUAL MODUL: mu_A = 0.80, mu_B = 0.60")
print("=" * 78)
a, b = 0.80, 0.60
print(f"Min={tnorm_min(a, b):.2f}  Product={tnorm_product(a, b):.2f}  BoundedDiff={tnorm_bounded_diff(a, b):.2f}")
print(f"Max={tconorm_max(a, b):.2f}  AlgSum={tconorm_algebraic_sum(a, b):.2f}  BoundedSum={tconorm_bounded_sum(a, b):.2f}")

print()
print("BAGIAN A2 - TABEL SKENARIO MODUL")
print("| Kasus | muA  | muB  | Min  | Prod | BDiff | Max  | ASum | BSum |")
print("|------:|-----:|-----:|-----:|-----:|------:|-----:|-----:|-----:|")
for i, (p, q) in enumerate([(0.9, 0.9), (0.7, 0.4), (0.5, 0.5), (0.3, 0.2), (0.0, 0.85)], 1):
    print(f"| {i:>5} | {p:.2f} | {q:.2f} | {tnorm_min(p, q):.2f} | {tnorm_product(p, q):.2f} | "
          f"{tnorm_bounded_diff(p, q):.2f}  | {tconorm_max(p, q):.2f} | {tconorm_algebraic_sum(p, q):.2f} | "
          f"{tconorm_bounded_sum(p, q):.2f} |")

# ==========================================================
# BAGIAN B - TUGAS BANDWIDTH
# ==========================================================
X = np.linspace(0, 100, 1001)
mu_A = mf_segitiga(X, 30, 60, 90)
mu_B = mf_trapesium(X, 40, 55, 75, 95)

fig, ax = plt.subplots(2, 2, figsize=(14, 9))

ax[0, 0].plot(X, mu_A, label='A: Bandwidth Cukup', color='#1f77b4', linewidth=2.5)
ax[0, 0].plot(X, mu_B, label='B: Packet Loss Rendah', color='#ff7f0e', linewidth=2.5)
ax[0, 0].plot(X, fuzzy_not(mu_A), label='NOT A', color='gray', linestyle='--', linewidth=1.8)
ax[0, 0].set_title('1. Himpunan A, B, dan Komplemen NOT A', fontweight='bold')

ax[0, 1].plot(X, tnorm_min(mu_A, mu_B), label='Zadeh Min', color='#2ca02c', linewidth=2.5)
ax[0, 1].plot(X, tnorm_product(mu_A, mu_B), label='Algebraic Product', color='#d62728', linestyle='-.', linewidth=2)
ax[0, 1].set_title('2. Intersection (AND)', fontweight='bold')

ax[1, 0].plot(X, tconorm_max(mu_A, mu_B), label='Zadeh Max', color='#2ca02c', linewidth=2.5)
ax[1, 0].plot(X, tconorm_algebraic_sum(mu_A, mu_B), label='Algebraic Sum', color='#d62728', linestyle='-.', linewidth=2)
ax[1, 0].set_title('3. Union (OR)', fontweight='bold')

ax[1, 1].fill_between(X, tnorm_min(mu_A, mu_B), color='#2ca02c', alpha=0.4, label='Area Min (A ∩ B)')
ax[1, 1].plot(X, tconorm_max(mu_A, mu_B), color='#d62728', linewidth=2, label='Batas Max (A ∪ B)')
ax[1, 1].plot(X, mu_A, color='#1f77b4', linestyle=':', alpha=0.7)
ax[1, 1].plot(X, mu_B, color='#ff7f0e', linestyle=':', alpha=0.7)
ax[1, 1].set_title('4. Irisan vs Gabungan Standar', fontweight='bold')

for axis in ax.ravel():
    axis.set_ylim(-0.05, 1.1)
    axis.set_xlabel('Throughput (Mbps)')
    axis.set_ylabel('μ(x)')
    axis.grid(True, linestyle=':', alpha=0.6)
    axis.legend()
plt.tight_layout()
plt.savefig('operasi_himpunan_fuzzy_komparasi.png', dpi=300)
plt.show()

print()
print("=" * 78)
print("BAGIAN B - TUGAS: BANDWIDTH KAMPUS (A: segitiga [30,60,90], B: trapesium [40,55,75,95])")
print("=" * 78)
print("| x (Mbps) | muA    | muB    | Min    | Product | Max    | AlgSum | NOT A  |")
print("|---------:|-------:|-------:|-------:|--------:|-------:|-------:|-------:|")
for x in [35, 50, 65, 80]:
    pa = float(mf_segitiga(x, 30, 60, 90))
    pb = float(mf_trapesium(x, 40, 55, 75, 95))
    print(f"| {x:>8} | {pa:.4f} | {pb:.4f} | {tnorm_min(pa, pb):.4f} | {tnorm_product(pa, pb):.4f}  | "
          f"{tconorm_max(pa, pb):.4f} | {tconorm_algebraic_sum(pa, pb):.4f} | {fuzzy_not(pa):.4f} |")

# ==========================================================
# BAGIAN C - VERIFIKASI NUMERIK
# ==========================================================
eps = 1e-12
assert np.all(tnorm_bounded_diff(mu_A, mu_B) <= tnorm_product(mu_A, mu_B) + eps)
assert np.all(tnorm_product(mu_A, mu_B) <= tnorm_min(mu_A, mu_B) + eps)
assert np.all(tnorm_min(mu_A, mu_B) <= np.minimum(mu_A, mu_B) + eps)
assert np.all(tconorm_max(mu_A, mu_B) <= tconorm_algebraic_sum(mu_A, mu_B) + eps)
assert np.all(tconorm_algebraic_sum(mu_A, mu_B) <= tconorm_bounded_sum(mu_A, mu_B) + eps)
for arr in (mu_A, mu_B):
    assert arr.min() >= 0.0 and arr.max() <= 1.0

dm1 = fuzzy_not(tconorm_max(mu_A, mu_B))
dm2 = tnorm_min(fuzzy_not(mu_A), fuzzy_not(mu_B))
dm3 = fuzzy_not(tconorm_algebraic_sum(mu_A, mu_B))
dm4 = tnorm_product(fuzzy_not(mu_A), fuzzy_not(mu_B))
print()
print("De Morgan (Max/Min)        : selisih maks =", float(np.max(np.abs(dm1 - dm2))))
print("De Morgan (AlgSum/Product) : selisih maks =", float(np.max(np.abs(dm3 - dm4))))
print("Urutan t-norm dan t-conorm terverifikasi pada seluruh X; semua mu berada di [0,1].")
print("\nGrafik tersimpan: operasi_himpunan_fuzzy_komparasi.png")
