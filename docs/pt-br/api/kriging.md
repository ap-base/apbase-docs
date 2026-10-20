# apbase.kriging

API de alto nível da krigagem.

Este pacote exporta as classes públicas usadas para ajustar modelos de semivariograma e rodar a krigagem ordinária local. A geração da grade de interpolação fica em `apbase.grid`.

::::{py:class} apbase.kriging.Kriging(*, radius=None, max_neighbors=40, min_neighbors=3, model_values=None)

Classes base: `object`

Ajusta um modelo de semivariograma e interpola valores com krigagem ordinária local.

Armazena as amostras finitas, ajusta ou recebe um modelo de semivariograma e estima os valores nos pontos a estimar com um kernel de krigagem ordinária local. As coordenadas não são projetadas internamente; passe coordenadas projetadas/métricas quando `radius` for métrico.

**Parâmetros**

- **radius** (*float | None*) – Raio de busca local. Se for `None`, a krigagem usa o `range` do semivariograma selecionado (`range / 3` com 10.000 pontos ou mais).
- **max_neighbors** (*int*) – Número máximo de pontos amostrais usados por ponto a estimar. Limitado a `apbase.config["max_neighbors_ceiling"]` (padrão `500`).
- **min_neighbors** (*int*) – Número mínimo de pontos amostrais dentro de `radius`; abaixo dele, os `max_neighbors` pontos mais próximos são usados, qualquer que seja a distância.
- **model_values** (*ArrayLike | None*) – Vetor de modelo de semivariograma nativo opcional, com cinco valores. Se for informado, o `fit` usa esse vetor em vez de ajustar um semivariograma a partir de `x`, `y` e `z`.

**Exemplos**

```pycon
>>> import numpy as np
>>> from apbase.kriging import Kriging
>>> x = np.ascontiguousarray([0.0, 10.0, 0.0, 10.0])
>>> y = np.ascontiguousarray([0.0, 0.0, 10.0, 10.0])
>>> z = np.ascontiguousarray([5.0, 7.0, 8.0, 10.0])
>>> targets = np.ascontiguousarray([[5.0, 5.0]])
>>> values = Kriging(radius=20.0, min_neighbors=3).fit(x, y, z).interpolate(targets)
```

:::{py:property} apbase.kriging.Kriging.radius
:type: float | None

Raio de busca local.

**Retorna**

Raio explícito, ou `None` para derivá-lo do alcance do semivariograma durante a interpolação.

**Tipo de retorno**

float ou None

:::

:::{py:property} apbase.kriging.Kriging.max_neighbors
:type: int

Número máximo de pontos amostrais usados por ponto a estimar.

**Retorna**

Limite superior de vizinhos locais.

**Tipo de retorno**

int

:::

:::{py:property} apbase.kriging.Kriging.min_neighbors
:type: int

Número mínimo de pontos amostrais dentro de `radius` antes de recorrer aos pontos mais próximos.

**Retorna**

Limite inferior de vizinhos locais.

**Tipo de retorno**

int

:::

:::{py:property} apbase.kriging.Kriging.n_threads
:type: int

Número de threads OpenMP passado às rotinas nativas.

Lido na hora de `apbase.config["n_threads"]` (veja a docstring da classe) a cada acesso – não fica guardado desde a construção.

**Retorna**

Número atual de threads OpenMP.

**Tipo de retorno**

int

:::

:::{py:method} apbase.kriging.Kriging.from_data(x, y, z, **kwargs)
:classmethod:

Cria e ajusta um interpolador de krigagem.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`Kriging <apbase.kriging.Kriging>`.

**Retorna**

Interpolador de krigagem ajustado.

**Tipo de retorno**

{obj}`Kriging <apbase.kriging.Kriging>`

:::

:::{py:property} apbase.kriging.Kriging.is_fitted
:type: bool

Se os dados de entrada e um modelo de semivariograma estão disponíveis.

**Retorna**

`True` depois que {meth}`fit() <apbase.kriging.Kriging.fit>` termina com sucesso.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.kriging.Kriging.model_values
:type: ndarray

Valores do melhor modelo de semivariograma ajustado.

**Retorna**

Vetor de modelo nativo usado pelo kernel de krigagem.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:property} apbase.kriging.Kriging.model_params
:type: dict[str, float | int | str]

Parâmetros legíveis do modelo de semivariograma selecionado.

**Retorna**

Id/nome do modelo, efeito pepita, contribuição, patamar, alcance e SSE (soma dos quadrados dos resíduos).

**Tipo de retorno**

dict

:::

:::{py:method} apbase.kriging.Kriging.fit(x, y, z)

Armazena os dados de entrada finitos e ajusta ou associa um modelo de semivariograma.

