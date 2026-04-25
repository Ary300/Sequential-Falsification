# Bayes-Optimal Knowledge Arbitration: Paper Draft

## Current best title options

1. `Bayes-Optimal Knowledge Arbitration for LLMs`
2. `When Should LLMs Trust Retrieval? Bayes-Optimal Knowledge Arbitration`
3. `Fixed Trust Policies Are Wrong: Bayes-Optimal Knowledge Arbitration for LLMs`
4. `Knowledge Arbitration Under Conflict: Bayes-Optimal Rules and Non-Monotone CoT Calibration`

## Best current one-sentence claim

We cast knowledge conflict as a posterior-predictive decision problem, derive a
Bayes-style arbitration rule that beats generic heuristics and fixed trust
policies on real conflict benchmarks, and show that reasoning amplifies
overconfidence under conflict, with the exact CoT shape depending on conflict
family.

## Current abstract draft

Large language models routinely face knowledge conflict: parametric memory,
retrieved context, and longer reasoning traces can each point toward different
answers. Existing systems handle this with heuristics such as fixed trust in
retrieval, fixed trust in the base model, or hand-tuned adaptive rules, but the
field lacks a decision-theoretic account of when each source should be trusted.
We formulate knowledge arbitration as a posterior-predictive decision problem
and derive a Bayes-style reliability-aware arbitration rule. On benchmark-backed
conflict matrices spanning PopQA, DynamicQA, NQ-Swap, WikiContradict, and
ConflictBank slices, the resulting policy beats a generic adaptive heuristic and
substantially outperforms fixed trust policies, which incur much larger regret.
In our corrected broad real wave, the Bayes proxy achieves mean regret
`-0.0461` versus `-0.0233` for the heuristic, while `always_context` and
`always_parametric` degrade to `7.2237` and `5.9356`. In the conflict-heavy
wave, the gap widens to `-0.1256` versus `-0.0752`, with fixed policies at
`5.9037` and `7.1329`. For reasoning-time calibration, real DeepSeek-R1-Distill
traces show that the original monotone “more CoT is worse” story is too simple:
7B traces peak at intermediate CoT on both `ConflictBank` and
`WikiContradict`, while the completed 14B replication shows benchmark-family
dependence: `WikiContradict` still partially recovers at long CoT, but
`ConflictBank` conflict remains catastrophically overconfident through
`cot=1024`. These results position knowledge arbitration as a principled
inference problem rather than a retrieval heuristic, and they give a concrete
recipe for replacing fixed trust policies with reliability-aware decoding
rules.

## What the intro should say plainly

- Retrieval should not be trusted by default.
- Parametric memory should not be trusted by default.
- The right object is a reliability-aware posterior-predictive arbitration rule.
- Fixed trust policies fail badly enough that this is not a small-tuning issue.
- Reasoning-time calibration under conflict is real, but the shape is
  conflict-family dependent rather than uniformly monotone.

## Best empirical bullets right now

- Broad corrected wave:
  `bayes_proxy = -0.0461`, `heuristic_adaptive = -0.0233`,
  `simulated_model = 0.1408`, `fixed_50 = 0.3650`.
- Conflict-heavy corrected wave:
  `bayes_proxy = -0.1256`, `heuristic_adaptive = -0.0752`,
  `simulated_model = 0.1104`, `fixed_50 = 0.3037`.
- Fixed-policy failures stay dramatic:
  `always_context = 7.2237` / `5.9037`,
  `always_parametric = 5.9356` / `7.1329`.
- Theorem-3 real-trace signal:
  `ConflictBank` conflict gap `0.5505 -> 0.7531 -> 0.5308`,
  `WikiContradict` conflict gap `0.2923 -> 0.4825 -> 0.4429`.
- Finished 14B scaling signal:
  `ConflictBank` conflict gap `0.5876 -> 0.9449 -> 0.9513`,
  `WikiContradict` conflict gap `0.2717 -> 0.4516 -> 0.3750`.

## Honest caveats we should write explicitly

- The theorem-1/2 benchmark waves are benchmark-backed proxy evaluations, not
  full real-generation sweeps.
- The broad-wave Bayes win has one exception:
  `Qwen2.5-14B-Instruct` slightly favors the generic heuristic.
- Theorem 3 is landed in revised family-dependent form, not the original
  monotone conflict-conditioned form.
- `WikiContradict` supports an intermediate-CoT peak with partial recovery,
  while `ConflictBank` conflict at 14B stays severely overconfident through
  long CoT.

## Best current figure order

1. Figure 1: corrected regret bars, Bayes proxy vs heuristic vs fixed policies.
2. Figure 2: oracle-vs-model arbitration gap on the corrected broad wave.
3. Figure 3: theorem-3 overconfidence-gap curves for `ConflictBank` and
   `WikiContradict`.
4. Figure 4: per-model Bayes-vs-heuristic gains, explicitly showing the
   `Qwen2.5-14B-Instruct` exception.
