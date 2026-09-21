# Inverse distance weighting

`IDW` implements Shepard's inverse distance weighting method
{cite}`Shepard1968`. It estimates a target value as a weighted average of
nearby known values, giving closer points more influence.

## Weighting formula

For a target location $x_0$ and $n$ known source points with values
$z_1, \dots, z_n$ at distances $d_1, \dots, d_n$ from $x_0$, each point's
weight is

$$
w_i = \frac{1}{d_i^{p}}
$$

where $p$ is the `power` parameter. The estimate at $x_0$ is the
weighted average

$$
\hat{z}(x_0) = \frac{\displaystyle\sum_{i=1}^{n} w_i \, z_i}{\displaystyle\sum_{i=1}^{n} w_i}
$$

If $x_0$ coincides exactly with a source point ($d_i = 0$), that point's
value is returned directly (the weight formula is undefined at zero
distance).

## Effect of `power`

- **Higher `power`** concentrates weight on the very nearest points --
  the surface becomes closer to a Voronoi-style nearest-neighbor
  assignment, with more visible "bullseyes" around source points.
- **Lower `power`** spreads influence more evenly across all neighbors in
  range, producing a smoother surface.
- `power=2.0` (inverse-square) is the conventional default and a
  reasonable starting point for most point-sampled fields.

## Local neighborhood, not the whole dataset

`IDW` in APbase is *local*: the sum uses only the nearest `max_neighbors`
source points within `radius` of $x_0`, not every point in the dataset.
`min_neighbors` sets a floor. Targets with too few in-range neighbors return
`NaN` instead of an estimate based on too little local information. This keeps
the cost bounded per target and keeps estimates tied to nearby evidence.

## When `radius` is not given

If `radius` is omitted, APbase fits a {doc}`variogram <variogram-fitting>`
from the source data and uses `range / 3`. This gives the search a radius that
usually includes meaningful spatial correlation without reaching too far into
uncorrelated data.
