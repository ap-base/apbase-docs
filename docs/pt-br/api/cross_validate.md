# apbase.cross_validate

Validação cruzada leave-one-out para IDW (inverso da distância ponderada), krigagem ordinária e cokrigagem.

Este pacote exporta as funções públicas usadas para avaliar a acurácia do IDW/krigagem e da cokrigagem colocalizada/ICM/LMC (MAE, RMSE, R²) no mesmo conjunto de dados de entrada, além de `select_best_model`, que escolhe automaticamente o método estatisticamente melhor a partir de qualquer um dos resultados.

::::{py:class} apbase.cross_validate.BestModelResult(method, metric, idw_score, kriging_score, margin, relative_margin, significant, confidence_level, ci_low, ci_high, n_common_valid)

Classes base: `object`

Escolha entre IDW e krigagem com respaldo estatístico.

**Variáveis**

- **method** (*{"idw", "kriging"}*) – Método selecionado.
- **metric** (*{"rmse", "mae"}*) – Métrica usada na comparação.
- **kriging_score** (*idw_score,*) – Métricas pareadas sobre as amostras retiradas finitas em comum.
- **relative_margin** (*margin,*) – Melhora absoluta e relativa do método selecionado.
- **significant** (*bool*) – Se o intervalo de confiança do bootstrap exclui o zero.
- **confidence_level** (*float*) – Nível de confiança usado no intervalo.
- **ci_high** (*ci_low,*) – Limites da diferença das métricas entre IDW e krigagem (IDW menos krigagem).
- **n_common_valid** (*int*) – Número de amostras finitas pareadas usadas na comparação.

**Parâmetros**

- **method** (*Literal\['idw', 'kriging'\]*)
- **metric** (*Literal\['rmse', 'mae'\]*)
- **idw_score** (*float*)
- **kriging_score** (*float*)
- **margin** (*float*)
- **relative_margin** (*float*)
- **significant** (*bool*)
- **confidence_level** (*float*)
- **ci_low** (*float*)
- **ci_high** (*float*)
- **n_common_valid** (*int*)

:::{py:attribute} apbase.cross_validate.BestModelResult.method
:type: Literal['idw', 'kriging']

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.metric
:type: Literal['rmse', 'mae']

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.idw_score
:type: float

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.kriging_score
:type: float

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.margin
:type: float

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.relative_margin
:type: float

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.significant
:type: bool

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.confidence_level
:type: float

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.ci_low
:type: float

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.ci_high
:type: float

:::

:::{py:attribute} apbase.cross_validate.BestModelResult.n_common_valid
:type: int

:::

::::

::::{py:class} apbase.cross_validate.CokrigingCrossValidationResult(by_method, n_samples, radius, model_params)

Classes base: `object`

Resultados da validação cruzada leave-one-out da cokrigagem colocalizada/ICM/LMC.

Veja {func}`cross_validate_cokriging() <apbase.cross_validate.cross_validate_cokriging>`.

**Variáveis**

- **by_method** (*dict\[str, MethodCrossValidation\]*) – Resultados da validação indexados pelo nome do método. Um método cujo modelo não pôde ser ajustado fica de fora; veja {func}`cross_validate_cokriging() <apbase.cross_validate.cross_validate_cokriging>`.
- **n_samples** (*int*) – Número de amostras primárias retiradas avaliadas.
- **radius** (*float*) – Raio de busca local compartilhado.
- **model_params** (*dict*) – Parâmetros ajustados da cokrigagem indexados pelo nome do método, com as mesmas chaves de `by_method`.

**Parâmetros**

- **by_method** (*dict\[str, MethodCrossValidation\]*)
- **n_samples** (*int*)
- **radius** (*float*)
- **model_params** (*dict\[str, dict\[str, Any\]\]*)

:::{py:attribute} apbase.cross_validate.CokrigingCrossValidationResult.by_method
:type: dict[str, MethodCrossValidation]

:::

:::{py:attribute} apbase.cross_validate.CokrigingCrossValidationResult.n_samples
:type: int

:::

:::{py:attribute} apbase.cross_validate.CokrigingCrossValidationResult.radius
:type: float

:::

:::{py:attribute} apbase.cross_validate.CokrigingCrossValidationResult.model_params
:type: dict[str, dict[str, Any]]

:::

::::

::::{py:class} apbase.cross_validate.CrossValidationResult(idw, kriging, n_samples, radius, model_params)

Classes base: `object`

Resultados da validação cruzada leave-one-out do IDW e da krigagem ordinária.

**Variáveis**

