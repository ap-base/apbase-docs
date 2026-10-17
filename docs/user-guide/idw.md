# Inverse distance weighting (IDW)

`IDW` estimates each target value as a distance-weighted average of nearby
source points. Most users can let `apbase.Map` handle it: the automatic
pipeline compares IDW with ordinary kriging and keeps IDW when it has the
lower leave-one-out RMSE for the current dataset.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.idw import IDW

idw = IDW(power=2.0, max_neighbors=40, min_neighbors=3).fit(x, y, z)
z_targets = idw.interpolate(targets)  # targets: (n, 2) array
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::idw::{IDW, IDWOptions};

let mut idw = IDW::new(IDWOptions { power: 2.0, max_neighbors: 40, min_neighbors: 3, ..Default::default() })?;
idw.fit(&x, &y, &z)?;
let z_targets = idw.interpolate(&targets)?; // targets: (n, 2) array or a fitted Grid
```

:::

::::

## Parameters

`x`, `y` : array_like
: Source coordinates passed to `fit`. `IDW` does not convert
  longitude/latitude: pass projected coordinates, in the same unit as
  `radius`.

`z` : array_like
: Source values. Must have the same length as `x` and `y`.

`targets` : array_like or Grid
: Target coordinates passed to `interpolate`: an `(n_targets, 2)` array, a
  fitted `Grid`, or point geometries (a list of Shapely points, or a
  `GeoSeries`/`GeoDataFrame`).

`radius` : float, optional
: Local search radius. If omitted, it is derived from a fitted variogram (see
  {doc}`../methodology/variogram-fitting`).

`power` : float, default `2.0`
: Distance exponent. Higher values give more weight to nearby points.

`max_neighbors` : int, default `40`
: Maximum source points used per target.

`min_neighbors` : int, default `3`
: Minimum source points within `radius`. When fewer are found, the
  `max_neighbors` nearest points are used regardless of distance.

## When IDW wins over kriging

IDW is a deterministic weighted average. It is fast, makes no distributional
assumptions, and behaves predictably when data is sparse. Ordinary kriging
also uses the spatial correlation captured by the variogram. It can be more
accurate when that structure is well fitted, but it costs more and is more
sensitive to a poor fit. `apbase.Map` and `apbase.create_map` compare both
methods on your data, so you do not need to choose manually.

See {doc}`../methodology/idw` for the weighting formula itself.
