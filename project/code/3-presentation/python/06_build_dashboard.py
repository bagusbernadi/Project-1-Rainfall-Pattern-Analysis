"""Langkah 11: membuat results/3-presentation/dashboard.html (satu file mandiri) dari results/2-analysis/*.csv.

Data disisipkan ke code/3-presentation/html/dashboard_template.html. Fungsi hitung di dashboard (blok CALC) lalu diuji di Node:
KPI K1-K5 untuk 'Semua lokasi, semua musim' harus sama dengan results/2-analysis/kpi_overall.csv.
"""
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import RAW_CSV, RES_PRESENT, result, ROOT, CODE

ZONE_ORDER = ["Tropis utara", "Pesisir timur", "Tenggara sedang", "Barat daya", "Pedalaman kering"]
SEASON_ID = ["Summer", "Autumn", "Winter", "Spring"]


def idn(v: float, d: int = 1) -> str:
    """Format angka gaya Indonesia: koma desimal, titik ribuan."""
    s = f"{abs(v):,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return ("−" if v < 0 else "") + s


def rows(df: pd.DataFrame, cols: list[str]) -> list[list]:
    out = []
    for r in df[cols].itertuples(index=False):
        out.append([x.item() if hasattr(x, "item") else x for x in r])
    return out


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(result(name))


