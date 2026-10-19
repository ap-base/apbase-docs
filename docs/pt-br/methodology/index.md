# Metodologia

O APbase usa métodos geoestatísticos clássicos no seu pipeline automático de
mapeamento. Você consegue gerar mapas sem ler esta seção. Use-a quando quiser
entender a matemática, ajustar um fluxo avançado ou ver por que um método
venceu o outro.

O pipeline padrão compara o IDW e a krigagem ordinária com validação cruzada
leave-one-out e usa o método com menor RMSE (raiz do erro quadrático médio)
nos dados atuais. A cokrigagem aparece aqui como método avançado, para fluxos
com variáveis secundárias selecionadas.

```{toctree}
:maxdepth: 1

variogram-fitting
idw
kriging
cross-validation
covariate-screening
cokriging
```

## Referências

As entradas da bibliografia trazem DOI, editora ou links estáveis de catálogo
quando disponíveis.

```{bibliography}
:all:
```
