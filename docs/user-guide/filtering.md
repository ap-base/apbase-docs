# Spatial filtering

`SpatialFilter` cleans the source points before interpolation. It removes
invalid rows and, when enabled, global and local spatial outliers using a
global-then-local approach developed for high-density agricultural data
{cite}`Maldaner2018,Maldaner2020`.

You usually do not need to call it yourself. `apbase.Map` runs the filter
internally before comparing interpolation methods. Use `SpatialFilter` when
you want to inspect the filtered data or tune the filtering stage.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.filtering import SpatialFilter

spatial_filter = SpatialFilter(
    filter_level="light",
    max_neighbors=120,
    cell_factor=3,
).fit(x, y, z)

x_filtered, y_filtered, z_filtered = spatial_filter.filter()
```

:::

::::

## What it does

Filtering happens in two passes:

1. **Global IQR pass** (optional, `apply_global_iqr=True` by default): one
   interquartile-range check over the source data removes extreme readings,
   such as sensor faults, before spatial checks begin. This follows the global
   filtering step in {cite}`Maldaner2018`.
2. **Local pass**: each point is compared with nearby points within `radius`,
   capped at `max_neighbors`. `filter_level` controls how strict the local
   threshold is, following the local filtering steps in
   {cite}`Maldaner2018`.

## Parameters

`x`, `y` : array_like
: Source coordinates passed to `fit`. Use projected/metric coordinates when
  `radius` is metric.

`z` : array_like
: Source values. Must have the same length as `x` and `y`.

`radius` : float, optional
: Local search radius. If omitted, a variogram is fit and `range / 3` is used.

`filter_level` : {"light", "moderate", "strict", "aggressive"}, default `"light"`
: Local outlier threshold, from loosest to strictest.

`apply_global_iqr` : bool, default `True`
: Run the global IQR pass before local filtering.

`max_neighbors` : int, default `120`
: Neighbor cap per point for the local pass. `0` uses every point within
  `radius`.

`cell_factor` : int, default `3`
: Spatial grid factor used by the local neighborhood search.

`dedup_radius`, `dedup_z_tol` : float, default `0.0`
: Optional duplicate handling for dense GPS logs. Leave disabled unless
  repeated near-identical points are causing local variance collapse.

## Reading results

After `fit`, you can inspect the result in three ways:

- `filter()` -- filtered `(x, y, z)` arrays (only the points that passed).
- `mask()` -- boolean keep-mask aligned with the original input.
- `statistics` -- per-point diagnostics (`pct_diff`, local z-score, local
  probability) for every input point, including ones that were dropped.

## Duplicate-heavy sources

Point sources with many near-duplicate coordinates, such as repeated GPS fixes
in high-frequency yield-monitor logs {cite}`Maldaner2020`, can collapse local
variance toward zero and create gaps after filtering. `dedup_radius` and
`dedup_z_tol` collapse near-duplicate clusters to one representative only
while building local neighborhood statistics. Every input point is still
scored individually. Leave both at `0.0` unless you see this pattern in your
data.

See {py:class}`apbase.filtering.SpatialFilter` in the API reference for
every parameter, including the less commonly tuned ones
(`candidate_fraction`, `global_iqr_whisker`).
