"""Board and Skrzypacz (2016) on US consumer prices: do goods with a season fall in price toward its end,
and do they fall further when stores are carrying more stock?

Three parts.
  1. The model. Solves the paper's single-unit cutoff equation (its eq. 7) for the parameters of its
     Figure 3, so the formula in the README can be checked.
  2. Prices over the season. Builds the average within-year price profile of 25 CPI items, 2000-2025,
     and compares goods sold in seasons (apparel, footwear) with staples that have no season.
  3. Inventory. Relates the stock that US clothing stores carry into each clearance period to how far
     apparel prices fall during it, 1993-2026.

Raw files are committed in data/raw/. If one is missing the script downloads it again (BLS public API
v1, which needs no key, and FRED's fredgraph.csv endpoint).

Usage (from the repository root):
    python src/markdowns.py
"""

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"
UA = {"User-Agent": "Brendyn Beasley research 83249437+brendynbeasley@users.noreply.github.com"}

# CPI-U, US city average, not seasonally adjusted. Names are from BLS's cu.item file. Groups were fixed
# before looking at any prices: "season" goods are sold in fall and spring assortments that are replaced
# each season; "staple" goods are bought all year with no assortment change; "other" goods have a model
# year or a gift season but not two clearance periods a year.
ITEMS = {
    "SEAA01": ("Men's suits, sport coats, and outerwear", "season"),
    "SEAA03": ("Men's shirts and sweaters", "season"),
    "SEAA04": ("Men's pants and shorts", "season"),
    "SEAA02": ("Men's underwear, nightwear, swimwear and accessories", "season"),
    "SEAB": ("Boys' apparel", "season"),
    "SEAC01": ("Women's outerwear", "season"),
    "SEAC02": ("Women's dresses", "season"),
    "SEAC03": ("Women's suits and separates", "season"),
    "SEAC04": ("Women's underwear, nightwear, swimwear and accessories", "season"),
    "SEAD": ("Girls' apparel", "season"),
    "SEAF": ("Infants' and toddlers' apparel", "season"),
    "SEAE01": ("Men's footwear", "season"),
    "SEAE02": ("Boys' and girls' footwear", "season"),
    "SEAE03": ("Women's footwear", "season"),
    "SEHN01": ("Household cleaning products", "staple"),
    "SEHN02": ("Household paper products", "staple"),
    "SEGB": ("Personal care products", "staple"),
    "SEGA": ("Tobacco and smoking products", "staple"),
    "SETA01": ("New vehicles", "other"),
    "SERE01": ("Toys", "other"),
    "SERC": ("Sporting goods", "other"),
    "SEHJ": ("Furniture and bedding", "other"),
    "SEHL": ("Other household equipment and furnishings", "other"),
    "SEAG01": ("Watches", "other"),
    "SEAG02": ("Jewelry", "other"),
}
PROFILE_YEARS = (2000, 2025)      # full calendar years used for the seasonal profiles
BLS_WINDOWS = [(2000, 2009), (2010, 2019), (2020, 2026)]  # API v1 allows ten years per request
FRED = {
    "CPIAPPNS": "CPI-U apparel, not seasonally adjusted (1982-84=100)",
    "MRTSIM448USN": "Clothing and accessories stores, end-of-month inventories, NSA ($ millions)",
    "MRTSSM448USN": "Clothing and accessories stores, monthly sales, NSA ($ millions)",
}
# Clearance windows, from the paper's own example (coats bought in autumn, cleared in January) and the
# mirror-image spring season. Stock is measured at the end of the month before clearance starts.
SEASONS = {"fall": {"stock_month": 10, "start": 10, "end": 1},     # end-Oct stock; Oct -> Jan prices
           "spring": {"stock_month": 4, "start": 4, "end": 7}}     # end-Apr stock; Apr -> Jul prices
COVID = {(2020, "spring"), (2020, "fall"), (2021, "spring")}       # store closures and reopening

# Board and Skrzypacz (2016), Figure 3: Poisson arrivals with rate 10 per season, values U[0,1],
# season length T = 1, interest rate r = ln(4/3) ("a good loses one-fourth of its value over the season").
FIG3 = {"lam": 10.0, "r": np.log(4 / 3), "T": 1.0}


# ----------------------------------------------------------------------------------------------- data

