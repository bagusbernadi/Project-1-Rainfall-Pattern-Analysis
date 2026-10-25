# Ringkasan profiling data mentah

Dihasilkan oleh `project/code/1-data-preparation/python/01_profile_audit.py`. Semua angka dihitung dari `project/data/raw/weatherAUS.csv`.

- Baris: **145,460** | Kolom: **23** | Lokasi: **49**
- Periode: **2007-11-01** sampai **2017-06-25**
- Duplikat kunci (Date, Location): **0**
- RainToday = Yes tepat jika Rainfall > 1,0 mm: **cocok** pada 142,199 baris terisi. Hari dengan Rainfall tepat 1,0 mm ada **1,759** dan semuanya 'No'.
- Lokasi yang baru mencatat sejak 2013: Katherine, Nhil, Uluru

## Kolom dengan nilai kosong terbanyak

| Kolom | Kosong (%) |
|---|---|
| Sunshine | 48.0 |
| Evaporation | 43.2 |
| Cloud3pm | 40.8 |
| Cloud9am | 38.4 |
| Pressure9am | 10.4 |
| Pressure3pm | 10.3 |
| WindDir9am | 7.3 |
| WindGustDir | 7.1 |

## Jumlah baris per tahun

| Tahun | Baris |
|---|---|
| 2007 | 61 |
| 2008 | 2,270 |
| 2009 | 16,789 |
| 2010 | 16,782 |
| 2011 | 15,407 |
| 2012 | 15,409 |
| 2013 | 16,415 |
| 2014 | 17,885 |
| 2015 | 17,885 |
| 2016 | 17,934 |
| 2017 | 8,623 |
