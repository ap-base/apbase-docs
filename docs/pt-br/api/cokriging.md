# apbase.cokriging

API de alto nível da cokrigagem.

Estima uma variável primária com a ajuda de uma ou mais variáveis secundárias com correlação espacial. Rode antes `apbase.cross_variogram.screen_secondary_variables()` para selecionar as variáveis secundárias admissíveis.

::::{py:class} apbase.cokriging.CoKriging(*, method='collocated', radius=None, max_neighbors=40, min_neighbors=3, n_structures=2, model_values=None)

Classes base: `object`

Ajusta um modelo de corregionalização e interpola valores com cokrigagem.

Estima uma variável primária com a ajuda de uma ou mais variáveis secundárias com correlação espacial (por exemplo, NDVI, altitude ou condutividade elétrica (CE) do solo junto com amostras esparsas de produtividade). Rode antes `screen_secondary_variables()` para escolher as variáveis secundárias admissíveis – o `CoKriging` não faz essa seleção sozinho.

**Parâmetros**

- **method** (*str*) – `"collocated"`, `"icm"` (modelo de corregionalização intrínseca) ou `"lmc"` (modelo linear de corregionalização completo).
- **radius** (*float | None*) – Raio de busca local da vizinhança da primária. Se for `None`, usa o `range` do semivariograma da primária (`range / 3` com 10.000 pontos ou mais). Com menos de `min_neighbors` pontos amostrais da primária dentro dele, um ponto a estimar usa os `max_neighbors` mais próximos. Com `method="collocated"`, uma variável secundária sem nenhum valor dentro desse raio em torno de um ponto a estimar fica fora do sistema desse ponto (se não sobrar nenhuma: krigagem ordinária da primária); `"icm"`/`"lmc"` buscam a vizinhança de cada variável de forma independente, então variáveis secundárias heterotópicas funcionam diretamente.
- **max_neighbors** (*int*) – Limites de vizinhos da primária, com o mesmo significado que no `Kriging`.
- **min_neighbors** (*int*) – Limites de vizinhos da primária, com o mesmo significado que no `Kriging`.
- **n_structures** (*int*) – Só com `method="lmc"`: número de estruturas de corregionalização aninhadas, incluindo a do efeito pepita. Padrão `2`.
- **model_values** (*ArrayLike | None*) – Vetor de modelo de corregionalização pré-ajustado opcional, só com `"collocated"`. Se for informado, o {meth}`fit() <apbase.cokriging.CoKriging.fit>` não ajusta o semivariograma da primária nem os semivariogramas cruzados de cada variável secundária.

:::{py:property} apbase.cokriging.CoKriging.method
:type: str

Método de cokrigagem usado pelo interpolador ajustado.

**Retorna**

Um de `"collocated"`, `"icm"` ou `"lmc"`.

**Tipo de retorno**

str

:::

:::{py:property} apbase.cokriging.CoKriging.radius
:type: float | None

Raio de busca local das vizinhanças da primária.

**Retorna**

Raio explícito, ou `None` quando o raio é derivado do alcance do semivariograma da primária durante a interpolação.

**Tipo de retorno**

float ou None

:::

:::{py:property} apbase.cokriging.CoKriging.max_neighbors
:type: int

Número máximo de vizinhos da primária usados por ponto a estimar.

**Retorna**

Limite superior de vizinhos locais da primária.

**Tipo de retorno**

int

:::

:::{py:property} apbase.cokriging.CoKriging.min_neighbors
:type: int

Número mínimo de pontos amostrais da primária dentro de `radius` antes de recorrer aos pontos mais próximos.

**Retorna**

Limite inferior de vizinhos locais da primária.

**Tipo de retorno**

int

:::

:::{py:property} apbase.cokriging.CoKriging.n_structures
:type: int

Número de estruturas aninhadas do LMC (modelo linear de corregionalização).

**Retorna**

Número de estruturas, usado só quando `method="lmc"`.