- **kriging** (*idw,*) – Resultados da validação por método.
- **n_samples** (*int*) – Número de amostras retiradas avaliadas.
- **radius** (*float*) – Raio de busca local compartilhado.
- **model_params** (*dict*) – Parâmetros legíveis do semivariograma ajustado.

**Parâmetros**

- **idw** (*MethodCrossValidation*)
- **kriging** (*MethodCrossValidation*)
- **n_samples** (*int*)
- **radius** (*float*)
- **model_params** (*dict\[str, float | int | str\]*)

:::{py:attribute} apbase.cross_validate.CrossValidationResult.idw
:type: MethodCrossValidation

:::

:::{py:attribute} apbase.cross_validate.CrossValidationResult.kriging
:type: MethodCrossValidation

:::

:::{py:attribute} apbase.cross_validate.CrossValidationResult.n_samples
:type: int

:::

:::{py:attribute} apbase.cross_validate.CrossValidationResult.radius
:type: float

:::

:::{py:attribute} apbase.cross_validate.CrossValidationResult.model_params
:type: dict[str, float | int | str]

:::

::::

::::{py:class} apbase.cross_validate.MethodCrossValidation(mae, rmse, r2, n_valid, predicted, actual)

Classes base: `object`

Resultados leave-one-out de um único método de interpolação.

**Variáveis**

- **r2** (*mae, rmse,*) – Métricas agregadas da validação, calculadas sobre as predições finitas.
- **n_valid** (*int*) – Número de predições finitas que entram nas métricas.
- **actual** (*predicted,*) – Valores preditos por amostra e valores reais retirados.

**Parâmetros**

- **mae** (*float*)
- **rmse** (*float*)
- **r2** (*float*)
- **n_valid** (*int*)
- **predicted** (*ndarray*)
- **actual** (*ndarray*)

:::{py:attribute} apbase.cross_validate.MethodCrossValidation.mae
:type: float

:::

:::{py:attribute} apbase.cross_validate.MethodCrossValidation.rmse
:type: float

:::

:::{py:attribute} apbase.cross_validate.MethodCrossValidation.r2
:type: float

:::

:::{py:attribute} apbase.cross_validate.MethodCrossValidation.n_valid
:type: int

:::

:::{py:attribute} apbase.cross_validate.MethodCrossValidation.predicted
:type: ndarray

:::

:::{py:attribute} apbase.cross_validate.MethodCrossValidation.actual
:type: ndarray

:::

::::

::::{py:class} apbase.cross_validate.MultiMethodBestModelResult(method, runner_up, metric, scores, margin, relative_margin, significant, confidence_level, ci_low, ci_high, n_common_valid)

Classes base: `object`

Escolha do melhor entre N métodos nomeados, com respaldo estatístico.

Generaliza o {class}`BestModelResult <apbase.cross_validate.BestModelResult>` para mais de dois métodos (por exemplo, {attr}`CokrigingCrossValidationResult.by_method <apbase.cross_validate.CokrigingCrossValidationResult.by_method>`) – veja {func}`select_best_model() <apbase.cross_validate.select_best_model>`.

**Variáveis**

- **runner_up** (*method,*) – Método selecionado e segundo colocado.
- **metric** (*{"rmse", "mae"}*) – Métrica usada na comparação.
- **scores** (*dict\[str, float\]*) – Métricas pareadas sobre as amostras retiradas finitas em comum.
- **relative_margin** (*margin,*) – Melhora absoluta e relativa de `method` sobre `runner_up`.
- **significant** (*bool*) – Se o intervalo de confiança do bootstrap exclui o zero.
- **confidence_level** (*float*) – Nível de confiança usado no intervalo.
- **ci_high** (*ci_low,*) – Limites da diferença das métricas entre o segundo colocado e o vencedor (segundo colocado menos vencedor).
- **n_common_valid** (*int*) – Número de amostras finitas pareadas usadas na comparação.

**Parâmetros**

- **method** (*str*)
- **runner_up** (*str*)
- **metric** (*Literal\['rmse', 'mae'\]*)
- **scores** (*dict\[str, float\]*)
- **margin** (*float*)
- **relative_margin** (*float*)
- **significant** (*bool*)
- **confidence_level** (*float*)
- **ci_low** (*float*)
- **ci_high** (*float*)
- **n_common_valid** (*int*)

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.method
:type: str

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.runner_up
:type: str

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.metric
:type: Literal['rmse', 'mae']

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.scores
:type: dict[str, float]

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.margin
:type: float

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.relative_margin
:type: float

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.significant
:type: bool

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.confidence_level
:type: float

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.ci_low
:type: float

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.ci_high
:type: float