def main() -> None:
    needed = ["rain_by_month.csv", "rule_thresholds.csv", "crosscheck.csv", "sensitivity.csv"]
    for n in needed:
        if not result(n).exists():
            raise SystemExit(f"{n} belum ada. Jalankan scripts 01-05 dulu.")

    rank = load("location_ranking.csv")
    zone_of = dict(zip(rank["Location"], rank["climate_zone"]))
    locs = sorted(zone_of, key=lambda l: (ZONE_ORDER.index(zone_of[l]), l))

    month = load("rain_by_month.csv")
    ls = load("rain_by_loc_season.csv").fillna({"sum_mm_rain_days": 0})
    ly = load("rain_by_loc_year.csv")
    panel = set(load("rain_trend_panel_locations.csv")["Location"])
    ly = ly[ly["Location"].isin(panel) & ly["year"].between(2009, 2016)]
    cond = load("conditions_by_loc_season.csv")
    rule = load("rule_counts_by_loc_season.csv")
    pers = load("persistence_counts.csv")
    wd = load("tropical_wet_dry.csv")
    sched = load("outdoor_schedule.csv")
    thr = load("rule_thresholds.csv")
    kpi = load("kpi_overall.csv").set_index("kpi_id")["value"]
    diff = load("conditions_diff.csv").set_index("variable")
    zs = load("rain_by_zone_season.csv")
    persall = load("persistence.csv").set_index("Location").loc["ALL"]
    per = load("rule_by_period.csv")
    wdir = load("wind_gust_dir.csv").sort_values("pct_rain_tomorrow", ascending=False)
    wspd = load("wind_gust_speed.csv")
    conc = load("missing_concentration.csv")
    sens = load("sensitivity.csv")
    xc = load("crosscheck.csv")
    prof = load("profile_columns.csv")
    audit = load("missing_audit.csv")
    mvt = load("missing_vs_target.csv").set_index("column_name")

    # ---- periode: akurasi dan recall per ambang untuk dua periode
    pr = []
    for th, g in per.groupby("threshold"):
        v = {}
        for p, gg in g.groupby("period"):
            r = gg.iloc[0]
            v[p] = (100 * (r.tp + r.tn) / (r.tp + r.fp + r.fn + r.tn), 100 * r.tp / (r.tp + r.fn))
        a, b = v["2007-2012"], v["2013-2017"]
        pr.append([int(th), int(th), round(a[0], 2), round(b[0], 2), round(a[1], 2), round(b[1], 2)])

    # ---- kolom dipakai analisis
    used_cols = set(audit.loc[audit["decision_code"].isin(
        ["drop_rows", "complete_case", "complete_case_report_n"]), "column_name"])
    miss = [[r.column_name, float(r.null_pct), int(r.locations_never_recording), int(r.column_name in used_cols)]
            for r in conc.sort_values("null_pct", ascending=False).itertuples()]

    nr = audit[audit["decision_code"] == "not_recorded"].groupby("column_name")["Location"].apply(list)
    parts = [f"{c}: {len(v)} lokasi tidak mencatat" for c, v in nr.sort_values(key=lambda s: -s.str.len()).items()]
    h3 = mvt.loc["Humidity3pm"]
    miss_note = ("Lokasi yang tidak mencatat kolom sama sekali dikeluarkan dari analisis kolom itu. " +
                 "; ".join(parts) + ". " +
                 f"Baris dengan Humidity3pm kosong lebih sering diikuti hujan ({idn(h3.pct_rain_tomorrow_if_missing)}% vs "
                 f"{idn(h3.pct_rain_tomorrow_if_present)}%), jadi kosongnya tidak sepenuhnya acak.")

    # ---- uji sensitivitas untuk tabel dashboard
    sens_rows = [[r.metric, float(r.dropna_A), float(r.impute_B), float(r.rel_diff_pct), bool(r.flag_review)]
                 for r in sens.itertuples()]

    # ---- cek silang
    n_pass = int((xc["status"] == "PASS").sum())
    xcheck = (f"<b>{n_pass} dari {len(xc)}</b> tabel hasil SQL dihitung ulang dari CSV mentah dengan pandas dan hasilnya sama. "
              f"Jumlah baris sama persis. Pecahan boleh berbeda paling besar setengah digit pembulatan. "
              f"Detail: results/2-analysis/crosscheck.csv.")

    # ---- temuan utama (semua angka dari tabel hasil)
    k = kpi
    r70 = thr[thr["threshold"] == 70].iloc[0]
    top, bot = rank.sort_values("pct_rain", ascending=False).iloc[0], rank.sort_values("pct_rain").iloc[0]
    wet = rank.sort_values("est_annual_mm", ascending=False).iloc[0]
    swing = zs.groupby("climate_zone")["pct_rain"].agg(["max", "min"]).assign(d=lambda d: d["max"] - d["min"]).sort_values("d", ascending=False)

    def season_swing(z):
        g = zs[zs["climate_zone"] == z].sort_values("pct_rain")
        return (f"<b>{z}</b>: {idn(g.iloc[-1].pct_rain)}% hari hujan pada {g.iloc[-1].season} "
                f"vs {idn(g.iloc[0].pct_rain)}% pada {g.iloc[0].season}")
    # akurasi dan baseline dihitung dari hitungan asli, bukan dari angka yang sudah dibulatkan
    n70 = r70.tp + r70.fp + r70.fn + r70.tn
    gap70 = 100 * (r70.tp + r70.tn) / n70 - 100 * (r70.fp + r70.tn) / n70
    trop = wd.assign(rd=wd["rain_days"], n=wd["n_obs"]).groupby("wet_dry")[["rd", "n"]].sum()
    pw, pdr = 100 * trop.loc["Basah", "rd"] / trop.loc["Basah", "n"], 100 * trop.loc["Kering", "rd"] / trop.loc["Kering", "n"]
    d_h, d_p, d_s, d_c = (diff.loc[v, "diff_yes_minus_no"] for v in ["Humidity3pm", "Pressure3pm", "Sunshine", "Cloud3pm"])
    findings = [
        f"Hujan turun pada <b>{idn(k['K1'])}%</b> hari. Lokasi paling sering hujan: <b>{top.Location}</b> ({idn(top.pct_rain)}%). "
        f"Paling jarang: <b>{bot.Location}</b> ({idn(bot.pct_rain)}%).",
        f"Sering hujan belum berarti paling banyak air: perkiraan curah tahunan terbesar ada di <b>{wet.Location}</b> "
        f"(&asymp; {idn(wet.est_annual_mm, 0)} mm, estimated), dengan {idn(wet.mean_mm_rain_day)} mm per hari hujan.",
        f"Musim memengaruhi pola dan polanya berbeda antar zona. Kontras terbesar, zona {season_swing(swing.index[0])}; "
        f"berikutnya zona {season_swing(swing.index[1])}. "
        f"Zona Tropis utara dibaca sebagai musim basah (Nov-Apr) {idn(pw)}% vs kering (Mei-Okt) {idn(pdr)}%.",
        f"Sebelum hujan, Humidity3pm rata-rata <b>{idn(abs(d_h))} poin lebih tinggi</b>, Pressure3pm {idn(abs(d_p))} hPa lebih rendah, "
        f"Sunshine {idn(abs(d_s))} jam lebih sedikit, dan Cloud3pm {idn(abs(d_c))} oktas lebih tinggi "
        f"(Sunshine dan Cloud3pm hanya dari lokasi yang mencatatnya).",
        f"Jika hari ini hujan, peluang hujan besok <b>{idn(persall.p_rain_tomorrow_if_rain_today)}%</b> vs {idn(persall.p_rain_tomorrow_if_dry_today)}% "
        f"jika tidak, yaitu <b>{idn(persall.ratio, 2)} kali</b> lebih besar.",
        f"Aturan Humidity3pm &ge; 70: akurasi {idn(r70.accuracy)}% vs baseline {idn(r70.baseline_accuracy)}% "
        f"(selisih {idn(gap70)} poin), tetapi hanya {idn(r70.recall)}% hari hujan tertangkap "
        f"dan {idn(r70.warn_pct)}% hari diberi peringatan (estimated, in-sample).",
    ]

    n_loc = len(locs)
    meta = pd.read_csv(RAW_CSV, usecols=["Date"], parse_dates=["Date"])
    n_rows, d0, d1 = len(meta), meta["Date"].min(), meta["Date"].max()

    D = {
        "locs": [[l, zone_of[l]] for l in locs],
        "ls": rows(ls, ["Location", "season", "n_obs", "rain_days", "sum_mm_rain_days"]),
        "m": rows(month, ["Location", "month", "n_obs", "rain_days"]),
        "ly": rows(ly, ["Location", "year", "n_obs", "rain_days"]),
        "cond": rows(cond, ["Location", "season", "variable", "rain_tomorrow_i", "n", "sum_val"]),
        "rule": rows(rule, ["Location", "season", "threshold", "tp", "fp", "fn", "tn"]),
        "pers": rows(pers, ["Location", "season", "today_yes_n", "tomorrow_yes_given_yes", "today_no_n", "tomorrow_yes_given_no"]),
        "wd": rows(wd, ["Location", "wet_dry", "n_obs", "rain_days"]),
        "rank": rows(rank, ["Location", "climate_zone", "n_obs", "rain_days", "pct_rain", "mean_mm_rain_day", "est_annual_mm"]),
        "sched": rows(sched, ["Location", "month", "n_obs", "pct_rain"]),
        "g": {
            "tag": f"weatherAUS: {n_rows:,} baris, {n_loc} lokasi, {d0:%Y-%m} s/d {d1:%Y-%m}".replace(",", "."),
            "findings": findings,
            "kpiAll": {f"k{i}": float(k[f"K{i}"]) for i in range(1, 6)},
            "heatMax": float(month["pct_rain"].max()),
            "windDir": rows(wdir, ["WindGustDir", "n", "pct_rain_tomorrow"]),
            "windSpeed": [[re.sub(r"^\d: ", "", r[0]), r[1], r[2]] for r in rows(wspd, ["gust_kmh_bin", "n", "pct_rain_tomorrow"])],
            "period": pr,
            "missing": miss,
            "missNote": miss_note,
            "sens": sens_rows,
            "xcheck": xcheck,
            "footer": "Data: weatherAUS (Kaggle, 'Rain in Australia'), pengamatan Bureau of Meteorology Australia. "
                      "Semua angka dihitung dari data oleh SQL (DuckDB) dan dicek silang dengan pandas. "
                      "Ketepatan aturan praktis berlabel estimated. Cek lisensi dataset sebelum dipublikasikan.",
        },
    }

    template = (CODE / "3-presentation" / "html" / "dashboard_template.html").read_text(encoding="utf-8")
    blob = json.dumps(D, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert "/*__DATA__*/null" in template
    html = template.replace("/*__DATA__*/null", blob, 1)
    out = RES_PRESENT / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"results/3-presentation/dashboard.html ditulis ({out.stat().st_size / 1024:.0f} KB)")

    verify_in_node(blob, template, kpi)


