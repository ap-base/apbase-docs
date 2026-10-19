# Produção e implantação na nuvem

O mesmo pipeline de mapeamento que roda num notebook pode rodar numa API, num
worker em segundo plano, num job em lote ou num serviço na nuvem. Esta página
mostra o que muda na implantação. As orientações valem para Python e Rust.

## Onde o APbase se encaixa

Use o APbase sempre que um serviço precisar transformar pontos de campo em
mapas:

- serviços de API que recebem pontos de campo e devolvem mapas interpolados;
- workers de fila ou de lote que processam arquivos de produtividade, de solo
  ou de sensores;
- jobs em contêiner no Kubernetes, Cloud Run, ECS/Fargate, Azure Container Apps
  ou runtimes gerenciados parecidos;
- servidores MCP e ferramentas de agentes que precisam gerar mapas de forma
  reproduzível;
- pipelines de dados agendados que gravam pontos de mapa ou rasters em
  armazenamento de objetos, Parquet, bancos de dados ou serviços de SIG.

Você não precisa de framework web, banco de dados, broker de mensagens, SIG de
desktop nem runtime de notebook para usar o pipeline. Forneça as coordenadas e
os valores de campo e consuma o mapa gerado no formato de que a sua aplicação
precisa.

## O que importa em produção

- Comece pelos pontos de entrada de alto nível: `apbase.Map` e
  `apbase.create_map` em Python, `apbase::Map` e `apbase::create_map` em Rust.
  Os componentes de nível mais baixo servem para diagnóstico e fluxos
  avançados.
- Filtragem, ajuste do semivariograma, IDW, krigagem e validação cruzada rodam
  em kernels numéricos compilados, então o trabalho pesado não acontece em
  laços sobre os pontos no código da aplicação.
- Defina limites quando precisar de orçamentos explícitos de CPU e memória.
  `max_cv_points` e `max_neighbors` são argumentos de `Map` e `create_map`
  (campos de `MapOptions` em Rust). O tamanho da grade e os pares do
  semivariograma são configurações do processo inteiro:
  `grid_max_points_ceiling`, `variogram_max_pairs` (pares amostrados pelo
  semivariograma que o pipeline ajusta) e `variogram_max_pairs_ceiling`,
  definidas com `apbase.config[key]` em Python ou `apbase::config.set(key, n)?`
  em Rust.
- Os resultados são compactos: só os pontos da grade dentro do contorno. Chame
  `to_raster()` apenas quando um cliente precisar da grade completa.
- Configure as threads do OpenMP uma vez por processo de worker, com
  `apbase.config["n_threads"]` em Python ou
  `apbase::config.set("n_threads", n)?` em Rust. Quando `n_threads` não é
  definido, as duas bibliotecas leem a variável de ambiente
  `APBASE_N_THREADS`.

## Usando o APbase num serviço

Defina as opções do processo uma vez, quando o serviço inicia. Deixe a
configuração global fora do handler da requisição.

::::{tab-set}

:::{tab-item} Python
:sync: python

Em Python:

```python
import os

import numpy as np

import apbase

apbase.config["n_threads"] = int(os.getenv("APBASE_N_THREADS", "2"))
apbase.config["grid_max_points_ceiling"] = int(
    os.getenv("APBASE_GRID_MAX_POINTS", "100000000")
)


def build_map_response(x, y, z, *, resolution, bounds=None):
    result = apbase.create_map(
        np.ascontiguousarray(x, dtype=np.float64),
        np.ascontiguousarray(y, dtype=np.float64),
        np.ascontiguousarray(z, dtype=np.float64),
        resolution=resolution,
        bounds=bounds,
        max_cv_points=500,
        max_neighbors=40,
        seed=42,
    )

    selected_cv = getattr(result.cross_validation, result.method)
    return {
        "method": result.method,
        "x": result.x,
        "y": result.y,
        "z": result.z,
        "rmse": selected_cv.rmse,  # RMSE na LOO-CV do método escolhido
        "n_source_points": result.n_source_points,  # pontos mantidos após a filtragem
    }
```

:::

:::{tab-item} Rust
:sync: rust

Em Rust:

