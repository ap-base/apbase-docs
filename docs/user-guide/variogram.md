# Variogram

`Variogram` fits an empirical semivariogram from source points and chooses the
best-fitting model from spherical, exponential, and Gaussian options.
`Kriging` always uses a fitted variogram; the other estimators use one to
derive `radius` when it is omitted (see {doc}`../methodology/variogram-fitting`).

`apbase.Map` fits the variogram for you. Use `Variogram` directly when you
want to inspect the fitted curve or control the fitting step.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.variogram import Variogram

variogram = Variogram(n_lags=50, max_pairs=100_000).fit(x, y, z)
gamma = variogram.evaluate(distances)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::variogram::{Variogram, VariogramOptions};

let mut variogram = Variogram::new(VariogramOptions { n_lags: 50, max_pairs: 100_000, ..Default::default() })?;
variogram.fit(&x, &y, &z)?;
let gamma = variogram.evaluate(&distances)?;
```

:::

::::

## Parameters

`x`, `y` : array_like
: Source coordinates passed to `fit`. `Variogram` does not convert
  longitude/latitude: pass projected coordinates.

`z` : array_like
: Source values. Must have the same length as `x` and `y`.

`n_lags` : int, default `50`
: Number of distance bins used to build the empirical semivariogram.

`max_pairs` : int, default `100_000`
: Maximum point pairs sampled while building the empirical semivariogram.
  `0` uses every eligible pair, subject to the native ceiling.

`max_distance` : float, default `0.0`
: Maximum pair distance considered. `0.0` lets the native kernel choose the
  extent from the data.

`distance` : array_like
: Distances passed to `evaluate`; returns semivariance for each distance.

## What `fit` does

`fit` computes the empirical semivariogram, estimates the nugget, partial sill,
and range for each candidate model, and keeps the fit with the lowest weighted
error. `evaluate(distance)` returns the fitted model's semivariance at
arbitrary distances, which is useful for inspecting the curve directly.

See {doc}`../methodology/variogram-fitting` for the math behind the
empirical estimator and the fitting procedure, and
{doc}`../methodology/kriging` for how the fitted model feeds into the
kriging system.