def verify_in_node(blob: str, template: str, kpi: pd.Series) -> None:
    """Jalankan blok CALC di Node dan bandingkan dengan kpi_overall.csv."""
    if not shutil.which("node"):
        print("PERINGATAN: node tidak ditemukan, verifikasi blok CALC dilewati")
        return
    calc = template.split("/* CALC START")[1].split("*/", 1)[1].split("/* CALC END */")[0]
    js = (f"const D={blob};\n{calc}\n"
          "const S=new Set(D.locs.map(l=>l[0]));\n"
          "console.log(JSON.stringify(calcKPI(D,S,'ALL')));\n")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "calc_check.js"
        p.write_text(js, encoding="utf-8")
        res = subprocess.run(["node", str(p)], capture_output=True, text=True, timeout=60)
    if res.returncode:
        raise SystemExit("Node gagal:\n" + res.stderr)
    got = json.loads(res.stdout)
    want = {"k1": kpi["K1"], "k2": kpi["K2"], "k3": kpi["K3"], "k4": kpi["K4"], "k5": kpi["K5"]}
    tol = {"k1": 0.005, "k2": 0.005, "k3": 0.005, "k4": 0.0005, "k5": 0.005}
    for key in want:
        d = abs(got[key] - want[key])
        status = "OK" if d <= tol[key] + 1e-9 else "BEDA"
        print(f"  verifikasi dashboard {key}: JS {got[key]:.4f} vs CSV {want[key]:.4f}  [{status}]")
        if status != "OK":
            raise SystemExit("Hitungan dashboard tidak cocok dengan kpi_overall.csv")


if __name__ == "__main__":
    main()
