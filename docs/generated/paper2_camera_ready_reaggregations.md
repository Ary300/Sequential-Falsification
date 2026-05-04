# Paper 2 Camera-Ready Reaggregations

This note packages the remaining low-compute reaggregations from already materialized Paper 2 artifacts.

## Powered Head-to-Head Positive Subset

We report both the mean gap over all `210` seeded cells and the positive-only subset mean (`Δ̂_+` here = average Bayes-vs-baseline gap over cells where the gap is positive).

| Baseline | Mean gap (all) | Positive cells | Δ̂_+ positive subset | Mean positive part | Max gap | Min gap |
|---|---:|---:|---:|---:|---:|---:|
| cocoa | 0.0426 | 201/210 | 0.0450 | 0.0431 | 0.0567 | -0.0112 |
| astute_rag | 0.0318 | 201/210 | 0.0341 | 0.0326 | 0.0426 | -0.0175 |
| self_rag | 0.0219 | 180/210 | 0.0598 | 0.0512 | 0.1231 | -0.6223 |

## Eta-Tempering Distribution Summary

- Available local slices: `3`
- This is the exact currently materialized local pool, which is smaller than the aspirational `n=30` sweep.

| Metric | Median | IQR | Max | Min |
|---|---:|---:|---:|---:|
| accuracy_delta | 0.4033 | [0.2117, 0.4033] | 0.4033 | 0.0200 |
| ece_delta | -0.4082 | [-0.4082, -0.2234] | -0.0386 | -0.4082 |
| brier_delta | -0.3898 | [-0.3898, -0.2062] | -0.0226 | -0.3898 |
| confidence_delta | -0.0134 | [-0.0134, -0.0017] | 0.0099 | -0.0134 |
| gap_delta | -0.4167 | [-0.4167, -0.2134] | -0.0101 | -0.4167 |
| selected_eta | 0.0000 | [0.0000, 0.1500] | 0.3000 | 0.0000 |

## Empirical Curvature Proxy

We approximate `∂²_{ww} R` with a finite-difference second derivative of Brier along the locally available eta grid.

- Number of curvature estimates: `27`
- Median: `-0.1125`
- IQR: `[-0.2488, 0.0562]`
- Max: `0.8443`
- Min: `-2.8641`

