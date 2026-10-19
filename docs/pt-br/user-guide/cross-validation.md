# Validação cruzada

`apbase.cross_validate.cross_validate` compara o IDW e a krigagem ordinária
sobre os mesmos dados amostrais. Ela usa validação cruzada leave-one-out com
uma única configuração compartilhada: um só semivariograma ajustado define o
raio de busca comum e o modelo de krigagem, e os dois métodos usam o mesmo
índice espacial.

Esta é a etapa de decisão por trás do `apbase.Map`: é assim que o APbase
escolhe o método com menor RMSE (raiz do erro quadrático médio) leave-one-out
para o conjunto de dados atual. Chame-a diretamente quando quiser inspecionar
a comparação ou rodá-la com os seus próprios limites.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_validate import cross_validate

result = cross_validate(x, y, z, max_points=500)
result.idw.rmse, result.kriging.rmse
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::cross_validate::{CrossValidateOptions, cross_validate};

let result = cross_validate(&x, &y, &z, CrossValidateOptions { max_points: 500, ..Default::default() })?;
(result.idw.rmse, result.kriging.rmse);
```

:::

::::

## Parâmetros

`x`, `y` : array_like
: Coordenadas dos pontos amostrais, num sistema de coordenadas projetado (sem
  conversão de longitude/latitude).

`z` : array_like
: Valores amostrais. Precisa ter o mesmo tamanho de `x` e `y`.

`max_points` : int, padrão `500`
: Número máximo de pontos amostrais avaliados. Conjuntos de dados maiores são
  amostrados aleatoriamente para manter o tempo de execução limitado.

`seed` : int, opcional
: Semente da subamostra de validação.

`radius` : float, opcional
: Raio de busca local compartilhado pelo IDW e pela krigagem. Se for omitido,
  o APbase o deriva do semivariograma ajustado (veja
  {doc}`../methodology/variogram-fitting`).

`power` : float, padrão `2.0`
: Expoente da distância no IDW.

`max_neighbors`, `min_neighbors` : int
: Limites de vizinhos compartilhados pelos dois métodos.

`model_values` : array_like, opcional
: Modelo de semivariograma pré-calculado, reaproveitado na avaliação da
  krigagem.

## Lendo o resultado

`result.idw` e `result.kriging` expõem `mae`, `rmse`, `r2` e as predições e os
valores observados de cada amostra usados para calculá-los. Esses valores
ajudam a ver se o erro de um método está sendo puxado por poucos pontos
outliers.

O `apbase.Map` roda esta função e depois `select_best_model` para escolher
entre IDW e krigagem automaticamente. Veja
{doc}`../methodology/cross-validation` para o procedimento leave-one-out e a
regra de seleção.

Para a cokrigagem (colocalizada/ICM/LMC), veja `cross_validate_cokriging` em
{doc}`cokriging`, que faz a validação cruzada dos três métodos juntos.
