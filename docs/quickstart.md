# Quickstart

`Map` turns raw field measurements into a validated map in one step. Pass it
`x`, `y`, `z`, and the desired resolution: it runs the whole pipeline, from
filtering to the final interpolation, and keeps the interpolation method with
the lower leave-one-out cross-validation (LOO-CV) RMSE.
{doc}`user-guide/grid-and-mapping` lists every stage, input, and result field.

## Inputs

`x`, `y` : array_like
: Source coordinates. Projected coordinates are used as-is. Geographic
  longitude/latitude is detected and converted internally to metric coordinates
  before distance calculations; the result is returned in the original
  coordinates.

`z` : array_like
: Source value for each coordinate pair. `x`, `y`, and `z` must be
  one-dimensional and have the same length.

`resolution` : float
: Required output grid spacing. For projected input, use the coordinate unit.
  For longitude/latitude input, use meters.

`bounds` : geometry, str, bytes, optional
: Interpolation domain. Accepts a Shapely geometry, WKT, or WKB in the same
  coordinate system as the original input. If omitted, APbase infers a
  boundary from the filtered source points.

In Rust, `x`, `y`, and `z` can be slices, `Vec`s, arrays, or `ndarray` arrays
of any numeric type. `resolution` is the argument of `MapOptions::new`, and
`bounds` is an optional `MapOptions` field holding WKT, WKB bytes, or a
`geos::Geometry`.

## Run the pipeline

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
import numpy as np

import apbase
from apbase import Map

apbase.config["n_threads"] = 4

# Synthetic source data: 500 points with spatially correlated values plus noise.
rng = np.random.default_rng(0)
x = rng.uniform(0, 1000, 500)
y = rng.uniform(0, 1000, 500)
z = np.sin(x / 150) * np.cos(y / 150) * 10 + rng.uniform(-0.5, 0.5, 500)

# One call: filter -> grid -> variogram -> CV -> best model.
mapper = Map(resolution=10.0)
result = mapper(x, y, z)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::{Map, MapOptions};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    apbase::config.set("n_threads", 4)?;

    // Synthetic source data: 500 points with spatially correlated values plus noise.
    let mut state: u64 = 0;
    let mut uniform = move || {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        (state >> 11) as f64 / (1u64 << 53) as f64
    };
    let (mut x, mut y, mut z) = (Vec::new(), Vec::new(), Vec::new());
    for _ in 0..500 {
        let (xi, yi) = (uniform() * 1000.0, uniform() * 1000.0);
        x.push(xi);
        y.push(yi);
        z.push((xi / 150.0).sin() * (yi / 150.0).cos() * 10.0 + (uniform() - 0.5));
    }

    // One call: filter -> grid -> variogram -> CV -> best model.
    let mut mapper = Map::new(MapOptions::new(10.0));
    let result = mapper.call(&x, &y, &z)?;
    println!("{}", result.method);
    Ok(())
}
```

:::

::::

:::{tip}
`apbase.config["n_threads"]` in Python and `apbase::config.set("n_threads", n)?`
in Rust are process-wide OpenMP configuration, not a `Map` argument. Set it
once before building any instance, not per call.
:::

## What you get back

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
result.method                  # "idw" or "kriging", whichever has the lower LOO-CV RMSE
result.x, result.y, result.z   # grid points inside the boundary
X, Y, Z = result.to_raster()   # optional (ny, nx) arrays, NaN outside boundary
```

:::

:::{tab-item} Rust
:sync: rust

```rust
result.method;                           // Method::Idw or Method::Kriging, whichever has the lower LOO-CV RMSE
(&result.x, &result.y, &result.z);       // grid points inside the boundary
let (rx, ry, rz) = result.to_raster()?;  // optional (ny, nx) arrays, NaN outside boundary
```

:::

::::

`result.x`, `result.y`, and `result.z` hold only the grid points inside the
boundary, with no NaN padding. Call `to_raster()` only when you need a full
`(ny, nx)` raster.

To audit what the pipeline did, inspect `result.cross_validation`,
`result.filter_statistics`, and `result.n_source_points`.

## The functional shortcut

`create_map` (`apbase.create_map` in Python, `apbase::create_map` in Rust)
wraps the same pipeline without instantiating `Map` explicitly:

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
result = apbase.create_map(x, y, z, resolution=10.0)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
let result = apbase::create_map(&x, &y, &z, apbase::MapOptions::new(10.0))?;
```

:::

::::

## Advanced manual control

For most applications, `Map` and `create_map` are all you need. Use the
lower-level modules to inspect intermediate results, force a specific
interpolation method, or build an advanced workflow such as cokriging; see
{doc}`user-guide/index`. {doc}`methodology/index` covers the mathematics
behind the automatic model choice.
