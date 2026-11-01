# Methods review: Board and Skrzypacz (2016)

- **Paper:** Simon Board and Andrzej Skrzypacz, "Revenue Management with Forward-Looking Buyers,"
  *Journal of Political Economy* 124(4), 2016, pp. 1046–1087. DOI 10.1086/686713.
- **Statistical focus:** Theorems 1 to 3 (deterministic cutoffs that fall with inventory and, when entry
  does not rise over time, with time; implementation by posted prices plus a final auction), and the
  numerical illustration in Figures 3 to 5 (Poisson arrivals at rate 10, values uniform on [0, 1], season
  length 1, interest rate ln(4/3)).
- **Review standard:** internal consistency of the formal results, explicit statement of assumptions,
  and the testability of the predictions, with the current AEA Data and Code Availability Policy applied to
  the numerical figures.
- **What was read:** the full published text (42 pages) from the copy on Andrzej Skrzypacz's Stanford web
  page (web.stanford.edu/~skrz/dynamic_auction.pdf), including the Appendix proofs at the level of their
  statements and structure. The online appendix and any code were not examined. Biographical facts come
  from the authors' Stanford GSB and UCLA faculty pages.

## Methods summary

The paper is a theory paper. A seller must sell K identical units by a deadline T. Buyers enter over time
in random numbers, each with a private value drawn from a common distribution F and a private arrival
date, and they can wait. Delay costs both sides through a common discount factor. The seller commits at
the start to any mechanism. Using the standard Myerson approach, profit is rewritten as expected
discounted marginal revenue, m(v) = v − (1 − F(v)) / f(v), so the seller's problem becomes a single-agent
dynamic program.

The results are proved, not estimated. Theorem 1 shows that the optimal rule awards a unit to the
highest remaining buyer when his value exceeds a cutoff that depends only on inventory and time, and that
cutoffs fall as inventory rises. Theorem 2 adds that when the number of entrants is weakly decreasing in
the usual stochastic order, cutoffs also fall over time and satisfy a one-period-look-ahead condition.
Theorem 3 shows that in the continuous-time limit, with Poisson entry, posted prices plus a second-price
auction for the last unit at T achieve the optimal profit up to a term of order h, the period length.
Section III works through the single-unit case, and Section VI extends the model to inventory costs,
expiring units, multiple buyer classes, changing value distributions and buyers who exit.

There is no data, no sample and no estimation. The only numbers are the parameters and plotted paths in
Figures 3 to 5 and a handful of figures quoted from other studies in the introduction and Section V.

### Research design

Formal mechanism design. The seller's problem is reduced to a single-agent dynamic program in marginal
revenues and solved by backward induction, first in discrete time (Section IV) and then in the
continuous-time limit with Poisson entry (Section V). Robustness is examined by extending the model, not
by data.

### Sampling strategy

Does not apply. No units are sampled. The closest analogue is the choice of the illustrative parameter
set in the Figure 3 caption, which is stated but not motivated beyond "a good loses one-fourth of its
value over the season."

### Sample size

Does not apply. The numerical illustration uses one parameter set (λ = 10, U[0, 1], T = 1, r = ln(4/3))
and two inventory levels (k = 1, 2).

### Inclusion and exclusion criteria

Does not apply as a data rule. The model's scope conditions play this role and are stated in Section II:
a common value distribution for all entrants, entry independent across periods, Poisson entry for the
price implementation, strictly increasing marginal revenue with m(0) < 0, full commitment, and zero
salvage value at T. Section VI relaxes several of these one at a time.

### Independent and dependent variables

In the formal sense, the primitives are the entry process (Nₜ or λₜ), the value distribution F, the
discount rate r, the deadline T and the inventory K. The derived objects are the cutoffs x(k, t), the
posted prices p(k, t), the probability of sale over time, and seller profit.

### Statistical methods

Does not apply. There is no estimation or inference. The "methods" are the proofs of the supporting lemmas and
Theorems 1 to 3 in the Appendix.

### Reported effect sizes

No empirical effect sizes are reported. The comparative statics are signed, not sized: cutoffs fall in
inventory (Theorem 1) and, with weakly decreasing entry, in time (Theorem 2); profits are higher with
forward-looking than with short-lived buyers (Section V.C). The figures show magnitudes for one parameter
set only, and the paper does not tabulate them.

### Confidence intervals

Does not apply; nothing is estimated.

### P-values, if applicable

Not applicable.

### Missing data treatment

Does not apply. The quoted external figures (Soysal and Krishnamurthi, Sweeting, Consumer Reports) are
cited without discussion of their samples.

### Stated limitations

