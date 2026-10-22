# Cokrigagem

O `CoKriging` estende a {doc}`krigagem ordinária <kriging>` acrescentando uma
ou mais variáveis secundárias relacionadas à primária. Por exemplo, uma
superfície densa de NDVI ou de condutividade elétrica (CE) do solo pode ajudar
a estimar amostras esparsas de produtividade quando essa relação é real e
admissível {cite}`Myers1982,Goovaerts1997,Wackernagel2003,ChilesDelfiner2012`.
Rode antes a {doc}`seleção de variáveis secundárias <covariate-screening>`: o
`CoKriging` não testa as próprias entradas, e uma variável secundária sem
relação ou inadmissível piora a estimativa em vez de melhorá-la.

Este é um método avançado, fora do caminho padrão do `apbase.Map`, que escolhe
entre IDW e krigagem ordinária. Antes de confiar na cokrigagem, compare o seu
resultado com uma krigagem sem variáveis secundárias como referência.

## Estimador e restrição

Dada uma variável primária $Z_0$ e $K$ secundárias $Z_1, \dots, Z_K$, a
estimativa num ponto a estimar $x_0$ reúne contribuições ponderadas da
vizinhança local de *cada* variável:

$$
\hat{Z}_0(x_0) = \sum_{u=0}^{K} \sum_{i=1}^{n_u} \lambda_{u,i} \, Z_u(x_{u,i})
$$

em que $n_u$ é o número de vizinhos da própria variável $u$: vizinhos
primários para $u=0$ e vizinhos da secundária $u$ para $u \geq 1$. Os três
métodos abaixo usam uma única **restrição global de não tendenciosidade**,
$\sum_{u,i} \lambda_{u,i} = 1$ (cokrigagem ordinária padronizada), em vez de
uma restrição por variável. Uma restrição única mantém o sistema solúvel
quando os pesos combinam variáveis com unidades diferentes e vizinhanças
locais diferentes.

Cada variável secundária é reescalada para a média e a variância da primária
antes do ajuste ou da interpolação:

$$
Z_u'(x) = \bar{Z}_0 + \left(Z_u(x) - \bar{Z}_u\right)\frac{\sigma_0}{\sigma_u}
$$

Isso mantém a restrição compartilhada com sentido mesmo quando as variáveis
secundárias usam unidades diferentes. As equações abaixo assumem que as
variáveis já foram padronizadas desse jeito.

## O sistema em blocos (ICM e LMC)

No **ICM** e no **LMC**, cada variável busca na sua própria vizinhança local
dentro de `radius`: a primária até `max_neighbors`, cada variável secundária
até `max_secondary_neighbors` (`max_neighbors` quando não é definido). A busca
não exige que as variáveis secundárias compartilhem os locais de amostragem da
primária, mas o ajuste das covariâncias cruzadas precisa de pares para cada
par de variáveis, inclusive entre variáveis secundárias: amostras associadas a
um ponto da outra variável nas mesmas coordenadas ou, com
`max_colocation_dist`, ao mais próximo dentro dessa distância. Uma variável
secundária com menos de dois pares com a primária gera um `ValueError`; um par
de variáveis cujos pares preenchem menos de três classes de distância faz o
ajuste gerar `CoKrigingInvalidModelError`. Escrevendo
$C_{uv}(h)$ para a covariância cruzada ajustada entre as variáveis $u$ e $v$
na separação $h$, os pesos e o multiplicador de Lagrange $\mu$ resolvem

$$
\begin{bmatrix}
\mathbf{C}_{00} & \mathbf{C}_{01} & \cdots & \mathbf{C}_{0K} & \mathbf{1} \\
\mathbf{C}_{10} & \mathbf{C}_{11} & \cdots & \mathbf{C}_{1K} & \mathbf{1} \\
\vdots & & \ddots & & \vdots \\
\mathbf{C}_{K0} & \mathbf{C}_{K1} & \cdots & \mathbf{C}_{KK} & \mathbf{1} \\
\mathbf{1}^\top & \mathbf{1}^\top & \cdots & \mathbf{1}^\top & 0
\end{bmatrix}
\begin{bmatrix} \boldsymbol\lambda_0 \\ \boldsymbol\lambda_1 \\ \vdots \\ \boldsymbol\lambda_K \\ \mu \end{bmatrix}
=
\begin{bmatrix} \mathbf{c}_0 \\ \mathbf{c}_1 \\ \vdots \\ \mathbf{c}_K \\ 1 \end{bmatrix}
$$

