# Spotlight Killer Figure

- Main SVG: `/Users/aryavdas/Downloads/Sequential Falsification with Calibrated Confidence/figures/spotlight_killer/spotlight_killer_figure.svg`
- Top-left: overall spotlight-matrix regret bars from `arbitration_spotlight_t12_benchmark_v2`.
- Top-right: benchmark conflict-density sweep using benchmark conflict priors and mean regret by benchmark.
- Bottom-left: reliability diagram comparing Bayes proxy vs heuristic adaptive on the spotlight matrix.
- Bottom-right: theorem-3 real-trace two-regime curves for DeepSeek `7B` and `14B` on `ConflictBank` and `WikiContradict`.

## Headline Read

- Bayes dominates the main theorem-1/theorem-2 comparison against the generic heuristic and fixed policies.
- The reliability diagram shows Bayes is closer to the diagonal than the heuristic across confidence bins.
- The theorem-3 panel shows benchmark-dependent structure rather than a universal monotone law: `ConflictBank` remains pathological at `14B`, while `WikiContradict` shows peak-then-partial-recovery.
