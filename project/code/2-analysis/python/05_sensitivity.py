"""Langkah 10 (Q14): uji sensitivitas data kosong.

Skenario A (dropna): setiap ukuran dihitung hanya pada baris yang terisi untuk variabel yang dipakai.
Skenario B (imputasi): nilai kosong variabel diisi median per lokasi x bulan (dari semua tahun).
  - Jika sebuah lokasi tidak punya satu pun nilai untuk variabel itu, nilai tetap kosong dan baris tidak ikut
    (tidak diisi dari lokasi lain karena iklim antar lokasi berbeda).
  - Kolom target (RainToday, RainTomorrow, Rainfall) tidak pernah diimputasi, jadi Q1-Q5, Q10, Q12 tidak
    terpengaruh oleh pilihan A atau B.

Tanda "perlu dicermati" (flag) memakai ambang buatan sendiri, bukan uji statistik:
  - arah selisih berubah tanda, atau
  - ukuran berubah lebih dari 10% secara relatif, atau
  - untuk aturan ambang: status "akurasi di atas baseline" berubah.

Keluaran: results/2-analysis/sensitivity.csv
"""
import numpy as np
import pandas as pd

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import RES_ANALYSIS, RAW_CSV, require_raw

VARS = ["Humidity3pm", "Pressure3pm", "Sunshine", "Cloud3pm"]
RULE_THRESHOLDS = [60, 70, 80]
REL_FLAG_PCT = 10.0


def impute_median(df: pd.DataFrame, col: str) -> pd.Series:
    med = df.groupby(["Location", "month"])[col].transform("median")
    return df[col].fillna(med)


def group_diff(d: pd.DataFrame, col: str) -> dict:
    y, n = d.loc[d["rm"] == 1, col], d.loc[d["rm"] == 0, col]
    return {"mean_yes": y.mean(), "mean_no": n.mean(), "diff": y.mean() - n.mean(), "n": len(d)}


def rule_metrics(d: pd.DataFrame, col: str, th: int) -> dict:
    w, y = d[col] >= th, d["rm"] == 1
    tp, fp, fn, tn = int((w & y).sum()), int((w & ~y).sum()), int((~w & y).sum()), int((~w & ~y).sum())
    n = tp + fp + fn + tn
    return {"accuracy": 100 * (tp + tn) / n, "recall": 100 * tp / (tp + fn), "warn_pct": 100 * (tp + fp) / n,
            "baseline": 100 * (fp + tn) / n, "n": n}


def main() -> None:
    require_raw()
    df = pd.read_csv(RAW_CSV, parse_dates=["Date"])
    df["month"] = df["Date"].dt.month
    df["rm"] = df["RainTomorrow"].map({"Yes": 1, "No": 0})
    for v in VARS:
        df[v + "_imp"] = impute_median(df, v)
    tg = df[df["rm"].notna()]

    rows = []

    def add(metric, a, b, n_a, n_b, extra_flag=False, signed=False):
        """signed=True untuk ukuran berupa selisih, yang tanda (arah)-nya bermakna."""
        diff = b - a
        rel = 100 * diff / abs(a) if a else np.nan
        same_dir = bool(np.sign(a) == np.sign(b)) if signed else True
        flag = (not same_dir) or (abs(rel) > REL_FLAG_PCT) or extra_flag
        rows.append((metric, round(a, 3), round(b, 3), round(diff, 3), round(rel, 2), n_a, n_b,
                     same_dir, bool(flag)))

    # selisih rata-rata antar kelompok (Q6-Q8)
    for v in VARS:
        a = group_diff(tg[tg[v].notna()], v)
        b = group_diff(tg[tg[v + "_imp"].notna()], v + "_imp")
        add(f"Selisih {v} (Yes - No)", a["diff"], b["diff"], a["n"], b["n"], signed=True)

    # aturan ambang Humidity3pm (Q11)
    ea = tg[tg["Humidity3pm"].notna()]
    eb = tg[tg["Humidity3pm_imp"].notna()]
    for th in RULE_THRESHOLDS:
        ma, mb = rule_metrics(ea, "Humidity3pm", th), rule_metrics(eb, "Humidity3pm_imp", th)
        beat_a, beat_b = ma["accuracy"] > ma["baseline"], mb["accuracy"] > mb["baseline"]
        for k, label in (("accuracy", "akurasi"), ("recall", "recall"), ("warn_pct", "hari bertanda peringatan")):
            add(f"Aturan Humidity3pm >= {th}: {label} (%)", ma[k], mb[k], ma["n"], mb["n"],
                extra_flag=(k == "accuracy" and beat_a != beat_b))
        add(f"Aturan Humidity3pm >= {th}: akurasi - baseline (poin)", ma["accuracy"] - ma["baseline"],
            mb["accuracy"] - mb["baseline"], ma["n"], mb["n"],
            extra_flag=(beat_a != beat_b), signed=True)

    cols = ["metric", "dropna_A", "impute_B", "diff_B_minus_A", "rel_diff_pct", "n_A", "n_B",
            "same_direction", "flag_review"]
    out = pd.DataFrame(rows, columns=cols)
    out.to_csv(RES_ANALYSIS / "sensitivity.csv", index=False)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 60)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
