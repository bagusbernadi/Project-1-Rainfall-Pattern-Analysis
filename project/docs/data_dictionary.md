# Data dictionary

## Kolom weatherAUS dan pemakaiannya
| Kolom | Dipakai | Untuk |
|---|---|---|
| Date, Location | Ya | kunci, tahun/bulan/musim, lokasi |
| Rainfall | Ya | K2, curah per lokasi |
| RainToday | Ya | hari hujan (Q1-Q5, Q10, Q12) |
| RainTomorrow | Ya | target Q6-Q11 |
| Humidity3pm | Ya | Q6-Q8, aturan Q11 |
| Pressure3pm | Ya | Q6-Q8 |
| Sunshine, Cloud3pm | Ya | Q6-Q8 (hanya lokasi yang mencatat) |
| WindGustDir, WindGustSpeed | Ya | Q9 |
| MinTemp, MaxTemp, Evaporation, Humidity9am, Pressure9am, Cloud9am, Temp9am, Temp3pm, WindDir9am/3pm, WindSpeed9am/3pm | Tidak | tidak dibutuhkan Q1-Q15; tetap ada di `weather_raw` |

## Tabel DuckDB (`weather.duckdb`, dibuat ulang oleh pipeline)
- `weather_raw`: salinan CSV apa adanya ("NA" jadi NULL).
- `weather_clean`: kolom terpilih + `year`, `month`, `season`, `wet_dry`, `climate_zone`, `rain_today_i`, `rain_tomorrow_i` (0/1), `has_today`, `has_target`, `miss_humidity3pm/pressure3pm/sunshine/cloud3pm`. **Nilai asli tidak diubah, tidak ada imputasi.**
- `dim_location`: Location, climate_zone, hemisphere_note.
- `missing_audit`: per lokasi x kolom, persen kosong dan keputusan (`results/1-data-preparation/missing_audit.csv`, 1.029 baris).
- Tabel hasil query `q*`, `rule_*`, `kpi_overall` diekspor ke `results/2-analysis/*.csv`.