def fetch_cpi(path):
    rows = []
    for y0, y1 in BLS_WINDOWS:
        body = {"seriesid": ["CUUR0000" + c for c in ITEMS], "startyear": str(y0), "endyear": str(y1)}
        r = requests.post("https://api.bls.gov/publicAPI/v1/timeseries/data/", json=body, headers=UA,
                          timeout=60)
        d = r.json()
        if d.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS API: {d.get('status')} {d.get('message')}")
        for s in d["Results"]["series"]:
            for obs in s["data"]:
                if obs["period"].startswith("M") and obs["period"] != "M13" and obs["value"] != "-":
                    rows.append((s["seriesID"][8:], int(obs["year"]), int(obs["period"][1:]),
                                 float(obs["value"])))
        time.sleep(2)
    df = pd.DataFrame(rows, columns=["item", "year", "month", "index"]).sort_values(["item", "year", "month"])
    df.to_csv(path, index=False)


def load_cpi():
    path = RAW / "bls_cpi_items.csv"
    if not path.exists():
        print("downloading CPI item indexes from the BLS public API ...")
        fetch_cpi(path)
    df = pd.read_csv(path)
    print(f"loaded {path.relative_to(ROOT)}: {len(df):,} monthly observations, {df.item.nunique()} items, "
          f"{df.year.min()}-{df.year.max()}")
    return df


def load_fred(sid):
    path = RAW / f"fred_{sid}.csv"
    if not path.exists():
        print(f"downloading {sid} from FRED ...")
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
    s = pd.read_csv(path, parse_dates=["observation_date"]).set_index("observation_date")[sid]
    s = pd.to_numeric(s, errors="coerce").dropna()
    print(f"loaded {path.relative_to(ROOT)}: {len(s)} months, {s.index.min():%Y-%m} to {s.index.max():%Y-%m}")
    return s


# ---------------------------------------------------------------------------------------------- model

def cutoff_one_unit(lam, r):
    """Eq. (7) with values U[0,1], so m(v) = 2v - 1 and E[max(m(v) - m(x), 0)] = (1 - x)^2.
    Solves r (2x - 1) = lam (1 - x)^2 for the constant cutoff x* before the deadline."""
    return optimize.brentq(lambda x: r * (2 * x - 1) - lam * (1 - x) ** 2, 0.5, 1.0)


def model_table():
    rows = []
    for lam in [1, 2, 5, 10, 20, 50]:
        x = cutoff_one_unit(lam, FIG3["r"])
        rows.append({"arrivals_per_season": lam, "cutoff_before_deadline": x, "cutoff_at_deadline": 0.5,
                     "share_of_entrants_who_clear_cutoff": 1 - x,
                     "expected_qualifying_arrivals": lam * (1 - x)})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "model_cutoffs.csv", index=False, float_format="%.4f")
    x = t.set_index("arrivals_per_season").loc[10.0, "cutoff_before_deadline"]
    print(f"model: Figure 3 parameters (lam=10, r=ln(4/3)) give a constant cutoff x* = {x:.4f} before the "
          f"deadline, dropping to 0.5 at it")
    return t


# ---------------------------------------------------------------------------------- seasonal profiles

