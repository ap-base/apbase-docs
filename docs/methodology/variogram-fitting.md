# Variogram fitting

Kriging always uses a fitted variogram. The other estimators use one to derive
the search radius when no `radius` is provided (see below). A variogram
describes how dissimilar values become as the distance between points
increases.
`Variogram` builds it in two steps: estimate the pattern from the data, then
fit a theoretical model to that estimate.

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
bin centered on $h$. Three parameters control the estimate:

- `n_lags`: the number of bins the pairwise distance range is divided into.
- `max_pairs`: the maximum number of point pairs sampled when more are
  available.
- `max_distance`: the maximum separation considered.

## Theoretical models

The empirical estimate $\hat\gamma(h)$ is a scatter of noisy points, one per
lag bin, rather than a function that can be evaluated at any distance.
`Variogram` fits three candidate theoretical models to it, each parameterized
by a **nugget** $c_0$ (discontinuity at $h=0$, representing measurement noise
or variability at scales shorter than the smallest lag), a **partial sill**
$c$ (additional variance contributed by spatial structure), and a **range**
$a$ (the distance beyond which points are treated as spatially uncorrelated).
Writing $r = h / a$:

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

The factor of 3 in the exponential and Gaussian models is the *practical
range* convention. It rescales $a$ so the model reaches about 95% of the sill
at $h = a$, matching the spherical model's behavior of reaching the sill
exactly at $h = a$ {cite}`Isaaks1989`. This keeps `range` comparable across
the three models.

## Fitting and model selection

For each candidate model, $c_0$, $c$, and $a$ are chosen by weighted least
squares between the model curve $\gamma(h)$ and the binned empirical estimate
$\hat\gamma(h)$, with Cressie's weights {cite}`Cressie1993`:

$$
w(h) = \frac{|N(h)|}{\gamma(h)^2}
$$

Each bin counts in proportion to its number of pairs, but relative to the
model's own value there, so the short lags that determine the nugget are not
swamped by the long lags, which hold most of the pairs. Because the weights
depend on the model, the fit starts from pair-count weights and is refined
over three reweighting passes. A negative nugget is clamped to 0 and the
partial sill is refitted with that constraint.

`Variogram.fit` returns the spherical, exponential, or Gaussian model with
the lowest weighted fitting error, so the caller does not need to choose one
first. The cross-variogram, ICM, and LMC fits use the same weights.

`Variogram.evaluate(distance)` returns the fitted model's semivariance at
arbitrary distances. These values feed directly into the
{doc}`kriging linear system <kriging>`.

## Deriving the search radius

When `radius` is omitted, APbase derives it from the fitted model's `range`:

- below 10,000 source points, the radius is the full `range`;
- from 10,000 points up, it is `range / 3`.

`Map`, `IDW`, `Kriging`, `cross_validate`, `CoKriging`, and
`cross_validate_cokriging` use this rule; cokriging applies it to the primary
variogram. `SpatialFilter` always uses `range / 3`. The rule is available as
`apbase.variogram.search_radius(model_params, n_points)` in Python and as the
`search_radius(n_points)` method of a Rust `ModelParams`.
