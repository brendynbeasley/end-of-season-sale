# Technical notes

Technical companion to the [README](README.md). Every table is in
[results/FINDINGS.md](results/FINDINGS.md), and every number comes from a CSV in `results/`.

## The original study

Simon Board and Andrzej Skrzypacz, "Revenue Management with Forward-Looking Buyers," *Journal of Political
Economy* 124(4), 2016, pp. 1046–1087. A seller must sell K units by a deadline T to buyers who arrive over
time with private values and can wait. With commitment, the optimal mechanism awards a unit to the highest
remaining buyer whose value clears a cutoff that depends only on inventory and time (Theorem 1). Cutoffs
fall as inventory rises, and fall over time when entry is weakly decreasing (Theorem 2). In continuous
time the optimum is implemented by posted prices with a second-price auction for the last unit at T
(Theorem 3). The conclusion states that with uniform entry and fixed inventory, "prices should be
decreasing and concave." The paper reports no estimates. Its numerical illustration (Figures 3 to 5) uses
Poisson entry at λ = 10 per season, values U[0, 1] (static monopoly cutoff 0.5), T = 1 and r = ln(4/3).

## Headline results

| Test | Result |
|---|---|
| Single-unit cutoff, eq. (7), Figure 3 parameters | x* = 0.857 before T, 0.5 at T |
| Within-year price swing, 14 season goods vs 4 staples, 2000–2025 | 7.68% vs 0.51%; Mann-Whitney p = 0.0003 |
| Same, item-year regression (468 item-years) | +7.70 points, SE 1.46, clustered p < 0.001 |
| Spring markdown acceleration, July minus May change | −1.33 points, t = −5.80, 26 years |
| Fall markdown acceleration, January minus November change | +1.07 points, t = 2.02, p = 0.054, 25 years |
| Aggregate stock overhang on clearance price change, excl. 2020–21 | +0.018 per point, p = 0.73, n = 63 |
| Retail trades: overhang on next-year gross-margin change, year effects | −0.070 points per log point, SE 0.028, p = 0.014, N = 489 |

## Data

| File | Source | Content |
|---|---|---|
| `data/raw/bls_cpi_items.csv` | BLS public data API v1, series CUUR0000 + item code | 25 CPI-U item indexes, US city average, NSA, monthly 2000–2026 |
| `data/raw/fred_CPIAPPNS.csv` | FRED `fredgraph.csv?id=CPIAPPNS` | CPI-U apparel, NSA |
| `data/raw/fred_MRTSIM448USN.csv` | FRED, Census Monthly Retail Trade Survey | End-of-month inventories, clothing and accessories stores (NAICS 448), NSA, $ millions |
| `data/raw/fred_MRTSSM448USN.csv` | FRED, Census Monthly Retail Trade Survey | Monthly sales, NAICS 448, NSA, $ millions |
| `data/raw/census_arts/gmper.xlsx`, `invent.xlsx`, `sales.xlsx` | Census Annual Retail Trade Survey, `www2.census.gov/programs-surveys/arts/tables/2022/` | Gross margin as percent of sales, end-of-year inventories, annual sales, by kind of business, 1992–2022 |

All files were downloaded on November 1, 2026. BLS published no CPI for October 2025 because of the
federal shutdown; that month is a gap, and the fall 2025 clearance is dropped from the inventory panel.
Item names come from the BLS `cu.item` file.

## Method

Rules fixed before seeing results:

- **Groups.** Season goods are 14 apparel and footwear item strata; staples are household cleaning
  products, household paper products, personal care products, and tobacco; other goods are new vehicles,
  toys, sporting goods, furniture and bedding, other household equipment, watches and jewelry.
- **Seasonal profile.** For each item, log index minus its centered 2×12 moving average, averaged by
  calendar month over 2000–2025. Amplitude is the maximum minus the minimum of the twelve monthly means.
  Year-by-year amplitude uses the same deviations within each calendar year.
- **Group tests.** One-sided Mann-Whitney U and Welch t on item amplitudes; OLS of item-year amplitude on a
  season dummy, errors clustered by item.
- **Concavity.** Mean monthly log change in the apparel CPI by calendar month, 2000–2025, with 95%
  intervals across years. Paired t-tests of the late-season against the early in-season month (July vs
  May; January vs November of the same fall season).
- **Aggregate inventory test.** One observation per clearance period, fall (stock at end-October, prices
  October to January) and spring (stock at end-April, prices April to July), 1993–2026. Overhang = 12-month
  log growth of end-of-month inventory minus 12-month log growth of three-month sales. Markdown = log change
  in the apparel CPI over the clearance. OLS with a season dummy, optionally the prior 12-month apparel
  inflation rate, Newey-West errors with 2 lags. Pandemic periods (spring and fall 2020, spring 2021)
  flagged and dropped in robustness rows.
- **Retail-trade test (extension).** Census Annual Retail Trade Survey, 2022 release, 1993–2022. The 18
  most detailed kinds of business published in all three tables (gross margin percent, end-of-year
  inventories, annual sales), so no code contains another. Overhang = 100 × (log inventory growth − log
  sales growth) over the year. Outcome = next year's change in gross margin percent. Variables winsorized
  at 2% and 98%. OLS with year fixed effects, errors clustered by kind of business. Six trades that sell
  seasonal assortments (NAICS 44811, 44812, 44814, 4482, 4511, 4521) examined separately and by
  interaction. Suppressed cells ("S") are missing. A kind-year needs an overhang and same-year and
  next-year margin changes, so overhang years run 1994–2021; 69 kind-years drop out.

