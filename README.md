[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 1: Rainfall Pattern Analysis (weatherAUS, tanpa ML)

**Status: Selesai (laporan versi 2).** Rancangan dan laporan (7 bagian: data, business question, kesesuaian dataset/tools/alur, project output, kesimpulan) ada di [`design-and-report/index.html`](design-and-report/index.html), tab *Design Project* dan *Report Project*. Dashboard interaktif: [`project/results/3-presentation/dashboard.html`](project/results/3-presentation/dashboard.html).

**Tujuan:** membangun analisis deskriptif (tanpa machine learning) yang menunjukkan kapan dan di lokasi mana hujan paling sering terjadi, serta kondisi cuaca apa yang mendahului hujan keesokan harinya, lengkap dengan catatan keputusan untuk data kosong, sehingga dapat disusun aturan praktis sederhana dan jadwal kegiatan luar ruang.

| | |
|---|---|
| Kategori | Cuaca / lingkungan |
| Tingkat | Mudah |
| Data | Dataset publik weatherAUS ("Rain in Australia", Kaggle) |
| Tools | DuckDB + SQL, Python (pandas), dashboard HTML. Looker Studio tidak dibuat |

## 1. Problem
Kapan dan di mana hujan paling sering terjadi, kondisi cuaca apa yang biasanya mendahului hujan, dan seberapa jauh aturan sederhana (Humidity3pm) bisa dipakai memberi peringatan hujan besok.

## 2. Data
Kaggle "Rain in Australia" (weatherAUS), 145.460 baris, 23 kolom, 49 lokasi, 2007-11-01 sampai 2017-06-25. Hari hujan = `RainToday = Yes` (Rainfall > 1,0 mm). Cara memperoleh data dan catatan lisensi (tidak ada lisensi terbuka eksplisit; hak cipta Bureau of Meteorology): `project/data/README.md`. File mentah tidak di-commit.

## 3. Analysis
Pipeline: SQL (DuckDB) membuat tabel dan query, pandas menghitung ulang secara independen sebagai crosscheck, dashboard menghitung ulang KPI sesuai filter dari tabel hitungan.

Temuan utama (angka dari `project/results/`):
- **Frekuensi**: 22,42% hari hujan (142.199 hari terisi); rata-rata 10,27 mm per hari hujan.
- **Musim**: perbedaan musim sangat bergantung zona. Selisih musim terbasah-terkering: Tropis utara 41,0 poin (Summer 47,6% vs Winter 6,6%), Barat daya 34,8 poin (Winter 43,4% vs Summer 8,6%), Pedalaman kering hanya 2,2 poin.
- **Tren 2009-2016** (30 lokasi, panel seimbang): 19,8% sampai 24,2% per tahun, tanpa arah yang jelas dan tanpa uji signifikansi.
- **Frekuensi vs jumlah**: Portland paling sering hujan (36,5% hari) tetapi curahnya sedang; Cairns terbasah (perkiraan 2.097 mm/tahun, estimated) dengan 31,8% hari. Peringkat keduanya tidak sama (korelasi peringkat 0,67).
- **Sebelum hujan**: Humidity3pm rata-rata 68,8 vs 46,5 (selisih 22,3 poin), Pressure3pm 3,8 hPa lebih rendah, Cloud3pm lebih tinggi, Sunshine lebih rendah.
- **Peluang beruntun**: peluang hujan besok 46,4% jika hari ini hujan vs 15,2% jika tidak (rasio 3,06).
- **Aturan Humidity3pm >= 70** (estimated, in-sample): akurasi 81,0% vs baseline "selalu tidak hujan" 77,7% (+3,3 poin), recall 51,1%, peringatan pada 19,5% hari.

## 4. Recommendation
- Gunakan frekuensi hari hujan per lokasi x bulan (dashboard, bagian Jadwal kegiatan) untuk memilih bulan kegiatan luar ruang; bacalah sebagai gambaran historis 2007-2017, bukan prakiraan.
- Humidity3pm tinggi dan hari ini hujan adalah dua sinyal sederhana yang paling jelas; jangan menilai aturan dari akurasi saja karena baseline sudah 77,7%.

## 5. Impact
Memberi dasar angka yang bisa dicek ulang untuk menjadwalkan kegiatan dan memahami batas aturan sederhana. Dampak nyata belum diukur (tidak ada data uji terpisah atau penerapan).

## Keputusan nilai kosong
Nilai asli tidak diubah dan target tidak pernah diimputasi. Kolom dipakai pada baris terisi; lokasi yang tidak mencatat Sunshine (19 lokasi) atau Cloud3pm (12 lokasi) dikeluarkan dari analisis kolom itu. Imputasi median Location x bulan hanya sebagai uji sensitivitas: selisih Humidity3pm dan Pressure3pm berubah < 2%, sedangkan Sunshine (+12,4%) dan Cloud3pm (-16,8%) melewati ambang 10% dan perlu dicermati. Rincian: `project/docs/missing_value_decisions.md`.

## Batasan
- Zona iklim dibuat manual (subjektif), NorfolkIsland pendekatan.
- Evaluasi aturan in-sample (tanpa data uji), semua ketepatan berlabel estimated.
- Sunshine/Cloud3pm hanya mewakili lokasi yang mencatat.
- Tren hanya deskriptif, 8 tahun, tanpa uji signifikansi.
- Kekosongan Humidity3pm/angin berkaitan dengan target (+4 poin) sehingga tidak sepenuhnya acak.
- Looker Studio dan one-pager tidak dibuat.

## Menjalankan
Semua perintah dari folder `project/`. Skrip membaca dan menulis dengan jalur relatif, jadi bisa dijalankan dari mana saja.
```
cd project
pip install -r requirements.txt
# taruh weatherAUS.csv di data/raw/ (lihat data/README.md di folder project)
python code/1-data-preparation/python/01_profile_audit.py   # profiling, missing audit
python code/1-data-preparation/python/02_build_tables.py    # weather.duckdb (SQL 01-02)
python code/2-analysis/python/03_run_queries.py             # SQL 03-06 -> results/2-analysis/*.csv
python code/2-analysis/python/04_crosscheck.py              # SQL vs pandas (harus semua PASS)
python code/2-analysis/python/05_sensitivity.py             # uji sensitivitas
python code/3-presentation/python/06_build_dashboard.py     # results/3-presentation/dashboard.html
python code/3-presentation/python/07_build_notebook.py
jupyter nbconvert --to notebook --execute --inplace results/3-presentation/analysis.ipynb
```
Catatan: nama skrip berbeda dari rancangan awal (`03_run_queries`, `04_crosscheck`, `05_sensitivity`, `06_build_dashboard`, `06_kpi.sql`, `dashboard_template.html`). Rinciannya ada di tab *Report Project*.

## Struktur repository
Kode dan hasil dipisah, dan keduanya mengikuti tahap yang sama (1 data-preparation, 2 analysis, 3 presentation). Di dalam `code/` dipisah lagi per tool.
```
README.md                      ringkasan project (file ini)
index.html                     pengalihan ke design-and-report/ (agar URL GitHub Pages tetap sama)
design-and-report/
  index.html                   halaman Design Project dan Report Project
  src/                         sumber halaman
project/
  code/                        PROGRAM
    common.py                  jalur dan konstanta bersama
    1-data-preparation/        python/ (01, 02)   sql/ (01_load, 02_clean)
    2-analysis/                python/ (03, 04, 05)   sql/ (03-06)
    3-presentation/            python/ (06, 07)   html/ (dashboard_template)
  results/                     HASIL ANALISIS
    1-data-preparation/        csv profiling dan audit nilai kosong
    2-analysis/                csv hasil query, crosscheck, sensitivitas
    3-presentation/            dashboard.html, analysis.ipynb
  data/                        raw/ (tidak di-commit), reference/dim_location.csv, README.md
  docs/                        definisi, kamus data, keputusan nilai kosong, ringkasan profiling
  requirements.txt
```
