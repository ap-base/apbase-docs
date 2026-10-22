# Geração de mapas e grades

## Map: o pipeline automático

`Map` (`apbase.Map` em Python, `apbase::Map` em Rust) é o principal ponto de
entrada para criar mapas a partir de dados pontuais irregulares. Uma chamada
roda o pipeline de mapeamento completo:

1. filtra registros inválidos, outliers globais e outliers espaciais locais;
2. infere ou usa o contorno de interpolação;
3. monta a grade de interpolação regular;
4. ajusta um semivariograma compartilhado;
5. faz a validação cruzada do IDW contra a krigagem ordinária;
6. escolhe o método com menor RMSE (raiz do erro quadrático médio)
   leave-one-out;
7. interpola e devolve os pontos da grade dentro do contorno.

### Entradas do Map

`x`, `y` : array_like
: Coordenadas dos pontos amostrais. Coordenadas projetadas são usadas como
  estão. Longitude/latitude geográficas são detectadas e convertidas
  internamente para coordenadas métricas antes dos cálculos de distância.

`z` : array_like
: Valor amostral de cada par de coordenadas. `x`, `y` e `z` precisam ser
  unidimensionais e ter o mesmo tamanho.

`resolution` : float
: Espaçamento obrigatório da grade de saída. Para entrada projetada, use a
  unidade das coordenadas. Para entrada em longitude/latitude, use metros.

`filter` : bool, padrão `True`
: Roda o filtro espacial antes da validação cruzada e da interpolação.

`bounds` : geometry, str, bytes, opcional
: Domínio de interpolação. Aceita uma geometria Shapely, WKT ou WKB no mesmo
  sistema de coordenadas da entrada original. Se for omitido, o APbase infere
  um contorno a partir dos pontos amostrais filtrados.

`geographic_mode` : {"local", "utm"}, opcional
: Estratégia de projeção para entrada detectada em longitude/latitude. Deixe
  como `None` para a escolha automática.

`power` : float, padrão `2.0`
: Expoente da distância no IDW. É usado na validação cruzada leave-one-out do
  IDW e, se o IDW vencer, na interpolação final.

`max_neighbors` : int, padrão `40`
: Número máximo de pontos amostrais locais usados por ponto a estimar, na
  validação cruzada e na interpolação final.

`min_neighbors` : int, padrão `3`
: Número mínimo de pontos amostrais dentro do raio de busca. Quando há menos,
  são usados os `max_neighbors` pontos mais próximos, qualquer que seja a
  distância.

`max_cv_points` : int, padrão `500`
: Número máximo de pontos amostrais avaliados na validação cruzada
  leave-one-out. Mantém o tempo de execução limitado em conjuntos de dados
  grandes.

`seed` : int, opcional
: Semente aleatória usada quando a validação cruzada sorteia um subconjunto
  dos pontos amostrais.

`filter_kwargs` : dict, opcional
: Opções extras repassadas ao `SpatialFilter` quando `filter=True`. Em Rust,
  `Some(SpatialFilterOptions { .. })`.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase import Map

mapper = Map(resolution=10.0)
result = mapper(x, y, z)

result.method                  # "idw" ou "kriging", o que tiver menor RMSE na LOO-CV
result.x, result.y, result.z   # pontos da grade dentro do contorno

X, Y, Z = result.to_raster()   # opcional: arrays (ny, nx), NaN fora do contorno
array3d = result.to_array3d()  # np.dstack((X, Y, Z)) -> (ny, nx, 3)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::{Map, MapOptions};

let result = Map::new(MapOptions::new(10.0)).call(&x, &y, &z)?;

result.method;                           // Method::Idw ou Method::Kriging, o que tiver menor RMSE na LOO-CV
(&result.x, &result.y, &result.z);       // pontos da grade dentro do contorno

let (rx, ry, rz) = result.to_raster()?;  // opcional: arrays (ny, nx), NaN fora do contorno
let array3d = result.to_array3d()?;      // (ny, nx, 3): rx, ry e rz empilhados
```

:::

::::

Você pode reaproveitar uma instância de `Map`. Configure uma vez e rode o
mesmo pipeline sobre vários conjuntos de dados. Chamar a instância e chamar
`fit_generate` dá no mesmo: os dois rodam o pipeline, guardam o resultado na
instância (`mapper.result`) e o devolvem:

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
    bounds: Some(my_polygon_wkt.into()), // WKT, bytes WKB ou um geos::Geometry
    seed: Some(42),
    ..MapOptions::new(10.0)
});
let result_a = mapper.fit_generate(&x_a, &y_a, &z_a)?;
let result_b = mapper.call(&x_b, &y_b, &z_b)?;
```

:::

::::

Como a instância guarda o último resultado, não compartilhe um mesmo `Map`
entre requisições concorrentes. Crie um por requisição ou job, ou use
`create_map`.

`create_map` é o atalho funcional para o mesmo pipeline automático:

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

`create_map` aceita as mesmas entradas que `Map`. Use-o quando não precisar
reaproveitar um mapper configurado.

O `Map` ajusta o semivariograma uma vez e o reaproveita para o raio de busca,
a validação cruzada e o modelo final de krigagem.

