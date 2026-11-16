"""
from __future__ import annotations
 
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
 
import numpy as np
 
# ---------------------------------------------------------------------------
# 1. KONSTANTA DOMAIN
# ---------------------------------------------------------------------------
MASA_MIN, MASA_MAX = 0.0, 30.0            # tahun
KINERJA_MIN, KINERJA_MAX = 0.0, 100.0     # skor
GAJI_MIN_RP, GAJI_MAX_RP = 2_000_000, 20_000_000
SKALA_RP = 1_000_000                      # universe output dalam satuan juta rupiah
 
# Pendidikan terakhir dipetakan ke skor ordinal 1-4 agar dapat difuzzifikasi.
PENDIDIKAN_SKOR: Dict[str, float] = {"SMA": 1.0, "D3": 2.0, "S1": 3.0, "S2": 4.0}
PENDIDIKAN_VALID: Tuple[str, ...] = tuple(PENDIDIKAN_SKOR)
 
# Batas kategori gaji (juta rupiah)
BATAS_RENDAH = 6.0    # < 6 juta           -> Rendah
BATAS_TINGGI = 11.0   # >= 11 juta        -> Tinggi ; di antaranya -> Sedang
 
# ---------------------------------------------------------------------------
# 2. HIMPUNAN FUZZY & FUNGSI KEANGGOTAAN
#    ("tri" = segitiga [a,b,c]; "trap" = trapesium [a,b,c,d])
# ---------------------------------------------------------------------------
MF_MASA = {
    "Baru":   ("trap", [0, 0, 2, 6]),
    "Sedang": ("tri",  [3, 9, 15]),
    "Lama":   ("trap", [12, 20, 30, 30]),
}
MF_KINERJA = {
    "Kurang": ("trap", [0, 0, 40, 60]),
    "Cukup":  ("tri",  [50, 70, 85]),
    "Baik":   ("trap", [75, 90, 100, 100]),
}
MF_PENDIDIKAN = {
    "Dasar":    ("trap", [1, 1, 1.5, 2.5]),
    "Menengah": ("tri",  [1.5, 2.5, 3.5]),
    "Tinggi":   ("trap", [2.5, 3.5, 4, 4]),
}
MF_GAJI = {                                   # satuan: juta rupiah
    "Sangat Rendah": ("trap", [2, 2, 2.5, 4]),
    "Rendah":        ("tri",  [3, 5, 7.5]),
    "Sedang":        ("tri",  [6, 8.5, 11.5]),
    "Tinggi":        ("tri",  [10, 13, 16]),
    "Sangat Tinggi": ("trap", [14, 16.5, 20, 20]),
}
 
VARIABEL: Dict[str, Dict[str, Any]] = {
    "masa_kerja": {"judul": "Masa Kerja", "satuan": "tahun", "universe": (0.0, 30.0, 0.1), "mf": MF_MASA},
    "kinerja":    {"judul": "Nilai Kinerja", "satuan": "skor", "universe": (0.0, 100.0, 0.5), "mf": MF_KINERJA},
    "pendidikan": {"judul": "Pendidikan Terakhir", "satuan": "skor ordinal (1=SMA, 2=D3, 3=S1, 4=S2)",
                   "universe": (1.0, 4.0, 0.01), "mf": MF_PENDIDIKAN},
    "gaji":       {"judul": "Rekomendasi Gaji", "satuan": "juta rupiah", "universe": (2.0, 20.0, 0.01), "mf": MF_GAJI},
}
 
 
def trimf(x, abc) -> np.ndarray:
    """Fungsi keanggotaan segitiga [a, b, c]."""
    a, b, c = (float(v) for v in abc)
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x, dtype=float)
    if b > a:
        m = (x > a) & (x < b)
        y[m] = (x[m] - a) / (b - a)
    if c > b:
        m = (x > b) & (x < c)
        y[m] = (c - x[m]) / (c - b)
    y[x == b] = 1.0
    return y
 
 
def trapmf(x, abcd) -> np.ndarray:
    """Fungsi keanggotaan trapesium [a, b, c, d]."""
    a, b, c, d = (float(v) for v in abcd)
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x, dtype=float)
    if b > a:
        m = (x > a) & (x < b)
        y[m] = (x[m] - a) / (b - a)
    y[(x >= b) & (x <= c)] = 1.0
    if d > c:
        m = (x > c) & (x < d)
        y[m] = (d - x[m]) / (d - c)
    return y
 
 
def mf(x, spec) -> np.ndarray:
    """Hitung derajat keanggotaan berdasarkan spesifikasi ('tri'|'trap', parameter)."""
    jenis, param = spec
    return trimf(x, param) if jenis == "tri" else trapmf(x, param)
 
 
def universe(nama: str) -> np.ndarray:
    lo, hi, step = VARIABEL[nama]["universe"]
    n = int(round((hi - lo) / step)) + 1          # linspace -> titik ujung tepat (bebas galat floating point)
    return np.linspace(lo, hi, n)
 
 
# ---------------------------------------------------------------------------
# 3. BASIS ATURAN (27 aturan = 3 x 3 x 3)
# ---------------------------------------------------------------------------
LABEL_MASA = list(MF_MASA)
LABEL_KINERJA = list(MF_KINERJA)
LABEL_PEND = list(MF_PENDIDIKAN)
LABEL_GAJI = list(MF_GAJI)
 
 
@dataclass(frozen=True)
class Aturan:
    nomor: int
    masa: str
    kinerja: str
    pendidikan: str
    gaji: str
 
    def teks(self) -> str:
        return (f"IF Masa Kerja {self.masa} AND Kinerja {self.kinerja} "
                f"AND Pendidikan {self.pendidikan} THEN Gaji {self.gaji}")
 
 
def bangun_aturan() -> List[Aturan]:
    """
    Basis aturan disusun dari skor tertimbang tingkat (0..2) tiap variabel:
        skor = 0,40 * masa + 0,35 * kinerja + 0,25 * pendidikan
    Indeks himpunan gaji (0..4) = pembulatan(2 * skor). Dihitung dengan aritmetika
    bilangan bulat supaya bebas galat pembulatan: (8m + 7k + 5p + 5) // 10.
    Masa kerja diberi bobot terbesar karena skala gaji umumnya bertumpu pada senioritas,
    disusul kinerja, lalu pendidikan.
    """
    aturan: List[Aturan] = []
    nomor = 1
    for m in range(3):
        for k in range(3):
            for p in range(3):
                idx = (8 * m + 7 * k + 5 * p + 5) // 10
                aturan.append(Aturan(nomor, LABEL_MASA[m], LABEL_KINERJA[k], LABEL_PEND[p], LABEL_GAJI[idx]))
                nomor += 1
    return aturan
 
 
RULES: List[Aturan] = bangun_aturan()
 
# ---------------------------------------------------------------------------
# 4. VALIDASI INPUT (Praktikum 14)
# ---------------------------------------------------------------------------
 
 
class ValidasiError(ValueError):
    """Dilempar ketika input pengguna tidak memenuhi ketentuan."""
 
 
def _ke_angka(nilai: Any, nama: str) -> float:
    if nilai is None or (isinstance(nilai, str) and nilai.strip() == ""):
        raise ValidasiError(f"{nama} wajib diisi.")
    if isinstance(nilai, bool):
        raise ValidasiError(f"{nama} harus berupa angka.")
    try:
        if isinstance(nilai, str):
            angka = float(nilai.strip().replace(",", "."))
        else:
            angka = float(nilai)
    except (TypeError, ValueError):
        raise ValidasiError(f"{nama} harus berupa angka, bukan teks.") from None
    if not math.isfinite(angka):
        raise ValidasiError(f"{nama} tidak boleh NaN atau tak hingga.")
    return angka
 
 
def validasi_input(masa_kerja: Any, kinerja: Any, pendidikan: Any) -> Tuple[float, float, str]:
    """Validasi dan normalisasi input. Mengembalikan (masa, kinerja, pendidikan)."""
    masa = _ke_angka(masa_kerja, "Masa kerja")
    if masa < MASA_MIN:
        raise ValidasiError("Masa kerja tidak boleh negatif.")
    if masa > MASA_MAX:
        raise ValidasiError(f"Masa kerja maksimal {MASA_MAX:.0f} tahun.")
 
    kin = _ke_angka(kinerja, "Nilai kinerja")
    if kin < KINERJA_MIN or kin > KINERJA_MAX:
        raise ValidasiError(f"Nilai kinerja harus berada pada rentang {KINERJA_MIN:.0f}-{KINERJA_MAX:.0f}.")
 
    if not isinstance(pendidikan, str) or pendidikan.strip() == "":
        raise ValidasiError("Pendidikan terakhir wajib dipilih.")
    pend = pendidikan.strip().upper()
    if pend not in PENDIDIKAN_SKOR:
        raise ValidasiError("Pendidikan harus salah satu dari: " + ", ".join(PENDIDIKAN_VALID) + ".")
    return masa, kin, pend
 
 
# ---------------------------------------------------------------------------
# 5. MESIN INFERENSI MAMDANI + DEFUZZIFIKASI CENTROID
# ---------------------------------------------------------------------------
 
 
def centroid(x: np.ndarray, y: np.ndarray) -> float:
    """
    Defuzzifikasi Centroid: z* = integral(z * mu(z) dz) / integral(mu(z) dz).
    Integral dihitung eksak per segmen trapesium (hasil identik dengan
    skfuzzy.defuzz(x, mf, 'centroid')).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    dx = np.diff(x)
    y1, y2 = y[:-1], y[1:]
    area = 0.5 * dx * (y1 + y2)
    total = float(area.sum())
    if total <= 0.0:
        raise ZeroDivisionError("Luas daerah agregasi nol: tidak ada aturan yang aktif.")
    s = y1 + y2
    aman = np.where(s > 0, s, 1.0)
    pos = np.where(s > 0, dx * (y1 + 2.0 * y2) / (3.0 * aman), 0.0)
    return float(((x[:-1] + pos) * area).sum() / total)
 
 