**Tipo de retorno**

int

:::

:::{py:property} apbase.cokriging.CoKriging.n_threads
:type: int

Número de threads OpenMP usado pelos kernels nativos de cokrigagem.

**Retorna**

Valor atual, lido de `apbase.config`.

**Tipo de retorno**

int

:::

:::{py:method} apbase.cokriging.CoKriging.from_data(x0, y0, z0, secondaries, **kwargs)
:classmethod:

Cria e ajusta um interpolador de cokrigagem.

**Parâmetros**

- **x0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **y0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **z0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **secondaries** (*mapping ou sequence*) – Variáveis secundárias aceitas pelo {meth}`fit() <apbase.cokriging.CoKriging.fit>`.
- **\*\*kwargs** – Argumentos nomeados repassados para {class}`CoKriging <apbase.cokriging.CoKriging>`.

**Retorna**

Interpolador de cokrigagem ajustado.

**Tipo de retorno**

{obj}`CoKriging <apbase.cokriging.CoKriging>`

:::

:::{py:property} apbase.cokriging.CoKriging.is_fitted
:type: bool

Se um modelo de corregionalização já foi ajustado.

**Retorna**

`True` depois que {meth}`fit() <apbase.cokriging.CoKriging.fit>` termina com sucesso.

**Tipo de retorno**

bool

:::

:::{py:property} apbase.cokriging.CoKriging.model_values
:type: ndarray

Vetor de modelo de corregionalização nativo.

`"collocated"`: `[model_id, nugget, partial_sill, range, sse, rho_1..rho_K]`. `"icm"`: `[model_id, range, nugget_matrix.ravel(), sill_matrix.ravel()]`. `"lmc"`: `[model_id, structure_ranges, coefficient_matrices.ravel()]`. Achatado num vetor único em todos os casos – veja {attr}`model_params <apbase.cokriging.CoKriging.model_params>` para as matrizes de fato.

**Retorna**

Vetor de modelo nativo achatado do método ajustado.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:property} apbase.cokriging.CoKriging.model_params
:type: dict[str, Any]

Parâmetros ajustados legíveis – a estrutura muda conforme o {attr}`method <apbase.cokriging.CoKriging.method>`.

`"collocated"`: `{"primary": {...}, "rho": {name: rho, ...}}`. `"icm"`: `{"primary": {...}, "model_id", "model_name", "range", "secondary_names", "nugget_matrix", "sill_matrix"}`. `"lmc"`: `{"primary": {...}, "model_id", "model_name", "structure_ranges", "secondary_names", "coefficient_matrices"}` (`coefficient_matrices` tem formato `(n_structures, K+1, K+1)`, com o índice 0 = estrutura do efeito pepita). A variável 0 de toda matriz é a primária, e 1..K seguem a ordem de `secondary_names`.

**Retorna**

Parâmetros ajustados específicos do método. As entradas com matrizes são devolvidas como `numpy.ndarray`, sem cópia.

**Tipo de retorno**

dict

:::

:::{py:method} apbase.cokriging.CoKriging.fit(x0, y0, z0, secondaries)

Ajusta o modelo de corregionalização aos dados de entrada.

**Parâmetros**

- **x0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **y0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **z0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **secondaries** (*mapping ou sequence*) – Mapeamento de nome para os arrays de entrada `(x, y, z)`, ou uma sequência de tuplas `(x, y, z)`. As entradas em sequência recebem os nomes `"secondary_1"`, `"secondary_2"` e assim por diante.

**Retorna**

Interpolador ajustado. Os registros em que alguma coordenada ou algum valor da primária ou de uma secundária é `NaN` ou infinito são ignorados dentro daquela variável.

**Tipo de retorno**

{obj}`CoKriging <apbase.cokriging.CoKriging>`

**Exceções**

