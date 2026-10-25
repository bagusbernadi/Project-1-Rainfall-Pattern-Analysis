-- 04_conditions.sql  (Q6-Q10)
-- Perbandingan kondisi cuaca hari ini antara kelompok RainTomorrow = Yes dan No.
-- Hanya baris dengan RainTomorrow terisi (has_target) DAN variabel terisi. Tidak ada imputasi.

CREATE OR REPLACE TABLE q6_q8_long AS
SELECT Location, season, climate_zone, rain_tomorrow_i, 'Humidity3pm' AS variable, Humidity3pm AS val
FROM weather_clean WHERE has_target AND Humidity3pm IS NOT NULL
UNION ALL
SELECT Location, season, climate_zone, rain_tomorrow_i, 'Pressure3pm', Pressure3pm
FROM weather_clean WHERE has_target AND Pressure3pm IS NOT NULL
UNION ALL
SELECT Location, season, climate_zone, rain_tomorrow_i, 'Sunshine', Sunshine
FROM weather_clean WHERE has_target AND Sunshine IS NOT NULL
UNION ALL
SELECT Location, season, climate_zone, rain_tomorrow_i, 'Cloud3pm', Cloud3pm
FROM weather_clean WHERE has_target AND Cloud3pm IS NOT NULL;

-- sebaran per kelompok (semua lokasi)
CREATE OR REPLACE TABLE q6_q8_conditions AS
SELECT variable,
       CASE rain_tomorrow_i WHEN 1 THEN 'Yes' ELSE 'No' END AS rain_tomorrow,
       count(*)                          AS n,
       count(DISTINCT Location)          AS n_locations,
       round(avg(val), 3)                AS mean,
       round(quantile_cont(val, 0.25), 3) AS p25,
       round(quantile_cont(val, 0.50), 3) AS median,
       round(quantile_cont(val, 0.75), 3) AS p75
FROM q6_q8_long
GROUP BY variable, rain_tomorrow_i;

-- selisih rata-rata (Yes - No) per variabel
CREATE OR REPLACE TABLE q6_q8_diff AS
SELECT variable,
       max(CASE WHEN rain_tomorrow_i = 1 THEN n END)    AS n_yes,
       max(CASE WHEN rain_tomorrow_i = 0 THEN n END)    AS n_no,
       round(max(CASE WHEN rain_tomorrow_i = 1 THEN m END), 3) AS mean_yes,
       round(max(CASE WHEN rain_tomorrow_i = 0 THEN m END), 3) AS mean_no,
       round(max(CASE WHEN rain_tomorrow_i = 1 THEN m END)
           - max(CASE WHEN rain_tomorrow_i = 0 THEN m END), 3) AS diff_yes_minus_no
FROM (SELECT variable, rain_tomorrow_i, count(*) AS n, avg(val) AS m
      FROM q6_q8_long GROUP BY variable, rain_tomorrow_i)
GROUP BY variable;

-- jumlah dan total per lokasi x musim x kelompok (agar dashboard bisa menghitung ulang rata-rata sesuai filter)
CREATE OR REPLACE TABLE q6_q8_by_loc_season AS
SELECT Location, season, variable, rain_tomorrow_i,
       count(*)            AS n,
       round(sum(val), 3)  AS sum_val
FROM q6_q8_long
GROUP BY Location, season, variable, rain_tomorrow_i;

-- Q9 (tambahan): arah dan kecepatan hembusan angin
CREATE OR REPLACE TABLE q9_wind_dir AS
SELECT WindGustDir,
       count(*)                                              AS n,
       sum(rain_tomorrow_i)                                  AS rain_tomorrow_days,
       round(100.0 * sum(rain_tomorrow_i) / count(*), 2)     AS pct_rain_tomorrow
FROM weather_clean
WHERE has_target AND WindGustDir IS NOT NULL
GROUP BY WindGustDir;

CREATE OR REPLACE TABLE q9_wind_speed AS
SELECT CASE WHEN WindGustSpeed < 30 THEN '1: < 30'
            WHEN WindGustSpeed < 40 THEN '2: 30-39'
            WHEN WindGustSpeed < 50 THEN '3: 40-49'
            WHEN WindGustSpeed < 60 THEN '4: 50-59'
            ELSE '5: >= 60' END                               AS gust_kmh_bin,
       count(*)                                              AS n,
       sum(rain_tomorrow_i)                                  AS rain_tomorrow_days,
       round(100.0 * sum(rain_tomorrow_i) / count(*), 2)     AS pct_rain_tomorrow
FROM weather_clean
WHERE has_target AND WindGustSpeed IS NOT NULL
GROUP BY 1;

-- Q10: peluang hujan besok menurut RainToday. Butuh RainToday DAN RainTomorrow terisi.
CREATE OR REPLACE TABLE q10_persistence_counts AS
SELECT Location, season,
       count(*) FILTER (WHERE rain_today_i = 1)                          AS today_yes_n,
       count(*) FILTER (WHERE rain_today_i = 1 AND rain_tomorrow_i = 1)  AS tomorrow_yes_given_yes,
       count(*) FILTER (WHERE rain_today_i = 0)                          AS today_no_n,
       count(*) FILTER (WHERE rain_today_i = 0 AND rain_tomorrow_i = 1)  AS tomorrow_yes_given_no
FROM weather_clean
WHERE has_today AND has_target
GROUP BY Location, season;

CREATE OR REPLACE TABLE q10_persistence AS
WITH per_loc AS (
    SELECT Location,
           sum(today_yes_n) AS today_yes_n, sum(tomorrow_yes_given_yes) AS tomorrow_yes_given_yes,
           sum(today_no_n)  AS today_no_n,  sum(tomorrow_yes_given_no)  AS tomorrow_yes_given_no
    FROM q10_persistence_counts GROUP BY Location
    UNION ALL
    SELECT 'ALL',
           sum(today_yes_n), sum(tomorrow_yes_given_yes), sum(today_no_n), sum(tomorrow_yes_given_no)
    FROM q10_persistence_counts
)
SELECT Location, today_yes_n, tomorrow_yes_given_yes, today_no_n, tomorrow_yes_given_no,
       round(100.0 * tomorrow_yes_given_yes / today_yes_n, 2)  AS p_rain_tomorrow_if_rain_today,
       round(100.0 * tomorrow_yes_given_no  / today_no_n, 2)   AS p_rain_tomorrow_if_dry_today,
       round((1.0 * tomorrow_yes_given_yes / today_yes_n) / (1.0 * tomorrow_yes_given_no / today_no_n), 3) AS ratio
FROM per_loc;
