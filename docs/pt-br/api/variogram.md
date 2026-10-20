# apbase.variogram

API compartilhada de alto nível do semivariograma.

::::{py:class} apbase.variogram.Variogram(*, n_lags=50, max_pairs=100000, max_distance=0.0)

Classes base: `object`

Ajusta, seleciona e avalia um modelo nativo de semivariograma.

Ajusta modelos candidatos de semivariograma às amostras finitas e seleciona o melhor modelo nativo para avaliação ou krigagem. As coordenadas não são projetadas internamente; passe as coordenadas na mesma unidade esperada pelas distâncias calculadas depois.

**Parâmetros**

- **n_lags** (*int*) – Número de classes de distância usadas pelo ajuste nativo.
- **max_pairs** (*int*) – Número máximo de pares de pontos amostrados. `0` usa todos os pares elegíveis, com teto interno de `1_000_000`. Um valor explícito é limitado a `apbase.config["variogram_max_pairs_ceiling"]` (padrão `200_000`).
- **max_distance** (*float*) – Distância máxima entre pares considerada no ajuste. `0` usa a extensão padrão do kernel nativo.

**Exemplos**

```pycon
>>> import numpy as np
>>> from apbase.variogram import Variogram
>>> x = np.ascontiguousarray([0.0, 10.0, 0.0, 10.0])
>>> y = np.ascontiguousarray([0.0, 0.0, 10.0, 10.0])
>>> z = np.ascontiguousarray([5.0, 7.0, 8.0, 10.0])
>>> variogram = Variogram(n_lags=4, max_pairs=0).fit(x, y, z)
>>> gamma = variogram.evaluate(np.ascontiguousarray([5.0, 10.0]))
```

:::{py:property} apbase.variogram.Variogram.n_lags
:type: int

Número de classes de distância usadas pelo ajuste nativo.

**Retorna**

Número de classes de distância.

**Tipo de retorno**

int

:::

:::{py:property} apbase.variogram.Variogram.max_pairs
:type: int

Número máximo de pares de pontos amostrados.

**Retorna**

Limite de amostragem de pares; `0` significa todos os pares elegíveis, respeitando o teto nativo.

**Tipo de retorno**

int

:::

:::{py:property} apbase.variogram.Variogram.max_distance
:type: float

Distância máxima entre pares considerada no ajuste.

**Retorna**

Distância de corte, na unidade das coordenadas; `0.0` usa a extensão padrão do kernel nativo.

**Tipo de retorno**

float

:::

:::{py:property} apbase.variogram.Variogram.n_threads
:type: int

Número explícito de threads OpenMP usado ao avaliar o modelo.

Lido na hora de `apbase.config["n_threads"]` (veja a docstring da classe) a cada acesso – não fica guardado desde a construção.

**Retorna**

Número atual de threads OpenMP.

**Tipo de retorno**

int

:::

:::{py:method} apbase.variogram.Variogram.from_data(x, y, z, **kwargs)
:classmethod:

Cria e ajusta um semivariograma a partir dos dados de entrada.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`Variogram <apbase.variogram.Variogram>`.

**Retorna**

Semivariograma ajustado.

**Tipo de retorno**

{obj}`Variogram <apbase.variogram.Variogram>`

:::

:::{py:method} apbase.variogram.Variogram.from_model(model_values)
:classmethod:

Cria um semivariograma a partir de um vetor de modelo nativo existente.

**Parâmetros**

**model_values** (*array_like*) – Vetor de modelo nativo com cinco valores: `[model_id, nugget, partial_sill, range, sse]`.

**Retorna**

Instância de semivariograma baseada em `model_values`.

**Tipo de retorno**

{obj}`Variogram <apbase.variogram.Variogram>`

:::

:::{py:property} apbase.variogram.Variogram.is_fitted
:type: bool

Se já existe um modelo disponível.

**Retorna**

`True` depois que {meth}`fit() <apbase.variogram.Variogram.fit>` ou {meth}`set_model() <apbase.variogram.Variogram.set_model>` termina com sucesso.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.variogram.Variogram.model_values
:type: ndarray

Vetor de modelo nativo usado pelos kernels de krigagem e de avaliação.

**Retorna**

Vetor do modelo `[model_id, nugget, partial_sill, range, sse]`.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:property} apbase.variogram.Variogram.model_params
:type: dict[str, float | int | str]

Parâmetros legíveis do modelo de semivariograma selecionado.

**Retorna**

Id/nome do modelo, efeito pepita, contribuição, patamar, alcance e SSE (soma dos quadrados dos resíduos).

**Tipo de retorno**

dict

:::

:::{py:property} apbase.variogram.Variogram.range
:type: float

Alcance do modelo selecionado.

**Retorna**

Alcance do semivariograma ajustado, na unidade das coordenadas.

**Tipo de retorno**

float

:::

:::{py:method} apbase.variogram.Variogram.fit(x, y, z)

Ajusta os modelos candidatos de semivariograma às amostras.

**Parâmetros**

- **x** (*ArrayLike*) – Coordenadas x dos pontos amostrais, unidimensionais.
- **y** (*ArrayLike*) – Coordenadas y dos pontos amostrais, unidimensionais. Precisa ter o mesmo tamanho de `x`.
- **z** (*ArrayLike*) – Valores amostrais, unidimensionais. Precisa ter o mesmo tamanho de `x` e `y`.

**Retorna**

O semivariograma ajustado. Os registros em que `x`, `y` ou `z` são `NaN` ou infinitos são ignorados.

**Tipo de retorno**

{obj}`Variogram <apbase.variogram.Variogram>`

**Exceções**

- **ValueError** – Se os arrays de entrada tiverem tamanhos inconsistentes ou nenhum registro finito.
- **NativeExecutionError** – Se o ajuste nativo do semivariograma informar um status de falha.

**Exemplos**

```pycon
>>> variogram = Variogram(n_lags=8, max_pairs=0).fit(x, y, z)
>>> variogram.model_params["model_name"]
'spherical'
```

:::

:::{py:method} apbase.variogram.Variogram.set_model(model_values)

Associa um vetor de modelo nativo existente e seleciona seus parâmetros.

**Parâmetros**

**model_values** (*array_like*) – Vetor de modelo nativo com cinco valores: `[model_id, nugget, partial_sill, range, sse]`.

**Retorna**

Esta instância, marcada como ajustada.

**Tipo de retorno**

{obj}`Variogram <apbase.variogram.Variogram>`

**Exceções**

**ValueError** – Se o formato ou o conteúdo do vetor do modelo forem inválidos.

:::

:::{py:method} apbase.variogram.Variogram.evaluate(distance)

Avalia a semivariância nas distâncias informadas.

**Parâmetros**

**distance** (*ArrayLike*) – Distâncias escalares ou em array, na mesma unidade de coordenadas usada no {meth}`fit() <apbase.variogram.Variogram.fit>`.

**Retorna**

Valores de semivariância com o mesmo formato de `distance`.

**Tipo de retorno**

numpy.ndarray

**Exemplos**

```pycon
>>> gamma = variogram.evaluate(np.asarray([5.0, 10.0]))
```

:::

::::

:::{py:function} apbase.variogram.search_radius(model_params, n_points)

Raio de busca local padrão para `n_points` pontos amostrais.

`range` quando há menos de `FULL_RANGE_RADIUS_MAX_POINTS` pontos, `range / 3` caso contrário.

**Parâmetros**

- **model_params** (*dict\[str, float | int | str\]*)
- **n_points** (*int*)

**Tipo de retorno**

float

:::
