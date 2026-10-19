# Cokrigagem

O `CoKriging` estima uma variável primária com a ajuda de uma ou mais
variáveis secundárias relacionadas. Por exemplo, você pode combinar amostras
esparsas de produtividade com NDVI, altitude ou condutividade elétrica (CE) do
solo. O fluxo tem três etapas: selecionar as variáveis candidatas, ajustar e
interpolar com as que passarem e fazer a validação cruzada para conferir se a
cokrigagem de fato melhora o resultado.

A cokrigagem é um fluxo avançado. Hoje ela não faz parte da seleção padrão do
`apbase.Map`. Use-a quando tiver variáveis secundárias relevantes e quiser
testar se elas reduzem o erro.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_variogram import screen_secondary_variables
from apbase.cokriging import CoKriging
from apbase.cross_validate import cross_validate_cokriging, select_best_model

# 1. Seleção das candidatas: ficam só as que passam nos dois testes
screened = screen_secondary_variables(
    x0, y0, z0,
    {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze)},
    max_colocation_dist=30.0,  # pareia amostras a até 30 unidades de distância
)
screened.report      # rho, p_value, n_pairs, decision, status, ... de cada candidata
secondaries = screened.selected   # ex.: {"ndvi": (xn, yn, zn)}

# 2. Ajuste e interpolação
ck = CoKriging(method="icm", max_neighbors=40, min_neighbors=3)
ck.fit(x0, y0, z0, secondaries)
z_targets = ck.interpolate(targets)   # targets: array (n, 2)

# 3. Confirma pela LOO-CV que ela supera a krigagem sem variáveis secundárias
cv = cross_validate_cokriging(x0, y0, z0, secondaries)
best = select_best_model(cv.by_method)
best.method, best.significant
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::cokriging::{CoKriging, CoKrigingMethod, CoKrigingOptions, SecondaryInput};
use apbase::cross_validate::{
    CrossValidateCokrigingOptions, SelectBestModelOptions, cross_validate_cokriging, select_best_model,
};
use apbase::cross_variogram::{ScreeningOptions, screen_secondary_variables};
use indexmap::IndexMap;

// 1. Seleção das candidatas: ficam só as que passam nos dois testes
let candidates = IndexMap::from([
    ("ndvi".to_string(), (xn.clone(), yn.clone(), zn.clone())),
    ("ec".to_string(), (xe.clone(), ye.clone(), ze.clone())),
]);
let screened = screen_secondary_variables(
    &x0, &y0, &z0,
    &candidates,
    ScreeningOptions { max_colocation_dist: Some(30.0), ..Default::default() }, // pareia amostras a até 30 unidades de distância
)?;
screened.report;                                      // rho, p_value, n_pairs, decision, status, ... de cada candidata
let secondaries = SecondaryInput::from(screened.selected); // ex.: {"ndvi": (xn, yn, zn)}

// 2. Ajuste e interpolação
let mut ck = CoKriging::new(CoKrigingOptions {
    method: CoKrigingMethod::Icm,
    max_neighbors: 40,
    min_neighbors: 3,
    ..Default::default()
})?;
ck.fit(&x0, &y0, &z0, &secondaries)?;
let z_targets = ck.interpolate(&targets)?; // targets: array (n, 2)

