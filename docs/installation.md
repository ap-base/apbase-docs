# Installation

APbase's mapping pipeline is distributed with compiled numerical extensions.
Install the integration for the language and runtime you use.

For production deployments, install APbase in the runtime used by your API
service, worker, MCP server, agent backend, or batch container. See
{doc}`production` for cloud and worker sizing guidance.

## Requirements

::::{tab-set}

:::{tab-item} Python
:sync: python

- Python 3.12+
- `numpy`, `pyproj`, `shapely` (installed automatically as dependencies)

:::

::::

## Install

:::::{tab-set}

::::{tab-item} Python
:sync: python

```bash
pip install apbase
```

:::{note}
If `apbase` is available from your package index, the command above is
enough. Until it is published to a public index, install from a local
distribution or the project repository.
:::

```bash
pip install /path/to/apbase-python
```

```bash
pip install git+https://github.com/ap-base/apbase-python.git
```

::::

:::::

## Optional extras

::::{tab-set}

:::{tab-item} Python
:sync: python

Some Python helpers accept `GeoDataFrame` or `GeoSeries` inputs when
`geopandas` is installed. You can skip this extra when passing plain NumPy
arrays:

```bash
pip install geopandas
```

:::

::::

## Verify the install

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
import apbase

apbase.config["n_threads"] = 4
print(apbase.Map, apbase.create_map)
```

:::

::::

## Using it in production

::::{tab-set}

:::{tab-item} Python
:sync: python

The package already includes its compiled native extensions. Install it in the
production runtime with the package manager; the application image does not
need a Fortran compiler or a separate build stage.

Configure CPU parallelism once when the process starts:

```bash
export APBASE_N_THREADS=2
```

or in Python before handling work:

```python
import apbase

apbase.config["n_threads"] = 2
```

Keep `workers * APBASE_N_THREADS` at or below the vCPU allocated to the
service to avoid CPU oversubscription.

:::

::::