The model and the three estimating equations, with $`d_{it}`$ the log deviation of item $`i`$'s index from
its centered 2×12 moving average, $`S_i`$ the season-good dummy, $`O`$ the overhang, $`M_c`$ the clearance
markdown, $`\pi_c`$ prior 12-month apparel inflation, $`G`$ gross margin percent and $`\mu_y`$ year effects:

```math
\begin{aligned}
&r\,(2x^* - 1) = \lambda\,(1 - x^*)^2 && \text{eq. (7), } v \sim U[0,1] \\
&A_{iy} = \max_k s_{iy}(k) - \min_k s_{iy}(k) = \alpha + \beta\, S_i + \varepsilon_{iy} && \text{cluster: item} \\
&M_c = \alpha + \beta\, O_c + \gamma\,\text{Spring}_c + \delta\,\pi_c + \varepsilon_c && \text{Newey-West, 2 lags} \\
&G_{k,y+1} - G_{ky} = \beta\, O_{ky} + \mu_y + \varepsilon_{ky} && \text{cluster: kind of store}
\end{aligned}
```

The null in each regression is $`\beta = 0`$; the paper predicts $`\beta > 0`$ in the first and
$`\beta < 0`$ in the other two.

Added after seeing results, and labeled as such: the aggregate inventory-to-sales-ratio deviation measure
(log ratio minus its mean in the previous three same-season stock months).

## Full test statistics

Aggregate inventory regressions (`results/inventory_regressions.csv`), slope of the clearance price change
(percent) on the stock measure (log points):

| Sample | Slope | SE | p | n |
|---|---|---|---|---|
| All periods | −0.016 | 0.016 | 0.31 | 66 |
| All periods, prior inflation control | −0.006 | 0.016 | 0.72 | 66 |
| Excluding 2020–21 | +0.018 | 0.054 | 0.73 | 63 |
| Excluding 2020–21, inflation control | +0.006 | 0.033 | 0.87 | 63 |
| Fall only, excluding 2020–21 | −0.025 | 0.076 | 0.75 | 31 |
| Spring only, excluding 2020–21 | +0.057 | 0.058 | 0.33 | 32 |
| Secondary: ratio deviation, excluding 2020–21 | −0.054 | 0.011 | < 0.001 | 57 |
| Secondary: ratio deviation, excl. 2020–21, inflation control | −0.028 | 0.013 | 0.036 | 57 |
| Secondary: ratio deviation, all periods, inflation control | 0.000 | 0.008 | 0.95 | 60 |


Retail-trade regressions (`results/retail_regressions.csv`), slope of the gross-margin change (points) on
the overhang (log points), year effects, errors clustered by kind of business:

| Specification | Slope | SE | p | n | Kinds |
|---|---|---|---|---|---|
| All kinds, next-year margin | −0.070 | 0.028 | 0.014 | 489 | 18 |
| All kinds, same-year margin | +0.091 | 0.019 | < 0.001 | 489 | 18 |
| All kinds, next-year, excluding pandemic years | −0.080 | 0.032 | 0.013 | 446 | 18 |
| Seasonal-assortment trades only, next-year | −0.061 | 0.050 | 0.22 | 158 | 6 |
| Other trades only, next-year | −0.079 | 0.035 | 0.023 | 331 | 12 |
| Overhang × seasonal-trade interaction | +0.011 | 0.056 | 0.85 | 489 | 18 |

## Reproducing the results

```bash
pip install -r requirements.txt
python src/markdowns.py
python src/retail_margins.py
```

Both scripts run offline from `data/raw/` and download any deleted raw file again (no keys needed).

The extension was first designed on chains' quarterly SEC filings. The SEC data service returned HTTP 403
to every request for more than four hours on November 1, 2026, so the Census trade-level survey, which
measures the same quantities for whole kinds of store, replaced it.

## Repository layout

| Path | What it is |
|---|---|
| [src/markdowns.py](src/markdowns.py) | Model cutoffs, seasonal profiles, group tests, concavity, aggregate inventory test |
| [src/retail_margins.py](src/retail_margins.py) | Retail-trade panel, margin regressions, bins, named table |
| [results/FINDINGS.md](results/FINDINGS.md) | Plain-English summary and every table |
| `results/*.csv`, `results/*.png` | All outputs |

## References

- Board, S. & Skrzypacz, A. (2016). Revenue management with forward-looking buyers. *Journal of Political
  Economy* 124(4), 1046–1087.
- Coase, R. (1972). Durability and monopoly. *Journal of Law and Economics* 15(1).
- Lazear, E. (1986). Retail pricing and clearance sales. *American Economic Review* 76(1), 14–32.
- McAfee, R. P. & te Velde, V. (2006). Dynamic pricing in the airline industry. In *Economics and
  Information Systems*, ed. T. Hendershott. Elsevier.
- Myerson, R. (1981). Optimal auction design. *Mathematics of Operations Research* 6(1), 58–73.
- Soysal, G. & Krishnamurthi, L. (2012). Demand dynamics in the seasonal goods industry. *Marketing
  Science* 31(2), 293–316.
- Sweeting, A. (2012). Dynamic pricing behavior in perishable goods markets: evidence from secondary
  markets for Major League Baseball tickets. *Journal of Political Economy* 120(6), 1133–1172.
