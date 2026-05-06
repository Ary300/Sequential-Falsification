# Synthetic Oracle Convergence Note

This synthetic theorem-1 anchor uses a toy Gaussian-and-staleness setting where the oracle arbitration weight is analytically known and the estimated rule is fit from calibration samples.

## Headline

- Largest calibration size: `2048`
- Mean held-out `R^2` between estimated and oracle arbitration weight: `0.9984`
- Target `R^2 > 0.95` passed: `True`

## Convergence Table

| Calibration samples | Mean `R^2` | Std `R^2` | Mean selector accuracy | Mean Brier-to-oracle |
|---|---:|---:|---:|---:|
| 32 | 0.9287 | 0.0503 | 0.8173 | 0.0086 |
| 64 | 0.9301 | 0.0652 | 0.8163 | 0.0085 |
| 128 | 0.9861 | 0.0079 | 0.8211 | 0.0017 |
| 256 | 0.9929 | 0.0043 | 0.8255 | 0.0009 |
| 512 | 0.9923 | 0.0063 | 0.8247 | 0.0009 |
| 1024 | 0.9972 | 0.0020 | 0.8254 | 0.0003 |
| 2048 | 0.9984 | 0.0008 | 0.8261 | 0.0002 |

## Figure Paths

- Convergence curve: `figures/knowledge_arbitration/synthetic_oracle_convergence.pdf`
- Oracle-vs-estimated scatter: `figures/knowledge_arbitration/synthetic_oracle_scatter.pdf`
