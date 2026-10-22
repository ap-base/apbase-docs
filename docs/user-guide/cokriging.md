# Cokriging

`CoKriging` estimates a primary variable with help from one or more related
secondary variables. For example, you might combine sparse yield samples with
NDVI, elevation, or soil EC. The workflow has three steps: screen candidate
variables, fit and interpolate with the ones that pass, and cross-validate to
check whether cokriging actually improves the result.

Cokriging is an advanced workflow. It is not part of the default
`apbase.Map` selection today. Use it when you have meaningful secondary
variables and want to test whether they reduce error.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_variogram import screen_secondary_variables
from apbase.cokriging import CoKriging
from apbase.cross_validate import cross_validate_cokriging, select_best_model

# 1. Screen candidates: keep only those that pass both tests
screened = screen_secondary_variables(
    x0, y0, z0,
    {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze)},
    max_colocation_dist=30.0,  # pair samples up to 30 units apart
)
screened.report      # per-candidate rho, p_value, n_pairs, decision, status, ...
secondaries = screened.selected   # e.g. {"ndvi": (xn, yn, zn)}

# 2. Fit and interpolate
ck = CoKriging(method="icm", max_neighbors=40, min_neighbors=3, max_colocation_dist=30.0)
ck.fit(x0, y0, z0, secondaries)
z_targets = ck.interpolate(targets)   # targets: (n, 2) array

# 3. Confirm it's actually better than plain kriging via LOO-CV
cv = cross_validate_cokriging(x0, y0, z0, secondaries, max_colocation_dist=30.0)
best = select_best_model(cv.by_method)
best.method, best.significant
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::cokriging::{CoKriging, CoKrigingMethod, CoKrigingOptions, SecondaryInput};
use apbase::cross_validate::{
    CrossValidateCokrigingOptions, SelectBestModelOptions, cross_validate_cokriging, select_best_model,
};
use apbase::cross_variogram::{ScreeningOptions, screen_secondary_variables};
use indexmap::IndexMap;

// 1. Screen candidates: keep only those that pass both tests
let candidates = IndexMap::from([
    ("ndvi".to_string(), (xn.clone(), yn.clone(), zn.clone())),
    ("ec".to_string(), (xe.clone(), ye.clone(), ze.clone())),
]);
let screened = screen_secondary_variables(
    &x0, &y0, &z0,
    &candidates,
    ScreeningOptions { max_colocation_dist: Some(30.0), ..Default::default() }, // pair samples up to 30 units apart
)?;
screened.report;                                      // per-candidate rho, p_value, n_pairs, decision, status, ...
let secondaries = SecondaryInput::from(screened.selected); // e.g. {"ndvi": (xn, yn, zn)}

// 2. Fit and interpolate
let mut ck = CoKriging::new(CoKrigingOptions {
    method: CoKrigingMethod::Icm,
    max_neighbors: 40,
    min_neighbors: 3,
    max_colocation_dist: Some(30.0),
    ..Default::default()
})?;
ck.fit(&x0, &y0, &z0, &secondaries)?;
let z_targets = ck.interpolate(&targets)?; // targets: (n, 2) array

// 3. Confirm it's actually better than plain kriging via LOO-CV
let cv = cross_validate_cokriging(
    &x0, &y0, &z0,
    &secondaries,
    CrossValidateCokrigingOptions { max_colocation_dist: Some(30.0), ..Default::default() },
)?;
let best = select_best_model(&cv.by_method, SelectBestModelOptions::default())?;
(best.method, best.significant);
```

:::

::::

Do not skip the first step. Passing an unrelated secondary variable directly
to `CoKriging` may not raise an error, but it can make the estimate worse.

Set `max_colocation_dist` when the secondaries are sampled at their own
locations, as NDVI or EC surfaces usually are. Screening compares primary and
secondary values in pairs, and with the default `None` a pair forms only where
the coordinates are identical. Without it, no pairs form and every candidate
is rejected with status `"insufficient sample"`. Use a distance on the order of
the secondary's sampling spacing. `CoKriging` and `cross_validate_cokriging`
pair samples the same way to estimate the cross-covariances, so pass them the
same distance; without pairs, they raise a `ValueError`.

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
correlation with the primary (Fisher $z$-test) and an admissible
cross-variogram (Cauchy–Schwarz check). Only candidates that pass both checks
are kept. See {doc}`../methodology/covariate-screening` for the statistics.

### Screening parameters

`alpha` : float, default `0.05`
: Significance level for the Fisher $z$-test.

`correction` : {"bonferroni", "none"}, default `"bonferroni"`
: Multiple-testing correction used when screening several candidates.

`min_abs_rho` : float, default `0.3`
: Minimum practical correlation. A statistically significant but weak
  candidate is still rejected.

`max_violation_fraction` : float, default `0.1`
: Maximum fraction of evaluated lags allowed to violate the cross-variogram
  admissibility bound.

`max_colocation_dist` : float, optional
: Maximum distance used to pair primary and secondary samples. `None` pairs
  only identical coordinates (see above).

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
screened = screen_secondary_variables(
    x0, y0, z0,
    {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze), "random_noise": (xr, yr, zr)},
    alpha=0.05,
    min_abs_rho=0.3,
    max_colocation_dist=30.0,
)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
let candidates = IndexMap::from([
    ("ndvi".to_string(), (xn, yn, zn)),
    ("ec".to_string(), (xe, ye, ze)),
    ("random_noise".to_string(), (xr, yr, zr)),
]);
let screened = screen_secondary_variables(
    &x0, &y0, &z0,
    &candidates,
    ScreeningOptions {
        alpha: 0.05,
        min_abs_rho: 0.3,
        max_colocation_dist: Some(30.0),
        ..Default::default()
    },
)?;
```

