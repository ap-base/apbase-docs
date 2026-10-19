# Ajuste do semivariograma

A krigagem sempre usa um semivariograma ajustado. Os outros estimadores usam
um para derivar o raio de busca quando `radius` não é informado (veja
abaixo). O semivariograma descreve o quanto os valores ficam diferentes à
medida que a distância entre os pontos aumenta. O `Variogram` o constrói em
duas etapas: estima o padrão a partir dos dados e depois ajusta um modelo
teórico a essa estimativa.

## Semivariograma experimental

Para cada par de pontos amostrais $i, j$ separados pela distância
$h = d_{ij}$, a metade da diferença ao quadrado $\frac{1}{2}(z_i - z_j)^2$ é
uma amostra ruidosa do quão diferentes os valores tendem a ser naquela
separação. A média desses valores sobre todos os pares cuja distância cai
numa classe de distância em torno de $h$ dá o estimador clássico (de
Matheron) do semivariograma experimental {cite}`Matheron1971,Cressie1993`:

$$
\hat{\gamma}(h) = \frac{1}{2\,|N(h)|} \sum_{(i,j) \in N(h)} \left(z_i - z_j\right)^2
$$

em que $N(h)$ é o conjunto de pares de pontos cuja separação cai na classe de
distância centrada em $h$. Três parâmetros controlam a estimativa:

- `n_lags`: o número de classes em que a faixa de distâncias entre pares é
  dividida.
- `max_pairs`: o número máximo de pares de pontos amostrados quando há mais
  disponíveis.
- `max_distance`: a separação máxima considerada.

## Modelos teóricos

A estimativa experimental $\hat\gamma(h)$ é uma nuvem de pontos com ruído, um
por classe de distância, e não uma função que possa ser avaliada em qualquer
distância. O `Variogram` ajusta a ela três modelos teóricos candidatos, cada
um definido por um **efeito pepita** $c_0$ (descontinuidade em $h=0$, que
representa o erro de medição ou a variabilidade em escalas menores que o menor
lag, a menor distância de separação), uma **contribuição** $c$ (variância
adicional devida à estrutura espacial) e um **alcance** $a$ (a distância a
partir da qual os pontos são tratados como sem correlação espacial).
Escrevendo $r = h / a$:

**Esférico**

$$
\gamma(h) = \begin{cases}
c_0 + c\left(1.5\,r - 0.5\,r^{3}\right) & h < a \\
c_0 + c & h \geq a
\end{cases}
$$

**Exponencial**

$$
\gamma(h) = c_0 + c\left(1 - e^{-3r}\right)
$$

**Gaussiano**

$$
\gamma(h) = c_0 + c\left(1 - e^{-3r^{2}}\right)
$$

O fator 3 nos modelos exponencial e gaussiano é a convenção do *alcance
prático*. Ele reescala $a$ para que o modelo atinja cerca de 95% do patamar em
$h = a$, igualando o comportamento do modelo esférico, que atinge o patamar
exatamente em $h = a$ {cite}`Isaaks1989`. Assim o `range` (alcance) fica
comparável entre os três modelos.

## Ajuste e seleção do modelo

Para cada modelo candidato, $c_0$, $c$ e $a$ são escolhidos por mínimos
quadrados ponderados entre a curva do modelo $\gamma(h)$ e a estimativa
experimental por classes $\hat\gamma(h)$, com os pesos de Cressie
{cite}`Cressie1993`:

$$
w(h) = \frac{|N(h)|}{\gamma(h)^2}
$$

Cada classe conta na proporção do seu número de pares, mas em relação ao
próprio valor do modelo ali, então os lags curtos, que determinam o efeito
pepita, não são abafados pelos lags longos, que concentram a maioria dos
pares. Como os pesos dependem do modelo, o ajuste começa com pesos pelo número
de pares e é refinado em três passadas de reponderação. Um efeito pepita
negativo é fixado em 0, e a contribuição é reajustada com essa restrição.

O `Variogram.fit` devolve o modelo esférico, exponencial ou gaussiano com o
menor erro de ajuste ponderado, então quem chama não precisa escolher um
antes. Os ajustes do semivariograma cruzado, do ICM e do LMC usam os mesmos
pesos.

`Variogram.evaluate(distance)` devolve a semivariância do modelo ajustado em
distâncias quaisquer. Esses valores entram diretamente no
{doc}`sistema linear da krigagem <kriging>`.

## Derivando o raio de busca

Quando `radius` é omitido, o APbase o deriva do alcance (`range`) do modelo
ajustado:

- abaixo de 10.000 pontos amostrais, o raio é o `range` inteiro;
- a partir de 10.000 pontos, é `range / 3`.

`Map`, `IDW`, `Kriging`, `cross_validate`, `CoKriging` e
`cross_validate_cokriging` usam essa regra; a cokrigagem a aplica ao
semivariograma da variável primária. O `SpatialFilter` sempre usa
`range / 3`. A regra está disponível como
`apbase.variogram.search_radius(model_params, n_points)` em Python e como o
método `search_radius(n_points)` de um `ModelParams` em Rust.
