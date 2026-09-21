# Quickstart

`APbase.Map()` turns raw field measurements into a validated map in one step.
Pass it `x`, `y`, `z`, and the desired resolution. APbase cleans the input
data, builds the target grid, fits the variogram, compares interpolation
methods through cross-validation, and selects the best-performing method. The result is a ready-to-use map, without requiring you
to assemble each stage of the workflow yourself. Built for high-performance
processing, `Map` can run in local applications, batch jobs, APIs, and
cloud-based pipelines.

:::{note}
`Map` accepts metric/projected coordinates directly. Geographic lon/lat input
is detected and converted internally before interpolation; the result
coordinates are restored to the original coordinate system.
:::

## Inputs

`x`, `y` : array_like
: Source coordinates. Use projected/metric coordinates directly. Lon/lat is
  accepted by `Map` and converted internally before distance calculations.

`z` : array_like
: Source values at each `x`/`y` point. Must have the same length as `x` and
  `y`.

`resolution` : float
: Output grid spacing. For projected input, use the coordinate unit. For
  lon/lat input, use meters.

`bounds` : geometry, str, bytes, optional
: Optional interpolation boundary. Pass a Shapely geometry, WKT, or WKB in
  the same coordinate system as the original `x`/`y`. If omitted, APbase
  infers the boundary from the data.

## Run the pipeline

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
import numpy as np

import apbase
from apbase import Map

# OpenMP thread count is process-wide, not per-constructor -- set it once.
apbase.config["n_threads"] = 4

# Synthetic source data: 500 points with spatially correlated values plus noise.
rng = np.random.default_rng(0)
x = np.ascontiguousarray(rng.uniform(0, 1000, 500))
y = np.ascontiguousarray(rng.uniform(0, 1000, 500))
z = np.ascontiguousarray(
    np.sin(x / 150) * np.cos(y / 150) * 10 + rng.normal(0, 0.5, 500)
)

# One high-performance call: filter -> grid -> variogram -> CV -> best model.
mapper = Map(resolution=1.0)
result = mapper(x, y, z)
```

:::

::::

:::{tip}
`apbase.config["n_threads"]` is process-wide OpenMP configuration, not a
`Map` argument -- set it once before building any instance, not per call.
:::

## What you get back

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
result.method                  # "idw" or "kriging", picked by validation error
result.x, result.y, result.z   # compact point list inside the boundary
X, Y, Z = result.to_raster()   # optional (ny, nx) arrays, NaN outside boundary
```

:::

::::

The caller does not need to decide the filtering, grid extent, variogram fit,
cross-validation, or model choice. Inspect `result.cross_validation` and
`result.filter_statistics` when you need to audit what the pipeline did.

## The functional shortcut

`apbase.create_map` wraps the same pipeline without instantiating `Map`
explicitly:

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
result = apbase.create_map(x, y, z, resolution=10.0)
```

:::

::::

## Advanced manual control

For most applications, `Map` and `create_map` are all you need: they run the
complete, validated mapping pipeline described above. Use the lower-level
submodules when you need to inspect intermediate results, run diagnostics or
experiments, force a specific interpolation method, or build an advanced
workflow such as co-kriging.

See {doc}`user-guide/index` for advanced controls and
{doc}`methodology/index` for the mathematics behind the automatic model
choice.
