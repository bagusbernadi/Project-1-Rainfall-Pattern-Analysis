[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 1: Rainfall Pattern Analysis (weatherAUS, tanpa ML)

**Status: Design (rancangan).** Halaman rancangan ada di [`index.html`](index.html). Analisis, dashboard, dan angka hasil belum dikerjakan, sehingga bagian Analysis, Recommendation, dan Impact di bawah masih kosong.

**Tujuan:** membangun analisis deskriptif (tanpa machine learning) yang menunjukkan kapan dan di lokasi mana hujan paling sering terjadi, serta kondisi cuaca apa yang mendahului hujan keesokan harinya, lengkap dengan catatan keputusan untuk data kosong, sehingga dapat disusun aturan praktis sederhana dan jadwal kegiatan luar ruang.

| | |
|---|---|
| Kategori | Cuaca / lingkungan |
| Tingkat | Mudah |
| Data | Dataset publik weatherAUS ("Rain in Australia", Kaggle) |
| Tools | DuckDB + SQL, Python (pandas), dashboard HTML. Looker Studio opsional |

## 1. Problem

**Pertanyaan utama:** Kapan (musim atau bulan) dan di lokasi mana hujan paling sering terjadi, dan kondisi cuaca apa yang paling terkait dengan hujan keesokan harinya?

Rancangan memecahnya menjadi 15 pertanyaan (10 Utama, 4 Pendukung, 1 Tambahan) dalam 6 tema: pola waktu, lokasi, kondisi cuaca, hari ini dan besok, penerapan, serta data kosong dan validitas. Daftar lengkap ada di bagian 2 halaman rancangan.

## 2. Data

- Sumber: dataset weatherAUS di Kaggle, pengamatan cuaca harian dari Bureau of Meteorology Australia.
- Link dataset: [here](https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package) (Versi: 2, Tanggal akses: 23 Oktober 2026).
- Ukuran (perkiraan, **belum diverifikasi**): ±145 ribu baris, ±49 lokasi, 23 kolom, periode sekitar 2007 sampai 2017. Angka ini dicek saat data diunduh.
- Lisensi dan sitasi: dicek di halaman dataset sebelum project dipublikasikan.
- Data mentah tidak di-commit ke repository. Cara mengunduhnya akan ditulis di `data/README.md`.
- Rencana tabel: `weather_raw`, `weather_clean`, `dim_location`, `missing_audit`.
- Perlakuan nilai kosong (usulan awal): dibandingkan dua skenario, baris kosong dibuang (dropna) dan diisi median per lokasi dan bulan. Keputusan final dicatat setelah audit.

## 3. Analysis

Belum dikerjakan. Rencana langkah (12 langkah, tahap A sampai D) ada di bagian 6 halaman rancangan. Semua angka nanti dihitung dari data dengan SQL dan dicek silang dengan pandas.

## 4. Recommendation

Belum dikerjakan. Output yang direncanakan: aturan praktis berbasis ambang Humidity3pm yang dibandingkan dengan baseline "selalu tidak hujan", dan jadwal kegiatan luar ruang per lokasi.

## 5. Impact

Belum dikerjakan. Ketepatan aturan praktis akan dilaporkan dengan label `estimated`. Angka pada simulasi di halaman rancangan adalah angka contoh dan bukan hasil dari data weatherAUS.

## Batasan yang sudah diketahui

- Pola belum tentu penyebab. Analisis ini tidak menguji sebab-akibat.
- Akurasi bisa menyesatkan karena hari hujan jauh lebih sedikit daripada hari tidak hujan, jadi dibaca bersama recall dan proporsi hari bertanda peringatan.
- Hari-hari berdekatan saling terkait, sehingga baris data tidak sepenuhnya independen.
- Periode dan kolom terisi bisa berbeda antar lokasi, dan data berakhir sekitar 2017.

## Struktur repository

```
index.html   Halaman rancangan project (bisa dibuka di browser atau lewat GitHub Pages)
README.md    Dokumen ini
src/         Sumber halaman: body.html, script.js, template.html, build.py
```

Untuk membangun ulang `index.html` setelah mengubah `src/body.html` atau `src/script.js`: `cd src && python3 -I build.py`.

Folder `sql/`, `scripts/`, `dashboard/`, dan `outputs/` ditambahkan saat pengerjaan dimulai.
