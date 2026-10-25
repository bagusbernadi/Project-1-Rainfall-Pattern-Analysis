# Keputusan nilai kosong

Prinsip: nilai asli tidak diubah; kolom target (RainToday, RainTomorrow, Rainfall) tidak pernah diimputasi; tidak ada pengisian dari lokasi lain (iklim antar lokasi berbeda).

## Keputusan per jenis kolom (`results/1-data-preparation/missing_audit.csv`)
| Kode | Arti | Jumlah baris audit |
|---|---|---|
| drop_rows | kolom target kosong: baris tidak dipakai pada analisis yang memerlukannya | 147 |
| complete_case | dipakai pada baris terisi | 225 |
| complete_case_report_n | idem, jumlah baris dan lokasi dilaporkan (Sunshine, Cloud3pm) | 30 |
| not_recorded | lokasi tidak mencatat kolom sama sekali: dikeluarkan dari analisis kolom itu | 39 |
| unused | kolom tidak dipakai | 588 |

## Kolom paling kosong
Sunshine 48,0%, Evaporation 43,2%, Cloud3pm 40,8%, Cloud9am 38,4%, Pressure9am 10,4%, Pressure3pm 10,3%.
Sunshine tidak dicatat sama sekali di 19 lokasi dan Cloud3pm di 12 lokasi, jadi analisisnya hanya mewakili lokasi yang mencatat (Sunshine 30 lokasi, Cloud3pm 37 lokasi).
Kosong Pressure3pm, WindGustDir, Humidity3pm terkonsentrasi: 73-88% dari kekosongan ada di 5 lokasi teratas.

## Apakah kosong berkaitan dengan target? (`missing_vs_target.csv`)
Selisih P(hujan besok) antara baris kosong vs terisi: Humidity3pm +4,40 poin, WindGustDir +4,31, WindGustSpeed +4,20, Cloud3pm -3,54, Sunshine -0,41, Pressure3pm -0,17. Kosongnya Humidity3pm dan angin tidak acak sepenuhnya; angka dibaca dengan hati-hati. Hanya deskriptif, tanpa uji.

## Uji sensitivitas Q14 (`results/2-analysis/sensitivity.csv`)
Pembanding: dropna vs imputasi median Location x bulan.
- Selisih Humidity3pm: 22,29 vs 21,92 (-1,6%); Pressure3pm: -3,81 vs -3,74 (+1,8%). Tidak perlu dicermati.
- Selisih Sunshine: -4,08 vs -3,57 (+12,4%) dan Cloud3pm: 2,44 vs 2,03 (-16,8%): melewati ambang 10%, **perlu dicermati**; arah tidak berubah.
- Aturan Humidity3pm >= 60/70/80: akurasi, recall, dan persen peringatan berubah kurang dari 3%; status "di atas baseline" tidak berubah (>= 70 dan >= 80 di atas baseline; >= 60 di bawah).
Ambang 10% adalah ambang buatan sendiri, bukan uji statistik.
