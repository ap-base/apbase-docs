# Cokriging

`CoKriging` extends {doc}`ordinary kriging <kriging>` by adding one or more
secondary variables that are related to the primary. For example, a dense
NDVI or soil EC surface can help estimate sparse yield samples when that
relationship is real and admissible
{cite}`Myers1982,Goovaerts1997,Wackernagel2003,ChilesDelfiner2012`. Run
{doc}`secondary-variable screening <covariate-screening>` first: `CoKriging` does
not test its inputs itself, and an unrelated or inadmissible secondary
degrades the estimate rather than improving it.

This is an advanced method, not the default `apbase.Map` path, which chooses
between IDW and ordinary kriging. Before relying on cokriging, compare its
result with a plain kriging baseline.

## Estimator and constraint

Given a primary $Z_0$ and $K$ secondaries $Z_1, \dots, Z_K$, the estimate
at a target $x_0$ pools weighted contributions from *every* variable's
own local neighborhood:

$$
\hat{Z}_0(x_0) = \sum_{u=0}^{K} \sum_{i=1}^{n_u} \lambda_{u,i} \, Z_u(x_{u,i})
$$

where $n_u$ is variable $u$'s own neighbor count: primary neighbors for
$u=0$ and secondary-$u$ neighbors for $u \geq 1$. All three methods below
use one **global unbiasedness constraint**,
$\sum_{u,i} \lambda_{u,i} = 1$ (standardized ordinary cokriging), rather
than one constraint per variable. A single constraint keeps the system
solvable when the weights combine variables with different units and
different local neighborhoods.

Each secondary is rescaled to the primary's mean/variance before fitting
or interpolating:

$$
Z_u'(x) = \bar{Z}_0 + \left(Z_u(x) - \bar{Z}_u\right)\frac{\sigma_0}{\sigma_u}
$$

This keeps the shared constraint meaningful even when the secondary variables
use different units. The equations below assume the variables have already
been standardized this way.

## The block system (ICM and LMC)

For **ICM** and **LMC**, each variable searches its own local neighborhood.
`radius` and `max_neighbors` apply to every variable, not only the primary,
so secondary variables do not need to share the primary's sample locations.
Writing $C_{uv}(h)$ for the fitted cross-covariance between variables $u$
and $v$ at separation $h$, the weights and Lagrange multiplier $\mu$
solve

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

where block $\mathbf{C}_{uv}$ holds $C_{uv}(d_{ij})$ between variable $u$'s
neighbors and variable $v$'s neighbors, and $\mathbf{c}_u$ holds
$C_{0u}(d_{i0})$ from variable $u$'s neighbors to the target. This gives one
linear system of size $(n_0 + \cdots + n_K + 1)$ per target, extending the
single-variable kriging system to $K+1$ variables.

ICM and LMC differ only in how $C_{uv}(h)$ is built from the fitted
model:

**ICM (Intrinsic Coregionalization Model).** ICM uses one shared shape (model
and range), fitted jointly over all $(K+1)(K+2)/2$ variable pairs (each direct
variogram and each cross-variogram), scaled per pair by two $(K+1)\times(K+1)$
matrices: a nugget matrix $\mathbf{B}_0$ and a partial-sill matrix
$\mathbf{B}_1$:

$$
C_{uv}(h) = \begin{cases}
\left(\mathbf{B}_0\right)_{uv} + \left(\mathbf{B}_1\right)_{uv} & h = 0 \\
\left(\mathbf{B}_1\right)_{uv} \left(1 - g(h)\right) & h > 0
\end{cases}
$$

with $g$ the shared shape function (spherical, exponential, or Gaussian,
chosen as in {doc}`Variogram <variogram-fitting>` but by the total fit error
summed across all pairs).

$\mathbf{B}_0$ and $\mathbf{B}_1$ are fitted independently per pair by
closed-form weighted least squares, with the same Cressie weights as
{doc}`Variogram <variogram-fitting>`. Each matrix is then checked for positive
semidefiniteness (PSD) with a Cholesky attempt. A violation larger than 10%
of the largest total sill means the variables' spatial structures do not fit
one shared shape, and the fit raises `CoKrigingNonPSDCoregionalizationError`.
A smaller violation, such as nearly collinear variables whose fitted sills
imply a correlation slightly above 1, is treated as fitting noise: the matrix
is projected onto the PSD cone (negative eigenvalues clipped to 0) before it
is used, so the cokriging system never receives an indefinite matrix.

