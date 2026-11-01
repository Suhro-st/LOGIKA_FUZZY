# ==========================================================
# 1. BASIS ATURAN PROTOTIPE (matriks 3 x 3)
# ==========================================================
PENGALAMAN = ["Pemula", "Menengah", "Berpengalaman"]
TANGGUNG_JAWAB = ["Rendah", "Sedang", "Tinggi"]
 
 
def kategori_matriks(i, j):
    """Dasar penyusunan: jumlah tingkat ordinal (0..4). <=1 Rendah, 2 Menengah, >=3 Tinggi."""
    s = i + j
    return "Rendah" if s <= 1 else ("Menengah" if s == 2 else "Tinggi")
 
 
def buat_rule_base_prototipe():
    rules, n = [], 1
    for i, e in enumerate(PENGALAMAN):
        for j, t in enumerate(TANGGUNG_JAWAB):
            rules.append(FuzzyRule(f"R{n}", {"pengalaman": e, "tanggung_jawab": t},
                                   {"gaji": kategori_matriks(i, j)}))
            n += 1
    return rules
 
 
def evaluasi(rules, derajat, mode="min"):
    """Mengembalikan list (rule, alpha) untuk seluruh aturan."""
    return [(r, r.hitung_firing_strength(derajat, mode)) for r in rules]
 
 
def cetak_evaluasi(judul, rules, derajat, mode="min"):
    print("=" * 78)
    print(judul)
    print("=" * 78)
    hasil = evaluasi(rules, derajat, mode)
    for r, a in hasil:
        print(f"{r} --> {'AKTIF (alpha = %.2f)' % a if a > 0 else 'NONAKTIF'}")
    aktif = [(r.rule_id, r.label_output, a) for r, a in hasil if a > 0]
    print("-" * 78)
    if aktif:
        for rid, lbl, a in aktif:
            print(f" - {rid:<4}: Gaji = {lbl:<9} alpha = {a:.2f}")
    else:
        print(" Tidak ada aturan yang terpicu (semua alpha = 0)")
    print()
    return hasil, aktif
 
 
def agregasi_per_label(aktif):
    """Aturan berkonsekuen sama digabung dengan operator MAX."""
    agg = {}
    for _, lbl, a in aktif:
        agg[lbl] = max(agg.get(lbl, 0.0), a)
    return agg
 
 
def fuzzifikasi_crisp(pengalaman, tanggung_jawab):
    d = {}
    for kunci, x in (("pengalaman", pengalaman), ("tanggung_jawab", tanggung_jawab)):
        d[kunci] = {l: float(trimf(x, p)) for l, p in C.VARIABEL_INPUT[kunci]["himpunan"].items()}
    return d
 
 
