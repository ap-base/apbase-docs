# Semivariograma

O `Variogram` calcula o semivariograma experimental a partir dos pontos
amostrais e escolhe o modelo de melhor ajuste entre as opções esférica,
exponencial e gaussiana. O `Kriging` sempre usa um semivariograma ajustado; os
outros estimadores usam um para derivar `radius` quando ele é omitido (veja
{doc}`../methodology/variogram-fitting`).

O `apbase.Map` ajusta o semivariograma por você. Use o `Variogram`
diretamente quando quiser inspecionar a curva ajustada ou controlar a etapa de
ajuste.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.variogram import Variogram

variogram = Variogram(n_lags=50, max_pairs=100_000).fit(x, y, z)
gamma = variogram.evaluate(distances)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::variogram::{Variogram, VariogramOptions};

let mut variogram = Variogram::new(VariogramOptions { n_lags: 50, max_pairs: 100_000, ..Default::default() })?;
variogram.fit(&x, &y, &z)?;
let gamma = variogram.evaluate(&distances)?;
```

:::

::::

## Parâmetros

`x`, `y` : array_like
: Coordenadas dos pontos amostrais passadas ao `fit`. O `Variogram` não
  converte longitude/latitude: passe coordenadas projetadas.

`z` : array_like
: Valores amostrais. Precisa ter o mesmo tamanho de `x` e `y`.

`n_lags` : int, padrão `50`
: Número de classes de distância usadas para montar o semivariograma
  experimental.

`max_pairs` : int, padrão `100_000`
: Número máximo de pares de pontos amostrados na montagem do semivariograma
  experimental. `0` usa todos os pares elegíveis, respeitando o teto nativo.

`max_distance` : float, padrão `0.0`
: Distância máxima entre pares considerada. `0.0` deixa o kernel nativo
  escolher a extensão a partir dos dados.

`distance` : array_like
: Distâncias passadas ao `evaluate`; devolve a semivariância de cada
  distância.

## O que o `fit` faz

O `fit` calcula o semivariograma experimental, estima o efeito pepita, a
contribuição (patamar parcial) e o alcance de cada modelo candidato e fica com
o ajuste de menor erro ponderado. `evaluate(distance)` devolve a semivariância
do modelo ajustado em distâncias quaisquer, o que é útil para inspecionar a
curva diretamente.

Veja {doc}`../methodology/variogram-fitting` para a matemática por trás do
estimador experimental e do procedimento de ajuste, e
{doc}`../methodology/kriging` para como o modelo ajustado entra no sistema de
krigagem.