Both matrices are checked, not just the sill. The nugget adds its own
covariance component at $h=0$, like the nugget structure in LMC below. A
nugget matrix that is not PSD introduces a negative eigenvalue into the block
system just as a bad sill matrix would. This matters in practice because
independent per-pair fits often produce a near-zero nugget diagonal on
low-noise data.

**LMC (full Linear Model of Coregionalization).** LMC uses $S$ nested
structures (index $0$ = nugget, $1, \dots, S{-}1$ continuous, at geometrically
spread ranges), each with its own $(K+1)\times(K+1)$ coefficient matrix
$\mathbf{B}^{(l)}$:

$$
C_{uv}(h) = \begin{cases}
\sum_{l=0}^{S-1} \left(\mathbf{B}^{(l)}\right)_{uv} & h = 0 \\
\sum_{l=1}^{S-1} \left(\mathbf{B}^{(l)}\right)_{uv} \left(1 - g_l(h)\right) & h > 0
\end{cases}
$$

Every structure contributes at $h=0$; for $h>0$ only the continuous structures
($l \geq 1$) contribute, each attenuated by its own $g_l$.

Coefficients are fitted with the Goulard & Voltz (1992) algorithm
{cite}`Goulard1992`, a block-coordinate descent. Its weights are Cressie
weights computed once per pair from a nugget-plus-one-structure fit and kept
fixed during the descent. Each step updates one
structure by closed-form weighted least squares while holding the others
fixed, then projects its matrix onto the PSD cone: negative eigenvalues are
clipped to 0 and the matrix is rebuilt. Unlike ICM, positive
semidefiniteness is therefore guaranteed by construction on every sweep
rather than checked after fitting. Compared with ICM, LMC replaces the single
shared shape with $S{-}1$ independently shaped continuous structures, at the
cost of a heavier iterative fit.

## Collocated cokriging (MM1)

**Collocated cokriging** (Markov Model 1) {cite}`Xu1992,Journel1999` uses
the primary's neighborhood plus one *collocated* datum for each secondary:
the secondary value at, or nearest to, the target within `radius`. It does not
use a full secondary neighborhood. Under the Markov Model 1 hypothesis, the
collocated secondary value makes farther secondary data redundant: the
secondary informs the primary through their shared location rather than its
own spatial structure, so the cross-covariance collapses to a fixed multiple of
the primary's own covariance:

$$
C_{0u}(h) = \rho_u \, C_{00}(h) \qquad\qquad
C_{uv}(0) = \rho_u \rho_v \, C_{00}(0) \; (u, v \geq 1)
$$

where $\rho_u$ is the primary-secondary correlation from
{class}`~apbase.cross_variogram.CrossVariogram`. The system then has one
row per primary neighbor, one per secondary, and one constraint row, which is
far smaller than the full ICM/LMC block system.

The trade-off is twofold. The secondary value must be available at every
interpolation target, so a sparse secondary has to be pre-interpolated onto a
denser point set first. And the result is only as good as the MM1 hypothesis
itself.

## Choosing a method

| | Secondaries need own local search | System size per target | Coregionalization fit |
|---|---|---|---|
| Collocated | No: one collocated value at the target | primary neighbors + $K$ + 1 | closed-form $\rho_u$ per secondary |
| ICM | Yes | $\sum_u n_u$ + 1 | one shared shape, joint pair fit |
| LMC | Yes | $\sum_u n_u$ + 1 | $S$ shapes, Goulard & Voltz iterative |

Collocated is the cheapest option when its requirements above are met. ICM
captures multi-point secondary structure with one shared shape. LMC allows a
different shape for each structure when one shared shape is not enough, at a
higher fitting cost.

## Local parameters

As with {class}`~apbase.kriging.Kriging`, `radius`, `max_neighbors`, and the
`min_neighbors` fallback bound each local search; the fallback is applied to
the primary points. ICM and LMC apply these bounds independently to each
variable, so a sparse secondary and a dense primary can use different
neighborhoods at the same target.
