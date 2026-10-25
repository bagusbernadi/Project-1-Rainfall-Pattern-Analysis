-- 06_kpi.sql
-- 5 ukuran kunci (KPI) untuk seluruh data. Rumus ada di project/docs/definitions.md.
-- Ambang aturan praktis untuk KPI 5 ditetapkan di muka: Humidity3pm >= 70 (bukan hasil memilih ambang terbaik).

CREATE OR REPLACE TABLE kpi_overall AS
SELECT 'K1' AS kpi_id, 'Frekuensi hari hujan (%)' AS kpi,
       round(100.0 * sum(rain_today_i) / count(*), 2) AS value, count(*) AS n
FROM weather_clean WHERE has_today
UNION ALL
SELECT 'K2', 'Curah rata-rata per hari hujan (mm)',
       round(avg(Rainfall), 2), count(*)
FROM weather_clean WHERE rain_today_i = 1 AND Rainfall IS NOT NULL
UNION ALL
SELECT 'K3', 'Selisih Humidity3pm: sebelum hujan - sebelum tidak hujan (poin %)',
       diff_yes_minus_no, n_yes + n_no
FROM q6_q8_diff WHERE variable = 'Humidity3pm'
UNION ALL
SELECT 'K4', 'Rasio peluang hujan besok (hari ini hujan / hari ini tidak)',
       ratio, today_yes_n + today_no_n
FROM q10_persistence WHERE Location = 'ALL'
UNION ALL
SELECT 'K5', 'Recall aturan Humidity3pm >= 70 (%)',
       recall, n_eval
FROM q11_rule_thresholds WHERE threshold = 70;
