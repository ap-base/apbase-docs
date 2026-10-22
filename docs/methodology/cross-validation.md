# Cross-validation

`apbase.cross_validate` is the model-selection step behind `apbase.Map`. It
compares IDW and ordinary kriging on the same source data using
**leave-one-out cross-validation** (LOO-CV). `apbase.Map` then interpolates
with whichever method scored the lower RMSE, as decided by
`select_best_model` (see below); ties go to IDW.

## Leave-one-out procedure

For each evaluated source point $x_i$:

1. Temporarily remove $x_i$ (and its value $z_i$) from the source set.
2. Re-estimate a value $\hat{z}_i$ at $x_i$'s location using only the
   remaining $n - 1$ points, with the method under evaluation (IDW or
   kriging).
3. Compare $\hat{z}_i$ to the true, held-out $z_i$.

Repeating this for every evaluated point gives prediction errors
$e_i = z_i - \hat{z}_i$. Because each point is predicted without its own value,
these errors estimate how well the method would predict a new, unseen
observation. The variogram, and with it the kriging model and the default
search radius, is fitted once from all finite points and is not refitted for
each held-out point; only the neighbor search leaves $x_i$ out.

## Error metrics

Given the $m$ evaluated points where the method produced a finite prediction,
with $\bar{z}$ the mean of their true values ($R^2$ is NaN when those values
are all equal):

$$
\mathrm{MAE} = \frac{1}{m}\sum_{i=1}^{m} \left| e_i \right|
\qquad\qquad
\mathrm{RMSE} = \sqrt{\frac{1}{m}\sum_{i=1}^{m} e_i^{2}}
$$

$$
R^2 = 1 - \frac{\displaystyle\sum_{i=1}^{m} e_i^{2}}
{\displaystyle\sum_{i=1}^{m} \left(z_i - \bar{z}\right)^{2}}
$$

RMSE penalizes large individual errors more than MAE, which helps reveal a
method that is usually accurate but occasionally very wrong. $R^2$ expresses
how much of the source data's variance the method explains compared with
always predicting the mean.

## Shared variogram, shared neighborhood

Both methods use the same search radius, spatial index, and neighbors for each
held-out point. The radius comes from the variogram that is also the kriging
model, fitted to all finite points or given through `model_values`; an explicit
`radius` replaces it. Differences in MAE, RMSE, and $R^2$ therefore reflect the
interpolation method rather than a difference in configuration.

## Bounded runtime

Evaluating every source point requires $n$ leave-one-out predictions per
method, each with its own neighbor search and local solve, which can be
expensive for large datasets. `max_points` caps the number of
points tested. If there are more finite points than the limit, APbase draws a
random subsample of size `max_points`, using `seed` when provided. This keeps
runtime bounded as the dataset grows.

## Cokriging: three methods in one pass

`cross_validate_cokriging` applies the same leave-one-out procedure to
{doc}`collocated, ICM, and LMC cokriging <cokriging>` together. Only the
**primary** value is held out one point at a time. Each method's
coregionalization model is fitted once from the full dataset and kept fixed
throughout, matching how the model is used in practice. All three methods
share one primary spatial index and one radius, so their results remain
directly comparable. A method whose model cannot be fitted is left out instead
of failing the comparison: ICM or LMC when the fit is rejected as
non-positive-semidefinite or invalid. A secondary with too few samples paired
with the primary (see `max_colocation_dist` in {doc}`../user-guide/cokriging`)
blocks all three methods, since each needs its correlation with the primary,
so the call raises a `ValueError`. An error is raised only when no method can
be fitted.

## Selecting the best method

`select_best_model` is the step `apbase.Map` uses to pick its method. It
compares scores (RMSE by default) on the samples where *every* candidate
method produced a finite prediction, and the lower score wins; a tie between
IDW and kriging goes to IDW. Given a plain `cross_validate(...)` result, it
compares IDW against kriging directly and returns the two-method result type.
Given any mapping of two or more methods, such as `cv.by_method` from
cokriging, it first identifies the winner and runner-up from the point
estimates (a tie goes to the method listed first), then uses a paired
bootstrap for that pair.

The paired bootstrap estimates whether the margin between the winner and
runner-up is likely genuine rather than an artifact of which points were held
out. `n_bootstrap` resamples those common samples, recomputes the score
difference for each resample, and sets `significant=True` when the resulting
confidence interval excludes zero.