:::

:::{py:attribute} apbase.cross_validate.MultiMethodBestModelResult.n_common_valid
:type: int

:::

::::

:::{py:function} apbase.cross_validate.cross_validate(x, y, z, *, max_points=500, seed=None, radius=None, power=2.0, max_neighbors=40, min_neighbors=3, model_values=None)

Validação cruzada leave-one-out do IDW local e da krigagem ordinária local.

Cada ponto retirado é removido, um por vez, e estimado de novo a partir dos pontos amostrais restantes, reutilizando um único semivariograma/raio e um único índice espacial para os dois métodos. A avaliação fica limitada a `max_points` amostras retiradas; veja `max_points` para o comportamento da amostragem em conjuntos de dados maiores.

**Parâmetros**

- **x** (*ArrayLike*) – Coordenadas e valores dos pontos amostrais, unidimensionais. Os registros em que algum deles é `NaN` ou infinito são ignorados.
- **y** (*ArrayLike*) – Coordenadas e valores dos pontos amostrais, unidimensionais. Os registros em que algum deles é `NaN` ou infinito são ignorados.
- **z** (*ArrayLike*) – Coordenadas e valores dos pontos amostrais, unidimensionais. Os registros em que algum deles é `NaN` ou infinito são ignorados.
- **max_points** (*int*) – Número máximo de pontos amostrais avaliados pelo leave-one-out. Se o conjunto de dados (finitos) tiver mais pontos que isso, é sorteada uma subamostra aleatória desse tamanho em vez de avaliar todos os pontos.
- **seed** (*int | None*) – Semente do sorteio da subamostra quando `x` tem mais de `max_points` pontos finitos. `None` usa entropia nova.
- **radius** (*float | None*) – Raio de busca local compartilhado pelos dois métodos. Se for `None`, é derivado como o `range` do semivariograma ajustado (ou informado) (`range / 3` com 10.000 pontos ou mais), o mesmo padrão usado por {class}`IDW <apbase.idw.IDW>` e {class}`Kriging <apbase.kriging.Kriging>`.
- **power** (*float*) – Potência do IDW (expoente da distância).
- **max_neighbors** (*int*) – Limites de vizinhos compartilhados pelos dois métodos. `max_neighbors` é limitado a `apbase.config["max_neighbors_ceiling"]` (padrão `500`).
- **min_neighbors** (*int*) – Limites de vizinhos compartilhados pelos dois métodos. `max_neighbors` é limitado a `apbase.config["max_neighbors_ceiling"]` (padrão `500`).
- **model_values** (*ArrayLike | None*) – Vetor de modelo de semivariograma nativo opcional (5 valores). Se for omitido, um semivariograma é ajustado a partir de `x`, `y`, `z`.

**Retorna**

MAE (erro absoluto médio), RMSE (raiz do erro quadrático médio) e R² (coeficiente de determinação) dos dois métodos, além das predições por amostra e dos valores reais retirados.

**Tipo de retorno**

{obj}`CrossValidationResult <apbase.cross_validate.CrossValidationResult>`

**Exceções**

- **ValueError** – Se os arrays de entrada tiverem tamanhos inconsistentes, registros finitos de menos, limites de vizinhos inválidos, um raio inválido ou uma configuração inválida de bootstrap/amostragem.
- **NativeExecutionError** – Se o kernel nativo de validação cruzada informar um status de falha.

**Exemplos**

```pycon
>>> result = cross_validate(x, y, z, max_points=300)
>>> result.idw.rmse, result.kriging.rmse
```

:::

:::{py:function} apbase.cross_validate.cross_validate_cokriging(x0, y0, z0, secondaries, *, max_points=500, seed=None, radius=None, max_neighbors=40, min_neighbors=3, n_structures=2, max_colocation_dist=None, max_secondary_neighbors=None)

Validação cruzada leave-one-out conjunta da cokrigagem colocalizada, do ICM e do LMC.

Cada um dos três modelos de corregionalização é ajustado uma vez com o conjunto de dados completo (como no {meth}`fit() <apbase.cokriging.CoKriging.fit>`); depois, só a variável primária é retirada, um ponto por vez, e estimada de novo, com um único índice espacial da primária e um único raio compartilhados pelos três métodos – veja {func}`cross_validate() <apbase.cross_validate.cross_validate>` para a função equivalente de IDW/krigagem.

**Parâmetros**