def seasonal_profiles(cpi):
    """Ratio-to-moving-average: log index minus its centered 12-month (2x12) moving average, averaged by
    calendar month over PROFILE_YEARS. Gives each item's typical position in its own year, in percent."""
    out, yearly = [], []
    for item, g in cpi.groupby("item"):
        # Reindex to a full monthly grid so a missing month (BLS published no October 2025 index after the
        # federal shutdown) leaves gaps instead of shifting the moving average.
        grid = pd.MultiIndex.from_product([range(g.year.min(), g.year.max() + 1), range(1, 13)],
                                          names=["year", "month"])
        g = g.set_index(["year", "month"]).reindex(grid).reset_index()
        last = g["index"].last_valid_index()
        g = g.loc[:last]
        ly = np.log(g["index"])
        ma = ly.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
        g["dev"] = 100 * (ly - ma)
        g["chg"] = 100 * ly.diff()
        keep = g[g.year.between(*PROFILE_YEARS)].dropna(subset=["dev"])
        prof = keep.groupby("month").agg(dev=("dev", "mean"), chg=("chg", "mean"))
        name, group = ITEMS[item]
        amp_by_year = keep.groupby("year").dev.agg(lambda d: d.max() - d.min())
        months_down = int((prof.chg < 0).sum())
        out.append({"item": item, "name": name, "group": group,
                    "amplitude_pct": prof.dev.max() - prof.dev.min(),
                    "peak_month": int(prof.dev.idxmax()), "trough_month": int(prof.dev.idxmin()),
                    "months_with_avg_decline": months_down,
                    "median_yearly_amplitude_pct": amp_by_year.median(),
                    "years": int(keep.year.nunique()),
                    **{f"m{m:02d}": prof.dev.get(m, np.nan) for m in range(1, 13)}})
        for y, a in amp_by_year.items():
            yearly.append({"item": item, "group": group, "year": y, "amplitude_pct": a})
    prof = pd.DataFrame(out).sort_values(["group", "amplitude_pct"], ascending=[True, False])
    prof.to_csv(OUT / "seasonal_profiles.csv", index=False, float_format="%.5f")
    # Season-end drops implied by the profiles: October to January (fall) and March to July (spring),
    # with what a $200 item at the October price would cost in January.
    drops = prof[["item", "name", "group"]].copy()
    drops["fall_oct_to_jan_pct"] = 100 * (np.exp((prof.m01 - prof.m10) / 100) - 1)
    drops["spring_mar_to_jul_pct"] = 100 * (np.exp((prof.m07 - prof.m03) / 100) - 1)
    drops["oct_200_in_january"] = 200 * np.exp((prof.m01 - prof.m10) / 100)
    drops.to_csv(OUT / "season_end_drops.csv", index=False, float_format="%.4f")
    print(f"profiles: {len(prof)} items, {PROFILE_YEARS[0]}-{PROFILE_YEARS[1]}")
    return prof, pd.DataFrame(yearly)


def compare_groups(prof, yearly):
    s = prof[prof.group == "season"].amplitude_pct
    st = prof[prof.group == "staple"].amplitude_pct
    o = prof[prof.group == "other"].amplitude_pct
    mw = stats.mannwhitneyu(s, st, alternative="greater")
    wt = stats.ttest_ind(s, st, equal_var=False)
    # Year-by-year: amplitude on a season dummy, errors clustered by item.
    y = yearly[yearly.group.isin(["season", "staple"])].copy()
    y["season"] = (y.group == "season").astype(int)
    fit = smf.ols("amplitude_pct ~ season", data=y).fit(cov_type="cluster", cov_kwds={"groups": y.item})
    rows = [
        {"comparison": "mean amplitude, season goods (%)", "value": s.mean(), "n": len(s)},
        {"comparison": "mean amplitude, staples (%)", "value": st.mean(), "n": len(st)},
        {"comparison": "mean amplitude, other goods (%)", "value": o.mean(), "n": len(o)},
        {"comparison": "smallest season-good amplitude (%)", "value": s.min(), "n": len(s)},
        {"comparison": "largest staple amplitude (%)", "value": st.max(), "n": len(st)},
        {"comparison": "Mann-Whitney U (season > staple)", "value": mw.statistic, "p": mw.pvalue},
        {"comparison": "Welch t (season - staple)", "value": wt.statistic, "p": wt.pvalue},
        {"comparison": "item-year regression: season dummy (pct points)", "value": fit.params["season"],
         "se": fit.bse["season"], "p": fit.pvalues["season"], "n": int(fit.nobs),
         "ci_low": fit.conf_int().loc["season", 0], "ci_high": fit.conf_int().loc["season", 1]},
    ]
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "group_comparison.csv", index=False, float_format="%.6f")
    print(f"amplitude: season goods {s.mean():.2f}% (n={len(s)}) vs staples {st.mean():.2f}% (n={len(st)}); "
          f"Mann-Whitney p = {mw.pvalue:.4f}; item-year season coef {fit.params['season']:.2f} "
          f"(clustered p = {fit.pvalues['season']:.2g})")
    return t


