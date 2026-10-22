# Map and grid generation

## Map: the automatic pipeline

`Map` (`apbase.Map` in Python, `apbase::Map` in Rust) is the main entry point
for creating maps from irregular point data. One call runs the complete
mapping pipeline:

1. filter invalid rows, global outliers, and local spatial outliers;
2. infer or use the interpolation boundary;
3. build the regular target grid;
4. fit one shared variogram;
5. cross-validate IDW against ordinary kriging;
6. select the method with the lower leave-one-out RMSE;
7. interpolate and return the grid points inside the boundary.

### Map inputs

`x`, `y` : array_like
: Source coordinates. Projected coordinates are used as-is. Geographic
  longitude/latitude is detected and converted internally to metric coordinates
  before distance calculations.

`z` : array_like
: Source value for each coordinate pair. `x`, `y`, and `z` must be
  one-dimensional and have the same length.

`resolution` : float
: Required output grid spacing. For projected input, use the coordinate unit.
  For longitude/latitude input, use meters.

`filter` : bool, default `True`
: Run the spatial filter before cross-validation and interpolation.

`bounds` : geometry, str, bytes, optional
: Interpolation domain. Accepts a Shapely geometry, WKT, or WKB in the same
  coordinate system as the original input. If omitted, APbase infers a
  boundary from the filtered source points.

`geographic_mode` : {"local", "utm"}, optional
: Projection strategy for detected longitude/latitude input. Leave as `None`
  for the automatic choice.

`power` : float, default `2.0`
: IDW distance exponent. Used in IDW's leave-one-out cross-validation and, if
  IDW wins, in the final interpolation.

`max_neighbors` : int, default `40`
: Maximum local source points used per target during cross-validation and
  final interpolation.

`min_neighbors` : int, default `3`
: Minimum source points within the search radius. When fewer are found, the
  `max_neighbors` nearest points are used regardless of distance.

`max_cv_points` : int, default `500`
: Maximum source points evaluated during leave-one-out cross-validation. Keeps
  runtime bounded on large datasets.

`seed` : int, optional
: Random seed used when cross-validation samples a subset of source points.

`filter_kwargs` : dict, optional
: Extra options forwarded to `SpatialFilter` when `filter=True`. In Rust,
  `Some(SpatialFilterOptions { .. })`.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase import Map

mapper = Map(resolution=10.0)
result = mapper(x, y, z)

result.method                  # "idw" or "kriging", whichever has the lower LOO-CV RMSE
result.x, result.y, result.z   # grid points inside the boundary

X, Y, Z = result.to_raster()   # optional (ny, nx) arrays, NaN outside boundary
array3d = result.to_array3d()  # np.dstack((X, Y, Z)) -> (ny, nx, 3)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::{Map, MapOptions};

let result = Map::new(MapOptions::new(10.0)).call(&x, &y, &z)?;

result.method;                           // Method::Idw or Method::Kriging, whichever has the lower LOO-CV RMSE
(&result.x, &result.y, &result.z);       // grid points inside the boundary

let (rx, ry, rz) = result.to_raster()?;  // optional (ny, nx) arrays, NaN outside boundary
let array3d = result.to_array3d()?;      // (ny, nx, 3): rx, ry, rz stacked
```

:::

::::

You can reuse a `Map` instance. Configure it once, then run the same pipeline
against multiple datasets. Calling the instance and `fit_generate` are
equivalent: both run the pipeline, store the result on the instance
(`mapper.result`), and return it:

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase import Map

mapper = Map(resolution=10.0, bounds=my_polygon, seed=42)
result_a = mapper.fit_generate(x_a, y_a, z_a)
result_b = mapper(x_b, y_b, z_b)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::{Map, MapOptions};

let mut mapper = Map::new(MapOptions {
    bounds: Some(my_polygon_wkt.into()), // WKT, WKB bytes, or a geos::Geometry
    seed: Some(42),
    ..MapOptions::new(10.0)
});
let result_a = mapper.fit_generate(&x_a, &y_a, &z_a)?;
let result_b = mapper.call(&x_b, &y_b, &z_b)?;
```

:::

::::

Because the instance keeps the last result, do not share one `Map` across
concurrent requests. Create one per request or job, or use
`create_map`.

`create_map` is the functional shortcut around the same automatic pipeline:

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
import apbase

result = apbase.create_map(x, y, z, resolution=10.0)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::MapOptions;

