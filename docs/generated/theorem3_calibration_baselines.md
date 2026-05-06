# Theorem 3 Calibration Baselines

This note compares the headline theorem-3 eta-tempering result against standard post-hoc calibration baselines on the worst `ConflictBank` 14B conflict slice.

## Setup

- Benchmark / condition / CoT: `conflictbank` / `conflict_context` / `cot=1024`
- Calibration rows: `200`
- Baseline file: remote Delta raw 14B theorem-3 rows

## Headline

- Best Brier method: `isotonic`
- `eta`-tempering Brier: `0.530564`
- Identity Brier: `0.924083`
- Temperature-scaling Brier: `0.67548`
- Platt-scaling Brier: `0.01666`
- Isotonic Brier: `0.016379`

## Read

- Eta-tempering is materially better than the raw identity confidence on this slice.
- Standard post-hoc scalar calibrators are much stronger on pure Brier than eta-tempering here, especially isotonic and Platt scaling.
- So the honest theorem-3 method claim is not “best generic calibration algorithm”; it is “a theory-derived, post-trace decoding intervention that partially repairs RLVR overconfidence without retraining.”
