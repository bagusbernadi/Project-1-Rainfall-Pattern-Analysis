# Data

Dataset: **Rain in Australia** (weatherAUS.csv), Kaggle, v2 (145.460 baris, 23 kolom).
Sumber: https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package

## Cara memakai
1. Unduh `weatherAUS.csv` dari Kaggle.
2. Simpan di `project/data/raw/weatherAUS.csv`. Folder `project/data/raw/` ada di `.gitignore` (file mentah tidak di-commit).
3. Jalankan pipeline (lihat README utama).

## Yang perlu dicek sebelum publikasi
- Lisensi dan ketentuan kutipan dataset (cek halaman Kaggle). Belum diverifikasi dalam project ini.
- Data asli berasal dari Biro Meteorologi Australia (observasi harian). Cantumkan atribusi sesuai ketentuan.

## File di folder ini
- `reference/dim_location.csv`: zona iklim per lokasi, **dibuat manual** (subjektif, lihat `project/docs/definitions.md`).
