import json
import sys
import time
import pathlib
 
import numpy as np
 
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
 
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
 
from core import config as C
from core.membership import trimf
from core.gaji_model import bangun_fis_gaji, format_rupiah
from core.skenario import SKENARIO
from core.sugeno_tsukamoto import (hitung_sugeno, hitung_tsukamoto, invers_monoton_naik, invers_monoton_turun,
                                   sugeno_gaji, tsukamoto_gaji)
 
GAMBAR = ROOT / "hasil_pengujian" / "gambar"
 
# ---------------- Sistem 4 aturan (tugas modul, adaptasi gaji) ----------------
# 2 input x 2 label: himpunan segitiga yang saling melengkapi (mu_Singkat + mu_Lama = 1)
MF_E = {"Singkat": (0, 0, 30), "Lama": (0, 30, 30)}        # Pengalaman 0-30 tahun
MF_K = {"Rendah": (0, 0, 100), "Tinggi": (0, 100, 100)}    # Kinerja 0-100
ATURAN4 = [("Singkat", "Rendah", "Rendah"), ("Singkat", "Tinggi", "Menengah"),
           ("Lama", "Rendah", "Menengah"), ("Lama", "Tinggi", "Tinggi")]
 
 
def sistem4(e, k):
    me = {l: float(trimf(e, p)) for l, p in MF_E.items()}
    mk = {l: float(trimf(k, p)) for l, p in MF_K.items()}
    alphas = [min(me[a], mk[b]) for a, b, _ in ATURAN4]
    kons = [c for _, _, c in ATURAN4]
    z_s = [C.SUGENO0_KONSTANTA[c] for c in kons]
    fungsi = []
    for c in kons:
        arah, lo, hi = C.TSUKAMOTO_KONSEKUEN[c]
        fungsi.append((lambda a, lo=lo, hi=hi: invers_monoton_naik(a, lo, hi)) if arah == "naik"
                      else (lambda a, lo=lo, hi=hi: invers_monoton_turun(a, lo, hi)))
    s0 = hitung_sugeno(alphas, z_s)
    t, z_t = hitung_tsukamoto(alphas, fungsi)
    return dict(me=me, mk=mk, alphas=alphas, z_sugeno=z_s, z_tsuka=z_t, sugeno0=s0, tsukamoto=t)
 
 
