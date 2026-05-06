# Bayes Component Ablation Note

This note removes one component of the practical Bayes rule at a time on the completed three-seed model wave restricted to the spotlight benchmark family.

## Headline

- Full Bayes mean regret: `-0.1984`
- No prior-strength estimate mean regret: `-0.2226`
- No reliability estimate mean regret: `-0.1624`
- No posterior update mean regret: `0.1695`

Interpretation:
- Removing the reliability term or the posterior update is clearly harmful both in mean regret and per-series comparisons.
- Removing the prior-strength term is worse on most series, but not on the aggregate mean; that makes it a mixed, higher-variance component rather than a uniformly necessary one on this broader wave.

## Overall Table

| Variant | Mean regret | Rows |
|---|---:|---:|
| full_bayes | -0.1984 | 522240 |
| no_prior_strength | -0.2226 | 522240 |
| no_reliability | -0.1624 | 522240 |
| no_posterior_update | 0.1695 | 522240 |

## Series Degradation Relative To Full Bayes

| Ablation | Worse series | Total series | Worse-rate |
|---|---:|---:|---:|
| no_prior_strength | 111 | 150 | 0.7400 |
| no_reliability | 141 | 150 | 0.9400 |
| no_posterior_update | 141 | 150 | 0.9400 |
