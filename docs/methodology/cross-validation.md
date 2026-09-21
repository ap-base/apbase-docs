# Cross-validation

`apbase.cross_validate` is the model-selection step behind `apbase.Map`. It
compares IDW and ordinary kriging on the same source data using
**leave-one-out cross-validation** (LOO-CV). The pipeline then uses the method
with the lowest validation error for that dataset.

## Leave-one-out procedure

For each evaluated source point $x_i$:

1. Temporarily remove $x_i$ (and its value $z_i$) from the source set.
2. Re-estimate a value $\hat{z}_i$ at $x_i$'s location using only the
   remaining $n - 1$ points, with the method under evaluation (IDW or
   kriging).
3. Compare $\hat{z}_i$ to the true, held-out $z_i$.

Repeating this for every evaluated point gives prediction errors
$e_i = z_i - \hat{z}_i$. These errors show how well the method may generalize
to a new observation at each location because each point is predicted without
using its own value.

## Error metrics

Given $m$ evaluated points:

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

Both methods use the same fitted variogram, search radius, and spatial index.
Differences in MAE, RMSE, and $R^2$ therefore reflect the interpolation method
rather than a difference in configuration.

## Bounded runtime

Evaluating every source point requires $O(n)$ leave-one-out fits, which can be
expensive for large datasets. `max_points` caps the number of points tested.
If there are more finite points than the limit, APbase draws a random
subsample of size `max_points`, using `seed` when provided. This keeps runtime
bounded as the dataset grows.

`apbase.Map` runs this comparison automatically and interpolates with
whichever method scored the lower RMSE. `apbase.create_map` is the
functional shortcut for the same pipeline.

## Cokriging: three methods in one pass

`cross_validate_cokriging` applies the same leave-one-out procedure to
{doc}`collocated, ICM, and LMC cokriging <cokriging>` together. Only the
**primary** value is held out one point at a time. Each method's
coregionalization model is fitted once from the full dataset and kept fixed
throughout, matching how the model is used in practice. All three methods
share one primary spatial index and one radius, so their results remain
directly comparable.

## Selecting the best of more than two methods

`select_best_model` compares scores on the samples where *every* candidate
method produced a finite prediction. With more than two methods, it first
identifies the winner and runner-up from the point estimates, then uses a
paired bootstrap for that pair. With a plain `cross_validate(...)` result,
which compares IDW and kriging, it keeps the two-method behavior.

A paired bootstrap over the common-valid sample estimates whether the margin
between the winner and runner-up is likely genuine rather than an artifact of
which points were held out. `n_bootstrap` resamples the common-valid indices,
recomputes the score difference for each resample, and sets
`significant=True` when the resulting confidence interval excludes zero.