em que o bloco $\mathbf{C}_{uv}$ guarda $C_{uv}(d_{ij})$ entre os vizinhos da
variável $u$ e os da variável $v$, e $\mathbf{c}_u$ guarda $C_{0u}(d_{i0})$
dos vizinhos da variável $u$ até o ponto a estimar. Isso dá um sistema linear
de tamanho $(n_0 + \cdots + n_K + 1)$ por ponto a estimar, estendendo o
sistema de krigagem de uma variável para $K+1$ variáveis.

ICM e LMC diferem só na forma como $C_{uv}(h)$ é construída a partir do modelo
ajustado:

**ICM (modelo de corregionalização intrínseca).** O ICM usa uma única forma
compartilhada (modelo e alcance), ajustada em conjunto sobre todos os
$(K+1)(K+2)/2$ pares de variáveis (cada semivariograma direto e cada
semivariograma cruzado), escalada em cada par por duas matrizes
$(K+1)\times(K+1)$: uma matriz de efeito pepita $\mathbf{B}_0$ e uma matriz de
contribuição $\mathbf{B}_1$:

$$
C_{uv}(h) = \begin{cases}
\left(\mathbf{B}_0\right)_{uv} + \left(\mathbf{B}_1\right)_{uv} & h = 0 \\
\left(\mathbf{B}_1\right)_{uv} \left(1 - g(h)\right) & h > 0
\end{cases}
$$

com $g$ a função de forma compartilhada (esférica, exponencial ou gaussiana,
escolhida como no {doc}`Variogram <variogram-fitting>`, mas pelo erro total
de ajuste somado sobre todos os pares).

$\mathbf{B}_0$ e $\mathbf{B}_1$ são ajustadas de forma independente em cada
par por mínimos quadrados ponderados em forma fechada, com os mesmos pesos de
Cressie do {doc}`Variogram <variogram-fitting>`. Depois, cada matriz é
verificada quanto à semidefinição positiva (PSD) com uma tentativa de
decomposição de Cholesky. Uma violação maior que 10% do maior patamar total
significa que as estruturas espaciais das variáveis não cabem numa única forma
compartilhada, e o ajuste gera `CoKrigingNonPSDCoregionalizationError`. Uma
violação menor, como em variáveis quase colineares cujos patamares ajustados
implicam uma correlação um pouco acima de 1, é tratada como ruído do ajuste:
a matriz é projetada no cone das matrizes semidefinidas positivas (autovalores
negativos fixados em 0) antes de ser usada, então o sistema de cokrigagem
nunca recebe uma matriz indefinida.

As duas matrizes são verificadas, não só a do patamar. O efeito pepita
acrescenta o seu próprio componente de covariância em $h=0$, como a estrutura
de efeito pepita do LMC abaixo. Uma matriz de efeito pepita que não é PSD
introduz um autovalor negativo no sistema em blocos, do mesmo jeito que uma
matriz de patamar ruim. Isso importa na prática porque ajustes independentes
por par costumam produzir uma diagonal de efeito pepita perto de zero em
dados com pouco ruído.

**LMC (modelo linear de corregionalização completo).** O LMC usa $S$
estruturas aninhadas (índice $0$ = efeito pepita, $1, \dots, S{-}1$
contínuas), cada uma com a sua própria matriz de coeficientes
$(K+1)\times(K+1)$ $\mathbf{B}^{(l)}$. As estruturas contínuas compartilham uma
forma (esférica, exponencial ou gaussiana, escolhida como no ICM) com alcances
igualmente espaçados $a\,l/(S{-}1)$, em que $a$ é o alcance compartilhado da
mesma busca conjunta do ICM, então a última estrutura tem alcance $a$:

$$
C_{uv}(h) = \begin{cases}
\sum_{l=0}^{S-1} \left(\mathbf{B}^{(l)}\right)_{uv} & h = 0 \\
\sum_{l=1}^{S-1} \left(\mathbf{B}^{(l)}\right)_{uv} \left(1 - g_l(h)\right) & h > 0
\end{cases}
$$

Todas as estruturas contribuem em $h=0$; para $h>0$ só as estruturas contínuas
($l \geq 1$) contribuem, cada uma atenuada pela sua própria $g_l$.

