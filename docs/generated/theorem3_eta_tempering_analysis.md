# Theorem 3 Eta Tempering Analysis

This is an offline confidence-only eta tempering intervention over the observed long-CoT posterior.
It does not change answers, so it is a conservative read on how much calibration can be rescued without answer-level correction.

## Headline

- Mean conflict do-no-harm eta: `0.325`
- Mean no-conflict do-no-harm eta: `0.625`
- Conflict/no-conflict eta shrink factor: `0.52`
- ConflictBank conflict gap floor at eta -> 0: `0.482`
- ConflictBank conflict best attainable proxy gap: `0.482`
- WikiContradict conflict best attainable proxy gap: `0.0034` at eta `0.1`

## Slice Summary

| Benchmark | Split | Long acc | Long conf | Observed gap | Gap floor @ eta=0 | Best gap | Do-no-harm eta | Paired no-conf eta |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| conflictbank | conflict | 0.0180 | 0.9693 | 0.9513 | 0.4820 | 0.4820 | 0.10 | -- |
| conflictbank | no_conflict | 0.8620 | 0.9652 | 0.1032 | 0.3620 | 0.0005 | 0.75 | 1.00 |
| wikicontradict | conflict | 0.5650 | 0.9400 | 0.3750 | 0.0650 | 0.0034 | 0.55 | 1.00 |
| wikicontradict | no_conflict | 0.5300 | 0.9464 | 0.4164 | 0.0300 | 0.0058 | 0.50 | 1.00 |
