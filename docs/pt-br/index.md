# APbase

O APbase transforma dados de campo irregulares, como dados do monitor de
produtividade, amostras de solo e leituras de sensores, em mapas validados. Ele
filtra os pontos amostrais, trata coordenadas geográficas quando necessário,
monta a grade de interpolação, ajusta o semivariograma, compara métodos de
interpolação e fica com o de menor RMSE na validação cruzada. Você recebe um
mapa pronto para uso sem escolher um modelo matemático manualmente.

:::{note}
O trabalho numérico roda em kernels compilados. Com uma `seed` fixa, execuções
repetidas sobre os mesmos dados produzem o mesmo mapa.
:::

::::{tab-set}

:::{tab-item} Python
:sync: python

O pacote Python expõe o pipeline de mapeamento de alto nível por meio de
`apbase.Map` e `apbase.create_map`:

```python
import apbase

result = apbase.Map(resolution=10.0)(x, y, z)

result.method                  # "idw" ou "kriging", o que tiver menor RMSE leave-one-out
result.x, result.y, result.z   # pontos da grade dentro do contorno
```

:::

:::{tab-item} Rust
:sync: rust

O crate Rust `apbase` expõe o mesmo pipeline por meio de `apbase::Map` e
`apbase::create_map`:

```rust
use apbase::{Map, MapOptions};

let result = Map::new(MapOptions::new(10.0)).call(&x, &y, &z)?;

result.method;                      // Method::Idw ou Method::Kriging, o que tiver menor RMSE leave-one-out
(&result.x, &result.y, &result.z);  // pontos da grade dentro do contorno
```

:::

::::

## O que o pipeline resolve

- **Seleção automática do modelo.** O pipeline compara o IDW com a krigagem
  ordinária e usa o método com menor RMSE (raiz do erro quadrático médio) na
  validação cruzada leave-one-out para o conjunto de dados atual.
- **Trabalho numérico eficiente.** Um semivariograma ajustado é reaproveitado
  na escolha do raio, na validação cruzada e na krigagem final, sem repetir
  trabalho.
- **Pronto para serviços e jobs em lote.** A mesma chamada roda sem mudanças em
  um script, um serviço ou um job em lote, sem nenhum runtime extra para
  configurar. Veja {doc}`production`.
- **Funciona com pontos irregulares e com ruído.** Registros inválidos,
  outliers globais e outliers espaciais locais são removidos antes da
  interpolação.
- **Padrões úteis.** Quando nenhum raio de busca é informado, ele é derivado do
  alcance (`range`) do semivariograma ajustado (veja
  {doc}`methodology/variogram-fitting`).

Veja {doc}`quickstart` para um exemplo completo. Use {doc}`user-guide/index` e
{doc}`methodology/index` quando precisar de controle avançado ou quiser
auditar a matemática por trás da escolha automática.

## Conteúdo

```{toctree}
:maxdepth: 2

installation
quickstart
production
user-guide/index
methodology/index
Referência da API <api/index>
```
