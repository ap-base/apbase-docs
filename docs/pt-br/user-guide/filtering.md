# Filtragem espacial

O `SpatialFilter` limpa os pontos amostrais antes da interpolação. Ele remove
registros inválidos e, quando ativado, outliers globais e outliers espaciais
locais, com uma abordagem global e depois local desenvolvida para dados
agrícolas de alta densidade {cite}`Maldaner2018,Maldaner2020`.

Em geral você não precisa chamá-lo diretamente. O `apbase.Map` roda o filtro
internamente antes de comparar os métodos de interpolação. Use o
`SpatialFilter` quando quiser inspecionar os dados filtrados ou ajustar a
etapa de filtragem.

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.filtering import SpatialFilter

spatial_filter = SpatialFilter(
    filter_level="light",
    max_neighbors=120,
    cell_factor=3,
).fit(x, y, z)

x_filtered, y_filtered, z_filtered = spatial_filter.filter()
```

:::

:::{tab-item} Rust
:sync: rust

```rust
use apbase::filtering::{FilterLevel, SpatialFilter, SpatialFilterOptions};

let mut spatial_filter = SpatialFilter::new(SpatialFilterOptions {
    filter_level: FilterLevel::Light,
    max_neighbors: 120,
    cell_factor: 3,
    ..Default::default()
})?;
spatial_filter.fit(&x, &y, &z)?;

let (x_filtered, y_filtered, z_filtered) = spatial_filter.filter()?;
```

:::

::::

## O que ele faz

A filtragem acontece em duas etapas:

1. **Etapa global por IQR** (opcional, `apply_global_iqr=True` por padrão):
   uma verificação pelo intervalo interquartil (IQR) sobre os dados de entrada
   remove leituras extremas, como falhas de sensor, antes das verificações
   espaciais. Segue a etapa de filtragem global de {cite}`Maldaner2018`.
2. **Etapa local**: cada ponto é comparado com os pontos vizinhos dentro de
   `radius`, até `max_neighbors`. O `filter_level` controla o quão rigoroso é
   o limiar local, seguindo as etapas de filtragem local de
   {cite}`Maldaner2018`.

## Parâmetros

`x`, `y` : array_like
: Coordenadas dos pontos amostrais passadas ao `fit`. O `SpatialFilter` não
  converte longitude/latitude: passe coordenadas projetadas, na mesma unidade
  de `radius`.

`z` : array_like
: Valores amostrais. Precisa ter o mesmo tamanho de `x` e `y`.

`radius` : float, opcional
: Raio de busca local. Se for omitido, um semivariograma é ajustado e é usado
  `range / 3` (um terço do alcance).

`filter_level` : {"light", "moderate", "strict", "aggressive"}, padrão `"light"`
: Limiar para outliers locais, do mais brando ao mais rigoroso.

`apply_global_iqr` : bool, padrão `True`
: Roda a etapa global por IQR antes da filtragem local.

`max_neighbors` : int, padrão `120`
: Limite de vizinhos por ponto na etapa local. `0` usa todos os pontos dentro
  de `radius`.

`cell_factor` : int, padrão `3`
: Ajuste de velocidade da busca de vizinhos. Os pontos são indexados em
  células quadradas de lado `radius / cell_factor`; valores maiores geram
  células menores, então menos pontos fora do raio são percorridos, ao custo
  de mais células na memória.

`dedup_radius`, `dedup_z_tol` : float, padrão `0.0`
: Tratamento opcional de duplicados para registros densos de GPS. Deixe
  desligado, a menos que pontos repetidos quase idênticos estejam fazendo a
  variância local colapsar.

## Lendo os resultados

Depois do `fit`, você pode inspecionar o resultado de três formas:

- `filter()`: arrays `(x, y, z)` filtrados (só os pontos que passaram).
- `mask()`: máscara booleana de pontos mantidos, alinhada com a entrada
  original.
- `statistics`: diagnósticos por ponto (`pct_diff`, `local_z`, `local_prob`)
  para todos os pontos de entrada, inclusive os removidos.

## Dados com muitos duplicados

Fontes de pontos com muitas coordenadas quase duplicadas, como posições de
GPS repetidas nos dados de alta frequência do monitor de produtividade
{cite}`Maldaner2020`, podem fazer a variância local cair perto de zero e criar
falhas depois da filtragem. `dedup_radius` e `dedup_z_tol` juntam os grupos de
quase duplicados num único representante só durante o cálculo das estatísticas
da vizinhança local. Cada ponto de entrada continua sendo avaliado
individualmente. Deixe os dois em `0.0`, a menos que você veja esse padrão nos
seus dados.

Veja {py:class}`apbase.filtering.SpatialFilter` na referência da API (em
inglês) para todos os parâmetros, inclusive os ajustados com menos frequência
(`candidate_fraction`, `global_iqr_whisker`).