### MapResult

`result.x`, `result.y`, `result.z` : numpy.ndarray (`Array1<f64>` em Rust)
: Pontos da grade dentro do contorno de interpolação, no sistema de
  coordenadas original, sem preenchimento com NaN.

`result.method` : {"idw", "kriging"}
: Método com menor RMSE leave-one-out nos pontos retirados em que os dois
  métodos deram uma predição finita (um empate fica com o IDW). Em Rust, um
  enum `Method` que é igual a `"idw"` ou `"kriging"` numa comparação.

`result.cross_validation`
: Relatório da validação IDW × krigagem usado na seleção do modelo.

`result.radius` : float
: Raio de busca usado na validação cruzada e na interpolação final, derivado
  do semivariograma ajustado.

`result.resolution` : float
: Espaçamento da grade de saída.

`result.n_source_points` : int
: Número de pontos amostrais usados depois de remover registros não finitos
  e, quando ativada, da filtragem espacial.

`result.filter_statistics`
: Diagnósticos por ponto do filtro espacial (`pct_diff`, `local_z`,
  `local_prob`), ou `None` quando a filtragem está desligada.

`result.coordinate_transform`
: Transformação usada para devolver a entrada detectada em longitude/latitude
  às coordenadas originais, ou `None` para entrada projetada.

`result.to_raster()`
: Monta os arrays `(X, Y, Z)` só quando um raster completo é necessário.

`result.to_array3d()`
: Monta um único array `(ny, nx, 3)`, equivalente a `np.dstack((X, Y, Z))`.

Em Rust, `call` e `fit_generate` devolvem um `Arc<MapResult>`, e `create_map`
devolve um `MapResult`; `to_raster()` e `to_array3d()` devolvem `Result`s.

## Grid: pontos a estimar definidos manualmente

O `Grid` monta uma grade regular de pontos a estimar dentro de um contorno.
Você pode fornecer o contorno ou deixar o APbase inferi-lo a partir dos pontos
amostrais. Diferente do `Map`, o `Grid` não converte `x`/`y` em
longitude/latitude: passe coordenadas projetadas.

### Entradas do Grid

`resolution` : float, padrão `20.0`
: Espaçamento da grade, nas unidades das coordenadas.

`boundary` : geometry, str, bytes, opcional
: Contorno explícito da grade. Em Python, pode ser uma geometria Shapely, WKT
  ou WKB. Em Rust, é um `geos::Geometry`; use `Grid::from_wkt` ou
  `Grid::from_wkb` para WKT ou WKB.

`x`, `y` : array_like, opcional
: Coordenadas dos pontos amostrais usadas para inferir o contorno quando
  `boundary` é omitido. O contorno inferido é uma envoltória côncava dos
  pontos.

`hull_ratio` : float, padrão `0.12`
: Razão da envoltória côncava usada quando o contorno é inferido. Valores
  menores seguem os pontos mais de perto; `1.0` dá a envoltória convexa.

`geographic_mode` : {"local", "utm"}, opcional
: Usado quando `boundary` está em longitude/latitude mas `x`/`y` são
  projetados: o contorno é reprojetado com essa estratégia antes de montar a
  grade.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.grid import Grid

# Infere o contorno a partir dos pontos amostrais.
targets = Grid(resolution=10.0).generate(x, y)

# Ou fornece um contorno explícito (uma geometria Shapely).
targets = Grid(boundary=my_polygon, resolution=10.0).generate()
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::grid::{Grid, GridOptions};

// Infere o contorno a partir dos pontos amostrais.
let targets = Grid::new(GridOptions { resolution: 10.0, ..Default::default() })?
    .generate(Some(&x), Some(&y))?;

// Ou fornece um contorno explícito (WKT aqui; Grid::from_wkb e um geos::Geometry também funcionam).
let grid = Grid::from_wkt(my_polygon_wkt, GridOptions { resolution: 10.0, ..Default::default() })?;
let targets = grid.points()?;
```

:::

::::

Em Python, `Grid.from_wkt(wkt, resolution=10.0)` e
`Grid.from_wkb(wkb, resolution=10.0)` montam a grade direto a partir de um
contorno WKT ou WKB, sem pontos amostrais. `generate()` equivale a
`fit().points` numa chamada só. Use `fit()` diretamente quando também precisar
de `fitted_boundary`, o contorno preparado usado depois do buffer.
`apbase.grid.create_point_grid` é o atalho funcional.

Em Rust, `Grid::from_wkt` e `Grid::from_wkb` recebem um `GridOptions` e
devolvem uma grade ajustada. Leia os pontos a estimar com `grid.points()?` ou
passe o próprio `Grid` como `targets`. `Grid::generate` e `Grid::fit` recebem
`Option`s para `x` e `y` (`None` quando há contorno definido), e
`apbase::grid::create_point_grid` é o atalho funcional.

Use o `Grid` diretamente quando precisar de pontos a estimar manuais para uma
interpolação personalizada, diagnósticos ou experimentos fora do pipeline
automático do `Map`. Ele não é necessário para a criação normal de mapas.