let result = apbase::create_map(&x, &y, &z, MapOptions::new(10.0))?;
```

:::

::::

`create_map` accepts the same inputs as `Map`. Use it when you do not need to
reuse a configured mapper.

`Map` fits the variogram once and reuses it for the search radius,
cross-validation, and the final kriging model.

### MapResult

`result.x`, `result.y`, `result.z` : numpy.ndarray (`Array1<f64>` in Rust)
: Grid points inside the interpolation boundary, in the original coordinate
  system, with no NaN padding.

`result.method` : {"idw", "kriging"}
: Method with the lower leave-one-out RMSE over the held-out points where both
  methods gave a finite prediction (a tie goes to IDW). In Rust, a `Method`
  enum that compares equal to `"idw"` or `"kriging"`.

`result.cross_validation`
: IDW-vs-kriging validation report used for model selection.

`result.radius` : float
: Search radius used by cross-validation and the final interpolation, derived
  from the fitted variogram.

`result.resolution` : float
: Output grid spacing.

`result.n_source_points` : int
: Number of source points used after removing non-finite rows and, when
  enabled, spatial filtering.

`result.filter_statistics`
: Per-point diagnostics from the spatial filter (`pct_diff`, `local_z`,
  `local_prob`), or `None` when filtering is disabled.

`result.coordinate_transform`
: Transform used to return detected longitude/latitude input to its original
  coordinates, or `None` for projected input.

`result.to_raster()`
: Builds `(X, Y, Z)` arrays only when a full raster is needed.

`result.to_array3d()`
: Builds one `(ny, nx, 3)` array equivalent to `np.dstack((X, Y, Z))`.

In Rust, `call` and `fit_generate` return an `Arc<MapResult>`, and `create_map`
returns a `MapResult`; `to_raster()` and `to_array3d()` return `Result`s.

## Grid: manual target points

`Grid` builds a regular target-point grid inside a boundary. You can provide
the boundary yourself or let APbase infer one from the source points. Unlike
`Map`, `Grid` does not convert longitude/latitude `x`/`y`: pass projected
coordinates.

### Grid inputs

`resolution` : float, default `20.0`
: Grid spacing in coordinate units.

`boundary` : geometry, str, bytes, optional
: Explicit grid boundary. In Python, this can be a Shapely geometry, WKT, or
  WKB value. In Rust, it is a `geos::Geometry`; use `Grid::from_wkt` or
  `Grid::from_wkb` for WKT or WKB.

`x`, `y` : array_like, optional
: Source coordinates used to infer the boundary when `boundary` is omitted.
  The inferred boundary is a concave hull of the points.

`hull_ratio` : float, default `0.12`
: Concave-hull ratio used when the boundary is inferred. Lower values follow
  the points more closely; `1.0` gives the convex hull.

`geographic_mode` : {"local", "utm"}, optional
: Used when `boundary` is in longitude/latitude but `x`/`y` are projected: the
  boundary is reprojected with this strategy before the grid is built.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.grid import Grid

# Infer the boundary from source points.
targets = Grid(resolution=10.0).generate(x, y)

# Or supply an explicit boundary (a Shapely geometry).
targets = Grid(boundary=my_polygon, resolution=10.0).generate()
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::grid::{Grid, GridOptions};

// Infer the boundary from source points.
let targets = Grid::new(GridOptions { resolution: 10.0, ..Default::default() })?
    .generate(Some(&x), Some(&y))?;

// Or supply an explicit boundary (WKT here; Grid::from_wkb and a geos::Geometry also work).
let grid = Grid::from_wkt(my_polygon_wkt, GridOptions { resolution: 10.0, ..Default::default() })?;
let targets = grid.points()?;
```

:::

::::

In Python, `Grid.from_wkt(wkt, resolution=10.0)` and
`Grid.from_wkb(wkb, resolution=10.0)` build the grid directly from a WKT or
WKB boundary, without source points. `generate()` is `fit().points` in one
call. Use `fit()` directly when you also need `fitted_boundary`, the prepared
boundary used after buffering. `apbase.grid.create_point_grid` is the
functional shortcut.

In Rust, `Grid::from_wkt` and `Grid::from_wkb` take a `GridOptions` and return
a fitted grid. Read its targets with `grid.points()?`, or pass the `Grid`
itself as `targets`. `Grid::generate` and `Grid::fit` take `Option`s for `x`
and `y` (`None` when a boundary is set), and
`apbase::grid::create_point_grid` is the functional shortcut.

Use `Grid` directly when you need manual targets for custom interpolation,
diagnostics, or experiments outside the automatic `Map` pipeline. You do not
need it for normal map creation.
