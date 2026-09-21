# Cokriging

`CoKriging` extends {doc}`ordinary kriging <kriging>` by adding one or more
secondary variables that are related to the primary. For example, a dense
NDVI or soil EC surface can help estimate a sparse yield sample when that
relationship is real and admissible
{cite}`Myers1982,Goovaerts1997,Wackernagel2003,ChilesDelfiner2012`. Run
{doc}`covariate screening <covariate-screening>` first: `CoKriging` does
not test its inputs itself, and an unrelated or inadmissible secondary
degrades the estimate rather than improving it.

This is an advanced method, not the default `apbase.Map` path. The default
pipeline chooses between IDW and ordinary kriging. Use co-kriging only after
screening the secondary variables and comparing the result with a plain
kriging baseline.

## Estimator and constraint

Given a primary $Z_0$ and $K$ secondaries $Z_1, \dots, Z_K$, the estimate
at a target $x_0$ pools weighted contributions from *every* variable's
own local neighborhood:

$$
\hat{Z}_0(x_0) = \sum_{u=0}^{K} \sum_{i=1}^{n_u} \lambda_{u,i} \, Z_u(x_{u,i})
$$

where $n_u$ is variable $u$'s own neighbor count: primary neighbors for
$u=0$ and secondary-$u$ neighbors for $u \geq 1$. All three methods below
use one **global unbiasedness constraint**
$\sum_{u,i} \lambda_{u,i} = 1$ (standardized ordinary cokriging), rather
than one constraint per variable -- this is what keeps the system
solvable while combining weights across variables that are in different
units and different local neighborhoods.

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

**ICM (Intrinsic Coregionalization Model).** ICM uses one shared shape
(model and range), fitted jointly over every one of the
$\binom{K+1}{2}$ variable pairs, scaled per pair by two $(K+1)\times(K+1)$
matrices -- a nugget matrix $\mathbf{B}_0$ and a partial-sill matrix
$\mathbf{B}_1$:

$$
C_{uv}(h) = \begin{cases}
\left(\mathbf{B}_0\right)_{uv} + \left(\mathbf{B}_1\right)_{uv} & h = 0 \\
\left(\mathbf{B}_1\right)_{uv} \left(1 - g(h)\right) & h > 0
\end{cases}
$$

with $g$ the shared shape function (spherical/exponential/gaussian,
selected the same way as {doc}`Variogram <variogram-fitting>`, chosen by
total fit error summed across all pairs). $\mathbf{B}_0$ and
$\mathbf{B}_1$ are fit independently per pair by closed-form weighted
least squares, then each checked for positive semidefiniteness (PSD) via
a Cholesky attempt with a small relative floor
(`CoKrigingNonPSDCoregionalizationError` if either fails) -- **both**
matrices are checked, not just the sill: the nugget contributes its own
additive covariance component at $h=0$ (structurally identical to LMC's
own nugget structure below), so a nugget matrix that is not itself PSD
corrupts the block system with a negative eigenvalue just as readily as
a bad sill matrix would, even though independent per-pair fits routinely
produce a near-zero nugget diagonal for low-noise data.

**LMC (full Linear Model of Coregionalization).** LMC uses $S$ nested structures
(index $0$ = nugget, $1, \dots, S{-}1$ continuous, at geometrically
spread ranges), each with its own $(K+1)\times(K+1)$ coefficient matrix
$\mathbf{B}^{(l)}$:

$$
C_{uv}(h) = \sum_{l : h=0 \text{ or } l>0} \left(\mathbf{B}^{(l)}\right)_{uv}
\left(1 - g_l(h)\right)_{[l>0]}
$$

i.e. every structure contributes at $h=0$, only the continuous structures
($l \geq 1$) attenuate with $g_l$ for $h>0$. Coefficients are fit by the
Goulard & Voltz (1992) algorithm {cite}`Goulard1992`: block-coordinate
descent, alternating a closed-form weighted-least-squares update per
structure (holding the others fixed) with an eigendecomposition-based
projection onto the PSD cone (clip negative eigenvalues to 0,
reconstruct) after each update. Unlike ICM, PSD-ness is guaranteed by
construction every sweep, not checked post-hoc -- LMC trades ICM's single
shared shape for $S{-}1$ independently-shaped continuous structures, at
the cost of a heavier iterative fit.

## Collocated cokriging (MM1)

**Collocated cokriging** (Markov Model 1) {cite}`Xu1992,Journel1999` uses
the primary's neighborhood plus one *colocated* datum for each secondary:
the secondary value at, or nearest to, the target. It does not use a full
secondary neighborhood. Under the Markov screening assumption, the secondary
informs the primary through their shared location rather than its own spatial
structure, so the cross-covariance
collapses to a fixed multiple of the primary's own covariance:

$$
C_{0u}(h) = \rho_u \, C_{00}(h) \qquad\qquad
C_{uv}(0) = \rho_u \rho_v \, C_{00}(0) \; (u, v \geq 1)
$$

where $\rho_u$ is the primary-secondary correlation from
{class}`~apbase.cross_variogram.CrossVariogram`. This reduces the system
to primary-neighborhood size plus $K$ (one row/column per secondary) plus
one constraint row -- far smaller than ICM/LMC's full block system, at
the cost of needing the secondary value available at every interpolation
target (pre-interpolate a sparse secondary onto a denser point set first
if needed) and of the simpler screening assumption itself.

## Choosing a method

| | Secondaries need own local search | System size per target | Coregionalization fit |
|---|---|---|---|
| Collocated | No -- one colocated value at target | primary neighbors + $K$ + 1 | closed-form $\rho_u$ per secondary |
| ICM | Yes | $\sum_u n_u$ + 1 | one shared shape, joint pair fit |
| LMC | Yes | $\sum_u n_u$ + 1 | $S$ shapes, Goulard-Voltz iterative |

Collocated is the cheapest option and needs the least fitting, but it assumes
the Markov relationship and requires secondary coverage at every target. ICM
captures multi-point secondary structure with one shared shape. LMC allows a
different shape for each structure when one shared shape is not enough, at a
higher fitting cost.

## Local parameters

As with {class}`~apbase.kriging.Kriging`, `radius` and `max_neighbors` bound
each local search, while `min_neighbors` is the minimum needed for a finite
estimate. ICM and LMC apply these bounds independently to each variable, so a
sparse secondary and a dense primary can use different neighborhoods at the
same target.
