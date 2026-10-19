# Início rápido

O `Map` transforma medições brutas de campo em um mapa validado em um único
passo. Passe a ele `x`, `y`, `z` e a resolução desejada: ele roda o pipeline
inteiro, da filtragem à interpolação final, e fica com o método de
interpolação de menor RMSE (raiz do erro quadrático médio) na validação
cruzada leave-one-out (LOO-CV). {doc}`user-guide/grid-and-mapping` lista cada
etapa, entrada e campo do resultado.

## Entradas

`x`, `y` : array_like
: Coordenadas dos pontos amostrais. Coordenadas projetadas são usadas como
  estão. Longitude/latitude geográficas são detectadas e convertidas
  internamente para coordenadas métricas antes dos cálculos de distância; o
  resultado volta nas coordenadas originais.

`z` : array_like
: Valor amostral de cada par de coordenadas. `x`, `y` e `z` precisam ser
  unidimensionais e ter o mesmo tamanho.

`resolution` : float
: Espaçamento obrigatório da grade de saída. Para entrada projetada, use a
  unidade das coordenadas. Para entrada em longitude/latitude, use metros.

`bounds` : geometry, str, bytes, opcional
: Domínio de interpolação. Aceita uma geometria Shapely, WKT ou WKB no mesmo
  sistema de coordenadas da entrada original. Se for omitido, o APbase infere
  um contorno a partir dos pontos amostrais filtrados.

Em Rust, `x`, `y` e `z` podem ser slices, `Vec`s, arrays ou arrays `ndarray`
de qualquer tipo numérico. `resolution` é o argumento de `MapOptions::new`, e
`bounds` é um campo opcional de `MapOptions` com WKT, bytes WKB ou um
`geos::Geometry`.

## Rodar o pipeline

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
import numpy as np

import apbase
from apbase import Map

apbase.config["n_threads"] = 4

# Dados amostrais sintéticos: 500 pontos com valores espacialmente correlacionados mais ruído.
rng = np.random.default_rng(0)
x = rng.uniform(0, 1000, 500)
y = rng.uniform(0, 1000, 500)
z = np.sin(x / 150) * np.cos(y / 150) * 10 + rng.uniform(-0.5, 0.5, 500)

# Uma chamada: filtragem -> grade -> semivariograma -> validação cruzada -> melhor modelo.
mapper = Map(resolution=10.0)
result = mapper(x, y, z)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::{Map, MapOptions};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    apbase::config.set("n_threads", 4)?;

    // Dados amostrais sintéticos: 500 pontos com valores espacialmente correlacionados mais ruído.
    let mut state: u64 = 0;
    let mut uniform = move || {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        (state >> 11) as f64 / (1u64 << 53) as f64
    };
    let (mut x, mut y, mut z) = (Vec::new(), Vec::new(), Vec::new());
    for _ in 0..500 {
        let (xi, yi) = (uniform() * 1000.0, uniform() * 1000.0);
        x.push(xi);
        y.push(yi);
        z.push((xi / 150.0).sin() * (yi / 150.0).cos() * 10.0 + (uniform() - 0.5));
    }

    // Uma chamada: filtragem -> grade -> semivariograma -> validação cruzada -> melhor modelo.
    let mut mapper = Map::new(MapOptions::new(10.0));
    let result = mapper.call(&x, &y, &z)?;
    println!("{}", result.method);
    Ok(())
}
```

:::

::::

:::{tip}
`apbase.config["n_threads"]` em Python e `apbase::config.set("n_threads", n)?`
em Rust são configuração de OpenMP para o processo inteiro, não um argumento
de `Map`. Defina uma vez, antes de criar qualquer instância, e não a cada
chamada.
:::

## O que você recebe

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
result.method                  # "idw" ou "kriging", o que tiver menor RMSE na LOO-CV
result.x, result.y, result.z   # pontos da grade dentro do contorno
X, Y, Z = result.to_raster()   # opcional: arrays (ny, nx), NaN fora do contorno
```

:::

:::{tab-item} Rust
:sync: rust

```rust
result.method;                           // Method::Idw ou Method::Kriging, o que tiver menor RMSE na LOO-CV
(&result.x, &result.y, &result.z);       // pontos da grade dentro do contorno
let (rx, ry, rz) = result.to_raster()?;  // opcional: arrays (ny, nx), NaN fora do contorno
```

:::

::::

`result.x`, `result.y` e `result.z` guardam só os pontos da grade dentro do
contorno, sem preenchimento com NaN. Chame `to_raster()` apenas quando
precisar de um raster `(ny, nx)` completo.

Para auditar o que o pipeline fez, inspecione `result.cross_validation`,
`result.filter_statistics` e `result.n_source_points`.

## O atalho funcional

`create_map` (`apbase.create_map` em Python, `apbase::create_map` em Rust)
encapsula o mesmo pipeline sem instanciar `Map` explicitamente:

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
result = apbase.create_map(x, y, z, resolution=10.0)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
let result = apbase::create_map(&x, &y, &z, apbase::MapOptions::new(10.0))?;
```

:::

::::

## Controle manual avançado

Para a maioria das aplicações, `Map` e `create_map` bastam. Use os módulos de
nível mais baixo para inspecionar resultados intermediários, forçar um método
de interpolação específico ou montar um fluxo avançado, como a cokrigagem;
veja {doc}`user-guide/index`. {doc}`methodology/index` cobre a matemática por
trás da escolha automática do modelo.
