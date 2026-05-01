# Theorem 1 Log-Linearity Robustness Note

This synthetic sweep perturbs the theorem-1 oracle away from the exact log-linear family by adding a controlled nonlinear violation term while keeping the same calibration-fit procedure.

## Headline

- Calibration size: `2048`
- Mean held-out `R^2` at zero violation: `0.9988`
- Mean held-out `R^2` at maximum violation: `0.729`
- Mean excess Brier at zero violation: `0.000154`
- Mean excess Brier at maximum violation: `0.035153`

## Sweep

| Violation strength | Mean `R^2` | Std `R^2` | Mean Brier-to-oracle | Mean excess Brier |
|---|---:|---:|---:|---:|
| 0.0 | 0.9988 | 0.0006 | 0.000154 | 0.000154 |
| 0.1 | 0.9972 | 0.0013 | 0.000353 | 0.000353 |
| 0.2 | 0.9943 | 0.0013 | 0.000711 | 0.000711 |
| 0.3 | 0.9891 | 0.0019 | 0.001352 | 0.001352 |
| 0.4 | 0.9799 | 0.0030 | 0.002489 | 0.002489 |
| 0.5 | 0.9609 | 0.0048 | 0.004823 | 0.004823 |
| 0.6 | 0.9295 | 0.0069 | 0.008685 | 0.008685 |
| 0.7 | 0.8858 | 0.0085 | 0.014133 | 0.014133 |
| 0.8 | 0.8330 | 0.0114 | 0.020888 | 0.020888 |
| 0.9 | 0.7819 | 0.0138 | 0.027725 | 0.027725 |
| 1.0 | 0.7290 | 0.0160 | 0.035153 | 0.035153 |

## Read

- At zero violation the fitted rule recovers the oracle family extremely well, matching the main synthetic-oracle result.
- As violation strength grows, fit quality degrades smoothly rather than collapsing abruptly.
- This is the right empirical interpretation of theorem 1: the exact closed form belongs to the log-linear family, but the practical rule degrades gracefully under moderate family misspecification.
