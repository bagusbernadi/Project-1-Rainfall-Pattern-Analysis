"""Pengaturan bersama untuk semua skrip. Semua jalur relatif terhadap folder project/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # folder project/
RAW_CSV = ROOT / "data" / "raw" / "weatherAUS.csv"
DIM_CSV = ROOT / "data" / "reference" / "dim_location.csv"
DB_PATH = ROOT / "weather.duckdb"
CODE = ROOT / "code"
SQL_PREP = CODE / "1-data-preparation" / "sql"
SQL_ANALYSIS = CODE / "2-analysis" / "sql"
RES_PREP = ROOT / "results" / "1-data-preparation"
RES_ANALYSIS = ROOT / "results" / "2-analysis"
RES_PRESENT = ROOT / "results" / "3-presentation"
DOCS_DIR = ROOT / "docs"


def result(name):
    """Cari file hasil (CSV) di results/1-data-preparation lalu results/2-analysis."""
    for d in (RES_PREP, RES_ANALYSIS):
        if (d / name).exists():
            return d / name
    return RES_ANALYSIS / name


THRESHOLDS = list(range(40, 91, 5))
SEASON_ORDER = ["Summer", "Autumn", "Winter", "Spring"]
SEASON_OF_MONTH = {12: "Summer", 1: "Summer", 2: "Summer",
                   3: "Autumn", 4: "Autumn", 5: "Autumn",
                   6: "Winter", 7: "Winter", 8: "Winter",
                   9: "Spring", 10: "Spring", 11: "Spring"}
WET_MONTHS = {11, 12, 1, 2, 3, 4}  # musim basah zona Tropis utara


def require_raw():
    if not RAW_CSV.exists():
        raise SystemExit(f"File tidak ditemukan: {RAW_CSV}\nUnduh dulu, lihat project/data/README.md")
