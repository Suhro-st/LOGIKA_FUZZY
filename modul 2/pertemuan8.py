# ==========================================================
    # A. TUGAS MODUL: alpha = 0.5 / 0.8 / 0.2 -> lima metode defuzzifikasi
    # ==========================================================
    alpha_tugas = {"Rendah": 0.5, "Menengah": 0.8, "Tinggi": 0.2}
    impl, agg = agregasi_dari_alpha(z, alpha_tugas)
    hasil_a = {m: defuzzifikasi(z, agg, m) for m in METODE}
    print("=" * 66)
    print("A. TUGAS PRAKTIKUM 8: alpha Rendah=0.5, Menengah=0.8, Tinggi=0.2")
    print("=" * 66)
    for m, v in hasil_a.items():
        print(f" - {m.upper():<9}: {format_rupiah(v):>13}  ({v/C.JUTA:.4f} juta)")
    c_eks = centroid_eksak(z, agg)
    print(f" Centroid eksak (integral analitik per segmen): {c_eks/C.JUTA:.4f} juta")
    print(f" Selisih centroid diskrit vs eksak: Rp{abs(hasil_a['centroid']-c_eks):.2f}\n")
    V.plot_defuzz_compare(z, agg, hasil_a, str(GAMBAR / "p8_komparasi_defuzz.png"),
                          "Perbandingan lima metode defuzzifikasi (alpha: 0.5 / 0.8 / 0.2)")
    keluaran["tugas"] = dict(alpha=alpha_tugas, hasil=hasil_a, centroid_eksak=c_eks,
                             mu_maks=float(agg.max()),
                             plateau=(float(z[agg >= agg.max() - 1e-9].min()), float(z[agg >= agg.max() - 1e-9].max())))
 
    # ==========================================================
    # B. CONTOH PERHITUNGAN MANUAL (Skenario S6, titik patah dihitung tangan)
    # ==========================================================
    fis = bangun_fis_gaji()
    nilai6 = dict(SKENARIO[5][3])
    fis.compute(nilai6); h6 = fis.hasil
    aR, aM, aT = (h6["alpha_label"][k] for k in C.KATEGORI_OUTPUT)
    print("=" * 66)
    print(f"B. CONTOH MANUAL (S6) input {nilai6}")
    print("=" * 66)
    aktif = ringkasan_aturan_aktif(h6)
    for r, a in aktif:
        print(f" {r.rule_id}: alpha={a:.3f}  " + ", ".join(f"{v}={l}" for v, l in r.antecedent.items()) + f" -> {r.label_output}")
    print(f" alpha per kategori (max): Rendah={aR:.3f} Menengah={aM:.3f} Tinggi={aT:.3f}")
    # titik patah kurva agregasi (dalam rupiah): dihitung dari rumus sisi segitiga
    #   Menengah (5.5, 8.5, 11.5)jt dipotong di aM=0.5 ; Tinggi (10, 12.5, 15)jt dipotong di aT=0.2
    mR = C.HIMPUNAN_OUTPUT["Menengah"]; tT = C.HIMPUNAN_OUTPUT["Tinggi"]
    z_naik_M = mR[0] + aM * (mR[1] - mR[0])               # Menengah mencapai alpha
    z_turun_M = mR[2] - aM * (mR[2] - mR[1])              # Menengah turun lewat alpha
    z_naik_T = tT[0] + aT * (tT[1] - tT[0])               # Tinggi mencapai alpha
    z_turun_T = tT[2] - aT * (tT[2] - tT[1])              # Tinggi turun dari alpha
    # perpotongan sisi turun Menengah dengan garis y = aT :  (c - z)/(c - b) = aT
    z_pot = mR[2] - aT * (mR[2] - mR[1])
    titik = [(mR[0], 0.0), (z_naik_M, aM), (z_turun_M, aM), (z_pot, aT), (z_turun_T, aT), (tT[2], 0.0)]
    segmen = luas_momen_segmen(titik)
    A = sum(s["luas"] for s in segmen); M = sum(s["momen"] for s in segmen)
    c_manual = M / A
    print(" Titik patah agregasi (juta Rp, mu):", [(round(a / C.JUTA, 4), round(b, 3)) for a, b in titik])
    for i, s in enumerate(segmen, 1):
        print(f"  seg{i}: ({s['z1']/C.JUTA:.3f},{s['m1']:.3f})->({s['z2']/C.JUTA:.3f},{s['m2']:.3f})"
              f" luas={s['luas']/C.JUTA:.5f} momen={s['momen']/C.JUTA**2:.5f}")
    print(f" Luas total A = {A/C.JUTA:.5f} ; Momen total M = {M/C.JUTA**2:.5f} ; z* = M/A = {format_rupiah(c_manual)}")
    print(f" Program (centroid diskrit 1201 titik) = {format_rupiah(h6['crisp'])} ; selisih Rp{abs(c_manual-h6['crisp']):.2f}\n")
    V.plot_agregasi(h6, str(GAMBAR / "p8_contoh_manual_s6.png"), "Skenario S6: agregasi Mamdani dan centroid",
                    titik={"Bisector": float(defuzzifikasi(h6['z'], h6['agregasi'], 'bisector'))})
    keluaran["manual"] = dict(input=nilai6, aktif=[(r.rule_id, dict(r.antecedent), r.label_output, a) for r, a in aktif],
                              alpha=h6["alpha_label"], titik=titik, segmen=segmen, A=A, M=M,
                              z_manual=c_manual, z_program=h6["crisp"],
                              turunan=dict(z_naik_M=z_naik_M, z_turun_M=z_turun_M, z_pot=z_pot, z_naik_T=z_naik_T, z_turun_T=z_turun_T))
 
    # ==========================================================
    # C. PENGUJIAN SKENARIO: lima metode defuzzifikasi
    # ==========================================================
    print("=" * 66)
    print("C. PENGUJIAN 8 SKENARIO KARYAWAN (Mamdani Min-Max)")
    print("=" * 66)
    print(f"{'Skenario':<9}{'Centroid':>13}{'Bisector':>13}{'MOM':>13}{'SOM':>13}{'LOM':>13}")
    keluaran["skenario"] = {}
    for kode, nama, desk, nilai in SKENARIO:
        fis.compute(nilai); h = fis.hasil
        sem = fis.semua_defuzz()
        print(f"{kode:<9}" + "".join(f"{format_rupiah(sem[m]):>13}" for m in METODE))
        keluaran["skenario"][kode] = dict(nama=nama, input=nilai, alpha=h["alpha_label"], hasil=sem,
                                          jumlah_aktif=len(ringkasan_aturan_aktif(h)))
    print()
 
    # ==========================================================
    # D. ANALISIS: biaya komputasi, SOM vs LOM, distribusi bimodal
    # ==========================================================
    ulang = 2000
    t0 = time.perf_counter()
    for _ in range(ulang):
        defuzzifikasi(z, agg, "centroid")
    t_cog = (time.perf_counter() - t0) / ulang * 1e3
    t0 = time.perf_counter()
    for _ in range(ulang):
        defuzzifikasi(z, agg, "mom")
    t_mom = (time.perf_counter() - t0) / ulang * 1e3
    print(f"D1. Waktu rata-rata per defuzzifikasi (1201 titik, {ulang} ulangan, mesin ini): "
          f"centroid={t_cog:.4f} ms, MOM={t_mom:.4f} ms")
 
    bi = {"Rendah": 0.6, "Menengah": 0.0, "Tinggi": 0.6}
    _, agg_bi = agregasi_dari_alpha(z, bi)
    h_bi = {m: defuzzifikasi(z, agg_bi, m) for m in METODE}
    print("D2. Kurva bimodal (alpha Rendah=0.6, Tinggi=0.6):")
    for m, v in h_bi.items():
        print(f"    {m.upper():<9}: {format_rupiah(v)}  (mu pada titik ini = {np.interp(v, z, agg_bi):.3f})")
    V.plot_defuzz_compare(z, agg_bi, h_bi, str(GAMBAR / "p8_bimodal.png"),
                          "Kurva agregasi bimodal: kelemahan MOM")
    print()
    keluaran["analisis"] = dict(waktu_centroid_ms=t_cog, waktu_mom_ms=t_mom, ulangan=ulang,
                                bimodal=dict(alpha=bi, hasil=h_bi, mu_di_mom=float(np.interp(h_bi['mom'], z, agg_bi))))
 
    out = ROOT / "hasil_pengujian" / "praktikum8_hasil.json"
    out.write_text(json.dumps(keluaran, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    print(f"Hasil disimpan: {out}")
 
 
if __name__ == "__main__":
    main()