def main():
    keluaran = {}
 
    # ==========================================================
    # A. VERIFIKASI TERHADAP CONTOH MODUL (hasil modul: 5.571 dan 5.429 juta)
    # ==========================================================
    alphas = [0.2, 0.4, 0.2, 0.6]
    s0 = hitung_sugeno(alphas, [2, 4, 5, 8])
    s1 = hitung_sugeno(alphas, [3.9, 6.2, 6.5, 9.8])
    ts, zt = hitung_tsukamoto(alphas, [lambda a: invers_monoton_naik(a, 2.0, 10.0)] * 4)
    print("=" * 70)
    print("A. VERIFIKASI CONTOH MODUL (bonus kinerja tim IT, juta rupiah)")
    print("=" * 70)
    print(f" Sugeno orde 0 : {s0:.3f}   (modul: 5.571)  cocok: {abs(s0-5.571) < 5e-4}")
    print(f" Sugeno orde 1 : {s1:.3f}   (dihitung dari z = 3.9, 6.2, 6.5, 9.8 pada kode modul)")
    print(f" Tsukamoto     : {ts:.3f}   (modul: 5.429)  cocok: {abs(ts-5.429) < 5e-4}  z_i = {[round(v,2) for v in zt]}\n")
    keluaran["verifikasi_modul"] = dict(sugeno0=s0, sugeno1=s1, tsukamoto=ts, z_tsukamoto=zt,
                                        cocok_s0=abs(s0 - 5.571) < 5e-4, cocok_t=abs(ts - 5.429) < 5e-4)
 
    # ==========================================================
    # B. TUGAS MODUL: SISTEM 4 ATURAN, 5 VARIASI INPUT
    # ==========================================================
    print("=" * 70)
    print("B. SISTEM 4 ATURAN: Pengalaman (0-30 th) x Kinerja (0-100) -> Gaji")
    print("=" * 70)
    for i, (a, b, c) in enumerate(ATURAN4, 1):
        print(f" R{i}: IF Pengalaman {a} AND Kinerja {b} THEN Gaji {c}")
    variasi = [(2, 40), (5, 90), (15, 50), (25, 30), (28, 95)]
    print(f"\n{'Variasi':<8}{'Peng.':>6}{'Kin.':>6}{'Sugeno 0':>15}{'Tsukamoto':>15}{'Selisih':>14}")
    tabel_b = []
    for n, (e, k) in enumerate(variasi, 1):
        r = sistem4(e, k)
        sel = r["sugeno0"] - r["tsukamoto"]
        print(f"V{n:<7}{e:>6}{k:>6}{format_rupiah(r['sugeno0']):>15}{format_rupiah(r['tsukamoto']):>15}{format_rupiah(sel):>14}")
        tabel_b.append(dict(kode=f"V{n}", pengalaman=e, kinerja=k, **r, selisih=sel))
    keluaran["sistem4"] = dict(aturan=ATURAN4, tabel=tabel_b)
    print()
 
    # ==========================================================
    # C. PERBANDINGAN EMPAT METODE PADA SISTEM GAJI LENGKAP
    # ==========================================================
    fis = bangun_fis_gaji()
    print("=" * 70)
    print("C. PERBANDINGAN METODE PADA 8 SKENARIO (108 aturan, input & asumsi sama)")
    print("=" * 70)
    print(f"{'Skn':<5}{'Mamdani':>13}{'Sugeno 0':>13}{'Sugeno 1':>13}{'Tsukamoto':>13}")
    tabel_c = {}
    for kode, nama, desk, nilai in SKENARIO:
        mam = fis.compute(nilai); al = fis.hasil["alpha_aturan"]
        s0_, r0, _ = sugeno_gaji(nilai, al, 0)
        s1_, r1, _ = sugeno_gaji(nilai, al, 1)
        t_, rt, _ = tsukamoto_gaji(al)
        print(f"{kode:<5}{format_rupiah(mam):>13}{format_rupiah(s0_):>13}{format_rupiah(s1_):>13}{format_rupiah(t_):>13}")
        tabel_c[kode] = dict(nama=nama, input=nilai, mamdani=mam, sugeno0=s0_, sugeno1=s1_, tsukamoto=t_,
                             rincian_s0=r0, rincian_s1=r1, rincian_t=rt, jumlah_aktif=len(r0))
    keluaran["perbandingan"] = tabel_c
    print()
 
    # contoh perhitungan yang dapat ditelusuri: S4 (aturan aktif sedikit) -> rincian terurut
    kode_contoh = "S4"
    c = tabel_c[kode_contoh]
    print(f"Rincian {kode_contoh} (input {c['input']}):")
    print(f"{'Aturan':<8}{'Kat':<10}{'alpha':>8}{'z Sugeno0':>14}{'z Sugeno1':>14}{'z Tsukamoto':>14}")
    gabung = {}
    for (rid, kat, a, z) in c["rincian_s0"]: gabung[rid] = [kat, a, z, None, None]
    for (rid, kat, a, z) in c["rincian_s1"]: gabung[rid][3] = z
    for (rid, kat, a, z) in c["rincian_t"]: gabung[rid][4] = z
    for rid, (kat, a, z0, z1, zt_) in sorted(gabung.items(), key=lambda t: -t[1][1]):
        print(f"{rid:<8}{kat:<10}{a:>8.3f}{format_rupiah(z0):>14}{format_rupiah(z1):>14}{format_rupiah(zt_):>14}")
    keluaran["rincian_contoh"] = dict(kode=kode_contoh, baris=[(rid, *v) for rid, v in gabung.items()])
    print()
 
    # grafik perbandingan
    kode = list(tabel_c)
    lebar = 0.2
    x = np.arange(len(kode))
    fig, ax = plt.subplots(figsize=(11, 4.6))
    for i, (kunci, lbl, warna) in enumerate([("mamdani", "Mamdani (centroid)", "#1565C0"),
                                             ("sugeno0", "Sugeno orde 0", "#2E7D32"),
                                             ("sugeno1", "Sugeno orde 1", "#EF6C00"),
                                             ("tsukamoto", "Tsukamoto", "#C62828")]):
        ax.bar(x + (i - 1.5) * lebar, [tabel_c[k][kunci] / C.JUTA for k in kode], lebar, label=lbl, color=warna)
    ax.set_xticks(x); ax.set_xticklabels(kode); ax.set_ylabel("Rekomendasi gaji (juta rupiah)")
    ax.set_title("Perbandingan Mamdani, Sugeno, dan Tsukamoto pada 8 skenario", fontsize=10, fontweight="bold")
    ax.grid(axis="y", ls=":", alpha=.6); ax.legend(fontsize=8, ncol=4, loc="upper center")
    ax.set_ylim(0, 16)
    fig.tight_layout(); fig.savefig(GAMBAR / "p9_perbandingan_metode.png", dpi=200); plt.close(fig)
 
    # ==========================================================
    # D. BAHAN ANALISIS
    # ==========================================================
    # D1. kecepatan (seluruh tahap setelah fuzzifikasi)
    nilai = SKENARIO[5][3]
    ulang = 300
    t0 = time.perf_counter()
    for _ in range(ulang):
        fis.compute(nilai)
    t_mam = (time.perf_counter() - t0) / ulang * 1e3
    t0 = time.perf_counter()
    for _ in range(ulang):
        n_ = fis._cek_input(nilai); d_ = fis.fuzzifikasi(n_); a_ = fis.hitung_alpha(d_)
        sugeno_gaji(n_, a_, 0)
    t_sug = (time.perf_counter() - t0) / ulang * 1e3
    print(f"D1. Waktu inferensi lengkap per data (S6, {ulang} ulangan, mesin ini): Mamdani={t_mam:.3f} ms, Sugeno0={t_sug:.3f} ms")
 
    # D2. syarat monoton Tsukamoto: pada segitiga simetris, mu(z)=alpha punya DUA solusi
    a_uji = 0.5
    lo, pk, hi = C.HIMPUNAN_OUTPUT["Menengah"]
    z_kiri = lo + a_uji * (pk - lo); z_kanan = hi - a_uji * (hi - pk)
    print(f"D2. Segitiga Menengah, mu(z) = {a_uji}: z_kiri = {z_kiri/C.JUTA:.2f} jt, z_kanan = {z_kanan/C.JUTA:.2f} jt (dua solusi -> invers tidak tunggal)")
 
    # D3. Sugeno orde 1 vs orde 0 di dalam satu aturan dominan
    fis_ = bangun_fis_gaji()
    print("D3. Variasi pengalaman 20-30 th (pendidikan=100, kinerja=100, tanggung jawab=100):")
    print(f"{'Peng.':>6}{'Mamdani':>13}{'Sugeno 0':>13}{'Sugeno 1':>13}{'Tsukamoto':>13}")
    d3 = []
    for e in (20, 22, 25, 28, 30):
        nl = dict(pengalaman=e, pendidikan=100, kinerja=100, tanggung_jawab=100)
        m_ = fis_.compute(nl); al = fis_.hasil["alpha_aturan"]
        v = (m_, sugeno_gaji(nl, al, 0)[0], sugeno_gaji(nl, al, 1)[0], tsukamoto_gaji(al)[0])
        print(f"{e:>6}" + "".join(f"{format_rupiah(t):>13}" for t in v))
        d3.append(dict(pengalaman=e, mamdani=v[0], sugeno0=v[1], sugeno1=v[2], tsukamoto=v[3]))
    print()
    keluaran["analisis"] = dict(waktu_mamdani_ms=t_mam, waktu_sugeno_ms=t_sug, ulangan=ulang,
                                tsukamoto_dua_solusi=dict(alpha=a_uji, z_kiri=z_kiri, z_kanan=z_kanan), d3=d3)
 
    out = ROOT / "hasil_pengujian" / "praktikum9_hasil.json"
    out.write_text(json.dumps(keluaran, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    print(f"Hasil disimpan: {out}")
 
 
if __name__ == "__main__":
    main()
