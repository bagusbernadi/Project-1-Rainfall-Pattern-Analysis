"""Langkah 3-4: profiling data mentah dan audit nilai kosong (Q13).

Keluaran:
  project/docs/profiling_summary.md       ringkasan profiling (baris, lokasi, periode, kolom)
  results/1-data-preparation/profile_columns.csv     tipe, persen kosong, jumlah nilai unik per kolom
  results/1-data-preparation/missing_audit.csv       Location, column_name, null_pct, decision (+ n_rows, decision_code)
  results/1-data-preparation/missing_concentration.csv  apakah kosongnya acak atau terpusat di lokasi tertentu
  results/1-data-preparation/missing_vs_target.csv   apakah baris kosong punya peluang hujan yang berbeda
"""
import pandas as pd

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import DOCS_DIR, RES_PREP, RAW_CSV, require_raw

# Kolom yang dipakai analisis (lihat project/docs/data_dictionary.md)
TARGET_COLS = ["RainToday", "RainTomorrow", "Rainfall"]
CORE_COLS = ["Humidity3pm", "Pressure3pm", "Sunshine", "Cloud3pm"]   # pembanding Q6-Q8
WIND_COLS = ["WindGustDir", "WindGustSpeed"]                           # Q9
UNUSED_COLS = ["MinTemp", "MaxTemp", "Temp9am", "Temp3pm", "Evaporation", "Cloud9am",
               "Humidity9am", "Pressure9am", "WindDir9am", "WindDir3pm",
               "WindSpeed9am", "WindSpeed3pm"]


def decide(col: str, null_pct: float) -> tuple[str, str]:
    """Aturan keputusan per kolom dan per lokasi. Kembalikan (kode, teks keputusan)."""
    if col in ("Date", "Location"):
        return "none", "Tidak ada nilai kosong."
    if col in UNUSED_COLS:
        return "unused", "Tidak dipakai di analisis (tidak dibutuhkan Q1-Q15). Tetap ada di weather_raw."
    if null_pct >= 100:
        return "not_recorded", ("Lokasi tidak mencatat kolom ini sama sekali. Dikeluarkan dari analisis kolom ini, "
                                "tidak diisi dari lokasi lain karena iklim antar lokasi berbeda.")
    if col in TARGET_COLS:
        return "drop_rows", ("Baris kosong tidak dipakai pada analisis yang membutuhkan kolom ini "
                             "(has_today / has_target). Tidak pernah diimputasi.")
    if col in WIND_COLS:
        return "complete_case", "Dipakai pada baris terisi (hanya Q9). Tidak diimputasi."
    if col in CORE_COLS:
        if null_pct > 20:
            return "complete_case_report_n", ("Dipakai pada baris terisi, jumlah baris dan lokasi ditampilkan. "
                                              "Imputasi median lokasi x bulan hanya di uji sensitivitas (Q14).")
        return "complete_case", ("Dipakai pada baris terisi. Imputasi median lokasi x bulan diuji "
                                 "sebagai skenario pembanding (Q14).")
    return "unused", "Tidak dipakai di analisis."


