# apbase.mapping

API principal de geração automática de mapas.

Use {class}`apbase.mapping.Map <apbase.mapping.Map>` como ponto de entrada principal quando quiser que o APbase escolha sozinho a estratégia de interpolação. Ele roda a filtragem, a geração do contorno e da grade, um único ajuste de semivariograma compartilhado, a validação cruzada de IDW (inverso da distância ponderada) contra krigagem, a seleção do modelo pelo erro de validação e a interpolação final. Use {func}`apbase.mapping.create_map() <apbase.mapping.create_map>` quando uma chamada funcional única for mais conveniente.

Cada função e classe pública abaixo documenta suas entradas, valores padrão, valor de retorno e exemplos de uso, a partir da docstring do código.

:::{py:function} apbase.mapping.create_map(x, y, z, *, resolution, filter=True, bounds=None, geographic_mode=None, power=2.0, max_neighbors=40, min_neighbors=3, max_cv_points=500, seed=None, filter_kwargs=None)

Atalho funcional para o pipeline automático do {class}`Map <apbase.mapping.Map>`.

Filtra, faz a validação cruzada e interpola `x, y, z` em um mapa. Escolhe automaticamente entre IDW e krigagem ordinária com {func}`select_best_model() <apbase.cross_validate.select_best_model>`, a partir dos resultados leave-one-out de {func}`cross_validate() <apbase.cross_validate.cross_validate>`, e depois interpola numa grade regular construída a partir de `bounds` (ou de uma envoltória côncava inferida de `x`/`y`, quando `bounds` é omitido).

Por padrão (`geographic_mode=None`), `x`/`y` são verificados automaticamente (`apbase.common.coordinates.guess_xy_coordinate_system()`): entrada já projetada/métrica é usada como está, sem conversão de CRS – o mesmo comportamento de antes. Já a entrada geográfica (lon/lat) é detectada e tratada automaticamente: ela – e `bounds`, quando informado – é convertida internamente para coordenadas métricas (`apbase.common.coordinates.prepare_metric_xy()`, que escolhe sozinha entre `"local"` e `"utm"` pela extensão da própria entrada em relação a `apbase.config["local_mode_extent_km_ceiling"]`) antes de o pipeline rodar, e `result.x`/`result.y` voltam automaticamente para as coordenadas originais da entrada; você nunca chama `prepare_metric_xy`/`restore_original_xy` por conta própria. Passar `geographic_mode="local"` ou `"utm"` explicitamente força essa projeção em vez da escolha automática (e ela continua valendo só para a entrada de fato detectada como geográfica).

**Parâmetros**

- **x** (*ArrayLike*) – Coordenadas e valores dos pontos amostrais, unidimensionais.
- **y** (*ArrayLike*) – Coordenadas e valores dos pontos amostrais, unidimensionais.
- **z** (*ArrayLike*) – Coordenadas e valores dos pontos amostrais, unidimensionais.
- **resolution** (*float*) – Espaçamento da grade de saída. Na unidade métrica de `x`/`y` quando elas não são geográficas; em metros (UTM real ou a aproximação local esférica) quando a entrada geográfica é detectada, com `geographic_mode` deixado em `None` (escolha automática) ou definido explicitamente.
- **filter** (*bool*) – Se o {class}`SpatialFilter <apbase.filtering.SpatialFilter>` deve rodar nos dados de entrada antes da validação cruzada e da interpolação.
- **bounds** (*Bounds | None*) – Domínio de interpolação opcional: uma geometria Shapely, uma string WKT ou bytes WKB, na mesma unidade de `x`/`y` (antes de qualquer conversão geográfica). Quando omitido, uma envoltória côncava é inferida a partir dos pontos amostrais (filtrados).
- **geographic_mode** (*str | None*) – `None` (padrão): detecção automática, como descrito acima – a entrada geográfica escolhe sozinha `"local"` ou `"utm"`; entrada já métrica não é afetada. `"local"` ou `"utm"`: força essa projeção para a entrada geográfica detectada, com a mesma semântica do `geographic_mode` de `apbase.common.coordinates.prepare_metric_xy()`. `"local"` é sempre compatível com {meth}`MapResult.to_raster() <apbase.mapping.MapResult.to_raster>`; a reprojeção inversa de `"utm"` não é linear e pode quebrar a regularidade exata da grade em extensões não triviais – veja {meth}`MapResult.to_raster() <apbase.mapping.MapResult.to_raster>`.
- **power** (*float*) – Potência do IDW (expoente da distância), usada só se o IDW for selecionado.
- **max_neighbors** (*int*) – Limites de vizinhos compartilhados pela validação cruzada e pelo ajuste final de IDW/krigagem.
- **min_neighbors** (*int*) – Limites de vizinhos compartilhados pela validação cruzada e pelo ajuste final de IDW/krigagem.
- **max_cv_points** (*int*) – Repassado para {func}`cross_validate() <apbase.cross_validate.cross_validate>`.
- **seed** (*int | None*) – Repassado para {func}`cross_validate() <apbase.cross_validate.cross_validate>`.
- **filter_kwargs** (*dict\[str, Any\] | None*) – Argumentos nomeados extras repassados para {class}`SpatialFilter <apbase.filtering.SpatialFilter>` (ignorados quando `filter=False`).

