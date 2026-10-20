# apbase.idw

API de alto nível do inverso da distância ponderada (IDW).

Este pacote exporta a classe pública usada para rodar a interpolação por IDW.

::::{py:class} apbase.idw.IDW(*, radius=None, power=2.0, max_neighbors=40, min_neighbors=3)

Classes base: `object`

Interpola coordenadas projetadas pelo inverso da distância ponderada.

Armazena as amostras finitas, com coordenadas `x`/`y` e valores `z`, e depois estima os valores nos pontos a estimar com pesos pelo inverso da distância. As coordenadas não são projetadas internamente; passe coordenadas métricas/projetadas quando `radius` estiver em metros.

**Parâmetros**

- **radius** (*float | None*) – Raio de busca local. Se for `None`, o `fit` estima um semivariograma e usa o `range` (`range / 3` com 10.000 pontos ou mais).
- **power** (*float*) – Potência aplicada à distância nos pesos do IDW. `2.0` é a ponderação comum pelo inverso do quadrado da distância.
- **max_neighbors** (*int*) – Número máximo de pontos amostrais usados por ponto a estimar.
- **min_neighbors** (*int*) – Número mínimo de pontos amostrais dentro de `radius`; abaixo dele, os `max_neighbors` pontos mais próximos são usados, qualquer que seja a distância.

**Exemplos**

```pycon
>>> import numpy as np
>>> from apbase.idw import IDW
>>> x = np.ascontiguousarray([0.0, 10.0, 0.0, 10.0])
>>> y = np.ascontiguousarray([0.0, 0.0, 10.0, 10.0])
>>> z = np.ascontiguousarray([5.0, 7.0, 8.0, 10.0])
>>> targets = np.ascontiguousarray([[5.0, 5.0], [10.0, 10.0]])
>>> values = IDW(radius=20.0, min_neighbors=1).fit(x, y, z).interpolate(targets)
```

:::{py:property} apbase.idw.IDW.radius
:type: float | None

Raio de busca local.

**Retorna**

Raio explícito, ou `None` para derivá-lo do alcance do semivariograma durante o {meth}`fit() <apbase.idw.IDW.fit>`.

**Tipo de retorno**

float ou None

:::

:::{py:property} apbase.idw.IDW.power
:type: float

Potência aplicada à distância nos pesos do IDW.

**Retorna**

Potência da distância, positiva.

**Tipo de retorno**

float

:::

:::{py:property} apbase.idw.IDW.max_neighbors
:type: int

Número máximo de pontos amostrais usados por ponto a estimar.

**Retorna**

Limite superior de vizinhos locais.

**Tipo de retorno**

int

:::

:::{py:property} apbase.idw.IDW.min_neighbors
:type: int

Número mínimo de pontos amostrais dentro de `radius` antes de recorrer aos pontos mais próximos.

**Retorna**

Limite inferior de vizinhos locais.

**Tipo de retorno**

int

:::

:::{py:property} apbase.idw.IDW.n_threads
:type: int

Número de threads OpenMP passado às rotinas nativas.

Lido na hora de `apbase.config["n_threads"]` (veja a docstring da classe) a cada acesso – não fica guardado desde a construção.

**Retorna**

Número atual de threads OpenMP.

**Tipo de retorno**

int

:::

:::{py:method} apbase.idw.IDW.from_data(x, y, z, **kwargs)
:classmethod:

Cria e ajusta um interpolador IDW.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`IDW <apbase.idw.IDW>`.

**Retorna**

Interpolador IDW ajustado.

**Tipo de retorno**

{obj}`IDW <apbase.idw.IDW>`

:::

:::{py:property} apbase.idw.IDW.is_fitted
:type: bool

Se há dados de entrada finitos disponíveis.

**Retorna**

`True` depois que {meth}`fit() <apbase.idw.IDW.fit>` termina com sucesso.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.idw.IDW.model_params
:type: dict[str, float | int | str]

Parâmetros legíveis do semivariograma usado pelo raio padrão.

**Retorna**

Parâmetros do semivariograma usados para derivar o raio implícito.

**Tipo de retorno**

dict

**Exceções**

**ValueError** – Se o interpolador não foi ajustado ou foi ajustado com um raio explícito, de modo que nenhum semivariograma foi estimado.

:::

:::{py:method} apbase.idw.IDW.fit(x, y, z)

Armazena as amostras finitas usadas depois pela interpolação.

**Parâmetros**

- **x** (*ArrayLike*) – Coordenadas x dos pontos amostrais, unidimensionais. Use unidades projetadas/métricas quando `radius` for métrico.
- **y** (*ArrayLike*) – Coordenadas y dos pontos amostrais, unidimensionais. Precisa ter o mesmo tamanho de `x`.
- **z** (*ArrayLike*) – Valores amostrais a interpolar, unidimensionais. Precisa ter o mesmo tamanho de `x` e `y`.

**Retorna**

O interpolador ajustado. Os registros em que `x`, `y` ou `z` são `NaN` ou infinitos são ignorados.

**Tipo de retorno**

{obj}`IDW <apbase.idw.IDW>`

**Exceções**

**ValueError** – Se os arrays de entrada tiverem tamanhos inconsistentes ou menos de `min_neighbors` registros finitos.

**Exemplos**

```pycon
>>> idw = IDW(radius=30.0, min_neighbors=1)
>>> idw.fit(x, y, z)
>>> idw.is_fitted
True
```

:::

:::{py:method} apbase.idw.IDW.interpolate(targets)

Estima os valores nos pontos a estimar.

**Parâmetros**

**targets** (*Grid | ArrayLike*) – Coordenadas dos pontos a estimar, como um array `(n_targets, 2)` em que a coluna `0` é x e a coluna `1` é y. Também são aceitos uma {class}`Grid <apbase.grid.Grid>` ajustada, um GeoDataFrame/GeoSeries ou uma lista de objetos do tipo `Point`; eles são lidos pela função auxiliar compartilhada `extract_target_xy`.

**Retorna**

Array `float64` unidimensional com um valor interpolado por ponto a estimar. Pontos a estimar com menos de `min_neighbors` pontos amostrais dentro de `radius` usam os `max_neighbors` mais próximos.

**Tipo de retorno**

numpy.ndarray

**Exemplos**

```pycon
>>> targets = np.ascontiguousarray([[5.0, 5.0], [20.0, 20.0]])
>>> values = idw.interpolate(targets)
```

:::

:::{py:method} apbase.idw.IDW.predict(targets)

Estima os valores nos pontos a estimar.

**Parâmetros**

**targets** (*Grid ou array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`interpolate() <apbase.idw.IDW.interpolate>`.

**Retorna**

Um valor interpolado por ponto a estimar.

**Tipo de retorno**

numpy.ndarray

:::

::::

:::{py:function} apbase.idw.idw(x, y, z, targets, *, radius=None, power=2.0, max_neighbors=40, min_neighbors=3)

Ajusta o IDW aos dados de entrada e estima os valores nos pontos a estimar.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.
- **targets** (*array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`apbase.idw.IDW.interpolate() <apbase.idw.IDW.interpolate>`.
- **radius** (*float ou None, padrão None*) – Raio de busca local. Se for `None`, deriva o `range` de um semivariograma ajustado (`range / 3` com 10.000 pontos ou mais).
- **power** (*float, padrão 2.0*) – Potência do IDW (expoente da distância).
- **max_neighbors** (*int*) – Limites de vizinhos usados pela busca local.
- **min_neighbors** (*int*) – Limites de vizinhos usados pela busca local.

**Retorna**

Um valor interpolado por ponto a estimar.

**Tipo de retorno**

numpy.ndarray

:::
