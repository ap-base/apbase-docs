# Methodology

APbase uses standard geostatistical methods in its automatic mapping pipeline.
You can generate maps without reading this section. Use it when you want to
understand the mathematics, tune an advanced workflow, or see why one method
won over another.

The default pipeline compares IDW and ordinary kriging with leave-one-out
cross-validation, then uses the method with the lower RMSE on the current data.
Cokriging is covered here as an advanced method for workflows with screened
secondary variables.

```{toctree}
:maxdepth: 1

variogram-fitting
idw
kriging
cross-validation
covariate-screening
cokriging
```

## References

The bibliography entries include DOI, publisher, or stable catalog links when
available.

```{bibliography}
:all:
```
