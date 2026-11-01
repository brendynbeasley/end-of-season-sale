# Board and Skrzypacz (2016) on US prices and retail books: findings

## In plain English

Board and Skrzypacz showed that a store selling a fixed stock before a deadline, to shoppers who can
wait, should let its price fall over the season, faster toward the end, and should cut deeper when it has
more left to sell. This study checks those predictions against 2000–2025 consumer prices, 1993–2026
clothing-store inventories and 1993–2022 gross margins for 18 kinds of retail business.

- **Clothing prices fall through every season; staples do not.** Women's coats sit 10.5% above their
  yearly average in October and 10.2% below it in July. Household paper, cleaning products, personal care
  products and tobacco barely move. The 14 apparel and footwear groups swing 7.7% within a year on
  average, the four staples 0.5%.
- **The spring markdown speeds up toward its end; the fall markdown stops in January.** Apparel prices fall
  0.9% in May, 1.9% in June and 2.2% in July. In the fall they fall 1.7% in November and 2.8% in December,
  but only 0.7% in January.
- **Industry-wide stock does not predict the size of the sale in the price index.** Seasons when clothing
  stores went in overstocked did not see deeper markdowns.
- **Overstocked trades earn thinner margins the next year.** Across 18 kinds of store, from family clothing
  (Gap, Old Navy, TJX) and department stores (Macy's, Kohl's) to grocers, 10 points of extra stock growth
  goes with about 0.7 points less gross margin the following year. The effect is no stronger in the
  seasonal trades than in the rest.

A friendlier tour is in the [README](../README.md). The rest of this page is the technical detail.

**Key to the labels below:** *Season goods* = 14 CPI apparel and footwear item strata. *Staples* =
household cleaning products, household paper products, personal care products, tobacco. *Amplitude* =
highest minus lowest calendar-month mean of the log price relative to its centered 12-month average, in
percent. *Overhang* = log growth of inventory minus log growth of sales over a year, in log points.
*Markdown* = log change in the apparel CPI over a clearance, in percent. *GM* = gross margin as a percent
of sales. *Season trades* = NAICS 44811, 44812, 44814, 4482, 4511, 4521.

## The model (`model_cutoffs.csv`)

Single-unit cutoff from the paper's eq. (7) with values uniform on [0, 1] and r = ln(4/3); the cutoff at
the deadline is 0.5 in every row.

| Arrivals per season | Cutoff before deadline | Share of entrants above cutoff | Expected qualifying arrivals |
|---|---|---|---|
| 1 | 0.679 | 0.321 | 0.32 |
| 2 | 0.738 | 0.262 | 0.52 |
| 5 | 0.811 | 0.189 | 0.95 |
| 10 | 0.857 | 0.143 | 1.43 |
| 20 | 0.894 | 0.106 | 2.13 |
| 50 | 0.930 | 0.070 | 3.52 |

## Seasonal profiles, 2000–2025 (`seasonal_profiles.csv`, `season_end_drops.csv`)

The last two columns are the implied price change from the October to the January profile month and from
March to July. A $200 women's coat at the October level costs $174.83 at the January level.

| Item | Group | Amplitude | Peak | Low | October to January | March to July |
|---|---|---|---|---|---|---|
| Jewelry | other | 5.83% | August | December | −0.2% | +1.2% |
| Watches | other | 2.37% | October | December | −0.7% | +0.4% |
| Other household equipment and furnishings | other | 1.77% | February | December | 0.0% | −0.8% |
| Toys | other | 1.74% | February | December | +0.2% | −0.7% |
| New vehicles | other | 1.06% | February | September | +0.8% | −0.5% |
| Furniture and bedding | other | 0.69% | June | August | −0.1% | −0.1% |
| Sporting goods | other | 0.51% | April | December | 0.0% | +0.2% |
| Women's outerwear | season | 20.71% | October | July | −12.6% | −10.8% |
| Women's dresses | season | 17.17% | October | January | −15.8% | −13.7% |
| Women's suits and separates | season | 10.33% | October | July | −9.5% | −9.7% |
| Girls' apparel | season | 10.07% | October | July | −6.6% | −8.4% |
| Men's shirts and sweaters | season | 8.57% | October | July | −6.3% | −5.8% |
| Men's pants and shorts | season | 7.24% | May | December | +0.8% | −2.1% |
| Men's suits, sport coats, and outerwear | season | 5.65% | October | July | −4.9% | −3.3% |
| Boys' apparel | season | 5.51% | October | August | −3.4% | −3.9% |
| Women's footwear | season | 4.98% | October | January | −4.9% | −3.6% |
| Women's underwear, nightwear, swimwear and accessories | season | 4.38% | April | December | −1.6% | −2.6% |
| Men's underwear, nightwear, swimwear and accessories | season | 4.00% | May | December | −1.6% | −1.5% |
| Infants' and toddlers' apparel | season | 3.81% | October | July | −3.1% | −2.9% |
| Boys' and girls' footwear | season | 3.76% | October | July | −3.0% | −2.3% |
| Men's footwear | season | 1.41% | October | December | −0.9% | −0.8% |
| Tobacco and smoking products | staple | 0.89% | July | December | −0.1% | +0.7% |
| Personal care products | staple | 0.43% | April | December | −0.2% | −0.2% |
| Household paper products | staple | 0.40% | July | March | +0.1% | +0.4% |
| Household cleaning products | staple | 0.31% | December | September | +0.2% | −0.2% |

