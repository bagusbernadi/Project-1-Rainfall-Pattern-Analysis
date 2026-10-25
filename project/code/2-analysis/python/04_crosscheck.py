"""Langkah 9 (Q15): cek silang SQL vs pandas.

Semua angka dihitung ULANG dari CSV mentah memakai pandas (tanpa DuckDB), lalu dibandingkan dengan
file results/2-analysis/*.csv yang dihasilkan SQL. Jumlah baris harus sama persis. Nilai pecahan boleh berbeda
paling besar setengah digit pembulatan yang dipakai SQL.

Keluaran: results/2-analysis/crosscheck.csv. Skrip berhenti dengan kode 1 jika ada yang tidak cocok.
"""
import sys

import numpy as np
import pandas as pd

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import DIM_CSV, RES_ANALYSIS, RAW_CSV, SEASON_OF_MONTH, THRESHOLDS, WET_MONTHS, require_raw

RESULTS = []


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV, parse_dates=["Date"])
    dim = pd.read_csv(DIM_CSV)
    df = df.merge(dim[["Location", "climate_zone"]], on="Location", how="left")
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["season"] = df["month"].map(SEASON_OF_MONTH)
    df["wet_dry"] = np.where(df["climate_zone"] != "Tropis utara", None,
                             np.where(df["month"].isin(WET_MONTHS), "Basah", "Kering"))
    df["rt"] = df["RainToday"].map({"Yes": 1, "No": 0})
    df["rm"] = df["RainTomorrow"].map({"Yes": 1, "No": 0})
    return df


def compare(name: str, sql_file: str, expected: pd.DataFrame, keys: list[str], spec: dict) -> None:
    """spec: kolom -> jumlah desimal pembulatan SQL (None = harus sama persis)."""
    got = pd.read_csv(RES_ANALYSIS / sql_file)
    exp = expected.copy()
    status, max_diff, note = "PASS", 0.0, ""
    if len(got) != len(exp):
        status, note = "FAIL", f"jumlah baris SQL {len(got)} != pandas {len(exp)}"
    else:
        m = got.merge(exp, on=keys, how="outer", suffixes=("_sql", "_pd"), indicator=True)
        if (m["_merge"] != "both").any():
            status, note = "FAIL", f"{int((m['_merge'] != 'both').sum())} kunci tidak ada di salah satu sisi"
        else:
            for col, dec in spec.items():
                a, b = m[f"{col}_sql"], m[f"{col}_pd"]
                numeric = (pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b)
                           and not pd.api.types.is_bool_dtype(a) and not pd.api.types.is_bool_dtype(b))
                if not numeric:
                    bad = int((a.astype(str) != b.astype(str)).sum())
                    if bad:
                        status, note = "FAIL", f"{col}: {bad} baris beda"
                    continue
                both_nan = a.isna() & b.isna()
                d = (a - b).abs().where(~both_nan, 0.0)
                if d.isna().any():
                    status, note = "FAIL", f"{col}: NaN hanya di salah satu sisi"
                    continue
                tol = 1e-9 if dec is None else 0.5 * 10 ** (-dec) + 1e-9
                md = float(d.max())
                max_diff = max(max_diff, md)
                if md > tol:
                    status, note = "FAIL", f"{col}: selisih maks {md:.6g} > toleransi {tol:.3g}"
    RESULTS.append((name, sql_file, len(got), max_diff, status, note))
    print(f"[{status}] {name:34s} baris={len(got):>5} selisih_maks={max_diff:.3g} {note}")


