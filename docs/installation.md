# Installation

APbase is distributed with compiled numerical extensions. Install the package
for your language.

## Requirements

::::{tab-set}

:::{tab-item} Python
:sync: python

- CPython 3.12, 3.13, or 3.14
- `numpy` (2.0+), `pyproj`, `shapely` (installed automatically as dependencies)
- Prebuilt wheels for Linux on `x86_64` (glibc 2.28+), macOS on `arm64`
  (14+) and `x86_64` (15+), and Windows on `x86_64`. No source distribution
  is published, so other platforms and Python versions cannot install the
  package.

:::

:::{tab-item} Rust
:sync: rust

- Rust 1.85+ (edition 2024)
- Linux on `x86_64` (`x86_64-unknown-linux-gnu`), the only target with
  prebuilt native kernels today
- GEOS 3.12 or newer and PROJ 9.6.2 or newer (see the note below for an older
  PROJ), plus the Fortran, OpenMP, and BLAS runtime used by the native kernels

:::

::::

## Install

:::::{tab-set}

::::{tab-item} Python
:sync: python

```bash
pip install apbase
```

To install the development version from the repository instead:

```bash
pip install git+https://github.com/ap-base/apbase-python.git
```

::::

::::{tab-item} Rust
:sync: rust

Install the system libraries, then add the crate:

```bash
sudo apt install gfortran libopenblas-dev libgeos-dev libproj-dev pkg-config
cargo add apbase
```

or declare it in `Cargo.toml`:

```toml
[dependencies]
apbase = "0.1.4"
```

The Fortran kernels ship inside the crate as a static library, so no Fortran
compiler runs during the build. `gfortran` and `libopenblas-dev` are needed
only for the link step, which looks for `libgfortran.so` and `libopenblas.so`.

:::{note}
If the system PROJ is older than 9.6.2, the `proj-sys` dependency builds PROJ
from source, which also needs `cmake`, `sqlite3`, `libsqlite3-dev`, and
`libtiff-dev`. Each GitHub
[release](https://github.com/ap-base/apbase-rust/releases) of `apbase-rust`
also carries the packaged `apbase-<version>.crate`.
:::

Two build-time environment variables change what is linked:
`APBASE_BLAS_LIBS` takes space-separated BLAS/LAPACK libraries to link instead
of OpenBLAS, and `APBASE_NATIVE_LIB_DIR` points to a directory with your own
`libapbase_native.a` for development builds.

::::

:::::

## Optional extras

::::{tab-set}

:::{tab-item} Python
:sync: python

The `targets` argument of `IDW`, `Kriging`, and `CoKriging` also accepts a
`GeoDataFrame` or `GeoSeries` of points when `geopandas` is installed. You can
skip this extra when passing plain NumPy arrays:

```bash
pip install geopandas
```

:::

:::{tab-item} Rust
:sync: rust

The Rust crate has no optional extras. Boundaries are passed as WKT, WKB, or a
`geos::Geometry`, and targets as `ndarray` arrays, slices of `[x, y]` pairs,
point `geos::Geometry` values, or a fitted `Grid`.

:::

::::

## Verify the install

::::{tab-set}

:::{tab-item} Python
:sync: python

Build a tiny map to confirm the native kernels load and run:

```python
import numpy as np

import apbase

rng = np.random.default_rng(0)
x, y = rng.uniform(0, 100, 50), rng.uniform(0, 100, 50)
result = apbase.create_map(x, y, x + y, resolution=10.0)
print(result.method, result.z.size)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let x: Vec<f64> = (0..50).map(|i| (i * 37 % 100) as f64).collect();
    let y: Vec<f64> = (0..50).map(|i| (i * 61 % 100) as f64).collect();
    let z: Vec<f64> = x.iter().zip(&y).map(|(a, b)| a + b).collect();
    let result = apbase::create_map(&x, &y, &z, apbase::MapOptions::new(10.0))?;
    println!("{} {}", result.method, result.z.len());
    Ok(())
}
```

```bash
cargo run --release
```

:::

::::

## Using it in production

See {doc}`production` for thread configuration and worker sizing.

A Rust service built with `cargo build --release` links the native kernels
statically, but the runtime image still needs the shared libraries they depend
on: the Fortran, OpenMP, and BLAS runtime (`libgfortran5`, `libgomp1`, and
`libopenblas0` on Debian/Ubuntu), the GEOS C library (`libgeos-c1t64` on
Ubuntu 24.04), and PROJ when it was linked from the system. A PROJ built from
source is linked statically and needs only `libsqlite3-0` at run time.