// 3. Confirma pela LOO-CV que ela supera a krigagem sem variáveis secundárias
let cv = cross_validate_cokriging(&x0, &y0, &z0, &secondaries, CrossValidateCokrigingOptions::default())?;
let best = select_best_model(&cv.by_method, SelectBestModelOptions::default())?;
(best.method, best.significant);
```

:::

::::

Não pule a primeira etapa. Passar uma variável secundária sem relação direto
para o `CoKriging` pode não gerar erro, mas pode piorar a estimativa.

Defina `max_colocation_dist` quando as variáveis secundárias forem amostradas
nos seus próprios locais, como costumam ser as superfícies de NDVI ou de CE. A
seleção compara valores primários e secundários em pares e, com o padrão
`None`, um par só se forma onde as coordenadas são idênticas. Sem esse
parâmetro, nenhum par se forma e toda candidata é rejeitada com o status
`"insufficient sample"`. Use uma distância da ordem do espaçamento de
amostragem da variável secundária.

## Entradas principais

`x0`, `y0` : array_like
: Coordenadas dos pontos amostrais da variável primária.

`z0` : array_like
: Valores da variável primária. Precisa ter o mesmo tamanho de `x0` e `y0`.

`candidates` : dict[str, tuple[array_like, array_like, array_like]]
: Variáveis secundárias candidatas passadas a `screen_secondary_variables`,
  por exemplo `{"ndvi": (xn, yn, zn)}`.

`secondaries` : dict ou list
: Variáveis secundárias selecionadas, passadas a `CoKriging.fit` e
  `cross_validate_cokriging`. `screened.selected` já vem no formato certo.

`targets` : array_like ou Grid
: Coordenadas dos pontos a estimar passadas a `CoKriging.interpolate`.

## Etapa 1: seleção

`screen_secondary_variables` verifica se cada candidata tem correlação
relevante com a variável primária (teste $z$ de Fisher) e um semivariograma
cruzado admissível (verificação de Cauchy–Schwarz). Só as candidatas que
passam nas duas verificações são mantidas. Veja
{doc}`../methodology/covariate-screening` para a estatística.

### Parâmetros da seleção

`alpha` : float, padrão `0.05`
: Nível de significância do teste $z$ de Fisher.

`correction` : {"bonferroni", "none"}, padrão `"bonferroni"`
: Correção para testes múltiplos usada quando há várias candidatas.

`min_abs_rho` : float, padrão `0.3`
: Correlação prática mínima. Uma candidata estatisticamente significativa,
  mas fraca, continua sendo rejeitada.

`max_violation_fraction` : float, padrão `0.1`
: Fração máxima dos lags avaliados que pode violar o limite de
  admissibilidade do semivariograma cruzado.

`max_colocation_dist` : float, opcional
: Distância máxima usada para parear amostras primárias e secundárias. `None`
  pareia só coordenadas idênticas (veja acima).

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
screened = screen_secondary_variables(
    x0, y0, z0,
    {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze), "random_noise": (xr, yr, zr)},
    alpha=0.05,
    min_abs_rho=0.3,
    max_colocation_dist=30.0,
)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
let candidates = IndexMap::from([
    ("ndvi".to_string(), (xn, yn, zn)),
    ("ec".to_string(), (xe, ye, ze)),
    ("random_noise".to_string(), (xr, yr, zr)),
]);
let screened = screen_secondary_variables(
    &x0, &y0, &z0,
    &candidates,
    ScreeningOptions {
        alpha: 0.05,
        min_abs_rho: 0.3,
        max_colocation_dist: Some(30.0),
        ..Default::default()
    },
)?;
```

:::

::::

`screened.selected` já tem o formato esperado por `CoKriging.fit`, então passe
direto como `secondaries` (em Rust, `SecondaryInput::from(screened.selected)`).
`screened.report` inclui todas as candidatas, inclusive as rejeitadas: cada
`CovariateReport` traz `rho`, `p_value`, `n_pairs`, `admissible_fraction`,
`decision`, `status` e os `model_params` ajustados. É útil quando você precisa
registrar por que uma variável foi descartada.