Os coeficientes são ajustados com o algoritmo de Goulard e Voltz (1992)
{cite}`Goulard1992`, uma descida por coordenadas em blocos. Os seus pesos são
pesos de Cressie calculados uma vez por par a partir de um ajuste com efeito
pepita mais uma estrutura e mantidos fixos durante a descida. Cada passo
atualiza uma estrutura por mínimos quadrados ponderados em forma fechada,
mantendo as outras fixas, e depois projeta a sua matriz no cone das matrizes
semidefinidas positivas: autovalores negativos são fixados em 0 e a matriz é
reconstruída. Diferente do ICM, a semidefinição positiva é, portanto,
garantida por construção a cada varredura, em vez de verificada depois do
ajuste. Em comparação com o ICM, o LMC divide a estrutura única compartilhada
em $S{-}1$ estruturas contínuas da mesma forma com alcances diferentes, cada
uma com a sua própria matriz de coeficientes, ao custo de um ajuste iterativo
mais pesado.

Com a forma gaussiana, o ICM e o LMC dão a cada variável, e a cokrigagem
colocalizada dá à primária, um efeito pepita de pelo menos 0,01% do seu patamar
ao montar o sistema (também na validação cruzada). Sem efeito pepita, um modelo
gaussiano sobre pontos amostrais próximos, como os pixels de um raster, deixa o
sistema singular ou com pesos explosivos. `model_params` continua mostrando os
valores ajustados.

## Cokrigagem colocalizada (MM1)

A **cokrigagem colocalizada** (Modelo de Markov 1)
{cite}`Xu1992,Journel1999` usa a vizinhança da variável primária mais um dado
*colocalizado* de cada variável secundária: o valor secundário no ponto a
estimar, ou o mais próximo dele dentro de `radius`. Ela não usa uma vizinhança
secundária completa. Sob a hipótese do Modelo de Markov 1, o valor secundário
colocalizado torna redundantes os dados secundários mais distantes: a
variável secundária informa a primária pela localização em comum, e não pela
sua própria estrutura espacial, então a covariância cruzada se reduz a um
múltiplo fixo da covariância da própria primária:

$$
C_{0u}(h) = \rho_u \, C_{00}(h) \qquad\qquad
C_{uv}(0) = \rho_u \rho_v \, C_{00}(0) \; (u \neq v;\ u, v \geq 1)
$$

e $C_{uu}(0) = C_{00}(0)$, já que cada variável secundária padronizada tem a
variância da primária.

em que $\rho_u$ é a correlação entre a primária e a secundária obtida pelo
{class}`~apbase.cross_variogram.CrossVariogram`. O sistema passa a ter uma
linha por vizinho primário, uma por variável secundária com um ponto dentro de
`radius` e uma linha de restrição, o que é bem menor que o sistema em blocos
completo do ICM/LMC.

A troca tem dois lados. O valor colocalizado é o ponto da variável secundária
mais próximo dentro de `radius`, usado como se estivesse no ponto a estimar.
Uma variável secundária sem nenhum ponto dentro de `radius` fica fora do
sistema desse ponto e, se não sobrar nenhuma, o ponto recebe a krigagem
ordinária da primária; por isso, convém interpolar antes uma variável
secundária esparsa num conjunto de pontos mais denso. E o resultado só é tão
bom quanto a própria hipótese MM1.

## Escolhendo um método

| | Secundárias precisam de busca local própria | Tamanho do sistema por ponto a estimar | Ajuste da corregionalização |
|---|---|---|---|
| Colocalizada | Não: um valor colocalizado no ponto a estimar | vizinhos primários + até $K$ + 1 | $\rho_u$ em forma fechada por secundária |
| ICM | Sim | $\sum_u n_u$ + 1 | uma forma compartilhada, ajuste conjunto dos pares |
| LMC | Sim | $\sum_u n_u$ + 1 | $S$ estruturas de uma só forma, iterativo de Goulard e Voltz |

A colocalizada é a opção mais barata quando as trocas acima são aceitáveis. O
ICM capta a estrutura secundária com vários pontos usando uma única estrutura
compartilhada. O LMC acrescenta estruturas com vários alcances, cada uma com a
sua própria matriz de coeficientes, quando uma só não basta, com um custo de
ajuste maior.

## Parâmetros locais

Assim como no {class}`~apbase.kriging.Kriging`, `radius`, `max_neighbors` e o
recurso de `min_neighbors` limitam cada busca local; o recurso é aplicado aos
pontos primários. O ICM e o LMC buscam cada variável de forma independente,
com `max_secondary_neighbors` (padrão `max_neighbors`) limitando cada variável
secundária, então uma variável secundária esparsa e uma primária densa podem
usar vizinhanças diferentes no mesmo ponto a estimar.