def kategori_gaji(gaji_rp: float) -> str:
    juta = gaji_rp / SKALA_RP
    if juta < BATAS_RENDAH:
        return "Rendah"
    if juta < BATAS_TINGGI:
        return "Sedang"
    return "Tinggi"
 
 
def format_rupiah(nilai: float) -> str:
    """Format Rupiah Indonesia, mis. 12345678 -> 'Rp12.345.678'."""
    return "Rp" + f"{int(round(nilai)):,}".replace(",", ".")
 
 
@dataclass
class HasilFuzzy:
    masa_kerja: float
    kinerja: float
    pendidikan: str
    skor_pendidikan: float
    derajat_masa: Dict[str, float]
    derajat_kinerja: Dict[str, float]
    derajat_pendidikan: Dict[str, float]
    aturan_aktif: List[Tuple[Aturan, float]] = field(default_factory=list)
    kekuatan_output: Dict[str, float] = field(default_factory=dict)
    x_gaji: Optional[np.ndarray] = None
    agregasi: Optional[np.ndarray] = None
    gaji_juta: float = 0.0
    gaji_rp: float = 0.0
    kategori: str = ""
 
    @property
    def gaji_format(self) -> str:
        return format_rupiah(self.gaji_rp)
 
 
def inferensi_mamdani(masa: float, kinerja: float, pendidikan: str) -> HasilFuzzy:
    """Jalankan fuzzifikasi -> inferensi Mamdani -> agregasi -> defuzzifikasi Centroid.
    Input diasumsikan sudah tervalidasi (gunakan hitung_gaji / proses_input)."""
    skor = PENDIDIKAN_SKOR[pendidikan]
    d_masa = {k: float(mf(masa, s)) for k, s in MF_MASA.items()}
    d_kin = {k: float(mf(kinerja, s)) for k, s in MF_KINERJA.items()}
    d_pend = {k: float(mf(skor, s)) for k, s in MF_PENDIDIKAN.items()}
 
    x = universe("gaji")
    mf_out = {k: mf(x, s) for k, s in MF_GAJI.items()}
    agregasi = np.zeros_like(x)
    aktif: List[Tuple[Aturan, float]] = []
    kekuatan: Dict[str, float] = {k: 0.0 for k in MF_GAJI}
 
    for r in RULES:
        alpha = min(d_masa[r.masa], d_kin[r.kinerja], d_pend[r.pendidikan])      # AND = min
        if alpha > 0.0:
            aktif.append((r, alpha))
            kekuatan[r.gaji] = max(kekuatan[r.gaji], alpha)                      # agregasi = max
            agregasi = np.fmax(agregasi, np.fmin(alpha, mf_out[r.gaji]))         # implikasi = min
 
    z = centroid(x, agregasi)
    gaji_rp = z * SKALA_RP
    return HasilFuzzy(masa, kinerja, pendidikan, skor, d_masa, d_kin, d_pend, aktif, kekuatan,
                      x, agregasi, z, gaji_rp, kategori_gaji(gaji_rp))
 
 