def main() -> None:
    require_raw()
    RES_PREP.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(RAW_CSV, parse_dates=["Date"])  # 'NA' dibaca sebagai kosong secara bawaan

    # ---------- profiling ----------
    n_rows, n_cols = df.shape
    n_loc = df["Location"].nunique()
    dup_keys = int(df.duplicated(["Date", "Location"]).sum())
    prof = pd.DataFrame({
        "column_name": df.columns,
        "dtype": [str(t) for t in df.dtypes],
        "n_null": df.isna().sum().values,
        "null_pct": (df.isna().mean() * 100).round(2).values,
        "n_unique": df.nunique().values,
    })
    prof.to_csv(RES_PREP / "profile_columns.csv", index=False)

    m = df.dropna(subset=["Rainfall", "RainToday"])
    n_exact_one = int((m["Rainfall"] == 1.0).sum())
    rt_consistent = (m["Rainfall"] > 1.0) == (m["RainToday"] == "Yes")
    per_loc = df.groupby("Location")["Date"].agg(["size", "min", "max"])
    late = per_loc[per_loc["min"] >= "2013-01-01"].index.tolist()

    lines = [
        "# Ringkasan profiling data mentah",
        "",
        "Dihasilkan oleh `project/code/1-data-preparation/python/01_profile_audit.py`. Semua angka dihitung dari `project/data/raw/weatherAUS.csv`.",
        "",
        f"- Baris: **{n_rows:,}** | Kolom: **{n_cols}** | Lokasi: **{n_loc}**",
        f"- Periode: **{df['Date'].min().date()}** sampai **{df['Date'].max().date()}**",
        f"- Duplikat kunci (Date, Location): **{dup_keys}**",
        f"- RainToday = Yes tepat jika Rainfall > 1,0 mm: **{'cocok' if rt_consistent.all() else 'TIDAK cocok'}** "
        f"pada {len(m):,} baris terisi. Hari dengan Rainfall tepat 1,0 mm ada **{n_exact_one:,}** dan semuanya 'No'.",
        f"- Lokasi yang baru mencatat sejak 2013: {', '.join(late) if late else 'tidak ada'}",
        "",
        "## Kolom dengan nilai kosong terbanyak",
        "",
        "| Kolom | Kosong (%) |",
        "|---|---|",
    ]
    for _, r in prof.sort_values("null_pct", ascending=False).head(8).iterrows():
        lines.append(f"| {r.column_name} | {r.null_pct:.1f} |")
    lines += ["", "## Jumlah baris per tahun", "", "| Tahun | Baris |", "|---|---|"]
    for y, c in df.groupby(df["Date"].dt.year).size().items():
        lines.append(f"| {y} | {c:,} |")
    (DOCS_DIR / "profiling_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---------- audit nilai kosong per lokasi x kolom (Q13) ----------
    cols = [c for c in df.columns if c not in ("Date", "Location")]
    null_pct = df.groupby("Location")[cols].agg(lambda s: s.isna().mean() * 100)
    n_by_loc = df.groupby("Location").size()
    rows = []
    for loc in null_pct.index:
        for col in cols:
            p = float(null_pct.loc[loc, col])
            code, text = decide(col, p)
            rows.append((loc, col, round(p, 2), int(n_by_loc[loc]), code, text))
    audit = pd.DataFrame(rows, columns=["Location", "column_name", "null_pct", "n_rows",
                                        "decision_code", "decision"])
    audit.to_csv(RES_PREP / "missing_audit.csv", index=False)

    # ---------- acak atau terpusat? ----------
    conc = []
    for col in cols:
        miss = df[col].isna().groupby(df["Location"]).sum()
        total = int(miss.sum())
        if total == 0:
            continue
        top5 = int(miss.sort_values(ascending=False).head(5).sum())
        all_null_locs = int((null_pct[col] >= 100).sum())
        conc.append((col, total, round(100 * total / len(df), 2), all_null_locs,
                     int((null_pct[col] > 0).sum()), round(100 * top5 / total, 1)))
    conc_df = pd.DataFrame(conc, columns=["column_name", "n_null", "null_pct", "locations_never_recording",
                                          "locations_with_any_null", "share_of_nulls_in_top5_locations_pct"])
    conc_df.sort_values("null_pct", ascending=False).to_csv(RES_PREP / "missing_concentration.csv", index=False)

    # ---------- apakah kosong berkaitan dengan hujan besok? ----------
    t = df.dropna(subset=["RainTomorrow"])
    mt = []
    for col in CORE_COLS + WIND_COLS:
        miss = t[col].isna()
        rate_missing = 100 * (t.loc[miss, "RainTomorrow"] == "Yes").mean() if miss.any() else float("nan")
        rate_present = 100 * (t.loc[~miss, "RainTomorrow"] == "Yes").mean()
        mt.append((col, int(miss.sum()), round(rate_missing, 2), round(rate_present, 2),
                   round(rate_missing - rate_present, 2)))
    pd.DataFrame(mt, columns=["column_name", "n_missing", "pct_rain_tomorrow_if_missing",
                              "pct_rain_tomorrow_if_present", "diff_pp"]).to_csv(
        RES_PREP / "missing_vs_target.csv", index=False)

    print(f"Profiling selesai: {n_rows:,} baris, {n_loc} lokasi, {df['Date'].min().date()} .. {df['Date'].max().date()}")
    print(f"Pasangan lokasi x kolom 100% kosong (kolom dipakai): "
          f"{int(((audit.decision_code == 'not_recorded')).sum())}")


if __name__ == "__main__":
    main()
