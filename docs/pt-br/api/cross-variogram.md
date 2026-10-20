# apbase.cross_variogram

Ajuste do semivariograma cruzado e seleção de variáveis secundárias para a cokrigagem.

Roda *antes* do {mod}`apbase.cokriging <apbase.cokriging>`: ajusta um modelo genérico de semivariograma cruzado entre duas variáveis quaisquer e testa as variáveis secundárias candidatas contra uma primária com um teste z de Fisher (significância) e uma verificação de Cauchy-Schwarz (admissibilidade).

::::{py:class} apbase.cross_variogram.CovariateReport(rho, p_value, admissible_fraction, n_pairs, decision, status, model_params)

Classes base: `object`

Resultado da seleção para uma variável secundária candidata.

**Parâmetros**

- **rho** (*float*)
- **p_value** (*float*)
- **admissible_fraction** (*float*)
- **n_pairs** (*int*)
- **decision** (*bool*)
- **status** (*str*)
- **model_params** (*dict\[str, float | int | str\] | None*)

:::{py:attribute} apbase.cross_variogram.CovariateReport.rho
:type: float

:::

:::{py:attribute} apbase.cross_variogram.CovariateReport.p_value
:type: float

:::

:::{py:attribute} apbase.cross_variogram.CovariateReport.admissible_fraction
:type: float

:::

:::{py:attribute} apbase.cross_variogram.CovariateReport.n_pairs
:type: int

:::

:::{py:attribute} apbase.cross_variogram.CovariateReport.decision
:type: bool

:::

:::{py:attribute} apbase.cross_variogram.CovariateReport.status
:type: str

:::

:::{py:attribute} apbase.cross_variogram.CovariateReport.model_params
:type: dict[str, float | int | str] | None

:::

::::

::::{py:class} apbase.cross_variogram.CrossVariogram(*, n_lags=50, max_pairs=100000, max_distance=0.0, max_colocation_dist=None)

Classes base: `object`

Ajusta um modelo de semivariograma cruzado experimental entre duas variáveis.

Simétrico em `a`/`b` – não há papel fixo de primária/secundária. Usado por {func}`screen_secondary_variables() <apbase.cross_variogram.screen_secondary_variables>` e pelo ajuste ICM/LMC do `CoKriging` para cada par de variáveis.

`a` e `b` podem ter sido amostradas em coordenadas diferentes: o ajuste nativo as pareia por vizinho mais próximo, aceitando um par dentro de `max_colocation_dist`.

**Parâmetros**

- **n_lags** (*int*) – Mesmo significado que no {class}`Variogram <apbase.variogram.Variogram>`, aplicado à amostra pareada.
- **max_pairs** (*int*) – Mesmo significado que no {class}`Variogram <apbase.variogram.Variogram>`, aplicado à amostra pareada.
- **max_distance** (*float*) – Mesmo significado que no {class}`Variogram <apbase.variogram.Variogram>`, aplicado à amostra pareada.
- **max_colocation_dist** (*float | None*) – Distância máxima aceita no pareamento por vizinho mais próximo. `None` exige coincidência exata.

**Exemplos**

```pycon
>>> import numpy as np
>>> from apbase.cross_variogram import CrossVariogram
>>> xa = np.ascontiguousarray([0.0, 10.0, 0.0, 10.0, 5.0])
>>> ya = np.ascontiguousarray([0.0, 0.0, 10.0, 10.0, 5.0])
>>> za = np.ascontiguousarray([5.0, 7.0, 8.0, 10.0, 6.5])
>>> zb = np.ascontiguousarray([1.2, 1.6, 1.7, 2.1, 1.4])
>>> cross = CrossVariogram(n_lags=4).fit(xa, ya, za, xa, ya, zb)
>>> cross.rho > 0.0
True
```

:::{py:property} apbase.cross_variogram.CrossVariogram.n_lags
:type: int

Número de classes de distância usadas pelo ajuste nativo.

**Retorna**

Número de classes de distância.

**Tipo de retorno**

int

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.max_pairs
:type: int

Número máximo de pares de pontos colocalizados amostrados.

**Retorna**

Limite de amostragem de pares; `0` significa todos os pares elegíveis, respeitando o teto nativo.

**Tipo de retorno**

int

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.max_distance
:type: float

Distância máxima entre pares considerada no ajuste.

**Retorna**

Distância de corte, na unidade das coordenadas; `0.0` usa a extensão padrão do kernel nativo.

**Tipo de retorno**

float

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.max_colocation_dist
:type: float | None

Distância máxima ao vizinho mais próximo aceita para colocalizar as amostras.

**Retorna**

Tolerância de distância, ou `None` para exigir coincidência exata das coordenadas.

**Tipo de retorno**

float ou None

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.n_threads
:type: int

Número de threads OpenMP usado pelas rotinas nativas do semivariograma cruzado.

