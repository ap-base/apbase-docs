# Variogram

`Variogram` fits an empirical semivariogram from source points and chooses the
best-fitting model from spherical, exponential, and gaussian options. `IDW`,
`Kriging`, and `SpatialFilter` use it internally when `radius` is omitted, but
you can also inspect it directly.

For normal map generation, `apbase.Map` fits and reuses the variogram before
comparing IDW and kriging. Use `Variogram` directly when you want to inspect
the fitted curve or control the fitting step.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.variogram import Variogram

variogram = Variogram(n_lags=50, max_pairs=100_000).fit(x, y, z)
gamma = variogram.evaluate(distances)
```

:::

::::

## Parameters

`x`, `y` : array_like
: Source coordinates passed to `fit`.

`z` : array_like
: Source values. Must have the same length as `x` and `y`.

`n_lags` : int, default `50`
: Number of distance bins used to build the empirical semivariogram.

`max_pairs` : int, default `100_000`
: Maximum point pairs sampled while building the empirical semivariogram.
  `0` uses every eligible pair, subject to the native ceiling.

`max_distance` : float, default `0.0`
: Maximum pair distance considered. `0.0` uses the native default extent.

`distances` : array_like
: Distances passed to `evaluate`; returns semivariance for each distance.

## What `fit` does

`fit` computes the empirical semivariogram, estimates nugget, sill, and range
for each candidate model, and keeps the fit with the lowest weighted error.
`evaluate(distances)` returns the fitted model's semivariance at arbitrary
distances, which is useful for inspecting the curve directly.

See {doc}`../methodology/variogram-fitting` for the math behind the
empirical estimator and the fitting procedure, and
{doc}`../methodology/kriging` for how the fitted model feeds into the
kriging system.
