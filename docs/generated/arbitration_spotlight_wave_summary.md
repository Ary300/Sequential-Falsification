# Spotlight Wave Summary

## Benchmark-backed spotlight matrix (`T1/T2`)

Source:
[`results/arbitration_spotlight_t12_benchmark_v1/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_spotlight_t12_benchmark_v1/report/summary.md)

- Coverage: `5` benchmarks x `5` models x `4` conditions x `4` CoT budgets
  on `174,080` parsed examples and `260` grouped slices.
- Benchmarks: `ConflictBank`, `FaithEval`, `MemoTrap`, `NQ-Swap`, `PopQA`.
- Models: `Llama-3.1-8B`, `Llama-3.1-70B`, `Qwen2.5-7B`, `Qwen2.5-14B`,
  `DeepSeek-R1-Distill-Qwen-7B`.

Headline regret ordering:

- `simulated_model = -0.2046`
- `bayes_proxy = -0.1722`
- `heuristic_adaptive = -0.0889`
- `fixed_50 = 0.4035`
- `always_parametric = 5.2420`
- `always_context = 7.9943`

The actionable theorem-1/theorem-2 comparison is:

- `bayes_proxy` beats `heuristic_adaptive` by `0.0833` mean-regret points on
  the expanded spotlight matrix.
- Relative to the heuristic magnitude, that is roughly a `1.94x` stronger
  regret result.

Other key diagnostics:

- mean oracle-vs-model absolute arbitration gap: `0.1932`
- mean oracle-vs-model KL: `1.4680`
- mean conflict ECE delta across CoT: `-0.1321`
- mean no-conflict ECE delta across CoT: `-0.0212`

## Proxy theorem-3 size-scaling matrix

Source:
[`results/arbitration_spotlight_t3_scaling_proxy_v1/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_spotlight_t3_scaling_proxy_v1/report/summary.md)

- Coverage: `5` benchmarks x `5` models x `3` conditions x `3` CoT budgets
  on `65,190` parsed examples and `195` grouped slices.
- Benchmarks: `AmbigDocs`, `ConflictBank`, `FaithEval`, `RAMDocs`,
  `WikiContradict`.
- Models: `Qwen2.5-7B`, `Qwen2.5-14B`, `Qwen2.5-32B`,
  `DeepSeek-R1-Distill-Qwen-7B`, `Llama-3.1-8B`.

Headline regret ordering:

- `bayes_proxy = -0.0774`
- `heuristic_adaptive = -0.0189`
- `simulated_model = 0.1533`
- `fixed_50 = 0.3352`
- `always_context = 6.5247`
- `always_parametric = 6.5751`

Key interpretation:

- the expanded proxy size-scaling matrix still favors the Bayes-style rule over
  the generic heuristic by `0.0585` mean-regret points;
- conflict slices move much more than no-conflict slices in the proxy stack
  (`-0.0736` vs `-0.0229` ECE delta), but this remains supporting evidence
  rather than the final theorem-3 claim.

## Live Delta theorem-3 family sweep

As of `2026-04-26`, the real-generation Qwen family jobs have moved past the
"did the jobs actually start?" phase and into usable theorem-3 evidence:

- `2196739` `theorem3_qwen7b` completed on `gh082`
- `2196740` `theorem3_qwen14b` completed on `gh082`
- `2196741` `theorem3_qwen32b` is running on `gh074`

Current theorem-3 read:

- Final `Qwen2.5-7B` `ConflictBank` conflict:
  `0.9856 -> 0.9849 -> 0.9693`
- Final `Qwen2.5-7B` `ConflictBank` no-conflict:
  `0.0868 -> 0.0723 -> 0.0537`
- Final `Qwen2.5-14B` `ConflictBank` conflict:
  `0.9776 -> 0.9731 -> 0.9584`
- Partial `Qwen2.5-32B` `ConflictBank` conflict:
  `0.9448 -> 0.9312 -> 0.8829`
- Partial `Qwen2.5-32B` `WikiContradict` conflict:
  `0.0945 -> 0.3520 -> 0.2635`

These rows are the strongest same-family theorem-3 evidence in the repo so far:
controlled conflict stays catastrophically overconfident through scale, while
naturalistic contradiction is the first place where long-CoT recovery reappears
at `32B`.