**Retorna**

Valor atual, lido de `apbase.config`.

**Tipo de retorno**

int

:::

:::{py:method} apbase.cross_variogram.CrossVariogram.from_data(xa, ya, za, xb, yb, zb, **kwargs)
:classmethod:

Cria e ajusta um semivariograma cruzado a partir dos dados de entrada.

**Parâmetros**

- **xa** (*array_like*) – Coordenadas e valores da primeira variável.
- **ya** (*array_like*) – Coordenadas e valores da primeira variável.
- **za** (*array_like*) – Coordenadas e valores da primeira variável.
- **xb** (*array_like*) – Coordenadas e valores da segunda variável.
- **yb** (*array_like*) – Coordenadas e valores da segunda variável.
- **zb** (*array_like*) – Coordenadas e valores da segunda variável.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`CrossVariogram <apbase.cross_variogram.CrossVariogram>`.

**Retorna**

Semivariograma cruzado ajustado.

**Tipo de retorno**

{obj}`CrossVariogram <apbase.cross_variogram.CrossVariogram>`

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.is_fitted
:type: bool

Se há um ajuste de semivariograma cruzado disponível.

**Retorna**

`True` depois que {meth}`fit() <apbase.cross_variogram.CrossVariogram.fit>` termina com sucesso.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.model_values
:type: ndarray

`[model_id, nugget, partial_sill, range, sse]`.

`nugget`/`partial_sill` (efeito pepita/contribuição) podem ser negativos para um par com correlação negativa – diferente de um semivariograma direto, um semivariograma cruzado não precisa ser, sozinho, uma covariância direta válida. Fica disponível sempre que o ajuste encontrou pelo menos 3 classes de distância preenchidas, mesmo que o modelo vencedor depois se mostre inválido para {attr}`model_params <apbase.cross_variogram.CrossVariogram.model_params>`/{meth}`evaluate() <apbase.cross_variogram.CrossVariogram.evaluate>` (por exemplo, com o `range` caindo a 0) – veja {attr}`n_pairs <apbase.cross_variogram.CrossVariogram.n_pairs>` para conferir se a amostra colocalizada era grande o bastante para tentar um ajuste.

**Retorna**

Vetor de modelo nativo do semivariograma cruzado.

**Tipo de retorno**

numpy.ndarray

**Tipo**

Vetor de modelo nativo

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.model_params
:type: dict[str, float | int | str]

Parâmetros legíveis do modelo de semivariograma cruzado selecionado.

Gera um erro do mesmo jeito que o {class}`Variogram <apbase.variogram.Variogram>` quando o ajuste degenera (por exemplo, com pares colocalizados de menos para preencher 3 classes de distância). Quem precisa tratar um ajuste degenerado sem erro (como {func}`screen_secondary_variables() <apbase.cross_variogram.screen_secondary_variables>`) deve conferir {attr}`n_pairs <apbase.cross_variogram.CrossVariogram.n_pairs>` antes de ler esta propriedade.

**Retorna**

Id/nome do modelo, efeito pepita, contribuição, patamar, alcance e SSE (soma dos quadrados dos resíduos).

**Tipo de retorno**

dict

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.rho
:type: float

Correlação de Pearson sobre a amostra colocalizada pareada.

**Retorna**

Coeficiente de correlação.

**Tipo de retorno**

float

:::

:::{py:property} apbase.cross_variogram.CrossVariogram.n_pairs
:type: int

Número de pares colocalizados encontrados no pareamento por vizinho mais próximo.

**Retorna**

Número de amostras finitas pareadas.

**Tipo de retorno**

int

:::

:::{py:method} apbase.cross_variogram.CrossVariogram.fit(xa, ya, za, xb, yb, zb)

Ajusta o modelo de semivariograma cruzado entre `a` e `b`.

**Parâmetros**

- **xa** (*array_like*) – Coordenadas e valores da primeira variável.
- **ya** (*array_like*) – Coordenadas e valores da primeira variável.
- **za** (*array_like*) – Coordenadas e valores da primeira variável.
- **xb** (*array_like*) – Coordenadas e valores da segunda variável.
- **yb** (*array_like*) – Coordenadas e valores da segunda variável.
- **zb** (*array_like*) – Coordenadas e valores da segunda variável.

**Retorna**

Semivariograma cruzado ajustado. Os registros não finitos são ignorados separadamente em cada variável antes do pareamento colocalizado.

**Tipo de retorno**

{obj}`CrossVariogram <apbase.cross_variogram.CrossVariogram>`

**Exceções**

**ValueError** – Se alguma das variáveis tiver tamanhos inválidos ou nenhum registro finito.

**Notas**

Os registros em que `xa`/`ya`/`za` (ou `xb`/`yb`/`zb`) são `NaN` ou infinitos são ignorados no respectivo lado antes do pareamento.

:::

