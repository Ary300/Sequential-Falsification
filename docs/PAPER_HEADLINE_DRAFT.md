# Bayes-Optimal Knowledge Arbitration: Paper Draft

## Current best title options

1. `Bayes-Optimal Knowledge Arbitration for LLMs`
2. `When Should LLMs Trust Retrieval? Bayes-Optimal Knowledge Arbitration`
3. `Fixed Trust Policies Are Wrong: Bayes-Optimal Knowledge Arbitration for LLMs`
4. `Knowledge Arbitration Under Conflict: Bayes-Optimal Rules and Non-Monotone CoT Calibration`

## Best current one-sentence claim

We cast knowledge conflict as a posterior-predictive decision problem, derive a
Bayes-style arbitration rule that beats generic heuristics and fixed trust
policies on real conflict benchmarks, and show that chain-of-thought amplifies
overconfidence on hard knowledge QA, with explicit conflict making the failure
more persistent on controlled conflict families at larger scale.

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
On the expanded spotlight-scale benchmark-backed matrix (`5` benchmarks x `5`
models, `174,080` examples), the Bayes proxy achieves mean regret `-0.1722`
versus `-0.0889` for the heuristic, while `always_context` and
`always_parametric` degrade to `7.9943` and `5.2420`.
In our corrected broad real wave, the Bayes proxy achieves mean regret
`-0.0461` versus `-0.0233` for the heuristic, while `always_context` and
`always_parametric` degrade to `7.2237` and `5.9356`. In the conflict-heavy
wave, the gap widens to `-0.1256` versus `-0.0752`, with fixed policies at
`5.9037` and `7.1329`. For reasoning-time calibration, corrected real
DeepSeek-R1-Distill traces show that the original conflict-only story does not
hold. The true `closed_book` control also becomes more overconfident with
longer CoT. What survives is a sharper, family-dependent result:
`ConflictBank` conflict at `14B` remains catastrophically overconfident through
`cot=1024`, while the live same-family `Qwen2.5` sweep shows the first `32B`
recovery signal on `WikiContradict` but persistent controlled-conflict failure
on `ConflictBank`. These results position knowledge
arbitration as a principled
inference problem rather than a retrieval heuristic, and they give a concrete
recipe for replacing fixed trust policies with reliability-aware decoding
rules.

## What the intro should say plainly

- Retrieval should not be trusted by default.
- Parametric memory should not be trusted by default.
- The right object is a reliability-aware posterior-predictive arbitration rule.
- Fixed trust policies fail badly enough that this is not a small-tuning issue.
- Reasoning-time calibration failure is real, but the corrected closed-book
  control shows it is not uniquely conflict-triggered.
- Explicit conflict still matters on `ConflictBank`, especially at `14B`, where
  longer CoT prevents recovery and drives near-maximal overconfidence.

## Best empirical bullets right now

- Broad corrected wave:
  `bayes_proxy = -0.0461`, `heuristic_adaptive = -0.0233`,
  `simulated_model = 0.1408`, `fixed_50 = 0.3650`.
- Conflict-heavy corrected wave:
  `bayes_proxy = -0.1256`, `heuristic_adaptive = -0.0752`,
  `simulated_model = 0.1104`, `fixed_50 = 0.3037`.
- Expanded benchmark-backed spotlight matrix:
  `bayes_proxy = -0.1722`, `heuristic_adaptive = -0.0889`,
  `simulated_model = -0.2046`, `fixed_50 = 0.4035`.
- Expanded theorem-3 proxy size-scaling matrix:
  `bayes_proxy = -0.0774`, `heuristic_adaptive = -0.0189`,
  `simulated_model = 0.1533`, `fixed_50 = 0.3352`.
- Fixed-policy failures stay dramatic:
  `always_context = 7.2237` / `5.9037` / `7.9943`,
  `always_parametric = 5.9356` / `7.1329` / `5.2420`.
- Theorem-3 real-trace signal:
  `ConflictBank` conflict gap `0.5505 -> 0.7531 -> 0.5308`,
  `WikiContradict` conflict gap `0.2923 -> 0.4825 -> 0.4429`.
- Finished 14B scaling signal:
  `ConflictBank` conflict gap `0.5876 -> 0.9449 -> 0.9513`,
  `WikiContradict` conflict gap `0.2717 -> 0.4516 -> 0.3750`.
- Live same-family Qwen theorem-3 sweep:
  `2196739` (`Qwen2.5-7B`) and `2196740` (`Qwen2.5-14B`) completed, while
  `2196741` (`Qwen2.5-32B`) is still running on Delta.
- Final same-family Qwen 7B controlled-conflict signal:
  `ConflictBank` conflict `0.9856 -> 0.9849 -> 0.9693` versus
  no-conflict `0.0868 -> 0.0723 -> 0.0537`.
- Final same-family Qwen 14B controlled-conflict signal:
  `ConflictBank` conflict `0.9776 -> 0.9731 -> 0.9584` versus
  no-conflict `0.0639 -> 0.0679 -> 0.0476`.
- Same-family Qwen 32B partial theorem-3 split:
  `ConflictBank` conflict `0.9448 -> 0.9312 -> 0.8829`, while
  `WikiContradict` conflict `0.0945 -> 0.3520 -> 0.2635`.
- Corrected closed-book control decision:
  option `A` is ruled out.
- The strongest theorem-3 statement is now:
  CoT amplifies overconfidence on hard knowledge QA, and explicit conflict can
  further intensify that pathology on controlled conflict families.

## Honest caveats we should write explicitly

- The theorem-1/2 benchmark waves are benchmark-backed proxy evaluations, not
  full real-generation sweeps.
- The broad-wave Bayes win has one exception:
  `Qwen2.5-14B-Instruct` slightly favors the generic heuristic.
- Theorem 3 is landed only in a weaker corrected form, not the original
  conflict-conditioned sign-flip form.
- `WikiContradict` supports an intermediate-CoT peak with partial recovery,
  while `ConflictBank` conflict at 14B stays severely overconfident through
  long CoT.
- The `Qwen2.5-7B` and `Qwen2.5-14B` theorem-3 evidence is final, but the
  `32B` `ConflictBank` numbers are still live partial reads and should be
  described as provisional until that Delta job finishes.

## Best current figure order

1. Figure 1: corrected regret bars, Bayes proxy vs heuristic vs fixed policies.
2. Figure 2: oracle-vs-model arbitration gap on the corrected broad wave.
3. Figure 3: theorem-3 overconfidence-gap curves for `ConflictBank` and
   `WikiContradict`, with a same-family `Qwen2.5 7B -> 14B -> 32B` overlay.
4. Figure 4: per-model Bayes-vs-heuristic gains, explicitly showing the
   `Qwen2.5-14B-Instruct` exception.
