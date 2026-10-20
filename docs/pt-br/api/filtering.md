# apbase.filtering

API de alto nível de filtragem espacial.

::::{py:class} apbase.filtering.FilterStatistics(pct_diff, local_z, local_prob)

Classes base: `NamedTuple`

Estatísticas da filtragem local por ponto.

**Variáveis**

- **pct_diff** (*numpy.ndarray*) – Estatística local de diferença percentual por registro da entrada original.
- **local_z** (*numpy.ndarray*) – Escore z local por registro da entrada original.
- **local_prob** (*numpy.ndarray*) – Estatística local de probabilidade por registro da entrada original.

**Parâmetros**

- **pct_diff** (*ndarray*)
- **local_z** (*ndarray*)
- **local_prob** (*ndarray*)

:::{py:attribute} apbase.filtering.FilterStatistics.pct_diff
:type: ndarray

Alias do campo número 0

:::

:::{py:attribute} apbase.filtering.FilterStatistics.local_z
:type: ndarray

Alias do campo número 1

:::

:::{py:attribute} apbase.filtering.FilterStatistics.local_prob
:type: ndarray

Alias do campo número 2

:::

::::

::::{py:class} apbase.filtering.SpatialFilter(*, radius=None, filter_level='light', apply_global_iqr=True, max_neighbors=120, candidate_fraction=1.0, cell_factor=3, global_iqr_whisker=3.0, dedup_radius=0.0, dedup_z_tol=0.0)

Classes base: `object`

Filtra amostras espaciais projetadas com o IQR (intervalo interquartil) global e estatísticas z locais.

Remove registros inválidos, remove opcionalmente os outliers globais por IQR e aplica um filtro local nativo usando vizinhanças espaciais. As coordenadas não são projetadas internamente; passe coordenadas projetadas/métricas quando `radius` for métrico.

**Parâmetros**

- **radius** (*float | None*) – Raio de busca local. Por padrão, `range / 3` de um semivariograma ajustado.
- **filter_level** (*str*) – Rigor do filtro, do mais brando ao mais rigoroso: `"light"`, `"moderate"`, `"strict"` ou `"aggressive"`.
- **apply_global_iqr** (*bool*) – Se os outliers globais por IQR devem ser removidos antes da filtragem local.
- **max_neighbors** (*int*) – Número máximo de vizinhos locais por ponto amostral. `0` usa todos os vizinhos dentro de `radius`, sem limite.
- **candidate_fraction** (*float*) – Fração (0, 1\] dos candidatos dentro do raio considerada na amostra local.
- **cell_factor** (*int*) – Fator da grade espacial usada pelo kernel local.
- **global_iqr_whisker** (*float*) – Bigode do IQR para o filtro global opcional; valores menores removem mais pontos. Ignorado quando `apply_global_iqr=False`.
- **dedup_radius** (*float*) – Distância abaixo da qual dois pontos são tratados como duplicados espaciais e juntados num único representante. `0.0` (padrão) desativa esse tratamento.
- **dedup_z_tol** (*float*) – Critério extra de proximidade de valor combinado com `dedup_radius`: os pontos só são juntados se também estiverem dentro dessa diferença de valor. `0.0` (padrão) significa que a proximidade espacial basta.

**Exemplos**

```pycon
>>> import numpy as np
>>> from apbase.filtering import SpatialFilter
>>> x = np.ascontiguousarray([0.0, 10.0, 0.0, 10.0])
>>> y = np.ascontiguousarray([0.0, 0.0, 10.0, 10.0])
>>> z = np.ascontiguousarray([5.0, 7.0, 8.0, 10.0])
>>> filt = SpatialFilter(radius=20.0, apply_global_iqr=False).fit(x, y, z)
>>> x_keep, y_keep, z_keep = filt.filter()
```

:::{py:property} apbase.filtering.SpatialFilter.radius
:type: float | None

Raio de busca local.

**Retorna**

Raio explícito, ou `None` para derivá-lo de um semivariograma ajustado.

**Tipo de retorno**

float ou None

:::

:::{py:property} apbase.filtering.SpatialFilter.filter_level
:type: str

Rigor da filtragem.

**Retorna**

Um de `"light"`, `"moderate"`, `"strict"` ou `"aggressive"`.

**Tipo de retorno**

str

:::

:::{py:property} apbase.filtering.SpatialFilter.apply_global_iqr
:type: bool

Se os outliers globais por IQR são removidos antes da filtragem local.

**Retorna**

`True` quando a filtragem global por IQR está ativada.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.filtering.SpatialFilter.max_neighbors
:type: int

Número máximo de vizinhos locais usados por ponto amostral.

**Retorna**

Limite da vizinhança local. `0` significa todos os vizinhos dentro do raio.

**Tipo de retorno**

int

:::

:::{py:property} apbase.filtering.SpatialFilter.candidate_fraction
:type: float

Fração dos candidatos dentro do raio amostrada localmente.

**Retorna**

Fração de amostragem dos candidatos em `(0, 1]`.

**Tipo de retorno**

float

:::

:::{py:property} apbase.filtering.SpatialFilter.cell_factor
:type: int

Fator da grade espacial usada pelo kernel local nativo.

**Retorna**

Fator positivo da grade espacial.

**Tipo de retorno**

int

:::