:::{py:method} apbase.cross_variogram.CrossVariogram.evaluate(distance)

Avalia a semivariância cruzada ajustada em uma ou mais distâncias.

**Parâmetros**

**distance** (*array_like*) – Distâncias na mesma unidade de coordenadas usada no ajuste.

**Retorna**

Valores de semivariância cruzada com o mesmo formato de `distance`.

**Tipo de retorno**

numpy.ndarray

:::

::::

::::{py:class} apbase.cross_variogram.ScreeningResult(selected, report)

Classes base: `object`

Resultado de {func}`screen_secondary_variables() <apbase.cross_variogram.screen_secondary_variables>`.

**Parâmetros**

- **selected** (*dict\[str, tuple\[ArrayLike, ArrayLike, ArrayLike\]\]*)
- **report** (*dict\[str, CovariateReport\]*)

:::{py:attribute} apbase.cross_variogram.ScreeningResult.selected
:type: dict[str, tuple[ArrayLike, ArrayLike, ArrayLike]]

:::

:::{py:attribute} apbase.cross_variogram.ScreeningResult.report
:type: dict[str, CovariateReport]

:::

::::

:::{py:function} apbase.cross_variogram.screen_secondary_variables(x0, y0, z0, candidates, *, alpha=0.05, correction='bonferroni', min_abs_rho=0.3, max_violation_fraction=0.1, max_colocation_dist=None, n_lags=50, max_pairs=100000, max_distance=0.0)

Testa se cada variável secundária candidata pode ser usada na cokrigagem.

Para cada candidata, roda um teste z de Fisher na correlação primária<->candidata (`Fisher1921`) e uma verificação de admissibilidade de Cauchy-Schwarz no semivariograma cruzado ajustado (`Journel1978`, `Myers1982`). Uma candidata só é mantida se a correlação for significativa (e relevante na prática, via `min_abs_rho`) e o semivariograma cruzado for admissível.

**Parâmetros**

- **x0** (*ArrayLike*) – Coordenadas e valores amostrais da variável primária.
- **y0** (*ArrayLike*) – Coordenadas e valores amostrais da variável primária.
- **z0** (*ArrayLike*) – Coordenadas e valores amostrais da variável primária.
- **candidates** (*dict\[str, tuple\[ArrayLike, ArrayLike, ArrayLike\]\]*) – Mapeamento do nome de cada candidata para os arrays de entrada `(x, y, z)`.
- **alpha** (*float*) – Nível de significância do teste z de Fisher, por candidata, antes de `correction`.
- **correction** (*Literal\['bonferroni', 'none'\]*) – `"bonferroni"` (padrão quando `len(candidates) > 1`) divide `alpha` pelo número de candidatas para controlar a taxa de falsos positivos no lote inteiro; `"none"` testa cada candidata diretamente ao nível `alpha`.
- **min_abs_rho** (*float*) – Limiar de relevância prática: uma candidata é rejeitada mesmo com um p-valor significativo se `|rho| < min_abs_rho`.
- **max_violation_fraction** (*float*) – Fração máxima dos lags avaliados que pode violar o limite de Cauchy-Schwarz antes de a candidata ser rejeitada como inadmissível.
- **max_colocation_dist** (*float | None*) – Repassado para o {class}`CrossVariogram <apbase.cross_variogram.CrossVariogram>` no pareamento primária<->candidata. `None` exige coincidência exata.
- **n_lags** (*int*) – Repassado tanto aos ajustes de `Variogram` da primária/candidata quanto ao ajuste do {class}`CrossVariogram <apbase.cross_variogram.CrossVariogram>`.
- **max_pairs** (*int*) – Repassado tanto aos ajustes de `Variogram` da primária/candidata quanto ao ajuste do {class}`CrossVariogram <apbase.cross_variogram.CrossVariogram>`.
- **max_distance** (*float*) – Repassado tanto aos ajustes de `Variogram` da primária/candidata quanto ao ajuste do {class}`CrossVariogram <apbase.cross_variogram.CrossVariogram>`.

**Retorna**

`selected`: subconjunto de `candidates` que passou nos dois testes, pronto para `CoKriging(...).fit(x0, y0, z0, secondaries=result.selected)`. `report`: diagnósticos por candidata (rho, p-valor, fração admissível, decisão, status) de todas as candidatas, mantidas ou não.

**Tipo de retorno**

{obj}`ScreeningResult <apbase.cross_variogram.ScreeningResult>`

**Notas**

Uma candidata rejeitada por “amostra insuficiente” (menos de 4 pares colocalizados) ou por um modelo ajustado inválido fica registrada em `report` com `decision=False` e o motivo em `status` – sem gerar erro.

**Exemplos**

```pycon
>>> result = screen_secondary_variables(x0, y0, z0, {"ndvi": (xn, yn, zn)})
>>> result.selected
{'ndvi': (xn, yn, zn)}
```

:::
