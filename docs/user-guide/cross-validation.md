# Cross-validation

`apbase.cross_validate.cross_validate` compares IDW and ordinary kriging on
the same source data. It uses leave-one-out cross-validation while sharing the
variogram, search radius, and spatial index between both methods.

This is the decision step behind `apbase.Map`: it is how APbase chooses the
method with the lowest validation error for the current dataset. Call it
directly when you want to inspect the comparison or run it with your own
limits.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_validate import cross_validate

result = cross_validate(x, y, z, max_points=500)
result.idw.rmse, result.kriging.rmse
```

:::

::::

## Parameters

`x`, `y` : array_like
: Source coordinates.

`z` : array_like
: Source values. Must have the same length as `x` and `y`.

`max_points` : int, default `500`
: Maximum source points evaluated. Larger datasets are randomly sampled to
  keep runtime bounded.

`seed` : int, optional
: Seed for the validation subsample.

`radius` : float, optional
: Shared local search radius for IDW and kriging. If omitted, APbase derives
  it from the fitted variogram.

`power` : float, default `2.0`
: IDW distance exponent.

`max_neighbors`, `min_neighbors` : int
: Shared neighbor limits for both methods.

`model_values` : array_like, optional
: Precomputed variogram model reused by the kriging evaluation.

## Reading the result

`result.idw` and `result.kriging` expose `mae`, `rmse`, `r2`, and the
per-sample predictions and actuals used to compute them. These values help you
see whether one method's error is being driven by a few outlier points.

`apbase.Map` uses this function internally to pick between IDW and kriging
automatically. `apbase.create_map` is the functional shortcut for the same
pipeline. See {doc}`../methodology/cross-validation` for the leave-one-out
procedure itself.

For cokriging (collocated/ICM/LMC), see `cross_validate_cokriging` in
{doc}`cokriging`, which cross-validates all three methods together.
