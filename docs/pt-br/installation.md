# Instalação

O APbase é distribuído com extensões numéricas compiladas. Instale o pacote da
sua linguagem.

## Requisitos

::::{tab-set}

:::{tab-item} Python
:sync: python

- CPython 3.12, 3.13 ou 3.14
- `numpy` (2.0+), `pyproj` e `shapely` (instalados automaticamente como
  dependências)
- Wheels prontas para Linux em `x86_64` (glibc 2.28+), macOS em `arm64` (14+)
  e `x86_64` (15+) e Windows em `x86_64`. Não é publicada distribuição de
  código-fonte, então outras plataformas e versões do Python não conseguem
  instalar o pacote.

:::

:::{tab-item} Rust
:sync: rust

- Rust 1.85+ (edition 2024)
- Linux em `x86_64` (`x86_64-unknown-linux-gnu`), o único target com kernels
  nativos pré-compilados hoje
- GEOS 3.12 ou mais recente e PROJ 9.6.2 ou mais recente (veja a nota abaixo
  para um PROJ mais antigo), além do runtime de Fortran, OpenMP e BLAS usado
  pelos kernels nativos

:::

::::

## Instalar

:::::{tab-set}

::::{tab-item} Python
:sync: python

```bash
pip install apbase
```

Para instalar a versão de desenvolvimento a partir do repositório:

```bash
pip install git+https://github.com/ap-base/apbase-python.git
```

::::

::::{tab-item} Rust
:sync: rust

Instale as bibliotecas do sistema e depois adicione o crate:

```bash
sudo apt install gfortran libopenblas-dev libgeos-dev libproj-dev pkg-config
cargo add apbase
```

ou declare-o no `Cargo.toml`:

```toml
[dependencies]
apbase = "0.1.4"
```

Os kernels Fortran vêm dentro do crate como biblioteca estática, então nenhum
compilador Fortran roda durante o build. `gfortran` e `libopenblas-dev` só são
necessários na etapa de link, que procura `libgfortran.so` e `libopenblas.so`.

:::{note}
Se o PROJ do sistema for anterior à 9.6.2, a dependência `proj-sys` compila o
PROJ a partir do código-fonte, o que também exige `cmake`, `sqlite3`,
`libsqlite3-dev` e `libtiff-dev`. Cada
[release](https://github.com/ap-base/apbase-rust/releases) do `apbase-rust` no
GitHub também traz o pacote `apbase-<version>.crate`.
:::

Duas variáveis de ambiente de build mudam o que é linkado:
`APBASE_BLAS_LIBS` recebe bibliotecas BLAS/LAPACK separadas por espaço para
linkar no lugar do OpenBLAS, e `APBASE_NATIVE_LIB_DIR` aponta para um
diretório com o seu próprio `libapbase_native.a`, para builds de
desenvolvimento.

::::

:::::

## Extras opcionais

::::{tab-set}

:::{tab-item} Python
:sync: python

O argumento `targets` de `IDW`, `Kriging` e `CoKriging` também aceita um
`GeoDataFrame` ou `GeoSeries` de pontos quando o `geopandas` está instalado.
Você pode dispensar esse extra se passar arrays NumPy simples:

```bash
pip install geopandas
```

:::

:::{tab-item} Rust
:sync: rust

O crate Rust não tem extras opcionais. Contornos são passados como WKT, WKB ou
`geos::Geometry`, e os pontos a estimar como arrays `ndarray`, slices de pares
`[x, y]`, valores `geos::Geometry` de ponto ou um `Grid` ajustado.

:::

::::

## Verificar a instalação

::::{tab-set}

:::{tab-item} Python
:sync: python

Gere um mapa pequeno para confirmar que os kernels nativos carregam e rodam:

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

## Uso em produção

Veja {doc}`production` para a configuração de threads e o dimensionamento de
workers.

Um serviço Rust compilado com `cargo build --release` linka os kernels nativos
estaticamente, mas a imagem de execução ainda precisa das bibliotecas
compartilhadas de que eles dependem: o runtime de Fortran, OpenMP e BLAS
(`libgfortran5`, `libgomp1` e `libopenblas0` no Debian/Ubuntu), a biblioteca C
do GEOS (`libgeos-c1t64` no Ubuntu 24.04) e o PROJ, quando ele foi linkado a
partir do sistema. Um PROJ compilado a partir do código-fonte é linkado
estaticamente e precisa apenas de `libsqlite3-0` em tempo de execução.
