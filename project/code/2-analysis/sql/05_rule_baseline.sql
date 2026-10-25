-- 05_rule_baseline.sql  (Q11)
-- Aturan praktis: peringatan hujan jika Humidity3pm >= ambang. Ambang 40-90, kelipatan 5.
-- Dievaluasi terhadap RainTomorrow pada baris dengan Humidity3pm DAN RainTomorrow terisi.
-- Baseline "selalu tidak hujan" dievaluasi pada baris yang SAMA agar adil.
-- Evaluasi ini in-sample (tanpa data uji terpisah); ketepatan dilaporkan sebagai estimated.

CREATE OR REPLACE TABLE rule_counts_by_loc_season AS
SELECT w.Location, w.season, t.threshold,
       count(*) FILTER (WHERE w.Humidity3pm >= t.threshold AND w.rain_tomorrow_i = 1) AS tp,
       count(*) FILTER (WHERE w.Humidity3pm >= t.threshold AND w.rain_tomorrow_i = 0) AS fp,
       count(*) FILTER (WHERE w.Humidity3pm <  t.threshold AND w.rain_tomorrow_i = 1) AS fn,
       count(*) FILTER (WHERE w.Humidity3pm <  t.threshold AND w.rain_tomorrow_i = 0) AS tn
FROM weather_clean w
CROSS JOIN (SELECT unnest(generate_series(40, 90, 5)) AS threshold) t
WHERE w.has_target AND w.Humidity3pm IS NOT NULL
GROUP BY w.Location, w.season, t.threshold;

CREATE OR REPLACE TABLE q11_rule_thresholds AS
WITH s AS (
    SELECT threshold, sum(tp) AS tp, sum(fp) AS fp, sum(fn) AS fn, sum(tn) AS tn
    FROM rule_counts_by_loc_season GROUP BY threshold
)
SELECT threshold,
       tp + fp + fn + tn                                         AS n_eval,
       tp, fp, fn, tn,
       round(100.0 * (tp + tn) / (tp + fp + fn + tn), 2)         AS accuracy,
       round(100.0 * tp / (tp + fn), 2)                          AS recall,
       round(100.0 * (tp + fp) / (tp + fp + fn + tn), 2)         AS warn_pct,
       round(100.0 * tp / nullif(tp + fp, 0), 2)                 AS precision,
       round(100.0 * (fp + tn) / (tp + fp + fn + tn), 2)         AS baseline_accuracy
FROM s;

-- kestabilan ambang antar periode (cek ringan terhadap risiko in-sample)
CREATE OR REPLACE TABLE q11_rule_by_period AS
SELECT CASE WHEN w.year <= 2012 THEN '2007-2012' ELSE '2013-2017' END AS period,
       t.threshold,
       count(*) FILTER (WHERE w.Humidity3pm >= t.threshold AND w.rain_tomorrow_i = 1) AS tp,
       count(*) FILTER (WHERE w.Humidity3pm >= t.threshold AND w.rain_tomorrow_i = 0) AS fp,
       count(*) FILTER (WHERE w.Humidity3pm <  t.threshold AND w.rain_tomorrow_i = 1) AS fn,
       count(*) FILTER (WHERE w.Humidity3pm <  t.threshold AND w.rain_tomorrow_i = 0) AS tn
FROM weather_clean w
CROSS JOIN (SELECT unnest(generate_series(40, 90, 5)) AS threshold) t
WHERE w.has_target AND w.Humidity3pm IS NOT NULL
GROUP BY 1, 2;