- **x0** (*ArrayLike*) – Coordenadas e valores amostrais da variável primária.
- **y0** (*ArrayLike*) – Coordenadas e valores amostrais da variável primária.
- **z0** (*ArrayLike*) – Coordenadas e valores amostrais da variável primária.
- **secondaries** (*SecondaryInput*) – As mesmas formas aceitas pelo {meth}`fit() <apbase.cokriging.CoKriging.fit>`.
- **max_points** (*int*) – Número máximo de pontos amostrais avaliados pelo leave-one-out; veja {func}`cross_validate() <apbase.cross_validate.cross_validate>`.
- **seed** (*int | None*) – Semente do sorteio da subamostra quando há mais de `max_points` pontos finitos. `None` usa entropia nova.
- **radius** (*float | None*) – Raio de busca local compartilhado pelos três métodos e pela busca de vizinhos de todas as variáveis. Se for `None`, é derivado como o `range` (`range / 3` com 10.000 pontos ou mais) de um semivariograma ajustado só à variável primária (independente do alcance conjunto ajustado por cada método).
- **max_neighbors** (*int*) – Limites de vizinhos compartilhados pelos três métodos.
- **min_neighbors** (*int*) – Limites de vizinhos compartilhados pelos três métodos.
- **n_structures** (*int*) – Número de estruturas aninhadas do LMC (S); veja {class}`CoKriging <apbase.cokriging.CoKriging>`.
- **max_colocation_dist** (*float | None*) – Distância de pareamento das covariâncias cruzadas e limite de vizinhos das variáveis secundárias (ICM e LMC); veja {class}`CoKriging <apbase.cokriging.CoKriging>`.
- **max_secondary_neighbors** (*int | None*) – Distância de pareamento das covariâncias cruzadas e limite de vizinhos das variáveis secundárias (ICM e LMC); veja {class}`CoKriging <apbase.cokriging.CoKriging>`.

**Retorna**

MAE (erro absoluto médio), RMSE (raiz do erro quadrático médio) e R² (coeficiente de determinação) por método em `by_method` (`"collocated"`, `"icm"`, `"lmc"`), além das predições por amostra e dos valores reais retirados (idênticos entre os métodos, avaliados nas mesmas amostras retiradas). Um método cujo modelo não pode ser ajustado fica de fora em vez de fazer a chamada falhar: qualquer método quando uma variável secundária tem amostras de menos pareadas com a primária (veja `max_colocation_dist`), e o ICM ou o LMC quando o ajuste é rejeitado por não ser semidefinido positivo ou por ser inválido. O erro só é gerado quando nenhum método pode ser ajustado.

**Tipo de retorno**

{obj}`CokrigingCrossValidationResult <apbase.cross_validate.CokrigingCrossValidationResult>`

**Exceções**

- **ValueError** – Se os arrays de entrada, os limites de vizinhos, as variáveis secundárias, o raio ou a configuração de amostragem forem inválidos.
- **NativeExecutionError** – Se o kernel de validação cruzada informar um status de falha, ou se o modelo de nenhum método puder ser ajustado (é gerado o primeiro erro de ajuste).

**Exemplos**

```pycon
>>> result = cross_validate_cokriging(x0, y0, z0, {"ndvi": (xu, yu, zu)})
>>> result.by_method["icm"].rmse
```

:::

:::{py:function} apbase.cross_validate.select_best_model(result: CrossValidationResult, *, metric: Literal['rmse', 'mae'] = 'rmse', n_bootstrap: int = 2000, confidence_level: float = 0.95, seed: int | None = None) -> BestModelResult

Escolhe o método estatisticamente melhor entre dois ou mais métodos avaliados.

Com um {class}`CrossValidationResult <apbase.cross_validate.CrossValidationResult>` (IDW contra krigagem), mantém o comportamento original de dois métodos e o mesmo tipo de retorno – veja abaixo. Com qualquer outro mapeamento nomeado de {class}`MethodCrossValidation <apbase.cross_validate.MethodCrossValidation>` (por exemplo, {attr}`CokrigingCrossValidationResult.by_method <apbase.cross_validate.CokrigingCrossValidationResult.by_method>`, ou um `{"a": ..., "b": ..., "c": ...}` montado à mão), generaliza para uma comparação entre o vencedor e o segundo colocado entre todos eles e devolve um {class}`MultiMethodBestModelResult <apbase.cross_validate.MultiMethodBestModelResult>`.

Escolhe o melhor entre IDW e krigagem a partir de um {class}`CrossValidationResult <apbase.cross_validate.CrossValidationResult>`.