**Parâmetros**

- **x** (*ArrayLike*) – Coordenadas x dos pontos amostrais, unidimensionais.
- **y** (*ArrayLike*) – Coordenadas y dos pontos amostrais, unidimensionais. Precisa ter o mesmo tamanho de `x`.
- **z** (*ArrayLike*) – Valores amostrais, unidimensionais. Precisa ter o mesmo tamanho de `x` e `y`.

**Retorna**

O interpolador de krigagem ajustado. Os registros em que `x`, `y` ou `z` são `NaN` ou infinitos são ignorados.

**Tipo de retorno**

{obj}`Kriging <apbase.kriging.Kriging>`

**Exceções**

**ValueError** – Se os arrays de entrada tiverem tamanhos inconsistentes ou menos de `min_neighbors` registros finitos.

**Exemplos**

```pycon
>>> kriging = Kriging(radius=30.0, min_neighbors=3)
>>> kriging.fit(x, y, z)
>>> kriging.model_params["range"] > 0.0
True
>>> kriging = Kriging(model_values=model_values, radius=30.0).fit(x, y, z)
```

:::

:::{py:method} apbase.kriging.Kriging.interpolate(targets)

Estima os valores nos pontos a estimar.

**Parâmetros**

**targets** (*Grid | ArrayLike*) – Coordenadas dos pontos a estimar, como um array `(n_targets, 2)` em que a coluna `0` é x e a coluna `1` é y. Também são aceitos uma `Grid` ajustada, um GeoDataFrame/GeoSeries ou uma lista de objetos do tipo `Point`; eles são lidos pela função auxiliar compartilhada `extract_target_xy`.

**Retorna**

Array `float64` unidimensional com uma estimativa de krigagem por ponto a estimar. Pontos a estimar com menos de `min_neighbors` pontos amostrais dentro de `radius` usam os `max_neighbors` mais próximos.

**Tipo de retorno**

numpy.ndarray

**Exemplos**

```pycon
>>> targets = np.ascontiguousarray([[5.0, 5.0], [20.0, 20.0]])
>>> values = kriging.interpolate(targets)
```

:::

:::{py:method} apbase.kriging.Kriging.predict(targets)

Estima os valores nos pontos a estimar.

**Parâmetros**

**targets** (*Grid ou array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`interpolate() <apbase.kriging.Kriging.interpolate>`.

**Retorna**

Uma estimativa de krigagem por ponto a estimar.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:method} apbase.kriging.Kriging.fit_interpolate(x, y, z, targets)

Ajusta o interpolador e já estima os valores nos pontos a estimar.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.
- **targets** (*Grid ou array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`interpolate() <apbase.kriging.Kriging.interpolate>`.

**Retorna**

Uma estimativa de krigagem por ponto a estimar.

**Tipo de retorno**

numpy.ndarray

:::

::::

:::{py:function} apbase.kriging.ordinary_kriging(x, y, z, targets, *, model_values=None, radius=None, max_neighbors=40, min_neighbors=3, return_diagnostics=False)

Ajusta a krigagem ordinária local e estima os valores em `targets`.

É um atalho de conveniência em torno de {class}`Kriging <apbase.kriging.Kriging>` para quem só quer uma chamada única de ajuste e interpolação. Prefira criar o `Kriging` diretamente quando for reutilizar o mesmo semivariograma ajustado em várias chamadas de `interpolate`, já que esta função sempre ajusta do zero.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.
- **targets** (*array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`apbase.kriging.Kriging.interpolate() <apbase.kriging.Kriging.interpolate>`.
- **model_values** (*array_like ou None, padrão None*) – Vetor de modelo de semivariograma nativo opcional. Se for omitido, um semivariograma é ajustado a partir de `x`, `y` e `z`.
- **radius** (*float ou None, padrão None*) – Raio de busca local. Se for `None`, deriva o `range` do semivariograma selecionado (`range / 3` com 10.000 pontos ou mais).
- **max_neighbors** (*int*) – Limites de vizinhos usados pela busca local.
- **min_neighbors** (*int*) – Limites de vizinhos usados pela busca local.
- **return_diagnostics** (*bool, padrão False*) – Se for `True`, devolve os diagnósticos da interpolação junto com as estimativas.

**Retorna**

Só as estimativas, ou `(estimates, diagnostics)` quando `return_diagnostics=True`.

**Tipo de retorno**

numpy.ndarray ou tuple\[numpy.ndarray, dict\]

:::

`apbase.kriging` também reexporta {class}`apbase.variogram.Variogram <apbase.variogram.Variogram>`; veja {doc}`apbase.variogram <variogram>` para a documentação dessa classe.