**Retorna**

Saída compacta do mapa, com os diagnósticos da validação cruzada e da filtragem.

**Tipo de retorno**

{obj}`MapResult <apbase.mapping.MapResult>`

**Exemplos**

```pycon
>>> result = create_map(x, y, z, resolution=10.0)
>>> result.method
'kriging'
```

:::

::::{py:class} apbase.mapping.Map(x=None, y=None, z=None, *, resolution, filter=True, bounds=None, geographic_mode=None, power=2.0, max_neighbors=40, min_neighbors=3, max_cv_points=500, seed=None, filter_kwargs=None)

Classes base: `object`

Construtor principal de mapas automáticos.

`Map` é o ponto de entrada de alto nível recomendado para gerar mapas em produção. Ele filtra os dados de entrada, constrói a grade de interpolação, ajusta um único semivariograma compartilhado, compara IDW e krigagem ordinária por validação cruzada, escolhe o método estatisticamente melhor e interpola o mapa final.

Configure uma vez e chame com os dados de entrada:

```python
builder = Map(resolution=10.0, bounds=boundary)
result = builder(x, y, z)
```

A mesma instância configurada pode ser reutilizada em vários conjuntos de dados:

```python
result_a = builder.fit_generate(x_a, y_a, z_a)
result_b = builder(x_b, y_b, z_b)
```

Para uso funcional numa única chamada, chame {func}`create_map() <apbase.mapping.create_map>`.

**Parâmetros**

- **x** (*array_like ou None, padrão None*) – Coordenadas e valores amostrais opcionais. Quando `x` é informado, os três precisam ser informados, e o mapa é gerado já na construção.
- **y** (*array_like ou None, padrão None*) – Coordenadas e valores amostrais opcionais. Quando `x` é informado, os três precisam ser informados, e o mapa é gerado já na construção.
- **z** (*array_like ou None, padrão None*) – Coordenadas e valores amostrais opcionais. Quando `x` é informado, os três precisam ser informados, e o mapa é gerado já na construção.
- **resolution** (*float*) – Espaçamento da grade de saída.
- **filter** (*bool, padrão True*) – Se o {class}`SpatialFilter <apbase.filtering.SpatialFilter>` deve ser aplicado.
- **bounds** (*geometry, str, bytes ou None, padrão None*) – Domínio de interpolação opcional, como geometria Shapely, WKT ou WKB.
- **geographic_mode** (*{"local", "utm"} ou None, padrão None*) – Modo de projeção geográfica repassado para {func}`create_map() <apbase.mapping.create_map>`.
- **power** (*float, padrão 2.0*) – Potência do IDW (expoente da distância).
- **max_neighbors** (*int*) – Limites de vizinhos compartilhados pela validação cruzada e pela interpolação final.
- **min_neighbors** (*int*) – Limites de vizinhos compartilhados pela validação cruzada e pela interpolação final.
- **max_cv_points** (*int, padrão 500*) – Número máximo de amostras leave-one-out usadas pela validação cruzada.
- **seed** (*int ou None, padrão None*) – Semente aleatória da amostragem da validação cruzada e da seleção do modelo.
- **filter_kwargs** (*dict ou None, padrão None*) – Argumentos nomeados extras repassados para {class}`SpatialFilter <apbase.filtering.SpatialFilter>`.

:::{py:attribute} apbase.mapping.Map.resolution

:::

:::{py:attribute} apbase.mapping.Map.filter

:::

:::{py:attribute} apbase.mapping.Map.bounds

:::

:::{py:attribute} apbase.mapping.Map.geographic_mode

:::

:::{py:attribute} apbase.mapping.Map.power

:::

:::{py:attribute} apbase.mapping.Map.max_neighbors

:::

:::{py:attribute} apbase.mapping.Map.min_neighbors

:::

:::{py:attribute} apbase.mapping.Map.max_cv_points

:::

:::{py:attribute} apbase.mapping.Map.seed

:::

:::{py:attribute} apbase.mapping.Map.filter_kwargs

:::

:::{py:attribute} apbase.mapping.Map.result
:type: MapResult | None

:::

:::{py:method} apbase.mapping.Map.fit_generate(x, y, z)

Roda o pipeline completo e guarda o mapa gerado.

**Parâmetros**

