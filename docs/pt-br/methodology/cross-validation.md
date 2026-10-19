# Validação cruzada

O `apbase.cross_validate` é a etapa de seleção do modelo por trás do
`apbase.Map`. Ele compara o IDW e a krigagem ordinária sobre os mesmos dados
amostrais usando **validação cruzada leave-one-out** (LOO-CV). O
`apbase.Map` então interpola com o método que obteve o menor RMSE (raiz do
erro quadrático médio), conforme decidido por `select_best_model` (veja
abaixo); em caso de empate, vence o IDW.

## Procedimento leave-one-out

Para cada ponto amostral avaliado $x_i$:

1. Retire temporariamente $x_i$ (e o seu valor $z_i$) do conjunto amostral.
2. Estime de novo um valor $\hat{z}_i$ na posição de $x_i$ usando só os
   $n - 1$ pontos restantes, com o método em avaliação (IDW ou krigagem).
3. Compare $\hat{z}_i$ com o valor verdadeiro $z_i$ que foi retirado.

Repetir isso para cada ponto avaliado gera os erros de predição
$e_i = z_i - \hat{z}_i$. Como cada ponto é predito sem o próprio valor, esses
erros estimam o quão bem o método prediria uma observação nova, ainda não
vista.

## Métricas de erro

Dados $m$ pontos avaliados:

$$
\mathrm{MAE} = \frac{1}{m}\sum_{i=1}^{m} \left| e_i \right|
\qquad\qquad
\mathrm{RMSE} = \sqrt{\frac{1}{m}\sum_{i=1}^{m} e_i^{2}}
$$

$$
R^2 = 1 - \frac{\displaystyle\sum_{i=1}^{m} e_i^{2}}
{\displaystyle\sum_{i=1}^{m} \left(z_i - \bar{z}\right)^{2}}
$$

O RMSE penaliza erros individuais grandes mais do que o MAE (erro absoluto
médio), o que ajuda a revelar um método que costuma acertar mas de vez em
quando erra muito. O $R^2$ (coeficiente de determinação) expressa quanto da
variância dos dados amostrais o método explica, em comparação com sempre
prever a média.

## Semivariograma e vizinhança compartilhados

Os dois métodos usam o mesmo raio de busca e o mesmo índice espacial. O raio
vem de um único semivariograma ajustado, que também é o modelo da krigagem.
Por isso, as diferenças de MAE, RMSE e $R^2$ refletem o método de
interpolação, e não uma diferença de configuração.

## Tempo de execução limitado

Avaliar todos os pontos amostrais exige $n$ ajustes leave-one-out, um por
ponto, o que pode sair caro em conjuntos de dados grandes. `max_points` limita
o número de pontos testados. Se houver mais pontos finitos do que o limite, o
APbase sorteia uma subamostra aleatória de tamanho `max_points`, usando `seed`
quando informada. Isso mantém o tempo de execução limitado à medida que o
conjunto de dados cresce.

## Cokrigagem: três métodos numa passada

`cross_validate_cokriging` aplica o mesmo procedimento leave-one-out à
{doc}`cokrigagem colocalizada, ICM e LMC <cokriging>` ao mesmo tempo. Só o
valor **primário** é retirado, um ponto por vez. O modelo de corregionalização
de cada método é ajustado uma vez com o conjunto de dados completo e mantido
fixo durante todo o processo, do mesmo jeito que o modelo é usado na prática.
Os três métodos compartilham um índice espacial primário e um raio, então os
resultados continuam diretamente comparáveis. Um método cujo modelo não pode
ser ajustado fica de fora em vez de interromper a comparação: a cokrigagem
colocalizada, quando uma variável secundária tem poucas amostras nos locais da
primária para estimar a sua correlação; e o ICM ou o LMC, quando o ajuste é
rejeitado por não ser semidefinido positivo ou por ser inválido. Só é gerado
um erro quando nenhum método pode ser ajustado.

## Selecionando o melhor método

`select_best_model` é a etapa que o `apbase.Map` usa para escolher o método.
Ela compara as métricas (o RMSE, por padrão) nas amostras em que *todos* os
métodos candidatos produziram uma predição finita, e vence a menor; um empate
entre IDW e krigagem fica com o IDW. Com o resultado de um
`cross_validate(...)` simples, ela compara o IDW diretamente com a krigagem e
devolve o tipo de resultado de dois métodos. Com mais de dois métodos, como o
`cv.by_method` da cokrigagem, ela primeiro identifica o vencedor e o segundo
colocado pelas estimativas pontuais e depois usa um bootstrap pareado para
esse par.

O bootstrap pareado estima se a vantagem do vencedor sobre o segundo colocado
é provavelmente real, e não um efeito de quais pontos foram retirados.
`n_bootstrap` reamostra essas amostras em comum, recalcula a diferença das
métricas em cada reamostragem e define `significant=True` quando o intervalo
de confiança resultante não inclui zero.
