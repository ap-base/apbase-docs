# Guia do usuário

Este guia explica como o APbase transforma dados de campo irregulares em mapas
validados. O APbase está disponível como o pacote Python `apbase` e o crate
Rust `apbase`; cada exemplo tem uma aba para cada linguagem. Comece por
{doc}`../installation` e {doc}`../quickstart` para instalar e criar o seu
primeiro mapa.

Para gerar mapas no dia a dia, comece por `Map` ou `create_map`, que rodam o
pipeline completo descrito em {doc}`grid-and-mapping`. Use os componentes de
nível mais baixo só quando precisar inspecionar ou controlar uma etapa.

Para orientações de implantação em serviços, workers, contêineres e na nuvem,
veja {doc}`../production`.

## Lendo os parâmetros em Rust

As listas de parâmetros deste guia usam os nomes e tipos do Python. O crate
Rust mantém os mesmos nomes e valores padrão, com estas convenções:

- Configurações obrigatórias são argumentos do construtor
  (`MapOptions::new(resolution)`); as opcionais são campos de uma struct
  `<Name>Options` que implementa `Default`, então você define só o que muda:
  `IDWOptions { power: 3.0, ..Default::default() }`.
- Os estimadores seguem `new(options)? -> fit(&x, &y, &z)? -> interpolate(&targets)?`.
- Valores ajustados são lidos por métodos getter, não por atributos:
  `kriging.model_params()?.range`, `ck.model_values()?`.
- `None` vira `Option`: `radius: Some(50.0)`, `seed: Some(42)`,
  `filter_kwargs: Some(SpatialFilterOptions { .. })`.
- Escolhas por string viram enums, como `FilterLevel::Light` ou
  `CoKrigingMethod::Icm`; eles também são lidos a partir das strings do Python
  (`"icm".parse()?`).
- `array_like` é qualquer slice, `Vec`, array ou array `ndarray` de tipo
  numérico; `targets` é um array `ndarray` `(n, 2)`, uma slice ou `Vec` de
  pares `[x, y]`, uma slice ou `Vec` de valores `geos::Geometry` de ponto, ou
  um `Grid` ajustado.
- Dicionários de variáveis são
  `IndexMap<String, (Array1<f64>, Array1<f64>, Array1<f64>)>`, e os resultados
  por método são `IndexMap`s numa ordem estável (`cv.by_method["icm"].rmse`).
  Os exemplos de cokrigagem precisam do crate `indexmap`, e alguns exemplos
  usam tipos de `ndarray` diretamente.
- Toda chamada que pode falhar devolve `Result<T, ApbaseError>`.
  `e.is(ErrorKind::InterpolationError)` é verdadeiro para esse tipo e para
  todos os tipos mais específicos abaixo dele, como `KrigingInvalidRadiusError`.

## Páginas deste guia

- {doc}`grid-and-mapping`: o pipeline automático do `Map`, o seu resultado e
  grades de pontos a estimar definidas manualmente.
- {doc}`filtering`: remoção de registros inválidos e outliers espaciais.
- {doc}`variogram`: ajuste e inspeção do semivariograma.
- {doc}`idw`: inverso da distância ponderada.
- {doc}`kriging`: krigagem ordinária local.
- {doc}`cross-validation`: a comparação IDW × krigagem por trás do `Map`.
- {doc}`cokriging`: estimativa com variáveis secundárias (avançado).

```{toctree}
:hidden:
:maxdepth: 1

grid-and-mapping
filtering
variogram
idw
kriging
cross-validation
cokriging
```

Para a matemática por trás da escolha automática entre IDW e krigagem, veja
{doc}`../methodology/index`. Para as assinaturas públicas, veja a
{doc}`referência da API (em inglês) <../api/index>`.