def main() -> None:
    require_raw()
    df = load()
    t = df[df["rt"].notna()]          # has_today
    tg = df[df["rm"].notna()]         # has_target
    both = df[df["rt"].notna() & df["rm"].notna()]

    def freq(d, keys):
        g = d.groupby(keys).agg(n_obs=("rt", "size"), rain_days=("rt", "sum")).reset_index()
        g["pct_rain"] = 100.0 * g["rain_days"] / g["n_obs"]
        return g

    sp = {"n_obs": None, "rain_days": None, "pct_rain": 2}

    # Q1
    compare("Q1 hujan per lokasi x bulan", "rain_by_month.csv", freq(t, ["Location", "climate_zone", "month"]),
            ["Location", "month"], {**sp, "climate_zone": None})
    # Q2
    ls = freq(t, ["Location", "climate_zone", "season"]).merge(
        df[df["rt"] == 1].groupby(["Location", "season"])["Rainfall"].sum().rename("sum_mm_rain_days").reset_index(),
        on=["Location", "season"], how="left")
    compare("Q2 hujan per lokasi x musim", "rain_by_loc_season.csv", ls,
            ["Location", "season"], {**sp, "sum_mm_rain_days": 3})
    z = freq(t, ["climate_zone", "season"]).merge(
        t.groupby(["climate_zone", "season"])["Location"].nunique().rename("n_locations").reset_index())
    compare("Q2 hujan per zona x musim", "rain_by_zone_season.csv", z, ["climate_zone", "season"],
            {**sp, "n_locations": None})
    compare("Q2 tropis musim basah/kering", "tropical_wet_dry.csv", freq(t[t["wet_dry"].notna()], ["Location", "wet_dry"]),
            ["Location", "wet_dry"], sp)
    # Q3
    ly = t.groupby(["Location", "year"]).agg(n_obs=("rt", "size"), rain_days=("rt", "sum")).reset_index()
    ly["is_complete"] = ly["n_obs"] >= 0.9 * np.where(ly["year"] % 4 == 0, 366, 365)
    compare("Q3 hujan per lokasi x tahun", "rain_by_loc_year.csv", ly, ["Location", "year"],
            {"n_obs": None, "rain_days": None, "is_complete": None})
    ok = ly[ly["year"].between(2009, 2016) & ly["is_complete"]].groupby("Location").size()
    panel = ok[ok == 8].index
    pl = pd.DataFrame({"Location": panel, "in_panel": True})
    compare("Q3 lokasi panel seimbang", "rain_trend_panel_locations.csv", pl, ["Location"], {"in_panel": None})
    tr = ly[ly["Location"].isin(panel) & ly["year"].between(2009, 2016)].groupby("year").agg(
        n_locations=("Location", "nunique"), n_obs=("n_obs", "sum"), rain_days=("rain_days", "sum")).reset_index()
    tr["pct_rain"] = 100.0 * tr["rain_days"] / tr["n_obs"]
    compare("Q3 tren tahunan panel", "rain_trend_year.csv", tr, ["year"],
            {"n_locations": None, "n_obs": None, "rain_days": None, "pct_rain": 2})
    # Q4-Q5
    loc = df.groupby(["Location", "climate_zone"]).apply(lambda g: pd.Series({
        "n_obs": g["rt"].notna().sum(),
        "rain_days": g["rt"].sum(),
        "mean_mm_rain_day": g.loc[g["rt"] == 1, "Rainfall"].mean(),
        "est_annual_mm": g["Rainfall"].sum() / g["Rainfall"].notna().sum() * 365.25,
    }), include_groups=False).reset_index()
    loc["pct_rain"] = 100.0 * loc["rain_days"] / loc["n_obs"]
    loc["rank_pct_rain"] = (loc["rain_days"] / loc["n_obs"]).rank(method="min", ascending=False)
    loc["rank_annual_mm"] = loc["est_annual_mm"].rank(method="min", ascending=False)
    compare("Q4-Q5 peringkat dan curah lokasi", "location_ranking.csv", loc, ["Location"],
            {"n_obs": None, "rain_days": None, "pct_rain": 2, "mean_mm_rain_day": 2, "est_annual_mm": 0,
             "rank_pct_rain": None, "rank_annual_mm": None})
    # Q12
    q1 = freq(t, ["Location", "climate_zone", "month"])
    q1["pct_r"] = q1["pct_rain"].round(2)
    q1 = q1.sort_values(["Location", "pct_r", "month"])
    q1["rank_safest"] = q1.groupby("Location").cumcount() + 1
    # rank() SQL memberi peringkat sama untuk nilai sama; bulan sebagai pemutus seri sehingga peringkat unik
    q1d = q1.sort_values(["Location", "pct_r", "month"], ascending=[True, False, True])
    q1["rank_rainiest"] = q1d.groupby("Location").cumcount().reindex(q1.index).values + 1
    compare("Q12 jadwal kegiatan luar ruang", "outdoor_schedule.csv", q1, ["Location", "month"],
            {"n_obs": None, "pct_rain": 2, "rank_safest": None, "rank_rainiest": None})
    # Q6-Q8
    var_list = ["Humidity3pm", "Pressure3pm", "Sunshine", "Cloud3pm"]
    long = pd.concat([tg.loc[tg[v].notna(), ["Location", "season", "rm", v]]
                      .rename(columns={v: "val"}).assign(variable=v) for v in var_list])
    cond = long.groupby(["variable", "rm"])["val"].agg(
        n="size", mean="mean", p25=lambda s: s.quantile(.25), median="median", p75=lambda s: s.quantile(.75)).reset_index()
    cond["n_locations"] = long.groupby(["variable", "rm"])["Location"].nunique().values
    cond["rain_tomorrow"] = cond["rm"].map({1: "Yes", 0: "No"})
    compare("Q6-Q8 sebaran kondisi cuaca", "conditions.csv", cond, ["variable", "rain_tomorrow"],
            {"n": None, "n_locations": None, "mean": 3, "p25": 3, "median": 3, "p75": 3})
    dd = cond.pivot(index="variable", columns="rm", values=["n", "mean"])
    diff = pd.DataFrame({"variable": dd.index, "n_yes": dd[("n", 1)].values, "n_no": dd[("n", 0)].values,
                         "mean_yes": dd[("mean", 1)].values, "mean_no": dd[("mean", 0)].values})
    diff["diff_yes_minus_no"] = diff["mean_yes"] - diff["mean_no"]
    compare("Q6-Q8 selisih rata-rata", "conditions_diff.csv", diff, ["variable"],
            {"n_yes": None, "n_no": None, "mean_yes": 3, "mean_no": 3, "diff_yes_minus_no": 3})
    bl = long.groupby(["Location", "season", "variable", "rm"])["val"].agg(n="size", sum_val="sum").reset_index()
    bl = bl.rename(columns={"rm": "rain_tomorrow_i"})
    compare("Q6-Q8 jumlah per lokasi x musim", "conditions_by_loc_season.csv", bl,
            ["Location", "season", "variable", "rain_tomorrow_i"], {"n": None, "sum_val": 3})
    # Q9
    w1 = tg[tg["WindGustDir"].notna()].groupby("WindGustDir").agg(n=("rm", "size"), rain_tomorrow_days=("rm", "sum")).reset_index()
    w1["pct_rain_tomorrow"] = 100.0 * w1["rain_tomorrow_days"] / w1["n"]
    compare("Q9 arah hembusan angin", "wind_gust_dir.csv", w1, ["WindGustDir"],
            {"n": None, "rain_tomorrow_days": None, "pct_rain_tomorrow": 2})
    ws = tg[tg["WindGustSpeed"].notna()].copy()
    ws["gust_kmh_bin"] = pd.cut(ws["WindGustSpeed"], [-np.inf, 30, 40, 50, 60, np.inf], right=False,
                                labels=["1: < 30", "2: 30-39", "3: 40-49", "4: 50-59", "5: >= 60"]).astype(str)
    w2 = ws.groupby("gust_kmh_bin").agg(n=("rm", "size"), rain_tomorrow_days=("rm", "sum")).reset_index()
    w2["pct_rain_tomorrow"] = 100.0 * w2["rain_tomorrow_days"] / w2["n"]
    compare("Q9 kecepatan hembusan angin", "wind_gust_speed.csv", w2, ["gust_kmh_bin"],
            {"n": None, "rain_tomorrow_days": None, "pct_rain_tomorrow": 2})
    # Q10
    pc = both.groupby(["Location", "season"]).apply(lambda g: pd.Series({
        "today_yes_n": (g["rt"] == 1).sum(),
        "tomorrow_yes_given_yes": ((g["rt"] == 1) & (g["rm"] == 1)).sum(),
        "today_no_n": (g["rt"] == 0).sum(),
        "tomorrow_yes_given_no": ((g["rt"] == 0) & (g["rm"] == 1)).sum()}), include_groups=False).reset_index()
    cnt_cols = ["today_yes_n", "tomorrow_yes_given_yes", "today_no_n", "tomorrow_yes_given_no"]
    compare("Q10 hitungan peluang beruntun", "persistence_counts.csv", pc, ["Location", "season"],
            {c: None for c in cnt_cols})
    pl_ = pc.groupby("Location")[cnt_cols].sum().reset_index()
    pl_ = pd.concat([pl_, pd.DataFrame([{"Location": "ALL", **pc[cnt_cols].sum().to_dict()}])], ignore_index=True)
    pl_["p_rain_tomorrow_if_rain_today"] = 100.0 * pl_["tomorrow_yes_given_yes"] / pl_["today_yes_n"]
    pl_["p_rain_tomorrow_if_dry_today"] = 100.0 * pl_["tomorrow_yes_given_no"] / pl_["today_no_n"]
    pl_["ratio"] = (pl_["tomorrow_yes_given_yes"] / pl_["today_yes_n"]) / (pl_["tomorrow_yes_given_no"] / pl_["today_no_n"])
    compare("Q10 rasio peluang beruntun", "persistence.csv", pl_, ["Location"],
            {**{c: None for c in cnt_cols}, "p_rain_tomorrow_if_rain_today": 2,
             "p_rain_tomorrow_if_dry_today": 2, "ratio": 3})
    # Q11
    ev = df[df["rm"].notna() & df["Humidity3pm"].notna()]

    def conf(d, keys):
        out = []
        for th in THRESHOLDS:
            w = d["Humidity3pm"] >= th
            y = d["rm"] == 1
            x = d.assign(threshold=th, tp=(w & y).astype(int), fp=(w & ~y).astype(int),
                         fn=(~w & y).astype(int), tn=(~w & ~y).astype(int))
            out.append(x.groupby(keys + ["threshold"])[["tp", "fp", "fn", "tn"]].sum().reset_index())
        return pd.concat(out, ignore_index=True)

    rc = conf(ev, ["Location", "season"])
    compare("Q11 hitungan aturan lokasi x musim", "rule_counts_by_loc_season.csv", rc,
            ["Location", "season", "threshold"], {c: None for c in ["tp", "fp", "fn", "tn"]})
    ra = rc.groupby("threshold")[["tp", "fp", "fn", "tn"]].sum().reset_index()
    ra["n_eval"] = ra[["tp", "fp", "fn", "tn"]].sum(axis=1)
    ra["accuracy"] = 100.0 * (ra.tp + ra.tn) / ra.n_eval
    ra["recall"] = 100.0 * ra.tp / (ra.tp + ra.fn)
    ra["warn_pct"] = 100.0 * (ra.tp + ra.fp) / ra.n_eval
    ra["precision"] = 100.0 * ra.tp / (ra.tp + ra.fp)
    ra["baseline_accuracy"] = 100.0 * (ra.fp + ra.tn) / ra.n_eval
    compare("Q11 ketepatan aturan per ambang", "rule_thresholds.csv", ra, ["threshold"],
            {"n_eval": None, "tp": None, "fp": None, "fn": None, "tn": None, "accuracy": 2, "recall": 2,
             "warn_pct": 2, "precision": 2, "baseline_accuracy": 2})
    ev2 = ev.assign(period=np.where(ev["year"] <= 2012, "2007-2012", "2013-2017"))
    rp = conf(ev2, ["period"])
    compare("Q11 aturan per periode", "rule_by_period.csv", rp, ["period", "threshold"],
            {c: None for c in ["tp", "fp", "fn", "tn"]})
    # KPI
    r70 = ra[ra["threshold"] == 70].iloc[0]
    kp = pd.DataFrame([
        ("K1", 100.0 * t["rt"].mean(), len(t)),
        ("K2", df.loc[(df["rt"] == 1) & df["Rainfall"].notna(), "Rainfall"].mean(), int(((df["rt"] == 1) & df["Rainfall"].notna()).sum())),
        ("K3", float(diff.loc[diff.variable == "Humidity3pm", "diff_yes_minus_no"].iloc[0]),
         int(diff.loc[diff.variable == "Humidity3pm", ["n_yes", "n_no"]].iloc[0].sum())),
        ("K4", float(pl_.loc[pl_.Location == "ALL", "ratio"].iloc[0]),
         int(pl_.loc[pl_.Location == "ALL", ["today_yes_n", "today_no_n"]].iloc[0].sum())),
        ("K5", float(r70["recall"]), int(r70["n_eval"])),
    ], columns=["kpi_id", "value", "n"])
    compare("KPI K1-K5", "kpi_overall.csv", kp, ["kpi_id"], {"value": 2, "n": None})
    # K4 dibulatkan 3 desimal di SQL; toleransi 0,005 di atas sudah mencukupi (lebih longgar)

    res = pd.DataFrame(RESULTS, columns=["check", "file", "n_rows", "max_abs_diff", "status", "note"])
    res.to_csv(RES_ANALYSIS / "crosscheck.csv", index=False)
    n_fail = int((res["status"] == "FAIL").sum())
    print(f"\nRingkasan: {len(res) - n_fail} PASS, {n_fail} FAIL dari {len(res)} pemeriksaan")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
