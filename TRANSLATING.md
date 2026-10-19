# Translating the documentation

The English pages in `docs/` are the source. Translations live in a folder per
locale that mirrors them file by file:

```
docs/installation.md                 → docs/pt-br/installation.md
docs/user-guide/kriging.md           → docs/pt-br/user-guide/kriging.md
docs/methodology/cokriging.md        → docs/pt-br/methodology/cokriging.md
```

[apbase.io](https://apbase.io) reads these files straight from this repository
and publishes them at `/pt-br/docs/...`, with the same slugs as `/en/docs/...`.
A page that has no translation yet is shown in English, with a notice, until
its file exists. Sphinx ignores `docs/pt-br/` (`exclude_patterns` in
`docs/conf.py`), so `make html` keeps building the English site only.

Not translated: `docs/api/` (generated from the English docstrings),
`references.bib` (shared by every language), `img/`, `_static/` and
`_templates/`.

## Checking what needs work

```bash
make translations
```

lists pages that are missing in `docs/pt-br/` and translations whose English
page changed after the translation's last commit, with the English commits to
carry over. Add `--strict` (`python3 scripts/check-translations.py --strict`)
to fail when anything needs work.

When you update an English page, either update its translation in the same
change or leave it for the report to pick up.

## Rules for every page

- **Same file, same structure.** Keep every heading, list, table, directive and
  tab in the same order as the English page, so both versions can be compared
  side by side.
- **Links keep their targets.** `{doc}` paths stay exactly as in English
  (`` {doc}`../installation` ``); they resolve inside the same language. Give
  links to the API reference an explicit title, because its pages are not
  translated: `` {doc}`referência da API <../api/index>` ``. In a `toctree`,
  write the entry as `Referência da API (em inglês) <api/index>`.
- **Code stays code.** Inside code blocks, translate comments only. Never
  translate function, class, module or parameter names (`Map`, `create_map`,
  `max_neighbors`), string values of the API (`"idw"`, `"kriging"`,
  `"collocated"`, `"icm"`, `"lmc"`, `"light"`) or error names.
- **Keep as written:** math, `{cite}` keys, tab labels (`Python`, `Rust`),
  `:sync:` keys and directive names (`note`, `tab-set`, `tab-item`).
- **No front matter** (`---` at the top of the file): the site renderer does not
  read it.
- **No links to an anchor in another page.** Heading anchors are built from the
  heading text, so they differ between languages. Link to the page instead.
- **Acronyms stay in English** (IDW, RMSE, MAE, IQR, ICM, LMC, MM1, BLUE,
  LOO-CV, NDVI, UTM). The first time each page uses one, expand it in the
  page's language: RMSE (raiz do erro quadrático médio).

## Português (pt-br)

Termos conferidos na literatura brasileira de geoestatística e agricultura de
precisão (Embrapa, ESALQ/USP, SciELO, Acta Scientiarum, RBCS) e na documentação
em PT-BR de QGIS, Google Cloud e Google Earth Engine. Regras gerais:

1. Termo consagrado em português ganha a forma em português: krigagem, efeito
   pepita, patamar, contribuição, alcance, validação cruzada.
2. Termo que a área usa em inglês fica em inglês: outlier, pipeline,
   leave-one-out, lag, raster, worker.
3. Siglas ficam em inglês, porque também são valores da API, com a expansão em
   português na primeira vez em cada página.

Tom: frases diretas, voz ativa, tratamento por "você".

### Semivariograma

| Inglês | Português | Nota |
|---|---|---|
| variogram, semivariogram | semivariograma | Forma usada na agronomia brasileira e termo exato para γ(h). As classes `Variogram` e `CrossVariogram` ficam com o nome em inglês. |
| semivariance | semivariância | |
| empirical semivariogram | semivariograma experimental | "Empírico" quase não aparece na literatura. |
| nugget (c₀) | efeito pepita | |
| sill | patamar | |
| partial sill (c) | contribuição | Também descrita como variância estrutural. |
| range (a) | alcance | O parâmetro `range` fica igual no código. |
| lag · lag bin | lag · classe de distância | Na primeira vez: lag (distância de separação). `n_lags` fica igual. |
| theoretical model · candidate model | modelo teórico · modelo candidato | |
| spherical · exponential · Gaussian | esférico · exponencial · gaussiano | |
| weighted least squares · Cressie's weights | mínimos quadrados ponderados · pesos de Cressie | |
| spatial structure · spatially uncorrelated | estrutura espacial · sem correlação espacial | |
| spatial correlation · spatial dependence | correlação espacial · dependência espacial | |
| nested structures | estruturas aninhadas | |

### Krigagem

| Inglês | Português | Nota |
|---|---|---|
| kriging · ordinary kriging · local kriging | krigagem · krigagem ordinária · krigagem local | |
| kriging system · kriging weights | sistema de krigagem · pesos de krigagem | |
| kriging variance · estimation variance | variância de krigagem · variância de estimação | |
| best linear unbiased estimator (BLUE) | melhor estimador linear não tendencioso (BLUE) | |
| unbiased · unbiasedness constraint · bias | não tendencioso · restrição de não tendenciosidade · viés | |
| Lagrange multiplier | multiplicador de Lagrange | |
| stationarity conditions (of the kriging system) | condições de otimalidade | É o ponto estacionário do cálculo, não a estacionariedade geoestatística. |
| estimate · estimator · prediction | estimativa · estimador · predição | |

### Cokrigagem

| Inglês | Português | Nota |
|---|---|---|
| cokriging | cokrigagem | |
| primary variable · secondary variable | variável primária · variável secundária | |
| covariate · candidate variable | covariável · variável candidata | |
| secondary-variable screening · covariate screening | seleção de variáveis secundárias · seleção de covariáveis | |
| cross-variogram · cross-covariance | semivariograma cruzado · covariância cruzada | |
| admissible | admissível | |
| coregionalization model | modelo de corregionalização | |
| Intrinsic Coregionalization Model (ICM) | modelo de corregionalização intrínseca (ICM) | |
| Linear Model of Coregionalization (LMC) | modelo linear de corregionalização (LMC) | |
| collocated cokriging · collocated datum | cokrigagem colocalizada · dado colocalizado | |
| Markov Model 1 (MM1) | Modelo de Markov 1 (MM1) | |
| heterotopic · isotopic data | dados heterotópicos · isotópicos | |
| block system | sistema em blocos | |
| PSD cone · eigenvalues | cone das matrizes semidefinidas positivas (PSD) · autovalores | |

### IDW e vizinhança

| Inglês | Português | Nota |
|---|---|---|
| inverse distance weighting (IDW) | inverso da distância ponderada (IDW) | |
| power | potência | O parâmetro `power` fica igual. |
| neighborhood · local neighborhood | vizinhança · vizinhança local | |
| neighbors · nearest neighbors | vizinhos · vizinhos mais próximos | |
| search radius | raio de busca | |
| source points · source data | pontos amostrais · dados de entrada | |
| target · target points | ponto a estimar · pontos a estimar | O argumento `targets` fica igual. |
| interpolation method · interpolator | método de interpolação · interpolador | |

### Validação cruzada e métricas

| Inglês | Português | Nota |
|---|---|---|
| cross-validation | validação cruzada | |
| leave-one-out cross-validation (LOO-CV) | validação cruzada leave-one-out (LOO-CV) | |
| RMSE | RMSE (raiz do erro quadrático médio) | |
| MAE · R² | MAE (erro absoluto médio) · R² (coeficiente de determinação) | |
| prediction error · held-out value | erro de predição · valor retirado | |
| Fisher z-test · significance level | teste z de Fisher · nível de significância | |
| Bonferroni correction | correção de Bonferroni | |

### Filtragem e outliers

| Inglês | Português | Nota |
|---|---|---|
| spatial filtering | filtragem espacial | |
| outlier | outlier (plural: outliers) | "Valores discrepantes" só como explicação. |
| global outlier · local spatial outlier | outlier global · outlier espacial local | |
| invalid rows | registros inválidos | |
| interquartile range (IQR) | intervalo interquartil (IQR) | |
| global pass · local pass | etapa global · etapa local | |
| threshold · filter level | limiar · nível de filtragem | |
| near-duplicate · GPS fixes | quase duplicados · posições de GPS | |
| sensor faults · extreme readings | falhas de sensor · leituras extremas | |

### Grade, contorno e coordenadas

| Inglês | Português | Nota |
|---|---|---|
| grid · target grid | grade · grade de interpolação | A classe `Grid` fica igual. |
| resolution | resolução | Tamanho da célula, em metros. |
| cell · raster | célula · raster | |
| boundary | contorno | |
| concave hull · convex hull | envoltória côncava · envoltória convexa | |
| clip · clipped map | recortar · mapa recortado | |
| projected metric coordinates (UTM) | coordenadas métricas projetadas (UTM) | |
| geographic coordinates (lon/lat) | coordenadas geográficas (lon/lat) | |
| compact output · full raster | saída compacta · raster completo | |

### Agricultura de precisão e dados de campo

| Inglês | Português | Nota |
|---|---|---|
| precision agriculture | agricultura de precisão | |
| field data · field | dados de campo · talhão | "Field" como área de cultivo vira talhão. |
| yield monitor · yield-monitor logs | monitor de produtividade · dados do monitor de produtividade | |
| yield · yield map | produtividade · mapa de produtividade | Nunca "rendimento". |
| soil samples · sensor readings | amostras de solo · leituras de sensores | |

### Software e produção

| Inglês | Português | Nota |
|---|---|---|
| pipeline | pipeline | |
| deployment · deploy | implantação · implantar | |
| production · service · API service | produção · serviço · serviço de API | |
| worker · queue · batch job | worker · fila · job em lote | |
| container | contêiner | Nomes de produto ficam como são (Azure Container Apps). |
| thread · OpenMP parallelism | thread · paralelismo OpenMP | |
| compiled numerical kernels | kernels numéricos compilados | |
| seed | semente | O parâmetro `seed` fica igual. |
| wheel · crate · binding | wheel · crate · binding | |
| deterministic | determinístico | |

### Títulos das páginas

| Inglês | Português |
|---|---|
| Overview | Visão geral |
| Installation | Instalação |
| Quickstart | Início rápido |
| Production and cloud deployment | Produção e implantação na nuvem |
| User guide | Guia do usuário |
| Map and grid generation | Geração de mapas e grades |
| Spatial filtering | Filtragem espacial |
| Variogram · Variogram fitting | Semivariograma · Ajuste do semivariograma |
| Kriging · Ordinary kriging | Krigagem · Krigagem ordinária |
| Inverse distance weighting (IDW) | Inverso da distância ponderada (IDW) |
| Cross-validation | Validação cruzada |
| Cokriging | Cokrigagem |
| Methodology · References | Metodologia · Referências |
| Secondary-variable screening | Seleção de variáveis secundárias |
| API Reference | Referência da API (em inglês) |