The authors name the full-commitment assumption and call the resulting profit an upper bound; they note
that cutoffs stop being deterministic when buyers can exit (Section VI.E) and that anonymous prices are no
longer optimal when later entrants have stronger value distributions, as with airlines (Section VI.D).
The conclusion adds that without commitment the seller would dispose of more inventory and prices may
cycle.

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Arrival rate in the illustration | λ = 10 buyers per season | Figure 3 caption, p. 1068 | Expected number of interested buyers entering over [0, T] | That real seasonal demand is Poisson or of this size |
| Value distribution | v ∼ U[0, 1]; static monopoly cutoff 0.5 | Figure 3 caption | Buyer heterogeneity; the cutoff m⁻¹(0) used at the deadline | That retail valuations are uniform or stable over a season |
| Discounting | r = ln(4/3), T = 1; "a good loses one-fourth of its value over the season" | Figure 3 caption | Cost of delay to buyers | A measured depreciation rate for any product |
| Single-unit cutoff condition | r m(x*) = λ E[max{m(v) − m(x*), 0}] | Eq. (7), p. 1056 | Seller's indifference between selling now and waiting for an entrant | Any number by itself; the paper does not report x* for the Figure 3 parameters (solving it gives about 0.857, computed in this repository) |
| Final buy-it-now price | p_T = δ^T E[max{y², m⁻¹(0)} given y¹ = x*] | Eq. (8), p. 1056 | Price that makes the cutoff type indifferent between buying and entering the final auction | That real sellers run a final auction |
| Price path, single unit | dp/dt = −r x* − (x* − p) λ [1 − F(x*)] | Eq. (9), p. 1056 | Rate at which posted prices must fall to keep the cutoff type indifferent | Observed markdown rates |
| Price path, k units | Eq. (20), p. 1068 | Section V.B | Prices fall smoothly and jump up after each sale | That price increases after sales are common in practice |
| Profit ranking | Forward-looking buyers give higher seller profit than short-lived buyers | Section V.C, footnote 24, p. 1070 | A proved inequality under commitment | Its size; no profit numbers are reported for Figures 3 to 5 |
| Women's coats, short-lived counterfactual | Profits 9 percent higher if customers were short-lived, at fixed retail prices | p. 1070, quoting Soysal and Krishnamurthi (2012) | An estimate from another paper's structural model | Anything about the optimal mechanism, which this paper says reverses the sign |
| Secondary baseball tickets | Prices decline by 60 percent in the month before the game | p. 1070, quoting Sweeting (2012) | Another paper's descriptive finding | A test of this model |
| JC Penney | Revenue dropped by 25 percent under a flatter pricing policy | p. 1047, citing Robinson (2014) | A press account | A causal effect of removing sales |
| Consumer survey | Around 60 percent of consumers "wait for a sale" | p. 1047, footnote 1 | A survey share | The share of buyers who are forward-looking in the model's sense |

## Interpretation notes

- The headline objects are theorems. Their validity rests on the proofs, which follow the standard
  backward-induction and envelope-theorem arguments and are laid out in the Appendix with each step
  stated. I found no internal inconsistency at the level read, but I did not check every inequality in
  the Appendix line by line.
- The assumptions are stated openly in Section II, including two strong ones: the seller can fully commit
  to a mechanism, and buyers' values are drawn from one distribution whatever their arrival date. The
  authors describe the commitment case as an upper bound on profit and note that without commitment the
  problem is much harder.
- The monotonicity in time (Theorem 2) needs entry to be weakly decreasing. With constant entry and a
  single unit, cutoffs are flat until T and prices still fall, because buyers must be compensated for
  delay and for the risk of a stock-out. The falling price path is therefore a prediction about prices,
  not about cutoffs, in the simplest case.
- Figures 3 to 5 are illustrations computed under one parameter set. No code, numerical method or grid
  is described, so the plotted paths cannot be reproduced from the text alone beyond the closed-form
  single-unit cutoff.
- The quoted empirical figures (60 percent, 25 percent, 9 percent) come from other sources and serve as
  motivation. None of them is a test of the model.

## Unanswered questions

- How large is the profit gain from forward-looking buyers in the Figure 3 example? The ranking is proved
  but not quantified.
- How sensitive are the cutoff and price paths to the arrival rate and the discount rate? The figures fix
  one value of each.
- Which observable features separate this model from a seller without commitment? The conclusion
  suggests more disposal of inventory and price cycles without commitment, but no test is proposed.
- How much does the result depend on independent private values? Footnote 8 relies on symmetric
  independent values for revenue equivalence in the final auction.

## Items requiring expert verification

- A line-by-line check of the proofs of Lemma 3, Theorem 2 and Theorem 3, especially the O(h) bounds in
  the continuous-time implementation.
- Whether eq. (9) is written in present-value prices; footnote 4 says prices must be rescaled under the
  alternative utility specification, and the boundary condition (8) carries a discount factor.
- Whether the numerical paths in Figures 3 to 5 match a fresh computation from eqs. (18) to (20).

The modern rerun in this repository does not reproduce the paper, which has no data. It solves eq. (7)
for the Figure 3 parameters and then asks whether US price indexes and Census retail-trade data show the
patterns the theorems predict for goods sold against a deadline.
