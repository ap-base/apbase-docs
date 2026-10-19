# Inverso da distância ponderada (IDW)

O `IDW` implementa o método do inverso da distância ponderada de Shepard
{cite}`Shepard1968`. Ele estima o valor num ponto a estimar como uma média
ponderada dos valores conhecidos próximos, dando mais influência aos pontos
mais perto.

## Fórmula de ponderação

Para um ponto a estimar $x_0$ e $n$ pontos amostrais conhecidos, com valores
$z_1, \dots, z_n$ a distâncias $d_1, \dots, d_n$ de $x_0$, o peso de cada
ponto é

$$
w_i = \frac{1}{d_i^{p}}
$$

em que $p$ é o parâmetro `power` (potência). A estimativa em $x_0$ é a média
ponderada

$$
\hat{z}(x_0) = \frac{\displaystyle\sum_{i=1}^{n} w_i \, z_i}{\displaystyle\sum_{i=1}^{n} w_i}
$$

Se $x_0$ coincide exatamente com um ponto amostral ($d_i = 0$), o valor desse
ponto é devolvido diretamente (a fórmula do peso não é definida em distância
zero).

## Efeito de `power`

- **`power` maior** concentra o peso nos pontos mais próximos; a superfície
  fica mais parecida com uma atribuição ao vizinho mais próximo, ao estilo de
  Voronoi, com mais "olhos de boi" visíveis em volta dos pontos amostrais.
- **`power` menor** distribui a influência de forma mais uniforme entre todos
  os vizinhos dentro do raio, gerando uma superfície mais suave.
- `power=2.0` (inverso do quadrado da distância) é o padrão convencional e um
  ponto de partida razoável para a maioria dos atributos amostrados por
  pontos.

## Vizinhança local, não o conjunto de dados inteiro

O `IDW` do APbase é *local*: a soma usa só os `max_neighbors` pontos amostrais
mais próximos dentro de `radius` em torno de $x_0$, não todos os pontos do
conjunto de dados. Quando menos de `min_neighbors` pontos caem dentro de
`radius`, o ponto a estimar usa os `max_neighbors` pontos mais próximos,
qualquer que seja a distância, então áreas esparsas também recebem uma
estimativa. Isso mantém o custo limitado por ponto a estimar e as estimativas
presas à informação disponível mais próxima.

## Quando `radius` não é informado

Se `radius` for omitido, o APbase ajusta um
{doc}`semivariograma <variogram-fitting>` aos dados amostrais e deriva o raio
do seu alcance (`range`), como descrito no fim daquela página.