- **ValueError** – Se as entradas tiverem tamanhos inconsistentes, pontos finitos da primária de menos, nenhuma variável secundária utilizável, limites de vizinhos inválidos ou variáveis com variância zero.
- **NativeExecutionError** – Se o ajuste nativo da cokrigagem informar um status de falha.

:::

:::{py:method} apbase.cokriging.CoKriging.interpolate(targets)

Estima os valores da primária nos pontos a estimar.

**Parâmetros**

**targets** (*Grid | ArrayLike*) – Coordenadas dos pontos a estimar, nas mesmas formas aceitas por {meth}`interpolate() <apbase.kriging.Kriging.interpolate>`.

**Retorna**

Uma estimativa por ponto a estimar. Um ponto a estimar com menos de `min_neighbors` pontos amostrais da primária dentro de `radius` usa os `max_neighbors` mais próximos; com `method="collocated"`, uma variável secundária sem nenhum ponto amostral dentro de `radius` em torno dele fica de fora (veja a docstring da classe).

**Tipo de retorno**

numpy.ndarray

:::

:::{py:method} apbase.cokriging.CoKriging.predict(targets)

Estima os valores da primária nos pontos a estimar.

**Parâmetros**

**targets** (*Grid ou array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`interpolate() <apbase.cokriging.CoKriging.interpolate>`.

**Retorna**

Uma estimativa de cokrigagem por ponto a estimar.

**Tipo de retorno**

numpy.ndarray

:::

:::{py:method} apbase.cokriging.CoKriging.fit_interpolate(x0, y0, z0, secondaries, targets)

Ajusta o interpolador e já estima os valores nos pontos a estimar.

**Parâmetros**

- **x0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **y0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **z0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **secondaries** (*mapping ou sequence*) – Variáveis secundárias aceitas pelo {meth}`fit() <apbase.cokriging.CoKriging.fit>`.
- **targets** (*Grid ou array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`interpolate() <apbase.cokriging.CoKriging.interpolate>`.

**Retorna**

Uma estimativa de cokrigagem por ponto a estimar.

**Tipo de retorno**

numpy.ndarray

:::

::::

:::{py:function} apbase.cokriging.co_kriging(x0, y0, z0, secondaries, targets, *, method='collocated', model_values=None, radius=None, max_neighbors=40, min_neighbors=3)

Ajusta a cokrigagem e estima os valores em `targets` numa única chamada.

Atalho de conveniência em torno de {class}`CoKriging <apbase.cokriging.CoKriging>` para quem só quer uma chamada única de ajuste e interpolação. Prefira criar o `CoKriging` diretamente quando for reutilizar o mesmo modelo ajustado em várias chamadas de `interpolate`, já que esta função sempre ajusta do zero.

**Parâmetros**

- **x0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **y0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **z0** (*array_like*) – Coordenadas e valores amostrais da variável primária.
- **secondaries** (*mapping ou sequence*) – Variáveis secundárias aceitas por {meth}`apbase.cokriging.CoKriging.fit() <apbase.cokriging.CoKriging.fit>`.
- **targets** (*array_like*) – Coordenadas dos pontos a estimar aceitas por {meth}`apbase.cokriging.CoKriging.interpolate() <apbase.cokriging.CoKriging.interpolate>`.
- **method** (*{"collocated", "icm", "lmc"}, padrão "collocated"*) – Método de cokrigagem.
- **model_values** (*array_like ou None, padrão None*) – Vetor de modelo de corregionalização pré-ajustado opcional; por enquanto, aceito só com `method="collocated"`.
- **radius** (*float ou None, padrão None*) – Raio de busca local. Se for `None`, deriva o `range` do semivariograma da primária (`range / 3` com 10.000 pontos ou mais).
- **max_neighbors** (*int*) – Limites de vizinhos da primária usados pela busca local.
- **min_neighbors** (*int*) – Limites de vizinhos da primária usados pela busca local.

**Retorna**

Uma estimativa de cokrigagem por ponto a estimar.

**Tipo de retorno**

numpy.ndarray

:::
