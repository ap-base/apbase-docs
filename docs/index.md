# APbase

APbase is an intelligent mapping pipeline for irregular field data, such as
yield monitor, soil samples, and sensor grids. Its intelligence comes
from the way it handles the workflow automatically: it filters the source
data, handles geographic coordinates when needed, builds the target grid,
compares interpolation methods, and chooses the one with the lowest validation
error. The result is a ready-to-use map without requiring users to choose a
mathematical model by hand.

:::{note}
APbase is designed for high-performance geospatial workloads. The same mapping
pipeline can run in a local application, cloud API, batch worker, MCP server,
agent tool, or containerized data pipeline. Compiled numerical kernels keep
the processing deterministic and efficient.
:::

::::{tab-set}

:::{tab-item} Python
:sync: python

The current Python interface exposes the high-level mapping pipeline through
`apbase.Map` and `apbase.create_map`:

```python
import apbase

result = apbase.Map(resolution=10.0)(x, y, z)

result.method                  # "idw" or "kriging", picked by validation error
result.x, result.y, result.z   # compact map points inside the boundary
```

:::

::::

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

## What the pipeline handles

- **One mapping pipeline.** The high-level interface handles filtering,
  boundary and grid generation, variogram fitting, validation, model
  selection, and final interpolation in one workflow.
- **Automatic model selection.** The pipeline compares IDW with ordinary
  kriging and uses the method with the lower RMSE for the current dataset.
- **Efficient numerical work.** A fitted variogram is reused for radius
  selection, cross-validation, and final kriging, avoiding repeated work.
- **Ready for services and batch jobs.** The pipeline accepts field data and
  returns compact map results without requiring a web framework, database,
  desktop GIS, or notebook runtime.
- **Works with irregular, noisy points.** Invalid rows, global outliers, and
  local spatial outliers are removed before interpolation runs.
- **Useful defaults.** When no search radius is provided, IDW and kriging use
  the range estimated by the fitted variogram.

See {doc}`quickstart` for a full worked example and {doc}`production` for
deployment guidance. Use {doc}`user-guide/index` and
{doc}`methodology/index` when you need advanced control or want to audit the
mathematics behind the automatic choice.