def apparel_path(app):
    """Average monthly log change in the apparel index by calendar month, 2000-2025, with a 95% interval
    across years. Tests whether markdowns accelerate toward the end of each season."""
    app = app.asfreq("MS")   # missing months become gaps, so no change spans two months
    d = pd.DataFrame({"chg": 100 * np.log(app).diff()})
    d["year"], d["month"] = d.index.year, d.index.month
    d = d[d.year.between(*PROFILE_YEARS)].dropna()
    rows = []
    for m, g in d.groupby("month"):
        se = g.chg.std(ddof=1) / np.sqrt(len(g))
        tcrit = stats.t.ppf(0.975, len(g) - 1)
        rows.append({"month": m, "mean_change_pct": g.chg.mean(), "ci_low": g.chg.mean() - tcrit * se,
                     "ci_high": g.chg.mean() + tcrit * se, "share_of_years_down": (g.chg < 0).mean(),
                     "years": len(g)})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "apparel_monthly_changes.csv", index=False, float_format="%.5f")
    # Acceleration: is the last clearance month's fall bigger than the first in-season month's?
    acc = []
    for season, early, late in [("fall", 11, 1), ("spring", 5, 7)]:
        e = d[d.month == early].set_index("year").chg
        l = d[d.month == late].set_index("year").chg
        if season == "fall":
            l.index = l.index - 1   # January belongs to the previous year's fall season
        both = pd.concat([e, l], axis=1, keys=["early", "late"]).dropna()
        tt = stats.ttest_rel(both.late, both.early)
        acc.append({"season": season, "early_month": early, "late_month": late,
                    "early_mean": both.early.mean(), "late_mean": both.late.mean(),
                    "late_minus_early": (both.late - both.early).mean(), "t": tt.statistic, "p": tt.pvalue,
                    "years": len(both)})
    acc = pd.DataFrame(acc)
    acc.to_csv(OUT / "markdown_acceleration.csv", index=False, float_format="%.4f")
    print("apparel monthly changes:", " ".join(f"{int(r.month)}:{r.mean_change_pct:+.2f}" for r in t.itertuples()))
    return t, acc


# -------------------------------------------------------------------------------------- inventory test

def inventory_panel(app, inv, sales):
    """One row per clearance period. Stock overhang = 12-month log growth of end-of-month inventories
    minus 12-month log growth of sales over the three months to the stock month. Markdown = log change in
    the apparel CPI from the stock month to the end of clearance."""
    sales3 = sales.rolling(3).sum()
    rows = []
    for y in range(1993, 2027):
        for season, p in SEASONS.items():
            t0 = pd.Timestamp(y, p["stock_month"], 1)
            t1 = pd.Timestamp(y + 1 if p["end"] < p["start"] else y, p["end"], 1)
            ago = t0 - pd.DateOffset(years=1)
            need = [t0 in inv.index, ago in inv.index, t0 in sales3.index, ago in sales3.index,
                    t0 in app.index, t1 in app.index, ago in app.index]
            if not all(need) or pd.isna(sales3.get(ago)):
                continue
            rows.append({
                "season_year": y, "season": season, "label": f"{season} {y}",
                "inv_growth": 100 * np.log(inv[t0] / inv[ago]),
                "sales_growth": 100 * np.log(sales3[t0] / sales3[ago]),
                "is_ratio": inv[t0] / sales[t0],
                "markdown_pct": 100 * np.log(app[t1] / app[t0]),
                "apparel_inflation_prior12": 100 * np.log(app[t0] / app[ago]),
                "covid": (y, season) in COVID,
            })
    d = pd.DataFrame(rows)
    d["overhang"] = d.inv_growth - d.sales_growth
    # Secondary measure, added after the primary one came back flat: log inventory/sales ratio in the stock
    # month relative to its average over the previous three years' same-season stock months.
    lis = np.log(d.is_ratio)
    d["ratio_dev"] = 100 * (lis - lis.groupby(d.season).transform(lambda x: x.rolling(3).mean().shift(1)))
    d.to_csv(OUT / "inventory_seasons.csv", index=False, float_format="%.3f")
    print(f"inventory panel: {len(d)} clearance periods ({d.label.iloc[0]} to {d.label.iloc[-1]}); "
          f"{int(d.covid.sum())} flagged as pandemic periods")
    return d


