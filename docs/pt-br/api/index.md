# Referência da API

A API pública é pequena de propósito. Para criar mapas, comece por
{class}`apbase.Map <apbase.mapping.Map>` ou
{func}`apbase.create_map <apbase.mapping.create_map>`; use
{data}`apbase.config` para as configurações do processo inteiro.

A referência é gerada a partir das docstrings no estilo NumPy. Os módulos
geoestatísticos de nível mais baixo continuam disponíveis para fluxos de
trabalho avançados, mas não são o ponto de partida recomendado para criar
mapas.

## Python

```{toctree}
:maxdepth: 1

mapping
common
```

### Módulos avançados

```{toctree}
:maxdepth: 1

filtering
grid
variogram
idw
kriging
cross_validate
cross-variogram
cokriging
```

## Rust

O crate Rust tem os mesmos módulos e nomes em `apbase::` (por exemplo,
`apbase::Map`, `apbase::create_map` e `apbase::config`). A referência dele é
gerada pelo rustdoc e publicada em
[docs.rs/apbase](https://docs.rs/apbase); rode `cargo doc --open` para gerá-la
localmente.
