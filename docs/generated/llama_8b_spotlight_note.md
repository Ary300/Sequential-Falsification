# Llama-3.1-8B Spotlight Coverage Note

## Headline

- `Llama-3.1-8B-Instruct` is already present across all five spotlight benchmarks: `conflictbank`, `faitheval`, `memotrap`, `nq_swap`, and `popqa`.
- On the Llama-only five-benchmark slice, Bayes beats the generic heuristic by `0.1108` regret with bootstrap CI `[0.0895, 0.122]`.
- On that same slice, Bayes beats `CoCoA` by `0.0519` regret with CI `[0.0436, 0.0574]`.

## Per-Benchmark Read

- `conflictbank`: Bayes `-0.2594`, heuristic `-0.1324`, `CoCoA` `-0.2027`, `AdaCAD` `-0.1778`, `always_context` `6.5511`, `always_parametric` `6.5511`.
- `faitheval`: Bayes `-0.1718`, heuristic `-0.0677`, `CoCoA` `-0.117`, `AdaCAD` `-0.0928`, `always_context` `8.9658`, `always_parametric` `4.3607`.
- `memotrap`: Bayes `-0.1706`, heuristic `-0.068`, `CoCoA` `-0.1172`, `AdaCAD` `-0.093`, `always_context` `8.9375`, `always_parametric` `4.3863`.
- `nq_swap`: Bayes `-0.174`, heuristic `-0.0702`, `CoCoA` `-0.12`, `AdaCAD` `-0.0954`, `always_context` `8.9658`, `always_parametric` `4.3607`.
- `popqa`: Bayes `-0.2094`, heuristic `-0.1143`, `CoCoA` `-0.1819`, `AdaCAD` `-0.1619`, `always_context` `6.5511`, `always_parametric` `6.5511`.

## Read

- This closes the most visible model-coverage objection at the 8B open-weight tier: Llama is not missing from the main grid.
- No new GPU submission is required for this coverage claim because the finished spotlight matrix already contains the complete Llama-8B five-benchmark slice.