```rust
use apbase::common::ApbaseError;
use apbase::cross_validate::Method;
use apbase::mapping::{Bounds, MapOptions};
use ndarray::Array1;

/// Chame uma vez na inicialização do serviço, antes de atender qualquer requisição.
fn configure_apbase() -> Result<(), ApbaseError> {
    let env_or = |key: &str, default: usize| {
        std::env::var(key).ok().and_then(|value| value.parse().ok()).unwrap_or(default)
    };
    apbase::config.set("n_threads", env_or("APBASE_N_THREADS", 2))?;
    apbase::config.set("grid_max_points_ceiling", env_or("APBASE_GRID_MAX_POINTS", 100_000_000))?;
    Ok(())
}

struct MapResponse {
    method: Method,
    x: Array1<f64>,
    y: Array1<f64>,
    z: Array1<f64>,
    rmse: f64,            // RMSE na LOO-CV do método escolhido
    n_source_points: i64, // pontos mantidos após a filtragem
}

fn build_map_response(
    x: &[f64],
    y: &[f64],
    z: &[f64],
    resolution: f64,
    bounds: Option<Bounds>,
) -> Result<MapResponse, ApbaseError> {
    let result = apbase::create_map(x, y, z, MapOptions {
        bounds,
        max_cv_points: 500,
        max_neighbors: 40,
        seed: Some(42),
        ..MapOptions::new(resolution)
    })?;

    let selected_cv = match result.method {
        Method::Idw => &result.cross_validation.idw,
        Method::Kriging => &result.cross_validation.kriging,
    };
    Ok(MapResponse {
        method: result.method,
        rmse: selected_cv.rmse,
        n_source_points: result.n_source_points,
        x: result.x,
        y: result.y,
        z: result.z,
    })
}
```

:::

::::

Os exemplos definem `n_threads` explicitamente só para usar 2 threads por
padrão em vez de 1. `APBASE_GRID_MAX_POINTS` é uma variável destes exemplos,
não uma que o APbase leia. `seed=42` fixa a amostra da validação cruzada,
então a mesma entrada sempre escolhe o mesmo método.

Em serviços concorrentes, chame `create_map` a cada requisição ou crie uma
instância de `Map` dentro da requisição ou do job. Reaproveitar uma instância
de `Map` é útil em jobs sequenciais, mas ela guarda o último resultado.

## Escolhendo workers e threads

Escolha o número de workers de processo e de threads do OpenMP em conjunto:

```text
process_workers * APBASE_N_THREADS <= vCPU_disponíveis
```

Exemplos:

- contêiner com 2 vCPU: `process_workers=1`, `APBASE_N_THREADS=2`
- contêiner com 4 vCPU: `process_workers=2`, `APBASE_N_THREADS=2`
- job em lote sensível à latência: `process_workers=1`, `APBASE_N_THREADS`
  igual ao número de vCPU alocadas

Evite rodar muitos workers da aplicação, cada um com muitas threads do OpenMP.
Isso sobrecarrega a CPU e costuma deixar a krigagem mais lenta.

## Entradas na fronteira do serviço

- Passe arrays numéricos unidimensionais com as coordenadas x, as coordenadas
  y e os valores dos pontos amostrais.
- Prefira arrays `float64` contíguos na fronteira do serviço, para evitar
  cópias escondidas. Em Rust, `&[f64]` e `Vec<f64>` são usados sem conversão.
- Coordenadas projetadas são usadas diretamente.
- Entrada em longitude/latitude geográficas é aceita; passe `resolution` em
  metros para que as distâncias sejam tratadas corretamente.
- Quando o domínio de interpolação é conhecido, passe o contorno no formato
  aceito pela linguagem. Em Python, pode ser uma geometria Shapely, WKT ou
  WKB. Em Rust, é um `Bounds` criado a partir de uma string WKT, bytes WKB ou
  um `geos::Geometry`.

## Instalar e implantar

O pacote distribuído já inclui as extensões numéricas compiladas. Instale com
`pip` para Python ou `cargo` para Rust; veja {doc}`installation` para os
requisitos. Imagens de aplicação e workers não precisam compilar os kernels
nativos.

::::{tab-set}

:::{tab-item} Python
:sync: python

```bash
python -m pip install apbase
```

:::

:::{tab-item} Rust
:sync: rust

```bash
cargo add apbase
cargo build --release
```

A imagem de execução ainda precisa das bibliotecas compartilhadas do runtime
de Fortran/OpenMP/BLAS, do GEOS e do PROJ.

:::

::::

Depois da instalação:

1. No ambiente do serviço, defina `APBASE_N_THREADS` e as variáveis que o seu
   código de inicialização repassa para `apbase.config` (como os tetos acima).
2. Rode um teste rápido na inicialização que carrega o `apbase`, gera um mapa
   pequeno e verifica se os kernels nativos rodam corretamente.
3. Mantenha o código de API, fila, armazenamento e autenticação na sua
   aplicação; use o APbase como o núcleo geoespacial.

Veja {doc}`quickstart` para a chamada mínima de geração de mapa.
