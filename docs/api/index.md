# API Reference

The public API is intentionally small. Start with {class}`apbase.Map` or
{func}`apbase.create_map` to create maps; use {data}`apbase.config` for
process-wide runtime settings.

The reference is generated from NumPy-style docstrings, following the same
practical shape used by scientific packages such as Shapely: short purpose,
explicit parameters, return value, raised errors, and examples. Lower-level
geostatistical modules remain available for advanced workflows, but they are
not the recommended entry point for map creation.

```{toctree}
:maxdepth: 1

mapping
common
```
