-- 01_load.sql
-- Memuat CSV mentah apa adanya ke tabel weather_raw. Tidak ada perubahan nilai.
-- Dijalankan dari root project (project/code/1-data-preparation/python/02_build_tables.py mengatur working directory).
-- Nilai kosong di CSV ditulis sebagai teks 'NA'.

CREATE OR REPLACE TABLE weather_raw AS
SELECT *
FROM read_csv(
    'data/raw/weatherAUS.csv',
    header      = true,
    nullstr     = 'NA',
    sample_size = -1,
    types       = {'Date': 'DATE', 'Location': 'VARCHAR',
                   'WindGustDir': 'VARCHAR', 'WindDir9am': 'VARCHAR', 'WindDir3pm': 'VARCHAR',
                   'RainToday': 'VARCHAR', 'RainTomorrow': 'VARCHAR'}
);