Compara o IDW com a krigagem ordinária nas amostras retiradas em que *os dois* métodos produziram uma predição leave-one-out finita (uma amostra pode ser finita para um método e NaN para o outro – por exemplo, num sistema de krigagem local singular –, então as duas séries de erros continuam pareadas ponto a ponto). Vence o método com o menor `metric` (um empate fica com o `"idw"`, a mesma regra de seleção do {func}`create_map() <apbase.mapping.create_map>`). Em seguida, um bootstrap pareado sobre esse conjunto em comum estima um intervalo de confiança para a diferença das métricas (IDW menos krigagem); `significant` é `True` quando esse intervalo exclui o zero, isto é, quando é improvável que a vitória seja um efeito do sorteio específico das amostras retiradas.

**Parâmetros**

- **result** (*CrossValidationResult | Mapping\[str, MethodCrossValidation\]*) – Saída de {func}`cross_validate() <apbase.cross_validate.cross_validate>`.
- **metric** (*Literal\['rmse', 'mae'\]*) – Métrica de erro usada tanto na estimativa pontual quanto em cada réplica do bootstrap. `"rmse"` é a mesma métrica que o {func}`create_map() <apbase.mapping.create_map>` já usa para escolher o método automaticamente. O R² não é oferecido aqui de propósito: para um conjunto fixo de valores reais ele é monotônico no RMSE, mas a normalização dele (`1 - SS_res/SS_tot`) depende da variância do subconjunto avaliado, então a comparação deixa de ser tão limpa quando os padrões de NaN dos dois métodos divergem.
- **n_bootstrap** (*int*) – Número de reamostragens do bootstrap pareado. Memória e tempo crescem como `O(n_bootstrap * n_common_valid)`; o padrão é rápido (bem menos de um segundo) até o `max_points=500` padrão do `cross_validate`.
- **confidence_level** (*float*) – Nível de confiança bilateral do intervalo da diferença das métricas, por exemplo `0.95` para um IC de 95%.
- **seed** (*int | None*) – Semente do sorteio das reamostragens do bootstrap. `None` usa entropia nova.

**Retorna**

O método selecionado, com as métricas pareadas, a margem e o intervalo de confiança do bootstrap que sustentam a escolha. Para IDW contra krigagem, `ci_low`/`ci_high` limitam a diferença das métricas IDW menos krigagem: um intervalo positivo significa que a krigagem teve a melhor métrica, e um intervalo negativo, que o IDW teve a melhor métrica.

**Tipo de retorno**

{obj}`BestModelResult <apbase.cross_validate.BestModelResult>` ou {obj}`MultiMethodBestModelResult <apbase.cross_validate.MultiMethodBestModelResult>`

**Exceções**

**ValueError** – Se a configuração da métrica/do bootstrap for inválida, se os arrays de valores preditos/reais forem inconsistentes, se forem informados menos de dois métodos ou se não houver evidência pareada para a comparação.

**Notas**

Usa um bootstrap percentil sobre os erros pareados por amostra em vez de um teste paramétrico (por exemplo, um teste t pareado), então não precisa de nenhuma hipótese sobre a distribuição nem da dependência do SciPy: os `n_bootstrap` sorteios de índices são feitos uma única vez com `numpy.random.Generator.integers()`, e o RMSE/MAE de cada réplica é calculado numa única redução vetorizada, não num laço Python. A reamostragem reutiliza o *mesmo* sorteio para os dois métodos em cada réplica, o que preserva o pareamento/a correlação ponto a ponto entre os erros do IDW e da krigagem – essencial para um intervalo da diferença com significado.

Qualquer amostra retirada em que o próprio `actual` não é finito também é excluída (isso não acontece com a saída do próprio `cross_validate`, que é filtrada antes, mas protege entradas `CrossValidationResult` montadas à mão).

Se um método não tem nenhuma predição finita no conjunto em comum e o outro tem pelo menos uma, este vence direto (`significant=True`, `margin=inf`, sem bootstrap – não há o que reamostrar). Se nenhum dos métodos tem alguma predição finita, ou se as predições finitas dos dois métodos nunca coincidem na mesma amostra retirada, a função gera um `ValueError`: ao contrário do critério de desempate simples por RMSE do `create_map`, esta função se recusa a adivinhar quando não há evidência pareada em comum para comparar.

**Exemplos**

```pycon
>>> result = cross_validate(x, y, z, max_points=300)
>>> best = select_best_model(result)
>>> best.method
'kriging'
>>> best.significant
True
```

:::
