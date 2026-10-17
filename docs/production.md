# Production and cloud deployment

The same mapping pipeline that runs in a notebook can run in an API, a
background worker, a batch job, or a cloud service. This page covers what
changes when you deploy it. The guidance applies to both Python and Rust.

## Where APbase fits

Use APbase wherever a service needs to turn field points into maps:

- API services that receive field points and return interpolated maps;
- queue or batch workers that process yield, soil, or sensor files;
- container jobs on Kubernetes, Cloud Run, ECS/Fargate, Azure Container Apps,
  or similar managed runtimes;
- MCP servers and agent tools that need reproducible map generation;
- scheduled data pipelines that write map points or rasters to object storage,
  Parquet, databases, or GIS services.

You do not need a web framework, database, message broker, desktop GIS, or
notebook runtime to use the pipeline. Provide field coordinates and values,
then consume the generated map in the format your application needs.

## What matters in production

- Start with the high-level entry points: `apbase.Map` and `apbase.create_map`
  in Python, `apbase::Map` and `apbase::create_map` in Rust. Lower-level
  components are for diagnostics and advanced workflows.
- Filtering, variogram fitting, IDW, kriging, and cross-validation run through
  compiled numerical kernels, so the expensive work does not happen in
  application-level point loops.
- Set limits when you need explicit CPU and memory budgets. `max_cv_points`
  and `max_neighbors` are arguments of `Map` and `create_map` (`MapOptions`
  fields in Rust). Grid size and variogram pairs are process-wide settings:
  `grid_max_points_ceiling`, `variogram_max_pairs` (pairs sampled by the
  variogram the pipeline fits), and `variogram_max_pairs_ceiling`, set with
  `apbase.config[key]` in Python or `apbase::config.set(key, n)?` in Rust.
- Results are compact: only grid points inside the boundary. Call
  `to_raster()` only when a client needs a full grid.
- Configure OpenMP threads once per worker process with
  `apbase.config["n_threads"]` in Python or
  `apbase::config.set("n_threads", n)?` in Rust. When `n_threads` is not set,
  both libraries read the `APBASE_N_THREADS` environment variable.

## Using APbase in a service

Set process-wide options once when the service starts. Keep global
configuration out of the request handler.

::::{tab-set}

:::{tab-item} Python
:sync: python

In Python:

```python
import os

import numpy as np

import apbase

apbase.config["n_threads"] = int(os.getenv("APBASE_N_THREADS", "2"))
apbase.config["grid_max_points_ceiling"] = int(
    os.getenv("APBASE_GRID_MAX_POINTS", "100000000")
)


def build_map_response(x, y, z, *, resolution, bounds=None):
    result = apbase.create_map(
        np.ascontiguousarray(x, dtype=np.float64),
        np.ascontiguousarray(y, dtype=np.float64),
        np.ascontiguousarray(z, dtype=np.float64),
        resolution=resolution,
        bounds=bounds,
        max_cv_points=500,
        max_neighbors=40,
        seed=42,
    )

    selected_cv = getattr(result.cross_validation, result.method)
    return {
        "method": result.method,
        "x": result.x,
        "y": result.y,
        "z": result.z,
        "rmse": selected_cv.rmse,  # LOO-CV RMSE of the selected method
        "n_source_points": result.n_source_points,  # points kept after filtering
    }
```

:::

:::{tab-item} Rust
:sync: rust

In Rust:

