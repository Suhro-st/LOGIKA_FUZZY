import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import pandas as pd

import fuzzy_logic as fl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def path_db():
    """Lokasi berkas basis data (dapat diubah lewat variabel lingkungan GAJI_DB_PATH)."""
    return os.environ.get("GAJI_DB_PATH") or os.path.join(BASE_DIR, "gaji_karyawan.db")


SKEMA = """
CREATE TABLE IF NOT EXISTS karyawan (
    id_karyawan         TEXT PRIMARY KEY,
    nama_karyawan       TEXT NOT NULL,
    masa_kerja          REAL NOT NULL CHECK (masa_kerja BETWEEN 0 AND 30),
    nilai_kinerja       REAL NOT NULL CHECK (nilai_kinerja BETWEEN 0 AND 100),
    pendidikan          TEXT NOT NULL CHECK (pendidikan IN ('SMA', 'D3', 'S1', 'S2')),
    gaji_aktual         INTEGER NOT NULL CHECK (gaji_aktual > 0),
    gaji_prediksi_fuzzy INTEGER
);
CREATE TABLE IF NOT EXISTS riwayat_perhitungan (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu            TEXT    NOT NULL,
    masa_kerja       REAL    NOT NULL,
    nilai_kinerja    REAL    NOT NULL,
    pendidikan       TEXT    NOT NULL,
    gaji_rekomendasi INTEGER NOT NULL,
    kategori         TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS hasil_blackbox (
    no                 INTEGER PRIMARY KEY,
    skenario           TEXT NOT NULL,
    input              TEXT NOT NULL,
    hasil_diharapkan   TEXT NOT NULL,
    hasil_aktual       TEXT NOT NULL,
    status             TEXT NOT NULL,
    hasil_versi_awal   TEXT,
    status_versi_awal  TEXT
);
"""

# (id, nama, masa_kerja, nilai_kinerja, pendidikan, gaji_aktual) - data simulasi
DATA_AWAL = [
    ("K001", "Andi Pratama", 17.0, 65, "S1", 10350000),
    ("K002", "Siti Rahmawati", 6.5, 91, "D3", 8250000),
    ("K003", "Budi Santoso", 26.5, 68, "S1", 13400000),
    ("K004", "Dewi Lestari", 25.5, 72, "S2", 14650000),
    ("K005", "Rizky Ramadhan", 9.0, 79, "S1", 8500000),
    ("K006", "Putri Anggraini", 7.0, 91, "D3", 8250000),
    ("K007", "Agus Setiawan", 5.5, 98, "D3", 7400000),
    ("K008", "Nur Hidayati", 17.5, 98, "S1", 13200000),
    ("K009", "Fajar Nugroho", 13.5, 70, "SMA", 8100000),
    ("K010", "Maya Sari", 12.0, 77, "S1", 9400000),
    ("K011", "Hendra Wijaya", 15.0, 90, "SMA", 8650000),
    ("K012", "Lina Marlina", 27.5, 67, "SMA", 10550000),
    ("K013", "Yoga Permana", 20.5, 68, "S1", 12150000),
    ("K014", "Rina Oktaviani", 12.0, 80, "D3", 7900000),
    ("K015", "Dimas Prasetyo", 25.0, 60, "SMA", 9650000),
    ("K016", "Wulan Dari", 26.5, 71, "S2", 15250000),
    ("K017", "Eko Susanto", 8.0, 75, "D3", 6900000),
    ("K018", "Intan Permata", 3.0, 75, "S1", 7950000),
    ("K019", "Rudi Hartono", 14.0, 78, "S1", 10450000),
    ("K020", "Ayu Kartika", 5.5, 65, "S2", 8150000),
    ("K021", "Bayu Saputra", 18.0, 68, "SMA", 9000000),
    ("K022", "Citra Dewanti", 25.5, 57, "SMA", 8950000),
    ("K023", "Doni Kurniawan", 23.0, 78, "S1", 13800000),
    ("K024", "Elsa Fitriani", 11.5, 80, "S1", 8950000),
    ("K025", "Ferry Gunawan", 17.0, 57, "S2", 11200000),
    ("K026", "Gita Pramesti", 9.5, 73, "S1", 9500000),
    ("K027", "Hadi Purnomo", 19.0, 77, "S1", 11800000),
    ("K028", "Indah Wahyuni", 1.5, 88, "S1", 6850000),
    ("K029", "Joko Widodo Putra", 7.0, 78, "D3", 6800000),
    ("K030", "Kartika Sari", 24.5, 94, "SMA", 11100000),
    ("K031", "Lukman Hakim", 9.0, 86, "D3", 8450000),
    ("K032", "Mega Safitri", 23.0, 72, "D3", 10750000),
    ("K033", "Naufal Akbar", 27.0, 84, "S1", 14850000),
    ("K034", "Okta Purnama", 25.0, 93, "S2", 15200000),
    ("K035", "Prima Aditya", 20.0, 57, "S1", 9950000),
    ("K036", "Qori Amalia", 19.5, 62, "SMA", 8400000),
    ("K037", "Reza Maulana", 3.5, 85, "S1", 8800000),
    ("K038", "Sari Handayani", 6.5, 52, "S1", 7600000),
    ("K039", "Tono Suryanto", 3.5, 78, "S2", 8850000),
    ("K040", "Umi Kulsum", 9.5, 93, "SMA", 8600000)
]

