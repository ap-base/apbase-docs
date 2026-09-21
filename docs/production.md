# Production and cloud deployment

APbase provides an intelligent mapping pipeline that turns field data into
validated maps. Its automatic decisions cover input filtering, target-grid
creation, variogram fitting, method comparison, and model selection through
compiled numerical kernels.
The same pipeline can run in a local application, an API, a background worker,
a batch job, or a cloud service. The current package interface is Python, but
these concepts also apply to future language integrations.

## Where APbase fits

Use APbase wherever a service needs to turn field points into maps:

- API services that receive field points and return interpolated maps;
- queue or batch workers that process yield, soil, or sensor files;
- container jobs on Kubernetes, Cloud Run, ECS/Fargate, Azure Container Apps,
  or similar managed runtimes;
- MCP servers and agent tools that need deterministic map generation;
- scheduled data pipelines that write map points or rasters to object storage,
  Parquet, databases, or GIS services.

You do not need a web framework, database, message broker, desktop GIS, or
notebook runtime to use the pipeline. Provide field coordinates and values,
then consume the generated map in the format your application needs.

## What matters in production

The main points to keep in mind are:

- Start with the high-level mapping interface. Use lower-level components only
  when you need diagnostics or an advanced workflow. In Python, the high-level
  entry points are `apbase.Map` and `apbase.create_map`.
- Filtering, variogram fitting, IDW, kriging, and cross-validation run through
  compiled numerical kernels, so the expensive work does not happen in
  application-level point loops.
- The distributed package includes the native extensions. Install the package
  for your target language; the application container does not need a Fortran
  compiler.
- Set limits for cross-validation points, neighbors, grid size, and variogram
  pairs when you need explicit CPU and memory budgets. The Python interface
  exposes these as `max_cv_points`, `max_neighbors`,
  `apbase.config["grid_max_points_ceiling"]`, and variogram pair limits.
- Results contain only target points inside the interpolation boundary by
  default. Create a dense raster only when the downstream application needs
  one.
- Configure OpenMP threads once for each worker process. In Python, use
  `apbase.config["n_threads"]` or `APBASE_N_THREADS`.

## Using APbase in a service

Set process-wide options once when the service starts. Keep global
configuration out of the request handler.

::::{tab-set}

:::{tab-item} Python
:sync: python

The Python interface can be configured at service startup and called once per
request or job:

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
        "rmse": selected_cv.rmse,
        "n_source_points": result.n_source_points,
    }
```

:::

::::

For concurrent services, call `apbase.create_map(...)` per request or create a
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
  copies.
- Projected metric coordinates are used directly.
- Geographic longitude/latitude input is supported; pass `resolution` in
  meters so distances are handled correctly.
- When the interpolation domain is known, pass its boundary in the format
  supported by the target language. In Python, this can be a Shapely geometry,
  WKT, or WKB value.
- Keep dense raster creation at the edge of the pipeline. Store compact
  map points unless a downstream consumer specifically needs a padded raster.

## Install and deploy

The distributed package already includes its compiled numerical extensions.
For the current Python package, install it with `pip`; application images and
workers do not need to build the native extension themselves.

::::{tab-set}

:::{tab-item} Python
:sync: python

```bash
python -m pip install apbase
```

:::

::::

After installation:

1. Set `APBASE_N_THREADS` and any ceiling overrides in the service
   environment.
2. Run a small startup smoke test that imports `apbase`, builds a tiny map, and
   verifies native extensions load correctly.
3. Keep API, queue, storage, and authentication code in your application; use
   APbase as the deterministic geospatial kernel.

See {doc}`installation` for install commands and {doc}`quickstart` for the
minimal map-generation call.
