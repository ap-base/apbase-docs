# APbase

APbase turns irregular field data, such as yield-monitor logs, soil samples,
and sensor readings, into validated maps. It filters the source points,
handles geographic coordinates when needed, builds the target grid, fits the
variogram, compares interpolation methods, and keeps the one with the lower
cross-validation RMSE. You get a ready-to-use map without choosing a
mathematical model by hand.

Python package: [apbase-python](https://github.com/ap-base/apbase-python)

Rust crate: [apbase-rust](https://github.com/ap-base/apbase-rust)

The documentation is also published in Brazilian Portuguese (`docs/pt-br/`).
See [TRANSLATING.md](TRANSLATING.md) for how translations are organized.
