# Inverso da distância ponderada (IDW)

O `IDW` estima o valor de cada ponto a estimar como uma média dos pontos
amostrais vizinhos ponderada pela distância. A maioria dos usuários pode
deixar isso com o `apbase.Map`: o pipeline automático compara o IDW com a
krigagem ordinária e fica com o IDW quando ele tem o menor RMSE (raiz do erro
quadrático médio) leave-one-out para o conjunto de dados atual.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.idw import IDW

idw = IDW(power=2.0, max_neighbors=40, min_neighbors=3).fit(x, y, z)
z_targets = idw.interpolate(targets)  # targets: array (n, 2)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::idw::{IDW, IDWOptions};

let mut idw = IDW::new(IDWOptions { power: 2.0, max_neighbors: 40, min_neighbors: 3, ..Default::default() })?;
idw.fit(&x, &y, &z)?;
let z_targets = idw.interpolate(&targets)?; // targets: array (n, 2) ou um Grid ajustado
```

:::

::::

## Parâmetros

`x`, `y` : array_like
: Coordenadas dos pontos amostrais passadas ao `fit`. O `IDW` não converte
  longitude/latitude: passe coordenadas projetadas, na mesma unidade de
  `radius`.

`z` : array_like
: Valores amostrais. Precisa ter o mesmo tamanho de `x` e `y`.

`targets` : array_like ou Grid
: Coordenadas dos pontos a estimar passadas ao `interpolate`: um array
  `(n_targets, 2)`, um `Grid` ajustado ou geometrias de ponto (uma lista de
  pontos Shapely, ou um `GeoSeries`/`GeoDataFrame`).

`radius` : float, opcional
: Raio de busca local. Se for omitido, é derivado de um semivariograma
  ajustado (veja {doc}`../methodology/variogram-fitting`).

`power` : float, padrão `2.0`
: Potência (expoente) da distância. Valores maiores dão mais peso aos pontos
  próximos.

`max_neighbors` : int, padrão `40`
: Número máximo de pontos amostrais usados por ponto a estimar.

`min_neighbors` : int, padrão `3`
: Número mínimo de pontos amostrais dentro de `radius`. Quando há menos, são
  usados os `max_neighbors` pontos mais próximos, qualquer que seja a
  distância.

## Quando o IDW vence a krigagem

O IDW é uma média ponderada determinística. É rápido, não faz suposições sobre
a distribuição dos dados e se comporta de forma previsível quando os dados são
esparsos. A krigagem ordinária usa também a correlação espacial capturada pelo
semivariograma. Ela pode ser mais precisa quando essa estrutura está bem
ajustada, mas custa mais e é mais sensível a um ajuste ruim. O `apbase.Map` e
o `apbase.create_map` comparam os dois métodos nos seus dados, então você não
precisa escolher manualmente.

Veja {doc}`../methodology/idw` para a fórmula de ponderação.