def hitung_gaji(masa_kerja: Any, kinerja: Any, pendidikan: Any) -> HasilFuzzy:
    """Validasi lalu hitung. Melempar ValidasiError bila input tidak valid."""
    masa, kin, pend = validasi_input(masa_kerja, kinerja, pendidikan)
    return inferensi_mamdani(masa, kin, pend)
 
 
def proses_input(masa_kerja: Any, kinerja: Any, pendidikan: Any) -> Dict[str, Any]:
    """
    Pembungkus aman (error handling) untuk lapisan tampilan.
    Mengembalikan {"valid": bool, "pesan": str, "hasil": HasilFuzzy | None}.
    Tidak pernah melempar exception ke pemanggil.
    """
    try:
        hasil = hitung_gaji(masa_kerja, kinerja, pendidikan)
        return {"valid": True, "pesan": "Perhitungan berhasil.", "hasil": hasil}
    except ValidasiError as e:
        return {"valid": False, "pesan": str(e), "hasil": None}
    except Exception as e:  # pragma: no cover - jaring pengaman terakhir
        return {"valid": False, "pesan": f"Terjadi kesalahan internal: {type(e).__name__}: {e}", "hasil": None}
 
 
# ---------------------------------------------------------------------------
# 6. EVALUASI DATASET
# ---------------------------------------------------------------------------
 
 
def prediksi_dataset(df, kol_masa="Masa_Kerja", kol_kinerja="Nilai_Kinerja", kol_pend="Pendidikan") -> List[float]:
    """Hitung rekomendasi gaji (Rp) untuk setiap baris DataFrame."""
    return [hitung_gaji(m, k, p).gaji_rp for m, k, p in zip(df[kol_masa], df[kol_kinerja], df[kol_pend])]
 
 