## Group comparison (`group_comparison.csv`)

| Comparison | Value |
|---|---|
| Mean amplitude, season goods (n = 14) | 7.68% |
| Mean amplitude, staples (n = 4) | 0.51% |
| Mean amplitude, other goods (n = 7) | 1.99% |
| Smallest season-good amplitude | 1.41% (men's footwear) |
| Largest staple amplitude | 0.89% (tobacco) |
| Mann-Whitney U, season > staple | U = 56, p = 0.0003 |
| Welch t, season − staple | t = 4.92, p = 0.0003 |
| Item-year regression, season dummy, clustered by item | 7.70 points, SE 1.46, 95% CI [4.83, 10.56], N = 468 |

## Apparel price path by month, 2000–2025 (`apparel_monthly_changes.csv`, `markdown_acceleration.csv`)

| Month | Mean change | 95% CI | Share of years down | Years |
|---|---|---|---|---|
| January | −0.67% | [−1.43, +0.10] | 65% | 26 |
| February | +2.30% | [+1.99, +2.60] | 0% | 26 |
| March | +2.19% | [+1.68, +2.71] | 4% | 26 |
| April | +0.02% | [−0.43, +0.47] | 31% | 26 |
| May | −0.89% | [−1.17, −0.62] | 92% | 26 |
| June | −1.86% | [−2.31, −1.41] | 96% | 26 |
| July | −2.22% | [−2.62, −1.83] | 100% | 26 |
| August | +1.30% | [+1.05, +1.55] | 4% | 26 |
| September | +3.34% | [+3.01, +3.67] | 0% | 26 |
| October | +1.07% | [+0.64, +1.50] | 20% | 25 |
| November | −1.66% | [−2.04, −1.28] | 100% | 25 |
| December | −2.84% | [−3.17, −2.50] | 100% | 26 |

Paired by year, July minus May is −1.33 points (t = −5.80, p < 0.001, 26 years), and January minus
November is +1.07 points (t = 2.02, p = 0.054, 25 years).

## Clothing-store stock and clearance markdowns, 1993–2026 (`inventory_regressions.csv`, `inventory_terciles.csv`, `inventory_eras.csv`, `inventory_seasons.csv`)

Newey-West standard errors with two lags; all rows include a spring dummy except the single-season rows.
Rows marked "secondary" use a measure chosen after the primary rows were seen.

| Sample | Measure | Slope | SE | 95% CI | p | n |
|---|---|---|---|---|---|---|
| all periods | overhang | −0.016 | 0.016 | [−0.047, +0.015] | 0.312 | 66 |
| all periods, prior inflation control | overhang | −0.006 | 0.016 | [−0.037, +0.026] | 0.716 | 66 |
| excluding 2020-21 | overhang | +0.018 | 0.054 | [−0.088, +0.124] | 0.735 | 63 |
| excluding 2020-21, prior inflation control | overhang | +0.006 | 0.033 | [−0.058, +0.069] | 0.866 | 63 |
| fall only, excluding 2020-21 | overhang | −0.025 | 0.076 | [−0.173, +0.124] | 0.745 | 31 |
| spring only, excluding 2020-21 | overhang | +0.057 | 0.058 | [−0.058, +0.171] | 0.332 | 32 |
| secondary: ratio deviation, excluding 2020-21 | ratio_dev | −0.054 | 0.011 | [−0.075, −0.033] | 0.000 | 57 |
| secondary: ratio deviation, excl. 2020-21, inflation control | ratio_dev | −0.028 | 0.013 | [−0.053, −0.002] | 0.036 | 57 |
| secondary: ratio deviation, all periods, inflation control | ratio_dev | 0.000 | 0.008 | [−0.017, +0.016] | 0.955 | 60 |

| Overhang tercile, excluding 2020–21 | Periods | Mean overhang | Mean markdown | Markdown vs season mean |
|---|---|---|---|---|
| Lean stock | 21 | −5.65 | −4.95% | +0.14 |
| Middle | 21 | −0.04 | −5.18% | −0.08 |
| Heavy stock | 21 | +4.76 | −5.13% | −0.05 |

Averages by era, pandemic seasons excluded:

| Era | Season | Periods | Inventory-to-sales ratio | Mean markdown |
|---|---|---|---|---|
| 1993-99 | fall | 7 | 3.00 | −4.38% |
| 1993-99 | spring | 7 | 2.74 | −4.98% |
| 2000-09 | fall | 10 | 2.93 | −6.44% |
| 2000-09 | spring | 10 | 2.62 | −7.31% |
| 2010-19 | fall | 10 | 2.71 | −5.43% |
| 2010-19 | spring | 10 | 2.42 | −4.23% |
| 2021-26 | fall | 4 | 2.48 | −2.18% |
| 2021-26 | spring | 5 | 2.31 | −2.40% |

## Retail trades: stock and next year's gross margin, 1993–2022 (`retail_regressions.csv`, `retail_bins.csv`, `retail_named.csv`, `retail_kinds_panel.csv`)

All rows include year fixed effects; errors are clustered by kind of business. Variables are winsorized at
2% and 98%.

| Specification | Term | Slope | SE | 95% CI | p | n | Kinds |
|---|---|---|---|---|---|---|---|
| all kinds, next-year margin, year effects | overhang | −0.070 | 0.028 | [−0.125, −0.014] | 0.014 | 489 | 18 |
| all kinds, same-year margin, year effects | overhang | +0.091 | 0.019 | [+0.054, +0.128] | 0.000 | 489 | 18 |
| all kinds, next-year, excluding pandemic years | overhang | −0.080 | 0.032 | [−0.144, −0.017] | 0.013 | 446 | 18 |
| season trades only, next-year, year effects | overhang | −0.061 | 0.050 | [−0.160, +0.037] | 0.221 | 158 | 6 |
| other trades only, next-year, year effects | overhang | −0.079 | 0.035 | [−0.147, −0.011] | 0.023 | 331 | 12 |
| all kinds, next-year, season interaction | overhang:season | +0.011 | 0.056 | [−0.099, +0.120] | 0.850 | 489 | 18 |

| Fifth of overhang | Kind-years | Median overhang | Mean next-year margin change | Share falling |
|---|---|---|---|---|
| leanest fifth | 98 | −5.37 | +0.52 | 35% |
| second | 98 | −2.16 | +0.38 | 32% |
| middle | 97 | −0.67 | +0.29 | 33% |
| fourth | 98 | +0.80 | −0.11 | 51% |
| heaviest fifth | 98 | +3.69 | −0.25 | 60% |

The named chains are well-known members of each Census trade, listed for orientation; the survey reports
trades, not firms. "n/a" marks cells the Census suppressed.

| NAICS | Kind | Well-known chains | Overhang 2019 | GM 2019 | Overhang 2021 | GM 2021 | Overhang 2022 | GM 2022 | GM mean 1993-2019 |
|---|---|---|---|---|---|---|---|---|---|
| 44811 | Men's clothing stores | Men's Wearhouse | +2.4 | n/a | −35.1 | n/a | −1.7 | n/a | 49.0 |
| 44812 | Women's clothing stores | Chico's, Ann Taylor | −0.6 | n/a | −11.9 | n/a | +5.9 | n/a | 45.6 |
| 44814 | Family clothing stores | Gap, Old Navy, TJX, Ross, Burlington | −6.6 | 42.7 | −18.5 | 47.4 | +3.3 | 45.3 | 39.9 |
| 4482 | Shoe stores | Foot Locker, DSW | +0.5 | 47.5 | −25.4 | 50.9 | +24.3 | 51.0 | 45.6 |
| 4511 | Sporting goods, hobby and music stores | Dick's Sporting Goods | +2.0 | 43.7 | +1.2 | 45.6 | +15.1 | 45.0 | 39.5 |
| 4521 | Department stores | Macy's, Kohl's, Nordstrom, Dillard's | −5.9 | 33.0 | +2.6 | 37.1 | +0.1 | 34.7 | 31.8 |