- **x** (*array_like*) – Coordenadas e valores amostrais.
- **y** (*array_like*) – Coordenadas e valores amostrais.
- **z** (*array_like*) – Coordenadas e valores amostrais.

**Retorna**

Resultado do mapa gerado, também guardado em {attr}`result <apbase.mapping.Map.result>`.

**Tipo de retorno**

{obj}`MapResult <apbase.mapping.MapResult>`

:::

::::

::::{py:class} apbase.mapping.MapResult(x, y, z, method, cross_validation, radius, resolution, n_source_points, filter_statistics, coordinate_transform)

Classes base: `object`

Resultado da geração automática de mapas.

`x`, `y`, `z` formam uma lista compacta de pontos – uma linha por ponto a estimar dentro do contorno, sem preenchimento para as células fora dele. Chame {meth}`to_raster() <apbase.mapping.MapResult.to_raster>`/{meth}`to_array3d() <apbase.mapping.MapResult.to_array3d>` para gerar um array retangular com preenchimento só quando ele for realmente necessário.

**Variáveis**

- **z** (*x, y,*) – Coordenadas compactas dos pontos a estimar e valores interpolados.
- **method** (*{"idw", "kriging"}*) – Método de interpolação escolhido pela validação cruzada.
- **cross_validation** (*CrossValidationResult*) – Diagnósticos leave-one-out usados na seleção do método.
- **radius** (*float*) – Raio de busca local usado pela interpolação final.
- **resolution** (*float*) – Espaçamento da grade de saída.
- **n_source_points** (*int*) – Número de pontos amostrais usados depois do descarte de valores não finitos e da filtragem espacial opcional.
- **filter_statistics** (*FilterStatistics ou None*) – Diagnósticos da filtragem local, ou `None` quando a filtragem foi desativada.
- **coordinate_transform** (*CoordinateTransform ou None*) – Transformação usada para devolver as coordenadas de saída no sistema de coordenadas original da entrada.

**Parâmetros**

- **x** (*ndarray*)
- **y** (*ndarray*)
- **z** (*ndarray*)
- **method** (*Literal\['idw', 'kriging'\]*)
- **cross_validation** (*CrossValidationResult*)
- **radius** (*float*)
- **resolution** (*float*)
- **n_source_points** (*int*)
- **filter_statistics** (*FilterStatistics | None*)
- **coordinate_transform** (*CoordinateTransform | None*)

:::{py:attribute} apbase.mapping.MapResult.x
:type: ndarray

:::

:::{py:attribute} apbase.mapping.MapResult.y
:type: ndarray

:::

:::{py:attribute} apbase.mapping.MapResult.z
:type: ndarray

:::

:::{py:attribute} apbase.mapping.MapResult.method
:type: Literal['idw', 'kriging']

:::

:::{py:attribute} apbase.mapping.MapResult.cross_validation
:type: CrossValidationResult

:::

:::{py:attribute} apbase.mapping.MapResult.radius
:type: float

:::

:::{py:attribute} apbase.mapping.MapResult.resolution
:type: float

:::

:::{py:attribute} apbase.mapping.MapResult.n_source_points
:type: int

:::

:::{py:attribute} apbase.mapping.MapResult.filter_statistics
:type: FilterStatistics | None

:::

:::{py:attribute} apbase.mapping.MapResult.coordinate_transform
:type: CoordinateTransform | None

:::

:::{py:method} apbase.mapping.MapResult.to_raster()

Reconstrói `(X, Y, Z)` como arrays `(ny, nx)`, com NaN fora do contorno.

`X`/`Y` guardam as coordenadas reais da entrada (na mesma unidade de `x`/`y`/`bounds` de origem), não um índice `0..nx`/`0..ny` reindexado.

Quando `coordinate_transform.geographic_mode == "utm"` (isto é, o mapa foi construído com `geographic_mode="utm"` a partir de entrada geográfica detectada), a reprojeção inversa UTM->lon/lat não é linear, então uma grade exatamente regular internamente pode deixar de ser exatamente regular em lon/lat – isso pode gerar um `ValueError` em extensões não triviais. `geographic_mode="local"` usa uma transformação afim fixa e é sempre seguro para `to_raster`/`to_array3d`.

**Retorna**

Arrays retangulares `X`, `Y` e `Z`. As células mascaradas ficam como `NaN`.

**Tipo de retorno**

tuple\[numpy.ndarray, numpy.ndarray, numpy.ndarray\]

**Exceções**

**ValueError** – Se os pontos compactos não puderem ser representados como uma grade regular mascarada.

:::

:::{py:method} apbase.mapping.MapResult.to_array3d()

Empilha {meth}`to_raster() <apbase.mapping.MapResult.to_raster>` num único array `(ny, nx, 3)`.

**Retorna**

Array retangular cujo último eixo guarda `X`, `Y` e `Z`.

**Tipo de retorno**

numpy.ndarray

:::

::::
