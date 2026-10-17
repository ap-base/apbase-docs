# Secondary-variable screening

Cokriging helps only when a secondary variable (a covariate) is meaningfully
related to the primary and produces a valid cross-variogram. An unrelated or weak secondary
adds noise instead of useful information. `screen_secondary_variables` tests
each candidate before it reaches {doc}`cokriging <cokriging>`, so the selected
variables are based on evidence rather than intuition.

## Two independent tests per candidate

Each candidate must pass two independent checks:

**1. Significant, practically relevant correlation.** The Pearson
correlation $\rho$ between the primary and the candidate, computed over
their paired samples (see the pairing rule below), is tested against zero
with a Fisher
$z$-transform {cite}`Fisher1921`:

$$
z = \operatorname{artanh}(\rho) = \frac{1}{2}\ln\frac{1+\rho}{1-\rho}
\qquad\qquad
\mathrm{SE}(z) = \frac{1}{\sqrt{n_{\text{pairs}} - 3}}
$$

giving a two-sided $p$-value for $H_0: \rho = 0$. A candidate is rejected if
the test is not significant at `alpha`, or if $|\rho|$ is below `min_abs_rho`
even when significant. A large sample can make a tiny correlation
statistically significant, so both significance and practical strength matter.

When screening several candidates, `correction="bonferroni"` (the default)
divides `alpha` by the number of candidates before testing each one. This
controls the false-positive rate across the full batch.

**2. Admissible cross-variogram.** The primary-candidate relationship must
also form a valid coregionalization component, not just show correlation at
lag 0. APbase checks the Cauchy–Schwarz bound that every valid cross-covariance
must satisfy at each lag
{cite}`Journel1978,Myers1982`:

$$
\left|\gamma_{0u}(h)\right| \leq \sqrt{\gamma_{00}(h) \, \gamma_{uu}(h)}
$$

where $\gamma_{00}$ and $\gamma_{uu}$ are the primary and candidate
{doc}`variograms <variogram-fitting>`, and $\gamma_{0u}$ is their fitted
{class}`~apbase.cross_variogram.CrossVariogram`. APbase evaluates the bound
at 200 evenly spaced lags from 0 to three times the largest of the three
fitted ranges, allowing $|\gamma_{0u}(h)|$ to exceed the right-hand side by up
to 10%. The three variograms are fitted independently, so a nearly collinear
secondary can exceed the exact bound by a few percent through fitting noise
alone. A candidate is rejected when more than `max_violation_fraction` of those
evaluations violate the bound. This catches an inadmissible cross-variogram
before it can corrupt the cokriging system.

## The cross-variogram itself

`CrossVariogram` generalizes the empirical semivariogram estimator to two
different variables $a$ and $b$. Instead of squaring one variable's
increment, it multiplies the increments of both variables over the pairs
$(i, j) \in N(h)$, where each point carries a value of both variables (see the
pairing rule below):

$$
\hat{\gamma}_{ab}(h) = \frac{1}{2\,|N(h)|}
\sum_{(i,j) \in N(h)} \left(a_i - a_j\right)\left(b_i - b_j\right)
$$

This reduces to the ordinary semivariogram estimator when $a = b$.
Unlike an auto-variogram, `nugget` and `partial_sill` may be negative here.
A cross-variogram does not need to be a valid direct covariance by itself;
the Cauchy–Schwarz check above verifies whether it can be used safely.

`CrossVariogram` is symmetric and supports heterotopic data: `a` and `b` do
not need to share sample locations. The fit pairs them with a nearest-neighbor
join. `max_colocation_dist` limits how far apart a pair can be; `None`
requires exact coincidence. The same building block is reused for each
variable pair in the ICM and LMC coregionalization fits.

## Using the result

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_variogram import screen_secondary_variables

result = screen_secondary_variables(
    x0, y0, z0,
    {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze)},
    max_colocation_dist=30.0,
)
result.selected   # {"ndvi": (xn, yn, zn)}: only candidates that pass both tests
result.report     # every candidate's CovariateReport: rho, p_value, n_pairs, decision, status, ...
```

:::

::::

`result.selected` already has the shape expected by
{class}`~apbase.cokriging.CoKriging`, so pass it directly to
`CoKriging(...).fit(x0, y0, z0, secondaries=result.selected)`. A candidate
with too little data (fewer than four paired samples) or an invalid fitted
model is recorded in `report` with `decision=False` and a reason in `status`.
One unusable candidate does not stop the rest of the screening batch.
