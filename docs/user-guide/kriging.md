# Ordinary kriging

`Kriging` fits or accepts a variogram model and uses local ordinary kriging to
estimate target values. Most users can let `apbase.Map` decide whether it is
the better option: the pipeline compares kriging with IDW and keeps it only
when it has the lower leave-one-out RMSE.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.kriging import Kriging

kriging = Kriging(max_neighbors=40, min_neighbors=3).fit(x, y, z)
z_targets = kriging.interpolate(targets)  # targets: (n, 2) array
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::kriging::{Kriging, KrigingOptions};

let mut kriging = Kriging::new(KrigingOptions { max_neighbors: 40, min_neighbors: 3, ..Default::default() })?;
kriging.fit(&x, &y, &z)?;
let z_targets = kriging.interpolate(&targets)?; // targets: (n, 2) array or a fitted Grid
```

:::

::::

## Parameters

`x`, `y` : array_like
: Source coordinates passed to `fit`. `Kriging` does not convert
  longitude/latitude: pass projected coordinates, in the same unit as
  `radius`.

`z` : array_like
: Source values. Must have the same length as `x` and `y`.

`targets` : array_like or Grid
: Target coordinates passed to `interpolate`: an `(n_targets, 2)` array, a
  fitted `Grid`, or point geometries (a list of Shapely points, or a
  `GeoSeries`/`GeoDataFrame`).

`radius` : float, optional
: Local search radius. If omitted, it is derived from the fitted variogram
  (see {doc}`../methodology/variogram-fitting`).

`max_neighbors` : int, default `40`
: Maximum source points used per target.

`min_neighbors` : int, default `3`
: Minimum source points within `radius`. When fewer are found, the
  `max_neighbors` nearest points are used regardless of distance.

`model_values` : array_like, optional
: Precomputed variogram model (`Variogram.model_values`). If provided, `fit`
  uses it instead of fitting a new variogram.

## What "local" and "ordinary" mean here

*Local* means that each target is estimated from nearby source points within
`radius`, capped at `max_neighbors`, rather than from the entire dataset. This
keeps the linear system small and the method scalable. *Ordinary* means that
the process mean is treated as unknown and constant within each local
neighborhood. Simple kriging, by contrast, assumes the mean is known.

See {doc}`../methodology/kriging` for the full derivation (the linear system
solved per target and why it produces the best linear unbiased estimate) and
{doc}`../methodology/variogram-fitting` for the variogram models.