def main():
    rules = buat_rule_base_prototipe()
    keluaran = {"rules": [{"id": r.rule_id, "pengalaman": r.antecedent["pengalaman"],
                           "tanggung_jawab": r.antecedent["tanggung_jawab"],
                           "gaji": r.label_output, "teks": str(r)} for r in rules]}
 
    print("MATRIKS BASIS ATURAN (Pengalaman x Tanggung Jawab -> Gaji)")
    print(f"{'':<16}" + "".join(f"{t:<14}" for t in TANGGUNG_JAWAB))
    for i, e in enumerate(PENGALAMAN):
        print(f"{e:<16}" + "".join(f"R{i*3+j+1}: {kategori_matriks(i,j):<9}" for j in range(3)))
    print()
 
    # ---- Tugas modul: pengujian dengan derajat yang ditentukan ----
    d_tugas = {"pengalaman": {"Pemula": 0.2, "Menengah": 0.8, "Berpengalaman": 0.0},
               "tanggung_jawab": {"Rendah": 0.0, "Sedang": 0.5, "Tinggi": 0.5}}
    h, aktif = cetak_evaluasi("TUGAS PRAKTIKUM 6: pengujian dengan derajat dari instruksi modul", rules, d_tugas)
    keluaran["tugas"] = {"derajat": d_tugas, "aktif": aktif, "agregasi_label": agregasi_per_label(aktif)}
 
    # ---- Skenario A, B, C (analog skenario pada modul) ----
    skenario = {
        "A": ("Karyawan baru, tanggung jawab ringan",
              {"pengalaman": {"Pemula": 1.0, "Menengah": 0.0, "Berpengalaman": 0.0},
               "tanggung_jawab": {"Rendah": 0.8, "Sedang": 0.2, "Tinggi": 0.0}}),
        "B": ("Karyawan menengah menuju senior, tanggung jawab sedang-tinggi",
              {"pengalaman": {"Pemula": 0.0, "Menengah": 0.7, "Berpengalaman": 0.3},
               "tanggung_jawab": {"Rendah": 0.0, "Sedang": 0.4, "Tinggi": 0.6}}),
        "C": ("Karyawan senior, tanggung jawab maksimal",
              {"pengalaman": {"Pemula": 0.0, "Menengah": 0.0, "Berpengalaman": 1.0},
               "tanggung_jawab": {"Rendah": 0.0, "Sedang": 0.0, "Tinggi": 1.0}}),
    }
    keluaran["skenario"] = {}
    for kode, (desk, d) in skenario.items():
        h, aktif = cetak_evaluasi(f"SKENARIO {kode}: {desk}", rules, d)
        keluaran["skenario"][kode] = {"deskripsi": desk, "derajat": d, "aktif": aktif,
                                      "agregasi_label": agregasi_per_label(aktif)}
 
    # ---- Fuzzifikasi dari nilai crisp (menyambung dengan Modul 1) ----
    d_crisp = fuzzifikasi_crisp(10.0, 60.0)
    h, aktif = cetak_evaluasi("INPUT CRISP: Pengalaman = 10 tahun, Tanggung Jawab = 60", rules, d_crisp)
    keluaran["crisp"] = {"input": {"pengalaman": 10.0, "tanggung_jawab": 60.0}, "derajat": d_crisp,
                         "aktif": aktif, "agregasi_label": agregasi_per_label(aktif)}
 
    # ---- Operator OR dan AND-product (demonstrasi) ----
    r_or = FuzzyRule("R_OR", {"pengalaman": "Berpengalaman", "tanggung_jawab": "Tinggi"}, {"gaji": "Tinggi"}, "OR")
    r_and = FuzzyRule("R_AND", {"pengalaman": "Berpengalaman", "tanggung_jawab": "Tinggi"}, {"gaji": "Tinggi"}, "AND")
    d_b = skenario["B"][1]
    keluaran["operator"] = {
        "derajat": d_b,
        "AND_min": r_and.hitung_firing_strength(d_b, "min"),
        "AND_product": r_and.hitung_firing_strength(d_b, "product"),
        "OR_max": r_or.hitung_firing_strength(d_b),
    }
    print("DEMONSTRASI OPERATOR (Skenario B: Berpengalaman=0.3, Tanggung Jawab Tinggi=0.6)")
    print(f" AND (min)     : {keluaran['operator']['AND_min']:.2f}")
    print(f" AND (product) : {keluaran['operator']['AND_product']:.2f}")
    print(f" OR  (max)     : {keluaran['operator']['OR_max']:.2f}\n")
 
    # ---- Analisis 1: aturan tidak lengkap -> tidak ada aturan aktif ----
    tidak_lengkap = rules[:3]       # hanya R1-R3 (Pemula)
    d_sen = skenario["C"][1]
    h, aktif = cetak_evaluasi("ANALISIS 1: basis aturan TIDAK LENGKAP (hanya R1-R3) dengan input Skenario C",
                              tidak_lengkap, d_sen)
    keluaran["tidak_lengkap"] = {"jumlah_aturan": len(tidak_lengkap), "aktif": aktif}
 
    # ---- Analisis 2: aturan berkonsekuen sama -> agregasi MAX ----
    h, aktif = cetak_evaluasi("ANALISIS 2: R6, R8, R9 sama-sama berkonsekuen Gaji = Tinggi (Skenario B)",
                              rules, skenario["B"][1])
    sama = [(rid, a) for rid, lbl, a in aktif if lbl == "Tinggi"]
    print(f"Alpha aturan berkonsekuen Tinggi: {sama} -> agregasi MAX = {max(a for _, a in sama):.2f}\n")
    keluaran["konsekuen_sama"] = {"alpha": sama, "agregasi_max": max(a for _, a in sama)}
 
    # ---- Analisis 3: urutan aturan tidak berpengaruh ----
    acak = rules[:]
    random.Random(7).shuffle(acak)
    h1 = {r.rule_id: a for r, a in evaluasi(rules, d_tugas)}
    h2 = {r.rule_id: a for r, a in evaluasi(acak, d_tugas)}
    sama_hasil = h1 == h2
    print(f"ANALISIS 3: urutan aturan diacak -> alpha tiap aturan identik? {sama_hasil}")
    print(" urutan acak:", [r.rule_id for r in acak], "\n")
    keluaran["urutan"] = {"identik": sama_hasil, "urutan_acak": [r.rule_id for r in acak]}
 
    out = ROOT / "hasil_pengujian" / "praktikum6_hasil.json"
    out.write_text(json.dumps(keluaran, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Hasil disimpan: {out}")
 
 
if __name__ == "__main__":
    main()
