-- 02_clean.sql
-- Membuat dim_location (zona iklim, dibuat manual) dan weather_clean.
-- weather_clean TIDAK mengubah nilai asli. Ia hanya memilih kolom, menambah kolom turunan
-- (tahun, bulan, musim, penanda kosong) dan kolom angka 0/1 untuk RainToday/RainTomorrow.
-- Tidak ada imputasi di sini. Imputasi hanya terjadi di skenario uji sensitivitas (project/code/2-analysis/python/05_sensitivity.py).

CREATE OR REPLACE TABLE dim_location AS
SELECT * FROM read_csv('data/reference/dim_location.csv', header = true);

CREATE OR REPLACE TABLE weather_clean AS
SELECT
    w.Date,
    w.Location,
    d.climate_zone,
    year(w.Date)  AS year,
    month(w.Date) AS month,
    -- musim belahan bumi selatan (usulan awal di project/docs/definitions.md)
    CASE
        WHEN month(w.Date) IN (12, 1, 2) THEN 'Summer'
        WHEN month(w.Date) IN (3, 4, 5)  THEN 'Autumn'
        WHEN month(w.Date) IN (6, 7, 8)  THEN 'Winter'
        ELSE 'Spring'
    END AS season,
    -- musim basah/kering hanya untuk zona Tropis utara
    CASE
        WHEN d.climate_zone <> 'Tropis utara' THEN NULL
        WHEN month(w.Date) IN (11, 12, 1, 2, 3, 4) THEN 'Basah'
        ELSE 'Kering'
    END AS wet_dry,
    w.Rainfall,
    w.Humidity9am, w.Humidity3pm,
    w.Pressure9am, w.Pressure3pm,
    w.Sunshine,
    w.Cloud9am, w.Cloud3pm,
    w.WindGustDir, w.WindGustSpeed,
    w.RainToday,
    w.RainTomorrow,
    CASE w.RainToday    WHEN 'Yes' THEN 1 WHEN 'No' THEN 0 END AS rain_today_i,
    CASE w.RainTomorrow WHEN 'Yes' THEN 1 WHEN 'No' THEN 0 END AS rain_tomorrow_i,
    w.RainToday    IS NOT NULL AS has_today,
    w.RainTomorrow IS NOT NULL AS has_target,
    w.Humidity3pm IS NULL AS miss_humidity3pm,
    w.Pressure3pm IS NULL AS miss_pressure3pm,
    w.Sunshine    IS NULL AS miss_sunshine,
    w.Cloud3pm    IS NULL AS miss_cloud3pm
FROM weather_raw w
LEFT JOIN dim_location d USING (Location);