# Nama kolom DB -> nama kolom yang dipakai aplikasi/notebook
ALIAS_KARYAWAN = {"id_karyawan": "ID_Karyawan", "nama_karyawan": "Nama_Karyawan", "masa_kerja": "Masa_Kerja",
                  "nilai_kinerja": "Nilai_Kinerja", "pendidikan": "Pendidikan", "gaji_aktual": "Gaji_Aktual",
                  "gaji_prediksi_fuzzy": "Gaji_Prediksi_Fuzzy"}


@contextmanager
def koneksi(path=None):
    """Membuka koneksi SQLite, commit bila sukses, rollback bila gagal, dan selalu menutup koneksi."""
    con = sqlite3.connect(path or path_db())
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def isi_karyawan(con, ganti=False):
    """Mengisi tabel karyawan dari DATA_AWAL (beserta gaji prediksi dari mesin fuzzy)."""
    if ganti:
        con.execute("DELETE FROM karyawan")
    baris = [(i, n, m, k, p, g, int(round(fl.hitung_gaji(m, k, p).gaji_rp))) for i, n, m, k, p, g in DATA_AWAL]
    con.executemany("INSERT INTO karyawan VALUES (?, ?, ?, ?, ?, ?, ?)", baris)


def inisialisasi(path=None):
    """Membuat berkas/tabel bila belum ada dan mengisi data awal bila tabel karyawan masih kosong."""
    with koneksi(path) as con:
        con.executescript(SKEMA)
        if con.execute("SELECT COUNT(*) FROM karyawan").fetchone()[0] == 0:
            isi_karyawan(con)


def ambil_karyawan(path=None):
    """Seluruh data karyawan sebagai DataFrame (kolom: ID_Karyawan, Nama_Karyawan, ...)."""
    with koneksi(path) as con:
        df = pd.read_sql_query("SELECT * FROM karyawan ORDER BY id_karyawan", con)
    return df.rename(columns=ALIAS_KARYAWAN)


def tambah_riwayat(masa, kinerja, pendidikan, gaji_rp, kategori, path=None):
    with koneksi(path) as con:
        con.execute("INSERT INTO riwayat_perhitungan (waktu, masa_kerja, nilai_kinerja, pendidikan, gaji_rekomendasi, kategori) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), float(masa), float(kinerja), pendidikan, int(round(gaji_rp)), kategori))


def ambil_riwayat(path=None):
    with koneksi(path) as con:
        return pd.read_sql_query("SELECT id AS No, waktu AS Waktu, masa_kerja AS Masa_Kerja, nilai_kinerja AS Nilai_Kinerja, "
                                 "pendidikan AS Pendidikan, gaji_rekomendasi AS Gaji_Rekomendasi, kategori AS Kategori "
                                 "FROM riwayat_perhitungan ORDER BY id DESC", con)


def hapus_riwayat(path=None):
    with koneksi(path) as con:
        con.execute("DELETE FROM riwayat_perhitungan")


def simpan_blackbox(baris, path=None):
    """baris: list dict dengan kunci No, Skenario_Pengujian, Input, Hasil_Diharapkan, Hasil_Aktual, Status,
    Hasil_Aktual_Versi_Awal, Status_Versi_Awal."""
    with koneksi(path) as con:
        con.execute("DELETE FROM hasil_blackbox")
        con.executemany("INSERT INTO hasil_blackbox VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        [(r["No"], r["Skenario_Pengujian"], r["Input"], r["Hasil_Diharapkan"], r["Hasil_Aktual"], r["Status"],
                          r["Hasil_Aktual_Versi_Awal"], r["Status_Versi_Awal"]) for r in baris])


def ambil_blackbox(path=None):
    with koneksi(path) as con:
        return pd.read_sql_query("SELECT * FROM hasil_blackbox ORDER BY no", con)


def baca_bytes(path=None):
    """Isi berkas basis data (untuk tombol unduh)."""
    with open(path or path_db(), "rb") as f:
        return f.read()


if __name__ == "__main__":
    inisialisasi()
    with koneksi() as con:
        n = con.execute("SELECT COUNT(*) FROM karyawan").fetchone()[0]
    print(f"Basis data siap: {path_db()} ({n} karyawan)")