:::{py:property} apbase.filtering.SpatialFilter.global_iqr_whisker
:type: float

Bigode do IQR usado pelo filtro global opcional.

**Retorna**

Bigode do IQR, não negativo.

**Tipo de retorno**

float

:::

:::{py:property} apbase.filtering.SpatialFilter.dedup_radius
:type: float

Raio para juntar duplicados espaciais.

**Retorna**

Limiar de distância não negativo. `0.0` desativa a junção de duplicados espaciais.

**Tipo de retorno**

float

:::

:::{py:property} apbase.filtering.SpatialFilter.dedup_z_tol
:type: float

Critério de proximidade de valor usado junto com `dedup_radius`.

**Retorna**

Limiar de valor não negativo.

**Tipo de retorno**

float

:::

:::{py:property} apbase.filtering.SpatialFilter.n_threads
:type: int

Número explícito de threads OpenMP passado às rotinas nativas.

Lido na hora de `apbase.config["n_threads"]` (veja a docstring da classe) a cada acesso – não fica guardado desde a construção.

**Retorna**

Número atual de threads OpenMP.

**Tipo de retorno**

int

:::

:::{py:method} apbase.filtering.SpatialFilter.from_data(x, y, z, **kwargs)
:classmethod:

Cria e ajusta um filtro espacial.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`SpatialFilter <apbase.filtering.SpatialFilter>`.

**Retorna**

Filtro espacial ajustado.

**Tipo de retorno**

{obj}`SpatialFilter <apbase.filtering.SpatialFilter>`

:::

:::{py:property} apbase.filtering.SpatialFilter.is_fitted
:type: bool

Se os dados de entrada e os resultados da filtragem estão disponíveis.

**Retorna**

`True` depois que {meth}`fit() <apbase.filtering.SpatialFilter.fit>` termina com sucesso.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.filtering.SpatialFilter.model_params
:type: dict[str, float | int | str]

Parâmetros legíveis do semivariograma usado pelo raio padrão.

**Retorna**

Parâmetros do semivariograma usados para derivar o raio implícito.

**Tipo de retorno**

dict

**Exceções**

**ValueError** – Se o filtro não foi ajustado ou foi ajustado com um raio explícito.

:::

:::{py:property} apbase.filtering.SpatialFilter.statistics
:type: FilterStatistics

Arrays locais de diferença percentual, escore z e probabilidade.

**Retorna**

Cópias dos diagnósticos da filtragem local por registro de entrada.

**Tipo de retorno**

{obj}`FilterStatistics <apbase.filtering.FilterStatistics>`

:::

:::{py:method} apbase.filtering.SpatialFilter.fit(x, y, z)

Roda a filtragem global e local nas amostras.

**Parâmetros**

- **x** (*ArrayLike*) – Coordenadas x dos pontos amostrais, unidimensionais.
- **y** (*ArrayLike*) – Coordenadas y dos pontos amostrais, unidimensionais. Precisa ter o mesmo tamanho de `x`.
- **z** (*ArrayLike*) – Valores amostrais, unidimensionais. Precisa ter o mesmo tamanho de `x` e `y`.

**Retorna**

O filtro ajustado. Use {meth}`mask() <apbase.filtering.SpatialFilter.mask>`, {meth}`filter() <apbase.filtering.SpatialFilter.filter>` ou {attr}`statistics <apbase.filtering.SpatialFilter.statistics>` para ler os resultados.

**Tipo de retorno**

{obj}`SpatialFilter <apbase.filtering.SpatialFilter>`

**Exceções**

- **ValueError** – Se os arrays de entrada tiverem tamanhos inconsistentes, nenhum registro finito, nenhum registro depois da filtragem global ou um raio inválido.
- **NativeExecutionError** – Se um kernel nativo de filtragem informar um status de falha.

**Exemplos**

```pycon
>>> filt = SpatialFilter(radius=30.0, apply_global_iqr=False)
>>> filt.fit(x, y, z)
>>> keep = filt.mask()
```

:::

:::{py:method} apbase.filtering.SpatialFilter.mask()

Devolve a máscara booleana de pontos mantidos para os arrays de entrada ajustados.

**Retorna**

Array booleano alinhado com os registros da entrada original. `True` significa que o registro passou pelas filtragens de valores finitos, global e local.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:method} apbase.filtering.SpatialFilter.filter()

Devolve os arrays `x`, `y` e `z` filtrados.

**Retorna**

Coordenadas e valores amostrais onde a máscara de pontos mantidos é `True`.

**Tipo de retorno**

tuple\[numpy.ndarray, numpy.ndarray, numpy.ndarray\]

**Exemplos**

```pycon
>>> x_keep, y_keep, z_keep = filt.filter()
```

:::

:::{py:method} apbase.filtering.SpatialFilter.fit_mask(x, y, z)

Ajusta o filtro e devolve a máscara booleana de pontos mantidos.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.

**Retorna**

Máscara booleana de pontos mantidos, alinhada com os registros da entrada original.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:method} apbase.filtering.SpatialFilter.fit_filter(x, y, z)

Ajusta o filtro e devolve os arrays de entrada filtrados.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.

**Retorna**

Coordenadas e valores amostrais filtrados.

**Tipo de retorno**

tuple\[numpy.ndarray, numpy.ndarray, numpy.ndarray\]

:::

::::
