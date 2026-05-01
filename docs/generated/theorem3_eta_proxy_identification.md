# Theorem 3 Eta-Proxy Identification Note

This synthetic experiment calibrates the theorem-3 proxy `eta_hat_eff` against a known ground-truth `eta` in a controlled exponential-tilting environment.
Each trajectory accumulates trace-token evidence over time, the answer logit is sharpened with a user-set `eta`, and `eta_hat_eff` is recovered as the slope of answer-logit growth against cumulative trace evidence.

## Headline

- Seeds: `12`
- Trajectories per seed: `192`
- Steps per trajectory: `20`
- Spearman correlation between true `eta` and mean `eta_hat_eff`: `1.0`
- Mean estimate is strictly monotone over the sweep: `True`
- Max mean relative error across the sweep: `0.0203`
- Grid points with mean relative error <= 10%: `7/7`

## Sweep

| True `eta` | Mean `eta_hat_eff` | Std across seed means | Median `eta_hat_eff` | Mean relative error | Max seed relative error | Mean trajectory fraction within 10% |
|---|---:|---:|---:|---:|---:|---:|
| 0.2 | 0.2012 | 0.0052 | 0.2018 | 0.0203 | 0.0538 | 0.2365 |
| 0.4 | 0.4012 | 0.0052 | 0.4018 | 0.0101 | 0.0269 | 0.4787 |
| 0.6 | 0.6012 | 0.0052 | 0.6018 | 0.0068 | 0.0179 | 0.6584 |
| 0.8 | 0.8012 | 0.0052 | 0.8018 | 0.0051 | 0.0134 | 0.8025 |
| 1.0 | 1.0012 | 0.0052 | 1.0018 | 0.0041 | 0.0108 | 0.8811 |
| 1.5 | 1.5012 | 0.0052 | 1.5018 | 0.0027 | 0.0072 | 0.9826 |
| 2.0 | 2.0011 | 0.0052 | 2.0018 | 0.0020 | 0.0054 | 0.9978 |

## Read

- In this controlled environment, `eta_hat_eff` is not just directional: the seed-mean proxy tracks the true `eta` almost exactly across the full sweep.
- The per-trajectory estimate is noisier at the smallest `eta` values, but the aggregated proxy remains calibrated and monotone.
- This does not turn theorem 3 into a literal autoregressive proof. It does show that the current proxy is a usable instrument in the exact kind of exponential-tilting environment the theorem invokes.

## Figure

- `figures/knowledge_arbitration/theorem3_eta_proxy_identification.pdf`
