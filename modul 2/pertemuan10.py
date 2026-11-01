import csv
import json
import sys
import pathlib
 
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
 
from core import config as C
from core.gaji_model import bangun_fis_gaji, buat_rule_base, format_rupiah, ringkasan_aturan_aktif
from core.keputusan import (INTERPRETASI, evaluasi_lengkap, cetak_hasil, mode_interaktif, periksa_basis_aturan)
from core.skenario import SKENARIO
from core import visual as V
 
GAMBAR = ROOT / "hasil_pengujian" / "gambar"
def main():
    fis = bangun_fis_gaji()
    if "--interaktif" in sys.argv:
        mode_interaktif(fis); return
    rules = buat_rule_base()
    keluaran = {}
 
    print("=" * 78)
    print("1. PEMERIKSAAN BASIS ATURAN")
    print("=" * 78)
    pk = periksa_basis_aturan(fis, rules)
    for k, v in pk.items():
        print(f"  {k:<28}: {v}")
    from collections import Counter
    dist = Counter(r.label_output for r in rules)
    print("  distribusi konsekuen        :", dict(dist), "\n")
    keluaran["pemeriksaan_aturan"] = pk
    keluaran["distribusi_konsekuen"] = dict(dist)
 
    print("=" * 78)
    print("2. PENGUJIAN 8 SKENARIO KARYAWAN SIMULASI")
    print("=" * 78)
    baris_csv, keluaran["skenario"] = [], {}
    for kode, nama, desk, nilai in SKENARIO:
        print(f"[{kode}] {nama} - {desk}")
        e = evaluasi_lengkap(fis, nilai)
        cetak_hasil(nilai, e)
        h = e["h"]
        V.plot_agregasi(h, str(GAMBAR / f"p10_{kode.lower()}_agregasi.png"), f"{kode} - {nama}")
        aktif = ringkasan_aturan_aktif(h)
        keluaran["skenario"][kode] = dict(
            nama=nama, deskripsi=desk, input=nilai,
            derajat={v: {l: m for l, m in d.items() if m > 0} for v, d in h["derajat"].items()},
            jumlah_aktif=len(aktif), aktif_teratas=[(r.rule_id, a, r.label_output) for r, a in aktif[:5]],
            alpha=h["alpha_label"], mamdani=e["crisp"], kategori=e["kategori"], mu_kategori=e["mu_kategori"],
            sugeno0=e["sugeno0"], sugeno1=e["sugeno1"], tsukamoto=e["tsukamoto"], interpretasi=INTERPRETASI[e["kategori"]])
        baris_csv.append([kode, nama, nilai["pengalaman"], nilai["pendidikan"], nilai["kinerja"], nilai["tanggung_jawab"],
                          len(aktif), round(e["crisp"]), e["kategori"], round(e["sugeno0"]), round(e["sugeno1"]), round(e["tsukamoto"])])
    with open(ROOT / "hasil_pengujian" / "hasil_skenario.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kode", "nama", "pengalaman", "pendidikan", "kinerja", "tanggung_jawab", "aturan_aktif",
                    "mamdani_rp", "kategori", "sugeno0_rp", "sugeno1_rp", "tsukamoto_rp"])
        w.writerows(baris_csv)
 
    print("=" * 78)
    print("3. VISUALISASI PERMUKAAN KEPUTUSAN (DECISION SURFACE)")
    print("=" * 78)
    fungsi = lambda d: fis.compute(d)
    p1, rng1 = V.plot_decision_surface(fungsi, str(GAMBAR / "p10_surface_pengalaman_kinerja.png"), "pengalaman", "kinerja",
                                       dict(pendidikan=75, tanggung_jawab=50),
                                       "Permukaan keputusan: Pengalaman x Kinerja (pendidikan=75, tanggung jawab=50)")
    p2, rng2 = V.plot_decision_surface(fungsi, str(GAMBAR / "p10_surface_kinerja_tanggungjawab.png"), "kinerja", "tanggung_jawab",
                                       dict(pengalaman=12, pendidikan=75),
                                       "Permukaan keputusan: Kinerja x Tanggung Jawab (pengalaman=12, pendidikan=75)")
    print(f"  Surface 1: rentang gaji {rng1[0]:.3f} - {rng1[1]:.3f} juta")
    print(f"  Surface 2: rentang gaji {rng2[0]:.3f} - {rng2[1]:.3f} juta\n")
    keluaran["surface"] = dict(s1=rng1, s2=rng2)
    fis.compute(SKENARIO[5][3])   # pulihkan keadaan
 
    out = ROOT / "hasil_pengujian" / "praktikum10_hasil.json"
    out.write_text(json.dumps(keluaran, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    print(f"Hasil disimpan: {out}")
 
 
if __name__ == "__main__":
    main()
