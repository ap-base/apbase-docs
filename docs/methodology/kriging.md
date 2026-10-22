# Ordinary kriging

`Kriging` implements *local ordinary kriging*. For each target, it combines
nearby source values using the spatial correlation described by the fitted
{doc}`variogram <variogram-fitting>`. The weights give the **best linear
unbiased estimator** (BLUE) under that model
{cite}`Matheron1971,Cressie1993,Isaaks1989`.

## Setup

Given $n$ source points with values $z_1, \dots, z_n$, the estimate at a
target $x_0$ is a weighted sum

$$
\hat{z}(x_0) = \sum_{i=1}^{n} \lambda_i \, z_i
$$

The weights $\lambda_i$ are chosen so that the estimator is:

- **Unbiased**: $\sum_{i=1}^{n} \lambda_i = 1$. In ordinary kriging, the
  process mean is unknown but treated as constant within the local
  neighborhood. This constraint accounts for that unknown mean.
- **Minimum variance**: among all weights that satisfy the unbiasedness
  constraint, the chosen weights minimize the estimation variance
  $\operatorname{Var}[\hat{z}(x_0) - z(x_0)]$. This variance is written in
  terms of the semivariance $\gamma(h)$, which describes how dissimilar values
  tend to be at separation $h$.

## The kriging system

Minimizing variance subject to a linear equality constraint is a
Lagrange-multiplier problem. Introducing multiplier $\mu$ for the
unbiasedness constraint and solving the resulting stationarity conditions
gives a linear system in the $n$ weights plus $\mu$:

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

where $d_{ij}$ is the distance between source points $i$ and $j$, and
$d_{i0}$ is the distance from source point $i$ to the target $x_0$. The
$(n+1) \times (n+1)$ matrix on the left is symmetric. Its bottom row and
right column (all ones, with a zero corner) enforce $\sum \lambda_i = 1$.

Solving this system gives both the kriging weights $\lambda_i$ and the
**kriging variance**, an estimate of the uncertainty at $x_0$:

$$
\sigma_K^2(x_0) = \sum_{i=1}^{n} \lambda_i \, \gamma(d_{i0}) + \mu
$$

APbase does not compute or return the kriging variance: `Kriging.interpolate`
returns only the estimates.

Unlike IDW's fixed distance-decay weights, kriging accounts for redundancy
between source points. Points clustered together carry partly redundant
information, so kriging gives them less combined weight than the same number
of points spread around the target at similar distances.

## Local kriging

Solving the full system over every source point would become expensive as the
dataset grows. `Kriging` instead builds and solves the system for each target
using only the nearest `max_neighbors` source points within `radius`, with the
same `min_neighbors` fallback as {doc}`IDW <idw>`.

## Supplying a variogram directly

`model_values` lets you pass a precomputed variogram model instead of fitting
one from `x`/`y`/`z`. This is useful when several interpolation runs should
share exactly one model, as in `apbase.cross_validate`, which fits one
variogram and uses it for the shared search radius and the kriging model.
