# Data

Dataset: **Rain in Australia** (weatherAUS.csv), Kaggle, v2 (145.460 baris, 23 kolom).
Sumber: https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package

## Cara memakai
1. Unduh `weatherAUS.csv` dari Kaggle.
2. Simpan di `project/data/raw/weatherAUS.csv`. Folder `project/data/raw/` ada di `.gitignore` (file mentah tidak di-commit).
3. Jalankan pipeline (lihat README utama).

## Yang perlu dicek sebelum publikasi
- Lisensi (dicek 28 Oktober 2026): deskripsi dataset di Kaggle tidak menyatakan lisensi terbuka eksplisit. Hak cipta ada pada Bureau of Meteorology ("Copyright Commonwealth of Australia 2010, Bureau of Meteorology"). Ketentuan penggunaan ulang belum jelas, jadi anggap untuk penggunaan pribadi dan jangan publikasikan data mentahnya. Kolom License di sidebar Kaggle: "Other (specified in description)" (dicatat 28 Oktober 2026).
- Data asli berasal dari Bureau of Meteorology (observasi harian), dikompilasi oleh Graham Williams (Rattle) dan diunggah di Kaggle oleh Joe Young. Cantumkan atribusi ini saat mempublikasikan hasil.

## File di folder ini
- `reference/dim_location.csv`: zona iklim per lokasi, **dibuat manual** (subjektif, lihat `project/docs/definitions.md`).
