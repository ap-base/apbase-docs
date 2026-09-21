# Variogram fitting

Kriging, IDW, and `SpatialFilter` use a fitted variogram when no `radius` is
provided. A variogram describes how dissimilar values become as the distance
between points increases. `Variogram` builds it in two steps: estimate the
pattern from the data, then fit a theoretical model to that estimate.

## Empirical semivariogram

For every pair of source points $i, j$ separated by distance
$h = d_{ij}$, the squared half-difference $\frac{1}{2}(z_i - z_j)^2$ is a
noisy sample of how dissimilar values tend to be at that separation.
Averaging these over all pairs whose distance falls in a lag bin around
$h$ gives the classical (Matheron) empirical semivariogram estimator
{cite}`Matheron1971,Cressie1993`:

$$
\hat{\gamma}(h) = \frac{1}{2\,|N(h)|} \sum_{(i,j) \in N(h)} \left(z_i - z_j\right)^2
$$

where $N(h)$ is the set of point pairs whose separation falls in the lag
bin centered on $h$. `n_lags` controls how many such bins the pairwise
distance range is divided into; `max_pairs` bounds how many point pairs
are sampled when there are more than that available; `max_distance`
bounds the maximum separation considered.

## Theoretical models

The empirical estimate $\hat\gamma(h)$ is a scatter of noisy points, one per
lag bin, rather than a function that can be evaluated at any distance.
`Variogram` fits three candidate theoretical models to it, each parameterized by a **nugget**
$c_0$ (discontinuity at $h=0$, representing measurement noise or
sub-lag-scale variability), a **partial sill** $c$ (additional variance
contributed by spatial structure), and a **range** $a$ (the distance
beyond which points are treated as spatially uncorrelated). Writing
$r = h / a$:

**Spherical**

$$
\gamma(h) = \begin{cases}
c_0 + c\left(1.5\,r - 0.5\,r^{3}\right) & h < a \\
c_0 + c & h \geq a
\end{cases}
$$

**Exponential**

$$
\gamma(h) = c_0 + c\left(1 - e^{-3r}\right)
$$

**Gaussian**

$$
\gamma(h) = c_0 + c\left(1 - e^{-3r^{2}}\right)
$$

The factor of 3 in the exponential and gaussian models is the *practical
range* convention. It rescales $a$ so the model reaches about 95% of the sill
at $h = a$, matching the spherical model's behavior of reaching the sill
exactly at $h = a$ {cite}`Isaaks1989`. This keeps `range` comparable across
the three models.

## Fitting and model selection

For each candidate model, $c_0$, $c$, and $a$ are chosen to minimize the
(weighted) squared error between the model curve $\gamma(h)$ and the binned
empirical estimate $\hat\gamma(h)$. `Variogram.fit` returns the spherical,
exponential, or gaussian model with the lowest fitting error, so the caller
does not need to choose one first.

`Variogram.evaluate(distances)` returns the fitted model's semivariance at
arbitrary distances. These values feed directly into the
{doc}`kriging linear system <kriging>`.
