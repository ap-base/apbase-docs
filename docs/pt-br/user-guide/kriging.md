# Krigagem ordinária

O `Kriging` ajusta ou recebe um modelo de semivariograma e usa a krigagem
ordinária local para estimar os valores nos pontos a estimar. A maioria dos
usuários pode deixar o `apbase.Map` decidir se ela é a melhor opção: o
pipeline compara a krigagem com o IDW e só fica com ela quando tem o menor
RMSE (raiz do erro quadrático médio) leave-one-out.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.kriging import Kriging

kriging = Kriging(max_neighbors=40, min_neighbors=3).fit(x, y, z)
z_targets = kriging.interpolate(targets)  # targets: array (n, 2)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::kriging::{Kriging, KrigingOptions};

let mut kriging = Kriging::new(KrigingOptions { max_neighbors: 40, min_neighbors: 3, ..Default::default() })?;
kriging.fit(&x, &y, &z)?;
let z_targets = kriging.interpolate(&targets)?; // targets: array (n, 2) ou um Grid ajustado
```

:::

::::

## Parâmetros

`x`, `y` : array_like
: Coordenadas dos pontos amostrais passadas ao `fit`. O `Kriging` não converte
  longitude/latitude: passe coordenadas projetadas, na mesma unidade de
  `radius`.

`z` : array_like
: Valores amostrais. Precisa ter o mesmo tamanho de `x` e `y`.

`targets` : array_like ou Grid
: Coordenadas dos pontos a estimar passadas ao `interpolate`: um array
  `(n_targets, 2)`, um `Grid` ajustado ou geometrias de ponto (uma lista de
  pontos Shapely, ou um `GeoSeries`/`GeoDataFrame`).

`radius` : float, opcional
: Raio de busca local. Se for omitido, é derivado do semivariograma ajustado
  (veja {doc}`../methodology/variogram-fitting`).

`max_neighbors` : int, padrão `40`
: Número máximo de pontos amostrais usados por ponto a estimar.

`min_neighbors` : int, padrão `3`
: Número mínimo de pontos amostrais dentro de `radius`. Quando há menos, são
  usados os `max_neighbors` pontos mais próximos, qualquer que seja a
  distância.

`model_values` : array_like, opcional
: Modelo de semivariograma pré-calculado (`Variogram.model_values`). Se for
  informado, o `fit` usa esse modelo em vez de ajustar um novo semivariograma.

## O que "local" e "ordinária" significam aqui

*Local* quer dizer que cada ponto a estimar é estimado a partir dos pontos
amostrais vizinhos dentro de `radius`, até `max_neighbors`, e não do conjunto
de dados inteiro. Isso mantém o sistema linear pequeno e o método escalável.
*Ordinária* quer dizer que a média do processo é tratada como desconhecida e
constante dentro de cada vizinhança local. A krigagem simples, ao contrário,
assume que a média é conhecida.

Veja {doc}`../methodology/kriging` para a dedução completa (o sistema linear
resolvido para cada ponto a estimar e por que ele dá a melhor estimativa
linear não tendenciosa) e {doc}`../methodology/variogram-fitting` para os
modelos de semivariograma.
