# Krigagem ordinária

O `Kriging` implementa a *krigagem ordinária local*. Para cada ponto a
estimar, ele combina os valores amostrais próximos usando a correlação
espacial descrita pelo {doc}`semivariograma <variogram-fitting>` ajustado. Os
pesos dão o **melhor estimador linear não tendencioso** (BLUE) sob esse modelo
{cite}`Matheron1971,Cressie1993,Isaaks1989`.

## Formulação

Dados $n$ pontos amostrais com valores $z_1, \dots, z_n$, a estimativa num
ponto a estimar $x_0$ é uma soma ponderada

$$
\hat{z}(x_0) = \sum_{i=1}^{n} \lambda_i \, z_i
$$

Os pesos $\lambda_i$ são escolhidos para que o estimador seja:

- **Não tendencioso**: $\sum_{i=1}^{n} \lambda_i = 1$. Na krigagem ordinária,
  a média do processo é desconhecida, mas tratada como constante dentro da
  vizinhança local. Essa restrição dá conta dessa média desconhecida.
- **De variância mínima**: entre todos os pesos que satisfazem a restrição de
  não tendenciosidade, os pesos escolhidos minimizam a variância de estimação
  $\operatorname{Var}[\hat{z}(x_0) - z(x_0)]$. Essa variância é escrita em
  função da semivariância $\gamma(h)$, que descreve o quão diferentes os
  valores tendem a ser a uma separação $h$.

## O sistema de krigagem

Minimizar a variância sujeita a uma restrição linear de igualdade é um
problema de multiplicadores de Lagrange. Introduzindo o multiplicador $\mu$
para a restrição de não tendenciosidade e resolvendo as condições de
otimalidade resultantes, chega-se a um sistema linear nos $n$ pesos mais
$\mu$:

$$
\begin{bmatrix}
\gamma(d_{11}) & \cdots & \gamma(d_{1n}) & 1 \\
\vdots & \ddots & \vdots & \vdots \\
\gamma(d_{n1}) & \cdots & \gamma(d_{nn}) & 1 \\
1 & \cdots & 1 & 0
\end{bmatrix}
\begin{bmatrix} \lambda_1 \\ \vdots \\ \lambda_n \\ \mu \end{bmatrix}
=
\begin{bmatrix} \gamma(d_{10}) \\ \vdots \\ \gamma(d_{n0}) \\ 1 \end{bmatrix}
$$

em que $d_{ij}$ é a distância entre os pontos amostrais $i$ e $j$, e $d_{i0}$
é a distância do ponto amostral $i$ ao ponto a estimar $x_0$. A matriz
$(n+1) \times (n+1)$ à esquerda é simétrica. A última linha e a última coluna
(todas com 1 e um zero no canto) impõem $\sum \lambda_i = 1$.

Resolver esse sistema dá os pesos de krigagem $\lambda_i$ e também a
**variância de krigagem**, uma estimativa da incerteza em $x_0$:

$$
\sigma_K^2(x_0) = \sum_{i=1}^{n} \lambda_i \, \gamma(d_{i0}) + \mu
$$

O APbase não calcula nem devolve a variância de krigagem: o
`Kriging.interpolate` devolve só as estimativas.

Diferente dos pesos fixos do IDW, que só decaem com a distância, a krigagem
leva em conta a redundância entre pontos amostrais. Pontos agrupados carregam
informação em parte redundante, então a krigagem lhes dá menos peso somado do
que daria ao mesmo número de pontos espalhados em volta do ponto a estimar a
distâncias parecidas.

## Krigagem local

Resolver o sistema completo com todos os pontos amostrais ficaria caro à
medida que o conjunto de dados cresce. Em vez disso, o `Kriging` monta e
resolve o sistema para cada ponto a estimar usando só os `max_neighbors`
pontos amostrais mais próximos dentro de `radius`, com o mesmo recurso de
`min_neighbors` do {doc}`IDW <idw>`.

## Fornecendo um semivariograma diretamente

`model_values` permite passar um modelo de semivariograma pré-calculado em vez
de ajustar um a partir de `x`/`y`/`z`. Isso é útil quando várias execuções de
interpolação devem compartilhar exatamente o mesmo modelo, como no
`apbase.cross_validate`, que ajusta um semivariograma e o usa para o raio de
busca compartilhado e para o modelo de krigagem.
