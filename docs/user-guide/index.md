# User Guide

This guide explains how APbase turns irregular field data into validated maps.
The current implementation is the Python package `apbase-python`. Start with
{doc}`../installation` and {doc}`../quickstart` to install it and create your
first map.

For normal map generation, start with `apbase.Map` or `apbase.create_map`.
They run the full pipeline automatically: filtering, grid generation,
variogram fitting, cross-validation, model selection, and interpolation. Use
the lower-level components only when you need to inspect or control one stage.

For service, worker, container, and cloud deployment guidance, see
{doc}`../production`.

:::{note}
If you only need a map, the high-level interface is the simplest path. Use
`SpatialFilter`, `Grid`, `IDW`, `Kriging`, or `cross_validate` directly when
you need diagnostics, experiments, or a specific method.
:::

```{toctree}
:maxdepth: 1

grid-and-mapping
```

```{toctree}
:hidden:
:maxdepth: 1

filtering
variogram
idw
kriging
cokriging
cross-validation
```

For the mathematics behind the automatic IDW-vs-kriging choice, see
{doc}`../methodology/index`. For public signatures, see
{doc}`../api/index`.
