# Knowledge Arbitration Headline Bundle

## Headline Claims

- Theorem 1: A Bayes-style reliability-aware arbitration rule beats the generic heuristic and sharply beats fixed trust policies across the broad real matrix.
- Theorem 2: Fixed trust policies are minimax-bad in practice: in the conflict-heavy wave, they incur much larger regret than the principled Bayes proxy.
- Theorem 3: Calibration failure peaks at an intermediate CoT budget, then partially self-corrects at very long CoT.

## Theorem 1

- Wave: `broad_real_headline_wave_reestimated_v3` across `176` series
- `bayes_proxy` mean regret: `-0.04607070194023072`
- `bayes_proxy` accuracy / ECE: `0.8866` / `0.1354`
- `heuristic_adaptive` mean regret: `-0.023349765237714086`
- Bayes minus heuristic regret gap: `0.0227`
- `simulated_model` mean regret: `0.1407719311984596`
- `fixed_50` mean regret: `0.3650119290428605`
- `always_context` mean regret: `7.223688766628678`
- `always_parametric` mean regret: `5.935552288286208`
- Mean oracle-model absolute gap: `0.1969`
- Mean oracle-model KL: `1.2288`
- Mean conflict / no-conflict ECE deltas: `-0.0054` / `-0.0238`

## Theorem 2

- Wave: `conflict_headline_wave_reestimated_v3` across `175` series
- `bayes_proxy` mean regret: `-0.12557343144995242`
- `bayes_proxy` accuracy / ECE: `0.9028` / `0.0724`
- `heuristic_adaptive` mean regret: `-0.07515526270093635`
- Bayes minus heuristic regret gap: `0.0504`
- `simulated_model` mean regret: `0.11035460812956133`
- `fixed_50` mean regret: `0.303704532192305`
- `always_context` mean regret: `5.903744200087245`
- `always_parametric` mean regret: `7.132882061129149`
- Mean oracle-model absolute gap: `0.2768`
- Mean oracle-model KL: `2.1393`
- Mean conflict / no-conflict ECE deltas: `-0.0191` / `-0.0383`

## Theorem 3

- Source run: `delta_job_2190906` on `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- Total parsed rows: `4200`

| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |
|---|---|---:|---:|---:|---:|---:|
| conflictbank | conflict | 0.5505 | 0.7531 | 0.5308 | 0.2026 | -0.2223 |
| conflictbank | no_conflict | 0.0996 | 0.2754 | -0.3724 | 0.1758 | -0.6478 |
| wikicontradict | conflict | 0.2923 | 0.4825 | 0.4429 | 0.1902 | -0.0396 |
| wikicontradict | no_conflict | 0.2643 | 0.5038 | 0.4331 | 0.2395 | -0.0707 |

## Current Read

- Theorem 1/2 are already paper-strong at the proxy-regret layer.
- Theorem 3 does not support the old monotone statement.
- The strongest current theorem-3 claim is the non-monotone intermediate-CoT overconfidence peak.
