# apbase.grid

Geração da grade regular de interpolação, compartilhada pela interpolação por IDW (inverso da distância ponderada) e por krigagem.

Este pacote exporta a classe `Grid` e uma função de conveniência para gerar as grades regulares de pontos usadas como pontos a estimar.

::::{py:class} apbase.grid.Grid(*, boundary=None, resolution=20.0, chunk_size=1000000, hull_ratio=0.12, coordinate_transform=None, geographic_mode=None)

Classes base: `object`

Gera pontos a estimar regulares dentro de um contorno.

O contorno vem de quem chama (`boundary=`, ou os construtores {meth}`from_wkt() <apbase.grid.Grid.from_wkt>`/{meth}`from_wkb() <apbase.grid.Grid.from_wkb>`) ou, quando nenhum é informado, é inferido como uma envoltória côncava dos pontos amostrais `x`/`y` ({meth}`from_data_xy() <apbase.grid.Grid.from_data_xy>`, ou simplesmente `fit(x, y)`).

**Parâmetros**

- **boundary** (*Boundary | None*) – Geometria Shapely opcional usada como domínio de interpolação. Quando omitida, uma envoltória côncava é inferida a partir dos pontos de entrada finitos.
- **resolution** (*float*) – Espaçamento da grade, na mesma unidade das coordenadas de entrada.
- **chunk_size** (*int*) – Número máximo de pontos candidatos testados por bloco.
- **hull_ratio** (*float*) – Razão passada para `shapely.concave_hull` quando o contorno é inferido. Não tem efeito quando `boundary` é informado explicitamente.
- **coordinate_transform** (*CoordinateTransform | None*) – `CoordinateTransform` opcional aplicada a `boundary` antes de construir a grade, para que ele fique no mesmo referencial de `x`/`y` já convertidos com `prepare_metric_xy`. Tem prioridade sobre `geographic_mode`.
- **geographic_mode** (*str | None*) – `None` (padrão), `"local"` ou `"utm"`. Quando `boundary` parece geográfico e `x`/`y` não, reprojeta `boundary` para coordenadas métricas antes de construir a grade.

:::{py:attribute} apbase.grid.Grid.boundary

:::

:::{py:attribute} apbase.grid.Grid.resolution

:::

:::{py:attribute} apbase.grid.Grid.chunk_size

:::

:::{py:attribute} apbase.grid.Grid.hull_ratio

:::

:::{py:attribute} apbase.grid.Grid.coordinate_transform

:::

:::{py:attribute} apbase.grid.Grid.geographic_mode

:::

:::{py:method} apbase.grid.Grid.from_data_xy(x, y, **kwargs)
:classmethod:

Cria uma grade e infere o contorno a partir dos pontos amostrais x/y (envoltória côncava).

Equivale a `Grid(**kwargs).fit(x, y)` sem `boundary` explícito. Quando o domínio já é conhecido, use {meth}`from_wkt() <apbase.grid.Grid.from_wkt>`, {meth}`from_wkb() <apbase.grid.Grid.from_wkb>` ou passe `boundary=` diretamente – nesse caso os pontos amostrais não são necessários.

**Parâmetros**

- **x** (*array_like*) – Coordenadas dos pontos amostrais usadas para inferir o contorno pela envoltória côncava.
- **y** (*array_like*) – Coordenadas dos pontos amostrais usadas para inferir o contorno pela envoltória côncava.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`Grid <apbase.grid.Grid>`.

**Retorna**

Grade ajustada.

**Tipo de retorno**

{obj}`Grid <apbase.grid.Grid>`

:::

:::{py:method} apbase.grid.Grid.from_wkt(wkt, **kwargs)
:classmethod:

Cria uma grade cujo contorno é lido de uma string WKT.

Não são necessários pontos amostrais: a grade é gerada diretamente a partir da geometria lida.

**Parâmetros**

- **wkt** (*str*) – Geometria do contorno codificada em WKT.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`Grid <apbase.grid.Grid>`.

**Retorna**

Grade ajustada.

**Tipo de retorno**

{obj}`Grid <apbase.grid.Grid>`

:::

:::{py:method} apbase.grid.Grid.from_wkb(wkb, **kwargs)
:classmethod:

Cria uma grade cujo contorno é lido de bytes WKB.

Não são necessários pontos amostrais: a grade é gerada diretamente a partir da geometria lida.

**Parâmetros**

- **wkb** (*bytes*) – Geometria do contorno codificada em WKB.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`Grid <apbase.grid.Grid>`.

**Retorna**

Grade ajustada.

**Tipo de retorno**

{obj}`Grid <apbase.grid.Grid>`

:::

:::{py:property} apbase.grid.Grid.is_fitted
:type: bool

Se os pontos da grade já foram gerados.

**Retorna**

