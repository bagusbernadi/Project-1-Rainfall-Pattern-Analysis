-- 03_rain_frequency.sql  (Q1-Q5, Q12)
-- "Hari hujan" = RainToday = 'Yes' (bawaan dataset: Rainfall > 1,0 mm).
-- Penyebut = hari dengan RainToday terisi (has_today). Baris RainToday kosong tidak dihitung.
-- Persentase disimpan dengan 2 desimal (poin persen).

-- Q1: lokasi x bulan (dasar heatmap)
CREATE OR REPLACE TABLE q1_rain_by_month AS
SELECT Location, climate_zone, month,
       count(*)                                          AS n_obs,
       sum(rain_today_i)                                 AS rain_days,
       round(100.0 * sum(rain_today_i) / count(*), 2)    AS pct_rain
FROM weather_clean
WHERE has_today
GROUP BY Location, climate_zone, month;

-- Q2: lokasi x musim (dipakai juga untuk filter dashboard)
-- sum_mm_rain_days = total Rainfall (mm) pada hari hujan; dipakai menghitung ulang KPI K2 sesuai filter di dashboard.
CREATE OR REPLACE TABLE q2_rain_by_loc_season AS
SELECT Location, climate_zone, season,
       count(*)                                          AS n_obs,
       sum(rain_today_i)                                 AS rain_days,
       round(100.0 * sum(rain_today_i) / count(*), 2)    AS pct_rain,
       round(sum(Rainfall) FILTER (WHERE rain_today_i = 1), 3) AS sum_mm_rain_days
FROM weather_clean
WHERE has_today
GROUP BY Location, climate_zone, season;

-- Q2: zona iklim x musim (dihitung langsung dari weather_clean, bukan dari tabel di atas)
CREATE OR REPLACE TABLE q2_rain_by_zone_season AS
SELECT climate_zone, season,
       count(DISTINCT Location)                          AS n_locations,
       count(*)                                          AS n_obs,
       sum(rain_today_i)                                 AS rain_days,
       round(100.0 * sum(rain_today_i) / count(*), 2)    AS pct_rain
FROM weather_clean
WHERE has_today
GROUP BY climate_zone, season;

-- Q2: zona Tropis utara dibaca sebagai musim basah (Nov-Apr) dan kering (Mei-Okt)
CREATE OR REPLACE TABLE q2_tropical_wet_dry AS
SELECT Location, wet_dry,
       count(*)                                          AS n_obs,
       sum(rain_today_i)                                 AS rain_days,
       round(100.0 * sum(rain_today_i) / count(*), 2)    AS pct_rain
FROM weather_clean
WHERE has_today AND wet_dry IS NOT NULL
GROUP BY Location, wet_dry;

-- Q3: lokasi x tahun. Lokasi-tahun "lengkap" jika RainToday terisi pada >= 90% hari dalam tahun itu.
-- Tren dibaca hanya pada tahun 2009-2016 dan pada lokasi yang lengkap di KEDELAPAN tahun (panel seimbang),
-- supaya perubahan tidak berasal dari lokasi yang masuk/keluar.
CREATE OR REPLACE TABLE q3_rain_by_loc_year AS
SELECT Location, year,
       count(*)                                          AS n_obs,
       sum(rain_today_i)                                 AS rain_days,
       count(*) >= 0.9 * (CASE WHEN year % 4 = 0 THEN 366 ELSE 365 END) AS is_complete
FROM weather_clean
WHERE has_today
GROUP BY Location, year;

CREATE OR REPLACE TABLE q3_panel_locations AS
SELECT Location, TRUE AS in_panel
FROM q3_rain_by_loc_year
WHERE year BETWEEN 2009 AND 2016 AND is_complete
GROUP BY Location
HAVING count(*) = 8;

CREATE OR REPLACE TABLE q3_rain_trend AS
SELECT y.year,
       count(DISTINCT y.Location)                        AS n_locations,
       sum(y.n_obs)                                      AS n_obs,
       sum(y.rain_days)                                  AS rain_days,
       round(100.0 * sum(y.rain_days) / sum(y.n_obs), 2) AS pct_rain
FROM q3_rain_by_loc_year y
JOIN q3_panel_locations p USING (Location)
WHERE y.year BETWEEN 2009 AND 2016
GROUP BY y.year;

-- Q4 dan Q5: peringkat lokasi dan perbandingan frekuensi vs jumlah hujan
-- mean_mm_rain_day = rata-rata Rainfall pada hari hujan.
-- est_annual_mm    = total Rainfall / jumlah hari Rainfall terisi x 365,25 (perkiraan, label estimated).
CREATE OR REPLACE TABLE q4_q5_location AS
WITH base AS (
    SELECT Location, climate_zone,
           count(*) FILTER (WHERE has_today)                                       AS n_obs,
           sum(rain_today_i)                                                       AS rain_days,
           avg(Rainfall) FILTER (WHERE rain_today_i = 1)                           AS mean_mm_rain_day,
           sum(Rainfall) / count(Rainfall) * 365.25                                AS est_annual_mm
    FROM weather_clean
    GROUP BY Location, climate_zone
)
SELECT Location, climate_zone, n_obs, rain_days,
       round(100.0 * rain_days / n_obs, 2)  AS pct_rain,
       round(mean_mm_rain_day, 2)           AS mean_mm_rain_day,
       round(est_annual_mm, 0)              AS est_annual_mm,
       rank() OVER (ORDER BY 1.0 * rain_days / n_obs DESC) AS rank_pct_rain,
       rank() OVER (ORDER BY est_annual_mm DESC)           AS rank_annual_mm
FROM base;

-- Q12: jadwal kegiatan luar ruang = bulan dengan persentase hari hujan terendah per lokasi (estimated)
CREATE OR REPLACE TABLE q12_outdoor_schedule AS
SELECT Location, climate_zone, month, n_obs, pct_rain,
       rank() OVER (PARTITION BY Location ORDER BY pct_rain ASC,  month) AS rank_safest,
       rank() OVER (PARTITION BY Location ORDER BY pct_rain DESC, month) AS rank_rainiest
FROM q1_rain_by_month;
