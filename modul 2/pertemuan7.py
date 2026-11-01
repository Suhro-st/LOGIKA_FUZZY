import json
import sys
import pathlib
import warnings
 
import numpy as np
 
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
 
from core import config as C
from core.gaji_model import (bangun_fis_gaji, buat_rule_base, format_rupiah, kategori_dari_nilai,
                             hitung_independen, ringkasan_aturan_aktif)
from core import visual as V
 
GAMBAR = ROOT / "hasil_pengujian" / "gambar"
KASUS = {
    "Kasus 1": dict(pengalaman=3, pendidikan=35, kinerja=38, tanggung_jawab=30),
    "Kasus 2": dict(pengalaman=8, pendidikan=60, kinerja=68, tanggung_jawab=60),
    "Kasus 3": dict(pengalaman=18, pendidikan=85, kinerja=88, tanggung_jawab=80),
}
 
 
def main():
    keluaran = {}
    rules = buat_rule_base()
    fis = bangun_fis_gaji()
    fis_prod = bangun_fis_gaji(implikasi="product")
 
    print("=" * 74)
    print("KNOWLEDGE BASE SISTEM")
    print("=" * 74)
    for k, info in C.VARIABEL_INPUT.items():
        print(f" Input  {info['nama']:<26} domain {info['domain']} {info['satuan']:<11} label: {list(info['himpunan'])}")
    print(f" Output Rekomendasi gaji            domain Rp{C.GAJI_MIN:,} - Rp{C.GAJI_MAX:,}".replace(",", "."))
    print(f" Jumlah aturan: {len(fis.rules)}\n")
 
    V.plot_alur_fis(str(GAMBAR / "p7_alur_fis.png"))
    V.plot_mf_input(str(GAMBAR / "mf_input.png"))
    V.plot_mf_output(str(GAMBAR / "mf_output.png"))
 
    # ---------------- Tiga kasus uji ----------------
    keluaran["kasus"] = {}
    print("=" * 74)
    print("PENGUJIAN 3 KOMBINASI INPUT")
    print("=" * 74)
    for nama, nilai in KASUS.items():
        crisp = fis.compute(nilai)
        h = fis.hasil
        crisp_prod = fis_prod.compute(nilai)
        pembanding = hitung_independen(nilai, rules)
        kat, mu_kat = kategori_dari_nilai(crisp)
        aktif = ringkasan_aturan_aktif(h)
        print(f"{nama}: {nilai}")
        print(f"   aturan aktif: {len(aktif)} | alpha per kategori: " +
              ", ".join(f"{k}={v:.3f}" for k, v in h["alpha_label"].items()))
        print(f"   Mamdani Min + Centroid : {format_rupiah(crisp)}  (kategori: {kat})")
        print(f"   Mamdani Product        : {format_rupiah(crisp_prod)}")
        print(f"   Pembanding independen  : {format_rupiah(pembanding)}  selisih = {abs(pembanding-crisp):.6f}\n")
        V.plot_agregasi(h, str(GAMBAR / f"p7_{nama.replace(' ', '').lower()}_agregasi.png"),
                        f"{nama}: agregasi dan defuzzifikasi centroid")
        keluaran["kasus"][nama] = dict(
            input=nilai, derajat=h["derajat"], alpha_label=h["alpha_label"], jumlah_aktif=len(aktif),
            crisp=crisp, crisp_product=crisp_prod, kategori=kat, mu_kategori=mu_kat,
            pembanding_independen=pembanding)
        if nama == "Kasus 2":
            keluaran["alur_kasus2"] = dict(
                derajat={v: {l: m for l, m in d.items() if m > 0} for v, d in h["derajat"].items()},
                aktif=[(r.rule_id, str(r), a) for r, a in aktif], alpha_label=h["alpha_label"], crisp=crisp)
            V.plot_pipeline(h, str(GAMBAR / "p7_pipeline_kasus2.png"), "Aliran data Kasus 2 dari input sampai output")
            fis.compute(nilai); hm = dict(fis.hasil)
            fis_prod.compute(nilai); hp = dict(fis_prod.hasil)
            V.plot_min_vs_product(hm, hp, str(GAMBAR / "p7_min_vs_product.png"),
                                  "Kasus 2: perbandingan implikasi Clipping (Min) dan Scaling (Product)")
 
    # ---------------- Analisis 3: semua alpha = 0 ----------------
    print("=" * 74)
    print("ANALISIS: SEMUA ALPHA = 0 (basis aturan sengaja dibuat tidak lengkap)")
    print("=" * 74)
    hanya_tinggi = [r for r in rules if r.label_output == "Tinggi"]
    input_rendah = dict(pengalaman=0, pendidikan=0, kinerja=0, tanggung_jawab=0)
    f_tak_lengkap = bangun_fis_gaji(rules=hanya_tinggi)
    h0 = None
    f_tak_lengkap.fallback = "tengah"
    c0 = f_tak_lengkap.compute(input_rendah); h0 = f_tak_lengkap.hasil
    print(f" Aturan hanya yang berkonsekuen Tinggi ({len(hanya_tinggi)} aturan), input batas bawah semua variabel")
    print(f" max(alpha) = {max(a for _, a in h0['alpha_aturan']):.1f} ; agregasi maksimum = {h0['agregasi'].max():.1f}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tanpa_fallback = float(np.sum(h0["z"] * h0["agregasi"]) / np.sum(h0["agregasi"]))
    print(f" Rumus centroid mentah  : sum(z*mu)/sum(mu) = 0/0 = {tanpa_fallback}")
    f_tak_lengkap.fallback = None
    try:
        f_tak_lengkap.compute(input_rendah)
        pesan = "tidak error"
    except RuntimeError as e:
        pesan = str(e)
    print(f" fallback dimatikan     : RuntimeError -> {pesan}")
    print(f" fallback 'tengah'      : {format_rupiah(c0)} (fallback dipakai: {h0['fallback']})\n")
    keluaran["alpha_nol"] = dict(jumlah_aturan=len(hanya_tinggi), centroid_mentah=str(tanpa_fallback),
                                 pesan_error=pesan, crisp_fallback=c0, fallback=h0["fallback"])
 
    # ---------------- Validasi input ----------------
    print("=" * 74)
    print("VALIDASI INPUT")
    print("=" * 74)
    uji = {"di luar domain (pengalaman=35)": dict(KASUS["Kasus 2"], pengalaman=35),
           "kosong (kinerja=None)": dict(KASUS["Kasus 2"], kinerja=None),
           "bukan angka (kinerja='baik')": dict(KASUS["Kasus 2"], kinerja="baik"),
           "NaN (tanggung_jawab)": dict(KASUS["Kasus 2"], tanggung_jawab=float("nan")),
           "variabel kurang": {"pengalaman": 5}}
    keluaran["validasi"] = {}
    for nama, d in uji.items():
        try:
            fis.compute(d); hasil = "DITERIMA (tidak diharapkan)"
        except (ValueError, KeyError) as e:
            hasil = f"DITOLAK: {e}"
        print(f" {nama:<34} -> {hasil}")
        keluaran["validasi"][nama] = hasil
    print()
 
    out = ROOT / "hasil_pengujian" / "praktikum7_hasil.json"
    out.write_text(json.dumps(keluaran, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Hasil disimpan: {out}")
 
 
if __name__ == "__main__":
    main()