`True` depois que {meth}`fit() <apbase.grid.Grid.fit>` termina com sucesso.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.grid.Grid.points
:type: ndarray

Coordenadas dos pontos a estimar geradas.

**Retorna**

Coordenadas `(n_points, 2)` dos pontos a estimar dentro do contorno ajustado.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:property} apbase.grid.Grid.fitted_boundary
:type: Boundary

Contorno preparado usado para manter os pontos a estimar dentro do domínio.

**Retorna**

Contorno com buffer e preparado, usado nos testes de ponto dentro do contorno.

**Tipo de retorno**

shapely.Geometry

:::

:::{py:property} apbase.grid.Grid.n_threads
:type: int

Número de threads usado para paralelizar os testes de pertinência ao contorno.

Lido na hora de `apbase.config["n_threads"]` (veja a docstring da classe) a cada acesso – não fica guardado desde a construção, então sempre reflete a configuração atual do processo inteiro.

**Retorna**

Número atual de threads.

**Tipo de retorno**

int

:::

:::{py:method} apbase.grid.Grid.fit(x=None, y=None)

Gera os pontos da grade.

Quando `boundary` foi passado ao construtor, a grade é construída diretamente a partir dele; nesse caso `x`/`y` são opcionais e servem só para conciliar `boundary` com `coordinate_transform`/ `geographic_mode` (veja a docstring da classe) – `x`/`y` nunca são usados para construir os pontos da grade quando `boundary` é informado. Caso contrário, `x`/`y` são obrigatórios: os pares não finitos são removidos e uma envoltória côncava inferida a partir dos restantes vira o contorno. As coordenadas de entrada devem já estar no sistema de coordenadas projetado de destino, a menos que sejam convertidas via `coordinate_transform`/ `geographic_mode`.

**Parâmetros**

- **x** (*array_like ou None, padrão None*) – Coordenadas dos pontos amostrais, usadas só para inferir um contorno ou conciliar um contorno informado com uma transformação de coordenadas.
- **y** (*array_like ou None, padrão None*) – Coordenadas dos pontos amostrais, usadas só para inferir um contorno ou conciliar um contorno informado com uma transformação de coordenadas.

**Retorna**

Esta grade, com `points` gerados e `fitted_boundary` preparado.

**Tipo de retorno**

{obj}`Grid <apbase.grid.Grid>`

**Exceções**

**ValueError** – Se nenhum contorno puder ser inferido, se a grade de candidatos gerada estiver vazia ou se ela passar de `apbase.config["grid_max_points_ceiling"]`.

:::

:::{py:method} apbase.grid.Grid.generate(x=None, y=None)

Ajusta a grade e devolve as coordenadas dos pontos a estimar geradas.

**Parâmetros**

- **x** (*array_like ou None, padrão None*) – Coordenadas dos pontos amostrais repassadas para {meth}`fit() <apbase.grid.Grid.fit>`.
- **y** (*array_like ou None, padrão None*) – Coordenadas dos pontos amostrais repassadas para {meth}`fit() <apbase.grid.Grid.fit>`.

**Retorna**

Coordenadas `(n_points, 2)` dos pontos a estimar dentro do contorno.

**Tipo de retorno**

numpy.ndarray

:::

::::

:::{py:function} apbase.grid.create_point_grid(*, x=None, y=None, resolution, boundary=None, chunk_size=1000000, hull_ratio=0.12)

Cria coordenadas regulares de pontos a estimar, a partir de um contorno ou de `x`/`y`.

**Parâmetros**

- **x** (*array_like ou None, padrão None*) – Coordenadas dos pontos amostrais, unidimensionais. Obrigatórias só quando `boundary` é omitido, para inferir um contorno como envoltória côncava dos pares finitos.
- **y** (*array_like ou None, padrão None*) – Coordenadas dos pontos amostrais, unidimensionais. Obrigatórias só quando `boundary` é omitido, para inferir um contorno como envoltória côncava dos pares finitos.
- **resolution** (*float*) – Espaçamento da grade, na mesma unidade de coordenadas de `x` e `y`.
- **boundary** (*object ou None, padrão None*) – Geometria Shapely opcional usada como contorno de interpolação. Quando informada, `x`/`y` não são necessários.
- **chunk_size** (*int, padrão DEFAULT_CHUNK_SIZE*) – Número máximo de pontos candidatos testados por bloco.
- **hull_ratio** (*float, padrão DEFAULT_HULL_RATIO*) – Razão usada pela envoltória côncava do Shapely quando `boundary` é omitido.

**Retorna**

Coordenadas `(n_points, 2)` dos pontos a estimar gerados dentro do contorno.

**Tipo de retorno**

numpy.ndarray

**Exceções**

**ValueError** – Se `boundary` for omitido e `x`/`y` não permitirem inferir um contorno válido, ou se a grade de candidatos estiver vazia ou for grande demais.

:::
