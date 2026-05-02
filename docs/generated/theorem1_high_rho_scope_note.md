# Theorem 1 High-Rho Scope Note

This note addresses the concern that theorem 1's empirical robustness weakens materially at the highest correlation / misspecification stress setting.

## Robustness Sweep Recap

From [theorem1_loglinearity_robustness.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem1_loglinearity_robustness.md):

- `rho-like violation = 0.0`
  - held-out `R^2 = 0.9988`
  - excess Brier `0.000154`
- `0.5`
  - held-out `R^2 = 0.9609`
  - excess Brier `0.004823`
- `1.0`
  - held-out `R^2 = 0.7290`
  - excess Brier `0.035153`

## Practical Read

- Up through the moderate regime (`<= 0.5`), the fitted rule remains extremely close to the oracle family.
- The main failure mode appears only in the strongest synthetic violation regime.
- So the cleanest empirical scope statement is:
  - theorem 1 is exact in the log-linear family
  - it remains very accurate under moderate misspecification
  - the `rho = 1.0` regime is a real stress failure mode rather than a hidden theorem guarantee

## Recommendation

If the theorem needs a concrete empirical scope boundary, the defensible threshold from the existing sweep is:

- safe empirical regime: `rho-like violation <= 0.5`
- stress / degraded regime: `rho-like violation = 1.0`

That is a much better read than pretending the theorem is equally robust everywhere.
