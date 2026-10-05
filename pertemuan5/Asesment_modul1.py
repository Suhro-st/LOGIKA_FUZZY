import os
import matplotlib.pyplot as plt
import numpy as np

# =====================================================================
# ASESMEN MODUL 1: PEMODELAN FUZZY
# Sistem Rekomendasi Beban SKS Mahasiswa
# Nama : Ahmad Suhrowardi
# NIM  : 240306019
# =====================================================================

def trimf(x, params):
  """Fungsi keanggotaan segitiga (a, b, c)."""
  a, b, c = params
  x = np.asarray(x, dtype=float)
  y = np.zeros_like(x)

  if b > a:
    idx1 = (x >= a) & (x <= b)
    y[idx1] = (x[idx1] - a) / (b - a)
  if c > b:
    idx2 = (x >= b) & (x <= c)
    y[idx2] = np.maximum(y[idx2], (c - x[idx2]) / (c - b))

  y[x == b] = 1.0
  return np.clip(y, 0.0, 1.0)

def trapmf(x, params):
  """Fungsi keanggotaan trapesium (a, b, c, d)."""
  a, b, c, d = params
  x = np.asarray(x, dtype=float)
  y = np.zeros_like(x)

  if a == b:
    y[x <= c] = 1.0
  else:
    idx1 = (x >= a) & (x <= b)
    y[idx1] = (x[idx1] - a) / (b - a)

  y[(x >= b) & (x <= c)] = 1.0

  if c == d:
    y[x >= b] = 1.0
  else:
    idx2 = (x >= c) & (x <= d)
    y[idx2] = np.maximum(y[idx2], (d - x[idx2]) / (d - c))

  return np.clip(y, 0.0, 1.0)

# Dictionary Model Fuzzy
MODEL_FUZZY = {
    'IPK': {
        'unit': 'Skala',
        'semesta': (0.0, 4.0),
        'membership': {
            'Rendah': ('trapmf', (0.0, 0.0, 2.0, 2.75)),
            'Sedang': ('trimf', (2.5, 3.0, 3.5)),
            'Tinggi': ('trapmf', (3.25, 3.75, 4.0, 4.0)),
        },
    },
    'Aktivitas': {
        'unit': 'Jam/Minggu',
        'semesta': (0, 40),
        'membership': {
            'Lengang': ('trapmf', (0, 0, 8, 16)),
            'Moderat': ('trimf', (12, 20, 28)),
            'Padat': ('trapmf', (24, 32, 40, 40)),
        },
    },
    'Rekomendasi SKS': {
        'unit': 'SKS',
        'semesta': (12, 24),
        'membership': {
            'Minimal': ('trapmf', (12, 12, 14, 17)),
            'Sedang': ('trimf', (15, 18, 21)),
            'Maksimal': ('trapmf', (19, 22, 24, 24)),
        },
    },
}

def hitung_derajat(tipe_kurva, params, nilai):
  val_arr = np.array([float(nilai)])
  if tipe_kurva == 'trimf':
    return float(trimf(val_arr, params)[0])
  elif tipe_kurva == 'trapmf':
    return float(trapmf(val_arr, params)[0])
  return 0.0

def fuzzifikasi(input_dict):
  """Fungsi pemetaan nilai masukan konkret ke derajat keanggotaan."""
  hasil = {}
  for var_name, nilai in input_dict.items():
    if var_name in MODEL_FUZZY:
      hasil[var_name] = {}
      for label, (tipe_kurva, params) in MODEL_FUZZY[var_name][
          'membership'
      ].items():
        deg = hitung_derajat(tipe_kurva, params, nilai)
        hasil[var_name][label] = round(deg, 4)
  return hasil

def plot_variabel(output_dir='.'):
  """Menyimpan dan MENAMPILKAN grafik fungsi keanggotaan."""
  os.makedirs(output_dir, exist_ok=True)
  for var_name, var_info in MODEL_FUZZY.items():
    x_min, x_max = var_info['semesta']
    x = np.linspace(x_min, x_max, 500)

    plt.figure(figsize=(8, 4), dpi=100)
    for label, (tipe_kurva, params) in var_info['membership'].items():
      if tipe_kurva == 'trimf':
        y = trimf(x, params)
      elif tipe_kurva == 'trapmf':
        y = trapmf(x, params)
      plt.plot(x, y, linewidth=2, label=label)

    plt.title(f'Fungsi Keanggotaan Variabel: {var_name}')
    plt.xlabel(f"{var_name} ({var_info['unit']})")
    plt.ylabel('Derajat Keanggotaan (μ)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()

    filename = os.path.join(output_dir, f"MF_{var_name.replace(' ', '_')}.png")
    plt.savefig(filename, bbox_inches='tight')

    # Menampilkan grafik langsung ke layar
    plt.show()

# Menjalankan fungsi untuk menampilkan grafik dan pengujian
if __name__ == '__main__':
  print('=== MENAMPILKAN GRAFIK FUNGSI KEANGGOTAAN ===')
  plot_variabel()

  print('\n=== CONTOH PENGUJJIAN FUZZIFIKASI ===')
  sampel_input = {'IPK': 3.40, 'Aktivitas': 26.0}
  hasil_fuzzifikasi = fuzzifikasi(sampel_input)
  print(f'Input: {sampel_input}')
  print(f'Hasil Fuzzifikasi: {hasil_fuzzifikasi}')