```rust
use apbase::common::ApbaseError;
use apbase::cross_validate::Method;
use apbase::mapping::{Bounds, MapOptions};
use ndarray::Array1;

/// Call once at service startup, before handling any request.
fn configure_apbase() -> Result<(), ApbaseError> {
    let env_or = |key: &str, default: usize| {
        std::env::var(key).ok().and_then(|value| value.parse().ok()).unwrap_or(default)
    };
    apbase::config.set("n_threads", env_or("APBASE_N_THREADS", 2))?;
    apbase::config.set("grid_max_points_ceiling", env_or("APBASE_GRID_MAX_POINTS", 100_000_000))?;
    Ok(())
}

struct MapResponse {
    method: Method,
    x: Array1<f64>,
    y: Array1<f64>,
    z: Array1<f64>,
    rmse: f64,            // LOO-CV RMSE of the selected method
    n_source_points: i64, // points kept after filtering
}

fn build_map_response(
    x: &[f64],
    y: &[f64],
    z: &[f64],
    resolution: f64,
    bounds: Option<Bounds>,
) -> Result<MapResponse, ApbaseError> {
    let result = apbase::create_map(x, y, z, MapOptions {
        bounds,
        max_cv_points: 500,
        max_neighbors: 40,
        seed: Some(42),
        ..MapOptions::new(resolution)
    })?;

    let selected_cv = match result.method {
        Method::Idw => &result.cross_validation.idw,
        Method::Kriging => &result.cross_validation.kriging,
    };
    Ok(MapResponse {
        method: result.method,
        rmse: selected_cv.rmse,
        n_source_points: result.n_source_points,
        x: result.x,
        y: result.y,
        z: result.z,
    })
}
```

:::

::::

The examples set `n_threads` explicitly only to default to 2 threads instead
of 1. `APBASE_GRID_MAX_POINTS` is a variable of these examples, not one APbase
reads. `seed=42` fixes the cross-validation sample, so the same input always
selects the same method.

For concurrent services, call `create_map` per request or create a
`Map` instance inside the request or job. Reusing a `Map` instance is useful
for sequential jobs, but it stores the last result on the instance.

## Choosing workers and threads

Choose the number of process workers and OpenMP threads together:

```text
process_workers * APBASE_N_THREADS <= available_vCPU
```

Examples:

- 2 vCPU container: `process_workers=1`, `APBASE_N_THREADS=2`
- 4 vCPU container: `process_workers=2`, `APBASE_N_THREADS=2`
- latency-sensitive batch job: `process_workers=1`, `APBASE_N_THREADS` equal
  to the allocated vCPU count

Avoid running many application workers with many OpenMP threads each. That
oversubscribes the CPU and usually makes kriging slower.

## Inputs at the service boundary

- Pass one-dimensional numeric arrays for the source x coordinates, y
  coordinates, and values.
- Prefer contiguous `float64` arrays at service boundaries to avoid hidden
  copies. In Rust, `&[f64]` and `Vec<f64>` are used without conversion.
- Projected coordinates are used directly.
- Geographic longitude/latitude input is supported; pass `resolution` in
  meters so distances are handled correctly.
- When the interpolation domain is known, pass its boundary in the format
  supported by the target language. In Python, this can be a Shapely geometry,
  WKT, or WKB value. In Rust, it is a `Bounds` built from a WKT string, WKB
  bytes, or a `geos::Geometry`.

## Install and deploy

The distributed package already includes its compiled numerical extensions.
Install it with `pip` for Python or `cargo` for Rust; see {doc}`installation`
for requirements. Application images and workers do not need to build the
native kernels themselves.

::::{tab-set}

:::{tab-item} Python
:sync: python

```bash
python -m pip install apbase
```

:::

:::{tab-item} Rust
:sync: rust

```bash
cargo add apbase
cargo build --release
```

The runtime image still needs the Fortran/OpenMP/BLAS runtime, GEOS, and PROJ
shared libraries.

:::

::::

After installation:

1. Set `APBASE_N_THREADS`, and any variables your startup code maps to
   `apbase.config` (such as the ceilings above), in the service environment.
2. Run a small startup smoke test that loads `apbase`, builds a tiny map, and
   verifies the native kernels run correctly.
3. Keep API, queue, storage, and authentication code in your application; use
   APbase as the geospatial kernel.

See {doc}`quickstart` for the minimal map-generation call.
