"""The inventory prediction across kinds of store: when a retail trade carries more stock than its sales
justify, does its gross margin fall the following year?

Board and Skrzypacz (2016) show that the optimal selling cutoffs fall as remaining inventory rises, so a
seller holding extra stock should mark down sooner and deeper. Markdowns are invisible in most data, but
they lower gross margin (sales minus the cost of the goods sold, as a share of sales). The Census Bureau's
Annual Retail Trade Survey publishes gross margin, end-of-year inventories and sales for each kind of
retail business every year, 1993-2022.

Data: www2.census.gov/programs-surveys/arts/tables/2022/ files gmper.xlsx, invent.xlsx and sales.xlsx,
committed in data/raw/census_arts/ (downloaded again if missing).

Usage (from the repository root):
    python src/retail_margins.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "census_arts"
OUT = ROOT / "results"
BASE = "https://www2.census.gov/programs-surveys/arts/tables/2022/"

# The most detailed kinds of business published in all three tables (no code here contains another).
# Chosen before looking at results. "season" marks the trades that buy seasonal assortments of apparel,
# footwear and sporting goods and clear them with markdowns; well-known chains are listed for orientation.
KINDS = {
    "4411": ("Automobile dealers", "other", ""),
    "4413": ("Auto parts and tire stores", "other", ""),
    "442": ("Furniture and home furnishings stores", "other", ""),
    "443": ("Electronics and appliance stores", "other", ""),
    "4441": ("Building materials dealers", "other", ""),
    "4451": ("Grocery stores", "other", ""),
    "4453": ("Beer, wine and liquor stores", "other", ""),
    "44611": ("Pharmacies and drug stores", "other", ""),
    "447": ("Gasoline stations", "other", ""),
    "44811": ("Men's clothing stores", "season", "Men's Wearhouse"),
    "44812": ("Women's clothing stores", "season", "Chico's, Ann Taylor"),
    "44814": ("Family clothing stores", "season", "Gap, Old Navy, TJX, Ross, Burlington"),
    "4482": ("Shoe stores", "season", "Foot Locker, DSW"),
    "4511": ("Sporting goods, hobby and music stores", "season", "Dick's Sporting Goods"),
    "4521": ("Department stores", "season", "Macy's, Kohl's, Nordstrom, Dillard's"),
    "4529": ("Other general merchandise stores", "other", ""),
    "453": ("Miscellaneous store retailers", "other", ""),
    "4541": ("Electronic shopping and mail order", "other", ""),
}
PANDEMIC_YEARS = [2020, 2021]   # store closures and the reopening rebound, dropped in robustness rows
WINSOR = (0.02, 0.98)           # trims the most extreme kind-years before regressions


def load_table(name):
    path = RAW / f"{name}.xlsx"
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        print(f"downloading {name}.xlsx from the Census Bureau ...")
        r = requests.get(BASE + f"{name}.xlsx", timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
    x = pd.read_excel(path, header=None, engine="openpyxl")
    years = [int(float(str(c).rstrip("r"))) for c in x.iloc[3, 2:]]
    body = x.iloc[4:, :].copy()
    body = body[body[0].notna() & body[0].astype(str).str.fullmatch(r"\d{3,6}")]
    body.index = body[0].astype(str)
    values = body.iloc[:, 2:].apply(pd.to_numeric, errors="coerce")   # "S" (suppressed) becomes missing
    values.columns = years
    long = values.stack().rename(name).reset_index()
    long.columns = ["naics", "year", name]
    print(f"loaded {path.relative_to(ROOT)}: {len(body)} kinds of business, {min(years)}-{max(years)}, "
          f"{int(values.isna().sum().sum())} suppressed or blank cells")
    return long


def build_panel():
    d = load_table("gmper").merge(load_table("invent"), on=["naics", "year"], how="outer")
    d = d.merge(load_table("sales"), on=["naics", "year"], how="outer")
    n0 = d.naics.nunique()
    d = d[d.naics.isin(KINDS)].copy()
    print(f"kept {d.naics.nunique()} of {n0} kinds of business (the most detailed published in all three "
          f"tables); dropped parents and kinds missing from a table")
    d["kind"] = d.naics.map(lambda c: KINDS[c][0])
    d["group"] = d.naics.map(lambda c: KINDS[c][1])
    d = d.sort_values(["naics", "year"])
    g = d.groupby("naics")
    d["inv_growth"] = 100 * np.log(d.invent / g.invent.shift(1))
    d["sales_growth"] = 100 * np.log(d.sales / g.sales.shift(1))
    d["overhang"] = d.inv_growth - d.sales_growth
    d["inv_to_sales_months"] = 12 * d.invent / d.sales
    d["d_gm"] = d.gmper - g.gmper.shift(1)
    d["d_gm_next"] = g.d_gm.shift(-1)
    d.to_csv(OUT / "retail_kinds_panel.csv", index=False, float_format="%.3f")
    return d


def winsor(s):
    return s.clip(s.quantile(WINSOR[0]), s.quantile(WINSOR[1]))


def regressions(d):
    e = d.dropna(subset=["overhang", "d_gm_next", "d_gm"]).copy()
    print(f"regression sample: {len(e)} kind-years with an overhang, this year's and next year's margin change "
          f"({e.year.min()}-{e.year.max()} overhang years); dropped {len(d) - len(e)} kind-years")
    for c in ["overhang", "d_gm_next", "d_gm"]:
        e[c] = winsor(e[c])
    e["season"] = (e.group == "season").astype(int)
    no_pan = e[~e.year.isin(PANDEMIC_YEARS) & ~(e.year + 1).isin(PANDEMIC_YEARS)]
    specs = [
        ("all kinds, next-year margin, year effects", e, "d_gm_next ~ overhang + C(year)", "overhang"),
        ("all kinds, same-year margin, year effects", e, "d_gm ~ overhang + C(year)", "overhang"),
        ("all kinds, next-year, excluding pandemic years", no_pan, "d_gm_next ~ overhang + C(year)", "overhang"),
        ("season trades only, next-year, year effects", e[e.season == 1], "d_gm_next ~ overhang + C(year)",
         "overhang"),
        ("other trades only, next-year, year effects", e[e.season == 0], "d_gm_next ~ overhang + C(year)",
         "overhang"),
        ("all kinds, next-year, season interaction", e, "d_gm_next ~ overhang * season + C(year)",
         "overhang:season"),
    ]
    rows = []
    for name, data, f, term in specs:
        fit = smf.ols(f, data=data).fit(cov_type="cluster", cov_kwds={"groups": data.naics})
        ci = fit.conf_int().loc[term]
        rows.append({"spec": name, "term": term, "slope": fit.params[term], "se": fit.bse[term],
                     "ci_low": ci[0], "ci_high": ci[1], "p": fit.pvalues[term], "n": int(fit.nobs),
                     "kinds": data.naics.nunique()})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "retail_regressions.csv", index=False, float_format="%.6f")
    for r in t.itertuples():
        print(f"  {r.spec:50s} {r.term:16s} {r.slope:+.4f} (se {r.se:.4f}, p {r.p:.3f}, n {r.n}, {r.kinds} kinds)")
    return e, t


def binned(e):
    e = e.copy()
    e["bin"] = pd.qcut(e.overhang, 5, labels=["leanest fifth", "second", "middle", "fourth", "heaviest fifth"])
    b = e.groupby("bin", observed=True).agg(kind_years=("naics", "size"), overhang=("overhang", "median"),
                                            d_gm_next_mean=("d_gm_next", "mean"),
                                            share_margin_down=("d_gm_next", lambda x: (x < 0).mean())).reset_index()
    b.to_csv(OUT / "retail_bins.csv", index=False, float_format="%.3f")
    print(b.to_string(index=False))
    return b


def named_table(d):
    """Season trades around the pandemic: stock and margins in 2019, 2021 (stock ran short) and 2022 (stock
    piled up), against each trade's 1993-2019 average margin. This release ends in 2022, so the margin
    response to the 2022 stock position is not yet observed."""
    rows = []
    for code, (kind, group, chains) in KINDS.items():
        if group != "season":
            continue
        g = d[d.naics == code].set_index("year")
        row = {"naics": code, "kind": kind, "chains": chains,
               "gm_1993_2019_mean": g.loc[1993:2019, "gmper"].mean()}
        for y in [2019, 2021, 2022]:
            row[f"overhang_{y}"] = g.loc[y, "overhang"]
            row[f"gm_{y}"] = g.loc[y, "gmper"]
        row["gm_change_2022"] = g.loc[2022, "gmper"] - g.loc[2021, "gmper"]
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "retail_named.csv", index=False, float_format="%.2f")
    return t


def figure(e, b):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for group, color, label in [("other", "#aaaaaa", "other kinds of store"),
                                ("season", "#b03a2e", "clothing, shoe, sporting goods, department stores")]:
        g = e[e.group == group]
        ax.scatter(g.overhang, g.d_gm_next, s=12, color=color, alpha=0.7, label=label)
    ax.plot(b.overhang, b.d_gm_next_mean, color="black", marker="s", lw=1.5, label="average by fifth of stock")
    ax.axhline(0, color="black", lw=0.5)
    ax.axvline(0, color="black", lw=0.5)
    ax.set_xlabel("Stock overhang this year: inventory growth minus sales growth (log points)")
    ax.set_ylabel("Change in gross margin next year (points)")
    ax.set_title("Retail stock and next year's gross margin, 18 kinds of store, 1994-2021", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "retail_margins.png", dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    d = build_panel()
    e, _ = regressions(d)
    b = binned(e)
    named_table(d)
    figure(e, b)
    print(f"wrote results to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
