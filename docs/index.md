# APbase

APbase turns irregular field data, such as yield-monitor logs, soil samples,
and sensor readings, into validated maps. It filters the source points,
handles geographic coordinates when needed, builds the target grid, fits the
variogram, compares interpolation methods, and keeps the one with the lower
cross-validation RMSE. You get a ready-to-use map without choosing a
mathematical model by hand.

:::{note}
The numerical work runs in compiled kernels. With a fixed `seed`, repeated runs
on the same data produce the same map.
:::

::::{tab-set}

:::{tab-item} Python
:sync: python

The Python package exposes the high-level mapping pipeline through
`apbase.Map` and `apbase.create_map`:

```python
import apbase

result = apbase.Map(resolution=10.0)(x, y, z)

result.method                  # "idw" or "kriging", whichever has the lower leave-one-out RMSE
result.x, result.y, result.z   # grid points inside the boundary
```

:::

:::{tab-item} Rust
:sync: rust

The Rust crate `apbase` exposes the same pipeline through `apbase::Map` and
`apbase::create_map`:

```rust
use apbase::{Map, MapOptions};

let result = Map::new(MapOptions::new(10.0)).call(&x, &y, &z)?;

result.method;                      // Method::Idw or Method::Kriging, whichever has the lower leave-one-out RMSE
(&result.x, &result.y, &result.z);  // grid points inside the boundary
```

:::

::::

## What the pipeline handles

- **Automatic model selection.** The pipeline compares IDW with ordinary
  kriging and uses the method with the lower leave-one-out cross-validation
  RMSE for the current dataset.
- **Efficient numerical work.** A fitted variogram is reused for radius
  selection, cross-validation, and final kriging, avoiding repeated work.
- **Ready for services and batch jobs.** The same call runs unchanged in a
  script, a service, or a batch job, with no extra runtime to set up. See
  {doc}`production`.
- **Works with irregular, noisy points.** Invalid rows, global outliers, and
  local spatial outliers are removed before interpolation runs.
- **Useful defaults.** When no search radius is provided, it is derived from
  the fitted variogram's `range` (see {doc}`methodology/variogram-fitting`).

See {doc}`quickstart` for a full worked example. Use {doc}`user-guide/index`
and {doc}`methodology/index` when you need advanced control or want to audit
the mathematics behind the automatic choice.

## Contents

```{toctree}
:maxdepth: 2

installation
quickstart
production
user-guide/index
methodology/index
api/index
```
