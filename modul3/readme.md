# Sistem Penerapan Gaji Karyawan Berbasis Logika Fuzzy

Proyek Praktikum 11–16 mata kuliah **Logika Fuzzy** (Modul 3). Sistem merekomendasikan gaji karyawan dari tiga masukan —
**masa kerja** (0–30 tahun), **nilai kinerja** (0–100), dan **pendidikan terakhir** (SMA, D3, S1, S2) — memakai
**Fuzzy Mamdani** dengan defuzzifikasi **Centroid**. Keluaran: Rp2.000.000–Rp20.000.000 beserta kategori Rendah / Sedang / Tinggi.

> **Catatan:** dataset adalah **simulasi**. Gaji yang dihasilkan merupakan **rekomendasi sistem**, bukan keputusan penggajian resmi.

## Struktur folder

```
Sistem_Gaji_Karyawan_Fuzzy/
├── Laporan_Praktikum_modul3.docx      Laporan lengkap (Word)
├── Laporan_Praktikum_modul3.pdf       Laporan lengkap (PDF)
├── README.md                         Dokumen ini
├── requirements.txt                  Dependensi Python
├── app.py                            Aplikasi Streamlit (tampilan)
├── fuzzy_logic.py                    Mesin fuzzy + validasi input (tanpa dependensi Streamlit)
├── database.py                       Lapisan basis data SQLite (skema, baca/tulis)
├── gaji_karyawan.db                  Basis data SQLite: karyawan, riwayat, hasil Black-Box
├── notebook/evaluasi_dataset.ipynb   Notebook Google Colab (Scikit-Fuzzy, MAE/RMSE, simpan ke SQLite)
├── grafik/                           Grafik & diagram yang dipakai pada laporan/presentasi
└── presentasi-_modul3.pptx   12 slide
```

## Instalasi

Membutuhkan Python 3.9 atau lebih baru. Basis data memakai **SQLite** (modul `sqlite3` bawaan Python), jadi tidak perlu memasang server database.

```bash
cd Sistem_Gaji_Karyawan_Fuzzy
python -m venv .venv
# Windows : .venv\Scripts\activate
# macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan aplikasi

```bash
streamlit run app.py
```

Peramban akan terbuka di `http://localhost:8501`.

## Cara menggunakan

1. **Dashboard** – ringkasan dataset, MAE, RMSE, grafik aktual vs prediksi, dan sebaran kategori.
2. **Hitung Rekomendasi** – isi masa kerja, nilai kinerja, dan pendidikan, lalu klik *Hitung Rekomendasi Gaji*.
   Hasil tampil dalam Rupiah dengan kategori gaji, grafik fungsi keanggotaan, visualisasi inferensi, dan aturan yang aktif.
   Input tidak valid (mis. masa kerja negatif, kinerja di luar 0–100) ditolak dengan pesan yang jelas.
3. **Dataset Karyawan** – melihat/menyaring tabel `karyawan` dari basis data; tersedia tombol unduh basis data (.db).
4. **Riwayat & Ekspor** – riwayat perhitungan disimpan permanen pada tabel `riwayat_perhitungan` (tetap ada setelah aplikasi ditutup); dapat dihapus atau basis datanya diunduh.
5. **Tentang Sistem** – variabel, fungsi keanggotaan, dan 27 aturan fuzzy.

## Basis data (SQLite)

Berkas `gaji_karyawan.db` berisi tiga tabel:

| Tabel | Isi |
|---|---|
| `karyawan` | 40 karyawan simulasi + `gaji_aktual` + `gaji_prediksi_fuzzy` (dengan batasan CHECK pada rentang nilai dan pendidikan) |
| `riwayat_perhitungan` | Riwayat perhitungan dari aplikasi (waktu, input, gaji rekomendasi, kategori) |
| `hasil_blackbox` | Hasil 23 skenario pengujian Black-Box |

Jika berkas `.db` tidak ada, aplikasi membuatnya otomatis dan mengisi data awal. Untuk membuat ulang secara manual:
`python database.py`. Lokasi berkas dapat diganti lewat variabel lingkungan `GAJI_DB_PATH`. Contoh membuka dengan CLI:
`sqlite3 gaji_karyawan.db "SELECT pendidikan, COUNT(*), AVG(gaji_aktual) FROM karyawan GROUP BY pendidikan;"`

## Menjalankan evaluasi di Google Colab

1. Unggah `notebook/evaluasi_dataset.ipynb` ke Google Colab (File → Upload notebook).
2. Pilih *Runtime → Run all*. Notebook memasang `scikit-fuzzy`, membuat dataset, menghitung MAE/RMSE, menyimpan grafik, dan menyimpan dataset ke `gaji_karyawan.db` (SQLite).

## Memakai mesin fuzzy tanpa Streamlit

```python
import fuzzy_logic as fl
hasil = fl.proses_input(masa_kerja=8, kinerja=78, pendidikan="S1")
if hasil["valid"]:
    h = hasil["hasil"]
    print(h.gaji_format, h.kategori)      # Rp10.951.510 Sedang
else:
    print(hasil["pesan"])
```

## Ringkasan hasil evaluasi (dataset simulasi 40 karyawan)

| Metrik | Nilai |
|---|---|
| MAE | Rp1.777.812 |
| RMSE | Rp2.108.631 |
| Pengujian Black-Box (versi akhir) | 23 dari 23 skenario lulus |

## Keterbatasan

- Data pada basis data adalah simulasi; gaji aktual dibangkitkan dari skema hipotetis dan bukan data perusahaan nyata.
- Basis aturan dirancang dari pengetahuan pakar (bukan hasil pelatihan) dan sudah dikalibrasi satu kali pada dataset yang sama
  (evaluasi *in-sample*), sehingga nilai MAE/RMSE tidak boleh dianggap sebagai performa pada data baru.
- Aplikasi Streamlit diuji secara otomatis dengan modul `streamlit` tiruan di lingkungan tanpa internet; jalankan langsung
  dengan `streamlit run app.py` untuk memastikan tampilan pada komputer Anda.
