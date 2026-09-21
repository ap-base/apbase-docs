# Methodology

APbase uses standard geostatistical methods in its automatic mapping pipeline.
You can generate maps without reading this section. Use it when you want to
understand the mathematics, tune an advanced workflow, or see why one method
won over another.

The default pipeline compares IDW and ordinary kriging using validation error,
then uses the method that performs better on the current data. In Python,
`apbase.create_map` is the functional shortcut for the same pipeline.
Co-kriging is covered here as an advanced method for workflows with screened
secondary variables.

```{toctree}
:maxdepth: 1

idw
kriging
variogram-fitting
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
