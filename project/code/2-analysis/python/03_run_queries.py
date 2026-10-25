"""Langkah 6-8: menjalankan code/2-analysis/sql/03-06 dan mengekspor tabel hasil ke results/2-analysis/*.csv."""
import os

import duckdb

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import DB_PATH, RES_ANALYSIS, ROOT, SQL_ANALYSIS

# tabel di DuckDB -> (nama file CSV, urutan baris)
EXPORTS = {
    "q1_rain_by_month":         ("rain_by_month.csv",            "Location, month"),
    "q2_rain_by_loc_season":    ("rain_by_loc_season.csv",       "Location, season"),
    "q2_rain_by_zone_season":   ("rain_by_zone_season.csv",      "climate_zone, season"),
    "q2_tropical_wet_dry":      ("tropical_wet_dry.csv",         "Location, wet_dry"),
    "q3_rain_by_loc_year":      ("rain_by_loc_year.csv",         "Location, year"),
    "q3_panel_locations":       ("rain_trend_panel_locations.csv", "Location"),
    "q3_rain_trend":            ("rain_trend_year.csv",          "year"),
    "q4_q5_location":           ("location_ranking.csv",         "rank_pct_rain, Location"),
    "q12_outdoor_schedule":     ("outdoor_schedule.csv",         "Location, month"),
    "q6_q8_conditions":         ("conditions.csv",               "variable, rain_tomorrow"),
    "q6_q8_diff":               ("conditions_diff.csv",          "variable"),
    "q6_q8_by_loc_season":      ("conditions_by_loc_season.csv", "Location, season, variable, rain_tomorrow_i"),
    "q9_wind_dir":              ("wind_gust_dir.csv",            "WindGustDir"),
    "q9_wind_speed":            ("wind_gust_speed.csv",          "gust_kmh_bin"),
    "q10_persistence_counts":   ("persistence_counts.csv",       "Location, season"),
    "q10_persistence":          ("persistence.csv",              "Location"),
    "rule_counts_by_loc_season": ("rule_counts_by_loc_season.csv", "Location, season, threshold"),
    "q11_rule_thresholds":      ("rule_thresholds.csv",          "threshold"),
    "q11_rule_by_period":       ("rule_by_period.csv",           "period, threshold"),
    "kpi_overall":              ("kpi_overall.csv",              "kpi_id"),
}


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("weather.duckdb belum ada. Jalankan project/code/1-data-preparation/python/02_build_tables.py dulu.")
    os.chdir(ROOT)
    RES_ANALYSIS.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    for f in sorted(SQL_ANALYSIS.glob("0[3-6]_*.sql")):
        con.execute(f.read_text(encoding="utf-8"))
        print("dijalankan:", f.name)
    for table, (fname, order) in EXPORTS.items():
        path = (RES_ANALYSIS / fname).as_posix()
        con.execute(f"COPY (SELECT * FROM {table} ORDER BY {order}) TO '{path}' (HEADER, DELIMITER ',')")
        n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"  {fname:34s} {n:>6,} baris")
    con.close()


if __name__ == "__main__":
    main()