def evaluasi(aktual, prediksi) -> Dict[str, float]:
    """MAE, RMSE, MAPE (%) dan R^2."""
    a = np.asarray(aktual, dtype=float)
    p = np.asarray(prediksi, dtype=float)
    err = p - a
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    mape = float(np.mean(np.abs(err) / a) * 100.0)
    ss_res = float(np.sum(err ** 2))
    ss_tot = float(np.sum((a - a.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"MAE": mae, "RMSE": rmse, "MAPE": mape, "R2": r2}
 
 
def cetak_detail_hasil(h: HasilFuzzy):
    """Cetak rincian inferensi fuzzy Mamdani ke terminal."""
    print("=" * 65)
    print("  SISTEM PENERAPAN GAJI KARYAWAN BERBASIS LOGIKA FUZZY (MAMDANI)")
    print("=" * 65)
    print("INPUT PENGUJIAN:")
    print(f"  • Masa Kerja     : {h.masa_kerja} tahun")
    print(f"  • Nilai Kinerja  : {h.kinerja}")
    print(f"  • Pendidikan     : {h.pendidikan} (skor ordinal: {h.skor_pendidikan})")
    print("-" * 65)
    print("1. DERAJAT KEANGGOTAAN (FUZZIFIKASI):")
    print("  • Masa Kerja     :", {k: round(v, 4) for k, v in h.derajat_masa.items() if v > 0})
    print("  • Kinerja        :", {k: round(v, 4) for k, v in h.derajat_kinerja.items() if v > 0})
    print("  • Pendidikan     :", {k: round(v, 4) for k, v in h.derajat_pendidikan.items() if v > 0})
    print("-" * 65)
    print(f"2. ATURAN YANG AKTIF ({len(h.aturan_aktif)} aturan):")
    for r, al in h.aturan_aktif:
        print(f"  • [R{r.nomor:02d}] {r.teks()}  ==> alpha = {al:.4f}")
    print("-" * 65)
    print("3. DEFUZZIFIKASI CENTROID & KEPUTUSAN:")
    print(f"  • Titik Centroid : {h.gaji_juta:.4f} juta")
    print(f"  • Rekomendasi    : {h.gaji_format}")
    print(f"  • Kategori       : {h.kategori}")
    print("=" * 65)


if __name__ == "__main__":
    contoh = proses_input(8, 78, "S1")
    if contoh["valid"]:
        cetak_detail_hasil(contoh["hasil"])
    else:
        print("Galat:", contoh["pesan"])
