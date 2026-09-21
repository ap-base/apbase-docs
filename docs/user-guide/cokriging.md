# Cokriging

`CoKriging` estimates a primary variable with help from one or more related
secondary variables. For example, you might combine sparse yield samples with
NDVI, elevation, or soil EC. The workflow has three steps: screen candidate
variables, fit and interpolate with the ones that pass, and cross-validate to
check whether cokriging actually improves the result.

Co-kriging is an advanced workflow. It is not part of the default
`apbase.Map` selection today. Use it when you have meaningful secondary
variables and want to test whether they reduce error.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_variogram import screen_secondary_variables
from apbase.cokriging import CoKriging
from apbase.cross_validate import cross_validate_cokriging, select_best_model

# 1. Screen candidates -- keep only the admissible ones
screened = screen_secondary_variables(x0, y0, z0, {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze)})
screened.report      # per-candidate rho, p-value, admissible_fraction, decision
secondaries = screened.selected   # e.g. {"ndvi": (xn, yn, zn)}

# 2. Fit and interpolate
ck = CoKriging(method="icm", max_neighbors=40, min_neighbors=3)
ck.fit(x0, y0, z0, secondaries)
z_targets = ck.interpolate(targets)   # targets: (n, 2) array

# 3. Confirm it's actually better than plain kriging via LOO-CV
cv = cross_validate_cokriging(x0, y0, z0, secondaries)
best = select_best_model(cv.by_method)
best.method, best.significant
```

:::

::::

Do not skip the first step. Passing an unrelated secondary variable directly
to `CoKriging` may not raise an error, but it can make the estimate worse.
Always screen candidates first.

## Core inputs

`x0`, `y0` : array_like
: Primary source coordinates.

`z0` : array_like
: Primary values. Must have the same length as `x0` and `y0`.

`candidates` : dict[str, tuple[array_like, array_like, array_like]]
: Candidate secondary variables passed to `screen_secondary_variables`, for
  example `{"ndvi": (xn, yn, zn)}`.

`secondaries` : dict or list
: Screened secondary variables passed to `CoKriging.fit` and
  `cross_validate_cokriging`. `screened.selected` already has the right shape.

`targets` : array_like or Grid
: Target coordinates passed to `CoKriging.interpolate`.

## Step 1: screening

`screen_secondary_variables` checks whether each candidate has a meaningful
correlation with the primary (Fisher $z$-test) and an admissible cross-
variogram (Cauchy-Schwarz check). Only candidates that pass both checks are
kept. See {doc}`../methodology/covariate-screening` for the statistics.

### Screening parameters

`alpha` : float, default `0.05`
: Significance level for the Fisher z-test.

`correction` : {"bonferroni", "none"}, default `"bonferroni"`
: Multiple-testing correction used when screening several candidates.

`min_abs_rho` : float, default `0.3`
: Minimum practical correlation. A statistically significant but weak
  candidate is still rejected.

`max_violation_fraction` : float, default `0.1`
: Maximum fraction of evaluated lags allowed to violate the cross-variogram
  admissibility bound.

`max_colocation_dist` : float, optional
: Maximum distance used to pair primary and secondary samples. `None` requires
  exact coordinate coincidence.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
screened = screen_secondary_variables(
    x0, y0, z0,
    {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze), "random_noise": (xr, yr, zr)},
    alpha=0.05,
    min_abs_rho=0.3,
)
```

:::

::::

`screened.selected` already has the shape expected by `CoKriging.fit`, so pass
it directly as `secondaries`. `screened.report` includes every candidate,
including rejected ones, and explains each decision. It is useful when you
need to record why a variable was dropped.

## Step 2: fitting and interpolating

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
ck = CoKriging(method="icm", radius=None, max_neighbors=40, min_neighbors=3)
ck.fit(x0, y0, z0, secondaries)
estimates = ck.interpolate(targets)
```

:::

::::

### Fitting parameters

`method` : {"collocated", "icm", "lmc"}, default `"collocated"`
: Co-kriging model. `"icm"` is a reasonable default when unsure: no Markov
  screening assumption and no per-secondary shape choice to tune.

`radius` : float, optional
: Local search radius. If omitted, APbase derives it from the primary
  variogram.

`max_neighbors`, `min_neighbors` : int
: Neighbor limits. For `"icm"` and `"lmc"`, these bound every variable's own
  neighbor search.

`n_structures` : int, default `2`
: Number of nested LMC structures. Used only by `"lmc"`.

`model_values` : array_like, optional
: Precomputed model values. Currently supported for `"collocated"`.

`ck.model_params` gives readable fitted parameters (per-method shape
differs -- see the class docstring); `ck.model_values` gives the flat
native vector, useful for reusing a fit without re-running it.

**Collocated cokriging needs the secondary value at every interpolation
target**, not only at its source points (see the class docstring). If needed,
pre-interpolate a sparse secondary onto a sufficiently dense grid first.
ICM/LMC do not have this requirement.

## Step 3: cross-validating

Fitting cokriging is only part of the job. Cross-validation shows whether it
actually beats plain kriging on *this* dataset.

### Cross-validation parameters

`max_points` : int, default `500`
: Maximum primary samples evaluated by leave-one-out validation.

`seed` : int, optional
: Seed used when validation samples a subset of primary points.

`radius`, `max_neighbors`, `min_neighbors`, `n_structures`
: Same meaning as in `CoKriging`.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_validate import cross_validate_cokriging, select_best_model
from apbase.kriging import Kriging

cv = cross_validate_cokriging(x0, y0, z0, secondaries, max_neighbors=40, min_neighbors=3)
cv.by_method["icm"].rmse, cv.by_method["lmc"].rmse, cv.by_method["collocated"].rmse

best = select_best_model(cv.by_method)
best.method       # e.g. "icm"
best.significant  # True if the margin over the runner-up is unlikely due to chance
```

:::

::::

`cross_validate_cokriging` runs leave-one-out on the primary for all
three methods in one pass, sharing one primary spatial index; see
{doc}`../methodology/cross-validation` for what stays fixed (the
coregionalization models) versus what is genuinely held out (the
primary). Compare `cv.by_method[...]` against a plain
`apbase.cross_validate.cross_validate(x0, y0, z0)` kriging-only baseline
to check whether adding secondaries helped at all, not just which
cokriging method is best among themselves.
