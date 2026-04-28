# Eta-Tempered Decoding Recipe

This is the concrete method package implied by the theorem-3 rewrite.
It is deliberately conservative: only the confidence layer is tempered, so any remaining error after tempering should be interpreted as answer-level failure rather than miscalibration alone.

## Recommended Recipe

1. Hold out a 200-example calibration split for each model-and-benchmark cell.
2. Generate standard CoT traces once, then sweep eta in [0.1, 1.0] over the post-trace answer distribution.
3. Choose the largest eta that improves Brier without hurting answer accuracy on the calibration split.
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
- `ConflictBank` conflict behaves like an answer-level failure regime: even maximal confidence tempering leaves a large residual gap, so the right next intervention there is retraining or answer-space correction, not just post-hoc calibration.