:::

::::

`screened.selected` already has the shape expected by `CoKriging.fit`, so pass
it directly as `secondaries` (in Rust,
`SecondaryInput::from(screened.selected)`). `screened.report` includes every
candidate, including rejected ones: each `CovariateReport` holds `rho`,
`p_value`, `n_pairs`, `admissible_fraction`, `decision`, `status`, and the
fitted `model_params`. It is useful when you need to record why a variable was
dropped.

## Step 2: fitting and interpolating

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
ck = CoKriging(
    method="icm", radius=None, max_neighbors=40, min_neighbors=3, max_colocation_dist=30.0
)
ck.fit(x0, y0, z0, secondaries)
estimates = ck.interpolate(targets)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
let mut ck = CoKriging::new(CoKrigingOptions {
    method: CoKrigingMethod::Icm,
    radius: None,
    max_neighbors: 40,
    min_neighbors: 3,
    max_colocation_dist: Some(30.0),
    ..Default::default()
})?;
ck.fit(&x0, &y0, &z0, &secondaries)?;
let estimates = ck.interpolate(&targets)?;
```

:::

::::

### Fitting parameters

`method` : {"collocated", "icm", "lmc"}, default `"collocated"`
: Cokriging model. The default `"collocated"` is the cheapest but has the
  two requirements described below. When they are not met, use `"icm"`: it
  has neither of them and no per-structure shapes to tune.

`radius` : float, optional
: Local search radius. If omitted, APbase derives it from the primary
  variogram.

`max_neighbors`, `min_neighbors` : int
: Neighbor limits of the primary. For `"icm"` and `"lmc"`, each secondary
  searches its own neighbors within `radius`, up to `max_secondary_neighbors`.

`n_structures` : int, default `2`
: Number of nested LMC structures. Used only by `"lmc"`.

`model_values` : array_like, optional
: Precomputed model values. Only `"collocated"` accepts it.

`max_colocation_dist` : float, optional
: Distance within which a primary sample is paired with its nearest secondary
  point to estimate the cross-covariances. `None` pairs only identical
  coordinates; heterotopic secondaries, such as rasters, need a distance (for
  example, half the cell diagonal).

`max_secondary_neighbors` : int, optional
: Maximum neighbors of each secondary per target, for `"icm"` and `"lmc"`
  only. `None` uses `max_neighbors`. Dense secondaries need far fewer than the
  primary, since the nearest ones screen the rest.

`ck.model_params` gives readable fitted parameters (their structure differs by
method; see the class docstring); `ck.model_values` gives the flat native
vector, which can be passed back as `model_values` to reuse a collocated fit.
In Rust, both are getters: `ck.model_params()?` returns a
`CoKrigingModelParams` enum with one variant per method, and
`ck.model_values()?` the vector.

**Collocated cokriging needs the secondary value at every interpolation
target**, not only at its source points (see the class docstring). If needed,
pre-interpolate a sparse secondary onto a sufficiently dense grid first. It
also relies on the Markov Model 1 (MM1) hypothesis: the secondary value at the
target is assumed to make farther secondary data redundant (see
{doc}`../methodology/cokriging`). ICM and LMC have neither requirement.

Every method estimates the cross-covariances from primary samples paired with
secondary points: at the same coordinates or, with `max_colocation_dist`, the
nearest secondary point within that distance. If a secondary has too few
pairs, `fit` raises a `ValueError` naming it; for heterotopic data, such as a
raster, set `max_colocation_dist`.

## Step 3: cross-validating

Fitting cokriging is only part of the job. Cross-validation shows whether it
actually beats plain kriging on *this* dataset.

### Cross-validation parameters

`max_points` : int, default `500`
: Maximum primary samples evaluated by leave-one-out validation.

`seed` : int, optional
: Seed used when validation samples a subset of primary points.

`radius`, `max_neighbors`, `min_neighbors`, `n_structures`, `max_colocation_dist`, `max_secondary_neighbors`
: Same meaning as in `CoKriging`.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_validate import cross_validate_cokriging, select_best_model

cv = cross_validate_cokriging(
    x0, y0, z0, secondaries, max_neighbors=40, min_neighbors=3, max_colocation_dist=30.0
)
{name: result.rmse for name, result in cv.by_method.items()}

best = select_best_model(cv.by_method)
best.method       # e.g. "icm"
best.significant  # True if the margin over the runner-up is unlikely due to chance
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::cross_validate::{
    CrossValidateCokrigingOptions, SelectBestModelOptions, cross_validate_cokriging, select_best_model,
};

let cv = cross_validate_cokriging(
    &x0, &y0, &z0,
    &secondaries,
    CrossValidateCokrigingOptions {
        max_neighbors: 40,
        min_neighbors: 3,
        max_colocation_dist: Some(30.0),
        ..Default::default()
    },
)?;
for (name, result) in &cv.by_method {
    println!("{name}: {}", result.rmse);
}

let best = select_best_model(&cv.by_method, SelectBestModelOptions::default())?;
best.method;      // e.g. "icm"
best.significant; // true if the margin over the runner-up is unlikely due to chance
```

:::

::::

`cross_validate_cokriging` runs leave-one-out on the primary for all three
methods in one pass. A method whose model cannot be fitted is left out of
`cv.by_method` instead of failing the run; {doc}`../methodology/cross-validation`
explains what is held out and when a method is dropped.

This tells you which cokriging method is best, not whether adding secondaries
helped at all. To check that, compare `cv.by_method[...]` against the
`result.kriging` scores from a plain
`apbase.cross_validate.cross_validate(x0, y0, z0)` run.
