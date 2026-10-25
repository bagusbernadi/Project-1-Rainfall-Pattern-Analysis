"""Langkah 5: membuat weather.duckdb berisi 4 tabel (weather_raw, weather_clean, dim_location, missing_audit)."""
import duckdb

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import DB_PATH, RES_PREP, ROOT, SQL_PREP, require_raw


def main() -> None:
    require_raw()
    audit_csv = RES_PREP / "missing_audit.csv"
    if not audit_csv.exists():
        raise SystemExit("Jalankan project/code/1-data-preparation/python/01_profile_audit.py dulu (missing_audit.csv belum ada).")

    import os
    os.chdir(ROOT)  # jalur di file SQL relatif terhadap root project
    con = duckdb.connect(str(DB_PATH))
    for f in ("01_load.sql", "02_clean.sql"):
        con.execute((SQL_PREP / f).read_text(encoding="utf-8"))
    con.execute("CREATE OR REPLACE TABLE missing_audit AS "
                "SELECT * FROM read_csv('results/1-data-preparation/missing_audit.csv', header = true)")

    # pemeriksaan integritas
    raw_n = con.execute("SELECT count(*) FROM weather_raw").fetchone()[0]
    clean_n = con.execute("SELECT count(*) FROM weather_clean").fetchone()[0]
    no_zone = con.execute("SELECT count(*) FROM weather_clean WHERE climate_zone IS NULL").fetchone()[0]
    dim_n = con.execute("SELECT count(*) FROM dim_location").fetchone()[0]
    loc_n = con.execute("SELECT count(DISTINCT Location) FROM weather_raw").fetchone()[0]
    assert raw_n == clean_n, f"baris raw {raw_n} != clean {clean_n}"
    assert no_zone == 0, f"{no_zone} baris tanpa zona iklim (lokasi belum ada di dim_location)"
    assert dim_n == loc_n, f"dim_location {dim_n} lokasi, data {loc_n} lokasi"
    for t in ("weather_raw", "weather_clean", "dim_location", "missing_audit"):
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"{t:15s} {n:>8,} baris")
    con.close()


if __name__ == "__main__":
    main()
