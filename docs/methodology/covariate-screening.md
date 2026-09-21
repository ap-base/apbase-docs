# Covariate screening

Cokriging helps only when a secondary variable is meaningfully related to the
primary and produces a valid cross-variogram. An unrelated or weak secondary
adds noise instead of useful information. `screen_secondary_variables` tests
each candidate before it reaches {doc}`cokriging <cokriging>`, so the selected
variables are based on evidence rather than intuition.

## Two independent tests per candidate

Each candidate must pass two independent checks:

**1. Significant, practically relevant correlation.** The Pearson
correlation $\rho$ between the primary and the candidate, computed over
their colocated (paired) sample, is tested against zero with a Fisher
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
lag 0. APbase checks the Cauchy-Schwarz bound that every valid cross-covariance
must satisfy at each lag
{cite}`Journel1978,Myers1982`:

$$
\left|\gamma_{0u}(h)\right| \leq \sqrt{\gamma_{00}(h) \, \gamma_{uu}(h)}
$$

where $\gamma_{00}$/$\gamma_{uu}$ are the primary and candidate
{doc}`variograms <variogram-fitting>`, and $\gamma_{0u}$ is their fitted
{class}`~apbase.cross_variogram.CrossVariogram`. APbase evaluates the bound
over lags extending several times beyond the larger range. A candidate is
rejected when more than `max_violation_fraction` of those evaluations violate
the bound. This catches an inadmissible cross-variogram before it can corrupt
the cokriging system.

## The cross-variogram itself

`CrossVariogram` generalizes the empirical semivariogram estimator to two
different variables $a$/$b$, using the parallel-bracket cross-semivariance
estimator over colocated pairs $(i, j) \in N(h)$:

$$
\hat{\gamma}_{ab}(h) = \frac{1}{2\,|N(h)|}
\sum_{(i,j) \in N(h)} \left(a_i - a_j\right)\left(b_i - b_j\right)
$$

This reduces to the ordinary semivariogram estimator when $a = b$.
Unlike an auto-variogram, `nugget` and `partial_sill` may be negative here.
A cross-variogram does not need to be a valid direct covariance by itself;
the Cauchy-Schwarz check above verifies whether it can be used safely.

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
result = screen_secondary_variables(x0, y0, z0, {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze)})
result.selected   # {"ndvi": (xn, yn, zn)} -- only the admissible candidates
result.report     # every candidate's rho, p-value, admissible_fraction, decision, status
```

:::

::::

`result.selected` already has the shape expected by
{class}`~apbase.cokriging.CoKriging`, so pass it directly to
`CoKriging(...).fit(x0, y0, z0, secondaries=result.selected)`. A candidate
with too little data (fewer than four colocated pairs) or an invalid fitted
model is recorded in `report` with `decision=False` and a reason in `status`.
One unusable candidate does not stop the rest of the screening batch.