## Etapa 2: ajuste e interpolação

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
ck = CoKriging(method="icm", radius=None, max_neighbors=40, min_neighbors=3)
ck.fit(x0, y0, z0, secondaries)
estimates = ck.interpolate(targets)
```

:::

:::{tab-item} Rust
:sync: rust

```rust
let mut ck = CoKriging::new(CoKrigingOptions {
    method: CoKrigingMethod::Icm,
    radius: None,
    max_neighbors: 40,
    min_neighbors: 3,
    ..Default::default()
})?;
ck.fit(&x0, &y0, &z0, &secondaries)?;
let estimates = ck.interpolate(&targets)?;
```

:::

::::

### Parâmetros do ajuste

`method` : {"collocated", "icm", "lmc"}, padrão `"collocated"`
: Modelo de cokrigagem. O padrão `"collocated"` é o mais barato, mas tem os
  requisitos descritos abaixo. Quando eles não são atendidos, use `"icm"`: ele
  não tem nenhum deles nem formas por estrutura para ajustar.

`radius` : float, opcional
: Raio de busca local. Se for omitido, o APbase o deriva do semivariograma da
  variável primária.

`max_neighbors`, `min_neighbors` : int
: Limites de vizinhos. Para `"icm"` e `"lmc"`, eles limitam a busca de
  vizinhos de cada variável.

`n_structures` : int, padrão `2`
: Número de estruturas aninhadas do LMC. Usado só por `"lmc"`.

`model_values` : array_like, opcional
: Valores de modelo pré-calculados. Só `"collocated"` aceita.

`ck.model_params` mostra os parâmetros ajustados de forma legível (a estrutura
muda conforme o método; veja a docstring da classe); `ck.model_values` dá o
vetor nativo achatado, que pode ser passado de volta como `model_values` para
reaproveitar um ajuste colocalizado. Em Rust, os dois são getters:
`ck.model_params()?` devolve um enum `CoKrigingModelParams` com uma variante
por método, e `ck.model_values()?`, o vetor.

**A cokrigagem colocalizada precisa do valor secundário em todos os pontos a
estimar da interpolação**, não só nos seus pontos amostrais (veja a docstring
da classe). Se for preciso, interpole antes uma variável secundária esparsa
numa grade densa o suficiente. Ela também depende da hipótese do Modelo de
Markov 1 (MM1): assume-se que o valor secundário no ponto a estimar torna
redundantes os dados secundários mais distantes (veja
{doc}`../methodology/cokriging`). Por fim, a cokrigagem colocalizada estima a
correlação de cada variável secundária a partir de amostras nas mesmas
coordenadas da primária. Se uma secundária tiver poucas delas, o `fit` gera um
`ValueError`; use `"icm"` ou `"lmc"` para esses dados heterotópicos. ICM e LMC
não têm nenhum desses requisitos.

## Etapa 3: validação cruzada

Ajustar a cokrigagem é só parte do trabalho. A validação cruzada mostra se ela
de fato supera a krigagem sem variáveis secundárias *neste* conjunto de dados.

### Parâmetros da validação cruzada

`max_points` : int, padrão `500`
: Número máximo de amostras primárias avaliadas na validação leave-one-out.

`seed` : int, opcional
: Semente usada quando a validação sorteia um subconjunto dos pontos
  primários.

`radius`, `max_neighbors`, `min_neighbors`, `n_structures`
: Mesmo significado que no `CoKriging`.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_validate import cross_validate_cokriging, select_best_model

cv = cross_validate_cokriging(x0, y0, z0, secondaries, max_neighbors=40, min_neighbors=3)
{name: result.rmse for name, result in cv.by_method.items()}

best = select_best_model(cv.by_method)
best.method       # ex.: "icm"
best.significant  # True se a vantagem sobre o segundo colocado dificilmente é acaso
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::cross_validate::{
    CrossValidateCokrigingOptions, SelectBestModelOptions, cross_validate_cokriging, select_best_model,
};

let cv = cross_validate_cokriging(
    &x0, &y0, &z0,
    &secondaries,
    CrossValidateCokrigingOptions { max_neighbors: 40, min_neighbors: 3, ..Default::default() },
)?;
for (name, result) in &cv.by_method {
    println!("{name}: {}", result.rmse);
}

let best = select_best_model(&cv.by_method, SelectBestModelOptions::default())?;
best.method;      // ex.: "icm"
best.significant; // true se a vantagem sobre o segundo colocado dificilmente é acaso
```

:::

::::

`cross_validate_cokriging` roda o leave-one-out sobre a variável primária para
os três métodos numa única passada. Um método cujo modelo não pode ser
ajustado fica de fora de `cv.by_method` em vez de interromper a execução;
{doc}`../methodology/cross-validation` explica o que é retirado e quando um
método é descartado.

Isso mostra qual método de cokrigagem é o melhor, não se acrescentar variáveis
secundárias ajudou. Para conferir isso, compare `cv.by_method[...]` com as
métricas de `result.kriging` de uma execução simples de
`apbase.cross_validate.cross_validate(x0, y0, z0)`.
