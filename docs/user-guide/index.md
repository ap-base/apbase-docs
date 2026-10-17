# User guide

This guide explains how APbase turns irregular field data into validated maps.
APbase is available as the Python package `apbase` and the Rust crate
`apbase`; each example has a tab for each language. Start with
{doc}`../installation` and {doc}`../quickstart` to install it and create your
first map.

For normal map generation, start with `Map` or `create_map`, which run the
full pipeline described in {doc}`grid-and-mapping`. Use the lower-level
components only when you need to inspect or control one stage.

For service, worker, container, and cloud deployment guidance, see
{doc}`../production`.

## Reading the parameters in Rust

The parameter lists in this guide use the Python names and types. The Rust
crate keeps the same names and defaults, with these conventions:

- Required settings are constructor arguments (`MapOptions::new(resolution)`);
  optional ones are fields of a `<Name>Options` struct that implements
  `Default`, so you set only what you change:
  `IDWOptions { power: 3.0, ..Default::default() }`.
- Estimators follow `new(options)? -> fit(&x, &y, &z)? -> interpolate(&targets)?`.
- Fitted values are read through getter methods, not attributes:
  `kriging.model_params()?.range`, `ck.model_values()?`.
- `None` becomes `Option`: `radius: Some(50.0)`, `seed: Some(42)`,
  `filter_kwargs: Some(SpatialFilterOptions { .. })`.
- String choices become enums, such as `FilterLevel::Light` or
  `CoKrigingMethod::Icm`; they also parse from the Python strings
  (`"icm".parse()?`).
- `array_like` is any slice, `Vec`, array, or `ndarray` array of a numeric
  type; `targets` is an `(n, 2)` `ndarray` array, a slice or `Vec` of `[x, y]`
  pairs, a slice or `Vec` of point `geos::Geometry` values, or a fitted `Grid`.
- Dictionaries of variables are `IndexMap<String, (Array1<f64>, Array1<f64>, Array1<f64>)>`,
  and results by method are `IndexMap`s in a stable order
  (`cv.by_method["icm"].rmse`). The cokriging examples need the `indexmap`
  crate, and some examples use `ndarray` types directly.
- Every fallible call returns `Result<T, ApbaseError>`.
  `e.is(ErrorKind::InterpolationError)` is true for that kind and for every
  more specific kind under it, such as `KrigingInvalidRadiusError`.

## Pages in this guide

- {doc}`grid-and-mapping`: the automatic `Map` pipeline, its result, and manual
  target grids.
- {doc}`filtering`: removing invalid rows and spatial outliers.
- {doc}`variogram`: fitting and inspecting the variogram.
- {doc}`idw`: inverse distance weighting.
- {doc}`kriging`: local ordinary kriging.
- {doc}`cross-validation`: the IDW-vs-kriging comparison behind `Map`.
- {doc}`cokriging`: estimating with secondary variables (advanced).

```{toctree}
:hidden:
:maxdepth: 1

grid-and-mapping
filtering
variogram
idw
kriging
cross-validation
cokriging
```

For the mathematics behind the automatic IDW-vs-kriging choice, see
{doc}`../methodology/index`. For public signatures, see
{doc}`../api/index`.
