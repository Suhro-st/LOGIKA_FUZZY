{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Praktikum 12 — Evaluasi Sistem Menggunakan Dataset\n",
    "## Sistem Penerapan Gaji Karyawan Berbasis Logika Fuzzy (Mamdani + Centroid)\n",
    "\n",
    "Notebook ini dijalankan di **Google Colab** dan berisi: (1) pembuatan dataset 40 karyawan dengan Pandas, (2) sistem fuzzy Mamdani dengan **Scikit-Fuzzy**, (3) defuzzifikasi **Centroid**, (4) pengujian pada seluruh dataset, (5) perhitungan **MAE dan RMSE**, (6) grafik evaluasi, serta (7) penyimpanan dataset ke **basis data SQLite**.\n",
    "\n",
    "> **Catatan penting:** dataset bersifat **simulasi**. Gaji hasil sistem merupakan **rekomendasi sistem**, bukan keputusan penggajian resmi.\n",
    "\n",
    "Cara menjalankan: menu *Runtime → Run all* (Jalankan semua)."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Instalasi dan impor pustaka"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!pip install -q scikit-fuzzy\n",
    "\n",
    "import os\n",
    "import sqlite3\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import skfuzzy as fuzz\n",
    "from sklearn.metrics import mean_absolute_error, mean_squared_error\n",
    "\n",
    "os.makedirs('grafik', exist_ok=True)      # folder keluaran grafik\n",
    "print('Versi scikit-fuzzy:', getattr(fuzz, '__version__', '-'), '| NumPy', np.__version__, '| Pandas', pd.__version__)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Membuat dataset karyawan (Pandas)\n",
    "Dataset berisi 40 karyawan. `Gaji_Aktual` adalah gaji simulasi yang dibangkitkan dari skema gaji hipotetis (gaji pokok per jenjang pendidikan + tambahan masa kerja + tunjangan kinerja + variasi acak, seed 2026), dibulatkan ke kelipatan Rp50.000."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "data = [\n",
    "    ('K001', 'Andi Pratama', 17.0, 65.0, 'S1', 10350000),\n",
    "    ('K002', 'Siti Rahmawati', 6.5, 91.0, 'D3', 8250000),\n",
    "    ('K003', 'Budi Santoso', 26.5, 68.0, 'S1', 13400000),\n",
    "    ('K004', 'Dewi Lestari', 25.5, 72.0, 'S2', 14650000),\n",
    "    ('K005', 'Rizky Ramadhan', 9.0, 79.0, 'S1', 8500000),\n",
    "    ('K006', 'Putri Anggraini', 7.0, 91.0, 'D3', 8250000),\n",
    "    ('K007', 'Agus Setiawan', 5.5, 98.0, 'D3', 7400000),\n",
    "    ('K008', 'Nur Hidayati', 17.5, 98.0, 'S1', 13200000),\n",
    "    ('K009', 'Fajar Nugroho', 13.5, 70.0, 'SMA', 8100000),\n",
    "    ('K010', 'Maya Sari', 12.0, 77.0, 'S1', 9400000),\n",
    "    ('K011', 'Hendra Wijaya', 15.0, 90.0, 'SMA', 8650000),\n",
    "    ('K012', 'Lina Marlina', 27.5, 67.0, 'SMA', 10550000),\n",
    "    ('K013', 'Yoga Permana', 20.5, 68.0, 'S1', 12150000),\n",
    "    ('K014', 'Rina Oktaviani', 12.0, 80.0, 'D3', 7900000),\n",
    "    ('K015', 'Dimas Prasetyo', 25.0, 60.0, 'SMA', 9650000),\n",
    "    ('K016', 'Wulan Dari', 26.5, 71.0, 'S2', 15250000),\n",
    "    ('K017', 'Eko Susanto', 8.0, 75.0, 'D3', 6900000),\n",
    "    ('K018', 'Intan Permata', 3.0, 75.0, 'S1', 7950000),\n",
    "    ('K019', 'Rudi Hartono', 14.0, 78.0, 'S1', 10450000),\n",
    "    ('K020', 'Ayu Kartika', 5.5, 65.0, 'S2', 8150000),\n",
    "    ('K021', 'Bayu Saputra', 18.0, 68.0, 'SMA', 9000000),\n",
    "    ('K022', 'Citra Dewanti', 25.5, 57.0, 'SMA', 8950000),\n",
    "    ('K023', 'Doni Kurniawan', 23.0, 78.0, 'S1', 13800000),\n",
    "    ('K024', 'Elsa Fitriani', 11.5, 80.0, 'S1', 8950000),\n",
    "    ('K025', 'Ferry Gunawan', 17.0, 57.0, 'S2', 11200000),\n",
    "    ('K026', 'Gita Pramesti', 9.5, 73.0, 'S1', 9500000),\n",
    "    ('K027', 'Hadi Purnomo', 19.0, 77.0, 'S1', 11800000),\n",
    "    ('K028', 'Indah Wahyuni', 1.5, 88.0, 'S1', 6850000),\n",
    "    ('K029', 'Joko Widodo Putra', 7.0, 78.0, 'D3', 6800000),\n",
    "    ('K030', 'Kartika Sari', 24.5, 94.0, 'SMA', 11100000),\n",
    "    ('K031', 'Lukman Hakim', 9.0, 86.0, 'D3', 8450000),\n",
    "    ('K032', 'Mega Safitri', 23.0, 72.0, 'D3', 10750000),\n",
    "    ('K033', 'Naufal Akbar', 27.0, 84.0, 'S1', 14850000),\n",
    "    ('K034', 'Okta Purnama', 25.0, 93.0, 'S2', 15200000),\n",
    "    ('K035', 'Prima Aditya', 20.0, 57.0, 'S1', 9950000),\n",
    "    ('K036', 'Qori Amalia', 19.5, 62.0, 'SMA', 8400000),\n",
    "    ('K037', 'Reza Maulana', 3.5, 85.0, 'S1', 8800000),\n",
    "    ('K038', 'Sari Handayani', 6.5, 52.0, 'S1', 7600000),\n",
    "    ('K039', 'Tono Suryanto', 3.5, 78.0, 'S2', 8850000),\n",
    "    ('K040', 'Umi Kulsum', 9.5, 93.0, 'SMA', 8600000)\n",
    "]\n",
    "df = pd.DataFrame(data, columns=['ID_Karyawan', 'Nama_Karyawan', 'Masa_Kerja', 'Nilai_Kinerja', 'Pendidikan', 'Gaji_Aktual'])\n",
    "\n",
    "assert len(df) >= 30, 'Dataset minimal 30 karyawan'\n",
    "assert df['Masa_Kerja'].between(0, 30).all() and df['Nilai_Kinerja'].between(0, 100).all()\n",
    "assert df['Pendidikan'].isin(['SMA', 'D3', 'S1', 'S2']).all()\n",
    "print('Jumlah karyawan:', len(df))\n",
    "df.head(10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Himpunan fuzzy dan fungsi keanggotaan\n",
    "Variabel input: **Masa Kerja** (0–30 tahun), **Nilai Kinerja** (0–100), **Pendidikan** (SMA=1, D3=2, S1=3, S2=4).\n",
    "Variabel output: **Gaji** (Rp2.000.000–Rp20.000.000; universe dalam satuan juta rupiah)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# --- Universe of discourse ---\n",
    "x_masa = np.linspace(0, 30, 301)\n",
    "x_kin  = np.linspace(0, 100, 201)\n",
    "x_pend = np.linspace(1, 4, 301)\n",
    "x_gaji = np.linspace(2, 20, 1801)           # juta rupiah\n",
    "\n",
    "# --- Fungsi keanggotaan (trimf = segitiga, trapmf = trapesium) ---\n",
    "masa_mf = {'Baru':   fuzz.trapmf(x_masa, [0, 0, 2, 6]),\n",
    "           'Sedang': fuzz.trimf(x_masa,  [3, 9, 15]),\n",
    "           'Lama':   fuzz.trapmf(x_masa, [12, 20, 30, 30])}\n",
    "kin_mf  = {'Kurang': fuzz.trapmf(x_kin, [0, 0, 40, 60]),\n",
    "           'Cukup':  fuzz.trimf(x_kin,  [50, 70, 85]),\n",
    "           'Baik':   fuzz.trapmf(x_kin, [75, 90, 100, 100])}\n",
    "pend_mf = {'Dasar':    fuzz.trapmf(x_pend, [1, 1, 1.5, 2.5]),\n",
    "           'Menengah': fuzz.trimf(x_pend,  [1.5, 2.5, 3.5]),\n",
    "           'Tinggi':   fuzz.trapmf(x_pend, [2.5, 3.5, 4, 4])}\n",
    "gaji_mf = {'Sangat Rendah': fuzz.trapmf(x_gaji, [2, 2, 2.5, 4]),\n",
    "           'Rendah':        fuzz.trimf(x_gaji,  [3, 5, 7.5]),\n",
    "           'Sedang':        fuzz.trimf(x_gaji,  [6, 8.5, 11.5]),\n",
    "           'Tinggi':        fuzz.trimf(x_gaji,  [10, 13, 16]),\n",
    "           'Sangat Tinggi': fuzz.trapmf(x_gaji, [14, 16.5, 20, 20])}\n",
    "\n",
    "SKOR_PEND = {'SMA': 1, 'D3': 2, 'S1': 3, 'S2': 4}\n",
    "\n",
    "# --- Visualisasi fungsi keanggotaan ---\n",
    "warna = ['#0B5563', '#F2A541', '#C8553D', '#5B8E7D', '#7A5C99']\n",
    "fig, axs = plt.subplots(2, 2, figsize=(10, 7.6))\n",
    "for ax, (judul, x, mfs) in zip(axs.ravel(), [('Masa Kerja (tahun)', x_masa, masa_mf), ('Nilai Kinerja (skor 0-100)', x_kin, kin_mf),\n",
    "                                             ('Pendidikan (skor ordinal)', x_pend, pend_mf), ('Rekomendasi Gaji (juta Rp)', x_gaji, gaji_mf)]):\n",
    "    for c, (nama, y) in zip(warna, mfs.items()):\n",
    "        ax.plot(x, y, lw=2.2, color=c, label=nama)\n",
    "    ax.set_title(judul, fontweight='bold'); ax.set_ylabel('Derajat keanggotaan'); ax.grid(alpha=.25)\n",
    "    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=8, frameon=False)\n",
    "fig.suptitle('Fungsi Keanggotaan Variabel Input dan Output', fontweight='bold')\n",
    "fig.tight_layout(); fig.savefig('grafik/fungsi_keanggotaan.png', dpi=200); plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Basis aturan fuzzy (27 aturan) dan mesin inferensi Mamdani\n",
    "Aturan disusun dari skor tertimbang tingkat tiap variabel: `skor = 0,40·masa + 0,35·kinerja + 0,25·pendidikan`; indeks himpunan gaji = `(8m + 7k + 5p + 5) // 10`. Operator **AND = min**, implikasi **min**, agregasi **max**, defuzzifikasi **centroid**."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "L_MASA, L_KIN, L_PEND = list(masa_mf), list(kin_mf), list(pend_mf)\n",
    "L_GAJI = list(gaji_mf)\n",
    "\n",
    "RULES = []\n",
    "for m in range(3):\n",
    "    for k in range(3):\n",
    "        for p in range(3):\n",
    "            RULES.append((L_MASA[m], L_KIN[k], L_PEND[p], L_GAJI[(8*m + 7*k + 5*p + 5) // 10]))\n",
    "\n",
    "tabel_aturan = pd.DataFrame(RULES, columns=['Masa Kerja', 'Kinerja', 'Pendidikan', 'Gaji'])\n",
    "tabel_aturan.index += 1\n",
    "print('Jumlah aturan:', len(RULES))\n",
    "display(tabel_aturan)\n",
    "\n",
    "def mamdani(masa, kinerja, pendidikan):\n",
    "    \"\"\"Mengembalikan rekomendasi gaji (Rupiah) memakai Mamdani + Centroid.\"\"\"\n",
    "    skor = SKOR_PEND[pendidikan]\n",
    "    d_masa = {k: fuzz.interp_membership(x_masa, v, masa)   for k, v in masa_mf.items()}\n",
    "    d_kin  = {k: fuzz.interp_membership(x_kin,  v, kinerja) for k, v in kin_mf.items()}\n",
    "    d_pend = {k: fuzz.interp_membership(x_pend, v, skor)    for k, v in pend_mf.items()}\n",
    "\n",
    "    agregasi = np.zeros_like(x_gaji)\n",
    "    for m, k, p, g in RULES:\n",
    "        alpha = min(d_masa[m], d_kin[k], d_pend[p])              # AND = min\n",
    "        agregasi = np.fmax(agregasi, np.fmin(alpha, gaji_mf[g]))  # implikasi min, agregasi max\n",
    "    return fuzz.defuzz(x_gaji, agregasi, 'centroid') * 1_000_000  # defuzzifikasi centroid\n",
    "\n",
    "print('Contoh (masa 8 th, kinerja 78, S1):', f\"Rp{mamdani(8, 78, 'S1'):,.0f}\".replace(',', '.'))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Pengujian pada seluruh dataset"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df['Gaji_Prediksi_Fuzzy'] = [round(mamdani(m, k, p)) for m, k, p in zip(df.Masa_Kerja, df.Nilai_Kinerja, df.Pendidikan)]\n",
    "df['Selisih'] = df['Gaji_Prediksi_Fuzzy'] - df['Gaji_Aktual']\n",
    "df['Galat_Absolut'] = df['Selisih'].abs()\n",
    "\n",
    "rp = lambda v: f\"Rp{v:,.0f}\".replace(',', '.')\n",
    "tabel = df[['ID_Karyawan', 'Nama_Karyawan', 'Masa_Kerja', 'Nilai_Kinerja', 'Pendidikan', 'Gaji_Aktual', 'Gaji_Prediksi_Fuzzy', 'Selisih']].copy()\n",
    "for kol in ['Gaji_Aktual', 'Gaji_Prediksi_Fuzzy', 'Selisih']:\n",
    "    tabel[kol] = tabel[kol].map(rp)\n",
    "tabel"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Evaluasi: MAE dan RMSE"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "mae  = mean_absolute_error(df.Gaji_Aktual, df.Gaji_Prediksi_Fuzzy)\n",
    "rmse = np.sqrt(mean_squared_error(df.Gaji_Aktual, df.Gaji_Prediksi_Fuzzy))\n",
    "mape = (df.Galat_Absolut / df.Gaji_Aktual).mean() * 100\n",
    "bias = df.Selisih.mean()\n",
    "mae_dasar = (df.Gaji_Aktual - df.Gaji_Aktual.mean()).abs().mean()   # pembanding: selalu menebak rata-rata\n",
    "\n",
    "print(f'MAE   = {rp(mae)}')\n",
    "print(f'RMSE  = {rp(rmse)}')\n",
    "print(f'MAPE  = {mape:.2f} %')\n",
    "print(f'Rata-rata galat (bias) = {rp(bias)}')\n",
    "print(f'MAE pembanding (menebak rata-rata gaji aktual) = {rp(mae_dasar)}')\n",
    "print()\n",
    "print(df.groupby('Pendidikan')['Galat_Absolut'].mean().reindex(['SMA', 'D3', 'S1', 'S2']).map(rp).rename('MAE per pendidikan'))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. Grafik perbandingan dan evaluasi"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "a = df.Gaji_Aktual / 1e6\n",
    "p = df.Gaji_Prediksi_Fuzzy / 1e6\n",
    "idx = np.arange(len(df)); w = 0.4\n",
    "\n",
    "# Grafik 1: perbandingan gaji aktual vs prediksi\n",
    "fig, ax = plt.subplots(figsize=(11, 4.8))\n",
    "ax.bar(idx - w/2, a, w, color='#0B5563', label='Gaji aktual')\n",
    "ax.bar(idx + w/2, p, w, color='#F2A541', label='Gaji prediksi fuzzy')\n",
    "ax.set_xticks(idx); ax.set_xticklabels(df.ID_Karyawan, rotation=90, fontsize=7)\n",
    "ax.set_ylabel('Gaji (juta Rupiah)'); ax.set_xlabel('ID karyawan'); ax.grid(axis='y', alpha=.3); ax.legend()\n",
    "ax.set_title('Perbandingan Gaji Aktual dan Gaji Prediksi Fuzzy', fontweight='bold')\n",
    "fig.tight_layout(); fig.savefig('grafik/perbandingan_gaji.png', dpi=200); plt.show()\n",
    "\n",
    "# Grafik 2: evaluasi (scatter, histogram galat, MAE per pendidikan)\n",
    "err = p - a\n",
    "fig, axs = plt.subplots(1, 3, figsize=(12, 4.2))\n",
    "lim = [min(a.min(), p.min()) - .5, max(a.max(), p.max()) + .5]\n",
    "axs[0].scatter(a, p, color='#0B5563', s=36, alpha=.85, edgecolor='white'); axs[0].plot(lim, lim, '--', color='#C8553D', label='Prediksi = Aktual')\n",
    "axs[0].set_xlim(lim); axs[0].set_ylim(lim); axs[0].set_xlabel('Gaji aktual (juta Rp)'); axs[0].set_ylabel('Gaji prediksi (juta Rp)')\n",
    "axs[0].set_title('(a) Aktual vs Prediksi', fontweight='bold'); axs[0].legend(fontsize=8); axs[0].grid(alpha=.25)\n",
    "axs[1].hist(err, bins=10, color='#F2A541', edgecolor='white'); axs[1].axvline(0, color='#12343B', lw=1.2)\n",
    "axs[1].axvline(err.mean(), color='#C8553D', ls='--', label=f'Rata-rata galat = {err.mean():+.2f}')\n",
    "axs[1].set_xlabel('Galat (prediksi - aktual, juta Rp)'); axs[1].set_ylabel('Jumlah karyawan'); axs[1].set_title('(b) Distribusi Galat', fontweight='bold'); axs[1].legend(fontsize=8)\n",
    "urut = ['SMA', 'D3', 'S1', 'S2']; mae_p = [df.loc[df.Pendidikan == u, 'Galat_Absolut'].mean() / 1e6 for u in urut]\n",
    "bars = axs[2].bar(urut, mae_p, color=warna[:4])\n",
    "for b, v in zip(bars, mae_p): axs[2].text(b.get_x() + b.get_width()/2, v + .03, f'{v:.2f}', ha='center', fontsize=9)\n",
    "axs[2].axhline(mae/1e6, color='#12343B', ls='--', lw=1, label=f'MAE total = {mae/1e6:.2f}')\n",
    "axs[2].set_ylabel('MAE (juta Rp)'); axs[2].set_title('(c) MAE per Pendidikan', fontweight='bold'); axs[2].legend(fontsize=8)\n",
    "fig.suptitle(f'Evaluasi Sistem: MAE = {rp(mae)} | RMSE = {rp(rmse)}', fontweight='bold')\n",
    "fig.tight_layout(); fig.savefig('grafik/evaluasi_gaji.png', dpi=200); plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 8. Penjelasan hasil evaluasi\n",
    "- **MAE** menunjukkan rata-rata selisih mutlak gaji prediksi terhadap gaji aktual; **RMSE** serupa tetapi memberi bobot lebih besar pada kesalahan besar, sehingga selalu ≥ MAE.\n",
    "- Nilai MAE yang hanya sedikit lebih baik daripada pembanding \"menebak rata-rata\" menandakan bahwa basis aturan masih **kasar** (3 himpunan per variabel) dan belum dikalibrasi terhadap data historis.\n",
    "- Histogram galat yang bergeser ke kanan menunjukkan kecenderungan sistem **sedikit melebihkan** gaji (bias positif). Hal ini wajar karena sistem fuzzy dirancang dari pengetahuan pakar, bukan dilatih dari dataset.\n",
    "- Karena dataset simulasi dan gaji aktualnya mengandung variasi acak, hasil ini dipakai untuk **latihan evaluasi**, bukan untuk menyimpulkan kualitas penggajian di dunia nyata.\n",
    "\n",
    "## 9. Simpan dataset beserta hasil prediksi ke basis data SQLite"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "kolom = {'ID_Karyawan': 'id_karyawan', 'Nama_Karyawan': 'nama_karyawan', 'Masa_Kerja': 'masa_kerja', 'Nilai_Kinerja': 'nilai_kinerja',\n",
    "         'Pendidikan': 'pendidikan', 'Gaji_Aktual': 'gaji_aktual', 'Gaji_Prediksi_Fuzzy': 'gaji_prediksi_fuzzy'}\n",
    "\n",
    "with sqlite3.connect('gaji_karyawan.db') as con:\n",
    "    df[list(kolom)].rename(columns=kolom).to_sql('karyawan', con, if_exists='replace', index=False)   # simpan ke tabel karyawan\n",
    "    cek = pd.read_sql_query('SELECT pendidikan, COUNT(*) AS jumlah, ROUND(AVG(gaji_aktual)) AS rata_gaji_aktual, '\n",
    "                            'ROUND(AVG(gaji_prediksi_fuzzy)) AS rata_gaji_prediksi FROM karyawan GROUP BY pendidikan', con)\n",
    "\n",
    "print('Basis data gaji_karyawan.db tersimpan (tabel karyawan). Unduh dari panel Files di Colab (ikon folder).')\n",
    "cek"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 10. Kesimpulan\n",
    "Sistem fuzzy Mamdani dengan defuzzifikasi Centroid berhasil menghasilkan rekomendasi gaji untuk seluruh 40 karyawan. Nilai MAE dan RMSE di atas menjadi tolok ukur awal; perbaikan dapat dilakukan dengan kalibrasi himpunan fuzzy, penambahan variabel (mis. jabatan), atau penyetelan otomatis (ANFIS/algoritma genetika). **Hasil merupakan rekomendasi sistem berbasis data simulasi, bukan keputusan penggajian resmi.**"
   ]
  }
 ],
 "metadata": {
  "colab": {
   "name": "evaluasi_dataset.ipynb",
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python 3",
   "name": "python3"
  },
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
