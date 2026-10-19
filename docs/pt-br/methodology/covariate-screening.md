# Seleção de variáveis secundárias

A cokrigagem só ajuda quando uma variável secundária (uma covariável) tem
relação relevante com a primária e produz um semivariograma cruzado válido.
Uma variável secundária sem relação, ou fraca, acrescenta ruído em vez de
informação útil. `screen_secondary_variables` testa cada candidata antes que
ela chegue à {doc}`cokrigagem <cokriging>`, para que as variáveis
selecionadas se apoiem em evidência, e não em intuição.

## Dois testes independentes por candidata

Cada candidata precisa passar em duas verificações independentes:

**1. Correlação significativa e relevante na prática.** A correlação de
Pearson $\rho$ entre a primária e a candidata, calculada sobre as amostras
pareadas (veja a regra de pareamento abaixo), é testada contra zero com a
transformação $z$ de Fisher {cite}`Fisher1921`:

$$
z = \operatorname{artanh}(\rho) = \frac{1}{2}\ln\frac{1+\rho}{1-\rho}
\qquad\qquad
\mathrm{SE}(z) = \frac{1}{\sqrt{n_{\text{pairs}} - 3}}
$$

o que dá um $p$-valor bilateral para $H_0: \rho = 0$. Uma candidata é
rejeitada se o teste não for significativo ao nível `alpha`, ou se $|\rho|$
ficar abaixo de `min_abs_rho` mesmo sendo significativo. Uma amostra grande
pode tornar estatisticamente significativa uma correlação minúscula, então
importam tanto a significância quanto a força na prática.

Quando há várias candidatas, `correction="bonferroni"` (o padrão) divide
`alpha` pelo número de candidatas antes de testar cada uma. Isso controla a
taxa de falsos positivos no lote inteiro.

**2. Semivariograma cruzado admissível.** A relação entre a primária e a
candidata também precisa formar um componente válido de corregionalização, e
não apenas mostrar correlação no lag 0. O APbase verifica o limite de
Cauchy–Schwarz que toda covariância cruzada válida precisa satisfazer em cada
lag {cite}`Journel1978,Myers1982`:

$$
\left|\gamma_{0u}(h)\right| \leq \sqrt{\gamma_{00}(h) \, \gamma_{uu}(h)}
$$

em que $\gamma_{00}$ e $\gamma_{uu}$ são os
{doc}`semivariogramas <variogram-fitting>` da primária e da candidata, e
$\gamma_{0u}$ é o {class}`~apbase.cross_variogram.CrossVariogram` ajustado
entre elas. O APbase avalia o limite em 200 lags igualmente espaçados, de 0 a
três vezes o maior dos três alcances ajustados, permitindo que
$|\gamma_{0u}(h)|$ passe do lado direito em até 10%. Os três semivariogramas
são ajustados de forma independente, então uma variável secundária quase
colinear pode passar do limite exato em alguns por cento só pelo ruído do
ajuste. Uma candidata é rejeitada quando mais de `max_violation_fraction`
dessas avaliações violam o limite. Isso pega um semivariograma cruzado
inadmissível antes que ele corrompa o sistema de cokrigagem.

## O semivariograma cruzado

O `CrossVariogram` generaliza o estimador do semivariograma experimental para
duas variáveis diferentes $a$ e $b$. Em vez de elevar ao quadrado o incremento
de uma variável, ele multiplica os incrementos das duas sobre os pares
$(i, j) \in N(h)$, em que cada ponto tem um valor de cada variável (veja a
regra de pareamento abaixo):

$$
\hat{\gamma}_{ab}(h) = \frac{1}{2\,|N(h)|}
\sum_{(i,j) \in N(h)} \left(a_i - a_j\right)\left(b_i - b_j\right)
$$

Quando $a = b$, ele se reduz ao estimador do semivariograma comum. Diferente
de um semivariograma direto, aqui `nugget` (efeito pepita) e `partial_sill`
(contribuição) podem ser negativos. Um semivariograma cruzado não precisa ser,
sozinho, uma covariância direta válida; a verificação de Cauchy–Schwarz acima
confere se ele pode ser usado com segurança.

O `CrossVariogram` é simétrico e aceita dados heterotópicos: `a` e `b` não
precisam compartilhar os locais de amostragem. O ajuste pareia as duas
variáveis por vizinho mais próximo. `max_colocation_dist` limita a distância
máxima de um par; `None` exige coincidência exata. O mesmo componente é
reaproveitado para cada par de variáveis nos ajustes de corregionalização do
ICM e do LMC.

## Usando o resultado

::::{tab-set}

:::{tab-item} Python
:sync: python

```python
from apbase.cross_variogram import screen_secondary_variables

result = screen_secondary_variables(
    x0, y0, z0,
    {"ndvi": (xn, yn, zn), "ec": (xe, ye, ze)},
    max_colocation_dist=30.0,
)
result.selected   # {"ndvi": (xn, yn, zn)}: só as candidatas que passam nos dois testes
result.report     # CovariateReport de cada candidata: rho, p_value, n_pairs, decision, status, ...
```

:::

::::

`result.selected` já tem o formato esperado pelo
{class}`~apbase.cokriging.CoKriging`, então passe direto para
`CoKriging(...).fit(x0, y0, z0, secondaries=result.selected)`. Uma candidata
com poucos dados (menos de quatro amostras pareadas) ou com um modelo ajustado
inválido fica registrada em `report` com `decision=False` e o motivo em
`status`. Uma candidata inutilizável não interrompe o resto do lote de
seleção.
