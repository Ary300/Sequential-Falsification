# Eta-Tempered Decoding Recipe

This is the concrete method package implied by the theorem-3 rewrite.
It is deliberately conservative: only the confidence layer is tempered, so any remaining error after tempering should be interpreted as answer-level failure rather than miscalibration alone.

## Recommended Recipe

1. Hold out a 200-example calibration split for each model-and-benchmark cell.
2. Generate standard CoT traces once, then sweep eta in [0.0, 1.0] over the post-trace answer distribution.
3. Choose the held-out Brier-optimal eta on the calibration split, and optionally report the largest no-harm eta as a conservative operating point.
4. Decode on the evaluation split with p_eta(a | trace, c) proportional to p(a | trace, c)^eta * p_theta(a | q)^(1-eta).
5. If the best eta still leaves a large confidence gap, treat the failure as answer-level and not calibration-only.

## Current Operating Point

- Mean conflict do-no-harm eta: `0.325`
- Mean no-conflict do-no-harm eta: `0.625`
- Conflict/no-conflict eta shrink factor: `0.52`
- `ConflictBank` conflict best attainable proxy gap: `0.482`
- `WikiContradict` conflict best attainable proxy gap: `0.0034` at eta `0.1`

## Read

- The theorem-3 method implication is not `eta < 1` everywhere; it is `eta` should shrink most aggressively on conflict slices and only modestly on no-conflict slices.
- `WikiContradict` behaves like a calibratable regime: confidence-only tempering nearly removes the long-CoT gap.
- On the real post-trace 14B run, the Brier-optimal eta for `ConflictBank` conflict collapses all the way to `0.0`, which is exactly the kind of misspecification signal theorem 3 is supposed to surface.
- `ConflictBank` conflict still behaves like an answer-level failure regime in the conservative operating-point sense: if you insist on shrinking eta only modestly, calibration barely improves and stronger rescue requires aggressive prior reweighting.