def inventory_tests(d):
    specs = [
        ("all periods", d, "markdown_pct ~ overhang + C(season)"),
        ("all periods, prior inflation control", d,
         "markdown_pct ~ overhang + C(season) + apparel_inflation_prior12"),
        ("excluding 2020-21", d[~d.covid], "markdown_pct ~ overhang + C(season)"),
        ("excluding 2020-21, prior inflation control", d[~d.covid],
         "markdown_pct ~ overhang + C(season) + apparel_inflation_prior12"),
        ("fall only, excluding 2020-21", d[(d.season == "fall") & ~d.covid], "markdown_pct ~ overhang"),
        ("spring only, excluding 2020-21", d[(d.season == "spring") & ~d.covid], "markdown_pct ~ overhang"),
        ("secondary: ratio deviation, excluding 2020-21", d[~d.covid], "markdown_pct ~ ratio_dev + C(season)"),
        ("secondary: ratio deviation, excl. 2020-21, inflation control", d[~d.covid],
         "markdown_pct ~ ratio_dev + C(season) + apparel_inflation_prior12"),
        ("secondary: ratio deviation, all periods, inflation control", d,
         "markdown_pct ~ ratio_dev + C(season) + apparel_inflation_prior12"),
    ]
    rows = []
    for name, data, f in specs:
        x = "ratio_dev" if "ratio_dev" in f else "overhang"
        data = data.dropna(subset=[x])
        fit = smf.ols(f, data=data).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
        ci = fit.conf_int().loc[x]
        rows.append({"sample": name, "measure": x, "slope": fit.params[x], "se": fit.bse[x],
                     "ci_low": ci[0], "ci_high": ci[1], "p": fit.pvalues[x], "n": int(fit.nobs),
                     "r2": fit.rsquared})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "inventory_regressions.csv", index=False, float_format="%.6f")
    for r in t.itertuples():
        print(f"  {r.sample:60s} slope {r.slope:+.3f} (se {r.se:.3f}, p {r.p:.3f}, n {r.n})")
    # Terciles of overhang, non-pandemic periods: average markdown relative to that season's mean
    e = d[~d.covid].copy()
    e["markdown_vs_season_mean"] = e.markdown_pct - e.groupby("season").markdown_pct.transform("mean")
    e["tercile"] = pd.qcut(e.overhang, 3, labels=["lean stock", "middle", "heavy stock"])
    ter = e.groupby("tercile", observed=True).agg(periods=("label", "size"), overhang=("overhang", "mean"),
                                                  markdown_vs_season_mean=("markdown_vs_season_mean", "mean"),
                                                  markdown_pct=("markdown_pct", "mean")).reset_index()
    ter.to_csv(OUT / "inventory_terciles.csv", index=False, float_format="%.5f")
    # Long run: stock carried and size of the sale by era (pandemic seasons left out)
    e["era"] = pd.cut(e.season_year, [1992, 1999, 2009, 2019, 2026], labels=["1993-99", "2000-09", "2010-19",
                                                                             "2021-26"])
    era = e.groupby(["era", "season"], observed=True).agg(periods=("label", "size"),
                                                          inventory_to_sales=("is_ratio", "mean"),
                                                          markdown_pct=("markdown_pct", "mean")).reset_index()
    era.to_csv(OUT / "inventory_eras.csv", index=False, float_format="%.5f")
    print(era.to_string(index=False))
    return t, ter


# ------------------------------------------------------------------------------------------- figures

def fig_profiles(prof):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    months = [f"m{m:02d}" for m in range(1, 13)]
    x = np.arange(1, 13)
    for code, color, lw in [("SEAC01", "#b03a2e", 2.4), ("SEAC02", "#e59866", 1.6), ("SEAA03", "#2e86c1", 1.6),
                            ("SEAE03", "#7d3c98", 1.6), ("SEHN02", "#555555", 2.0), ("SEGB", "#999999", 2.0)]:
        r = prof.set_index("item").loc[code]
        ax.plot(x, r[months].astype(float).values, color=color, lw=lw, marker="o", ms=3, label=r["name"])
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(x, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.set_ylabel("Price vs. its own 12-month average (%)")
    ax.set_title("Typical price through the year, US CPI, 2000-2025")
    ax.set_ylim(-13, 14)
    ax.legend(fontsize=8, frameon=False, loc="upper left", ncol=3)
    fig.tight_layout()
    fig.savefig(OUT / "seasonal_profiles.png", dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    model_table()
    cpi = load_cpi()
    before = len(cpi)
    cpi = cpi[cpi["item"].isin(ITEMS)]
    print(f"kept {len(cpi):,} of {before:,} CPI rows (items outside the list dropped: {before - len(cpi)})")
    prof, yearly = seasonal_profiles(cpi)
    compare_groups(prof, yearly)
    app = load_fred("CPIAPPNS")
    inv = load_fred("MRTSIM448USN")
    sales = load_fred("MRTSSM448USN")
    apparel_path(app)
    d = inventory_panel(app, inv, sales)
    inventory_tests(d)
    fig_profiles(prof)
    with open(OUT / "sources_markdowns.json", "w") as f:
        json.dump({"bls_items": {k: v[0] for k, v in ITEMS.items()}, "fred": FRED}, f, indent=1)
    print(f"wrote results to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
