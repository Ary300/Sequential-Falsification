# Bayes-Optimal Knowledge Arbitration: Results Tracker

## Purpose

This file tracks whether we actually have the kind of results the paper needs.

The goal is to prevent a repeat of vague "we're making progress" updates when
the headline results are still missing.

## Current landing

The project now has a real paper-level core:

- theorem 1 landed on the corrected broad wave;
- theorem 2 landed on the corrected conflict-heavy wave;
- theorem 1 / theorem 2 now also landed on an expanded benchmark-backed
  spotlight matrix covering `5` benchmarks x `5` models;
- theorem 3 landed in its rewritten benchmark-dependent two-regime form on
  real 7B and 14B DeepSeek traces plus a completed same-family
  `Qwen2.5 7B -> 14B -> 32B` sweep.

The strongest finished theorem-1/theorem-2 headline is now backed by bootstrap
uncertainty on the spotlight matrix:

- Bayes vs heuristic regret gap `0.0833` with bootstrap CI `[0.0371, 0.1112]`;
- Bayes vs strongest named comparator (`Self-RAG`) point estimate `0.0266`,
  with a wider CI `[-0.0379, 0.0686]`.

The strongest finished theorem-3 proxy headline is also now backed by bootstrap
uncertainty:

- Bayes vs heuristic regret gap `0.0585` with bootstrap CI `[0.0155, 0.0961]`;
- the named-comparator side is a near-tie against `CoCoA`, so the theorem-3
  headline should stay anchored on the heuristic comparison plus the real-trace
  two-regime story.

The new expanded spotlight-wave summary is explicit in
[`docs/generated/arbitration_spotlight_wave_summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/arbitration_spotlight_wave_summary.md).

The strongest current theorem-3 headline is:

- reasoning amplifies overconfidence on hard knowledge QA;
- `ConflictBank` conflict at 14B remains catastrophically overconfident
  through long CoT;
- the corrected `closed_book` control rules out a clean conflict-only sign
  flip.

The corrected closed-book control analysis is now explicit in
[`docs/generated/theorem3_closedbook_control_analysis.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_closedbook_control_analysis.md).
The current DeepSeek family comparison is also now explicit in
[`docs/generated/theorem3_deepseek_family_sweep.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_deepseek_family_sweep.md).
The completed same-family Qwen read is now explicit in
[`docs/generated/theorem3_qwen_family_final.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_qwen_family_final.md).
The new same-family threshold read is now explicit in
[`docs/generated/theorem3_same_family_threshold_summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_same_family_threshold_summary.md).
The new cross-family theorem-3 verdict is now explicit in
[`docs/generated/theorem3_cross_family_verdict.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_cross_family_verdict.md).
The new theorem-3 eta-tempering read is now explicit in
[`docs/generated/theorem3_eta_tempering_analysis.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_eta_tempering_analysis.md).
The explicit eta-decoding recipe is now also on disk in
[`docs/generated/eta_tempered_decoding_recipe.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/eta_tempered_decoding_recipe.md).
The benchmark-family consistency read is now explicit in
[`docs/generated/benchmark_family_consistency_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/benchmark_family_consistency_note.md).
The RLVR-conditioned theorem-3 framing note is now explicit in
[`docs/generated/theorem3_rlvr_reframing_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_rlvr_reframing_note.md).
The staged co-author / advisor outreach packet is now explicit in
[`docs/generated/senior_outreach_packet.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/senior_outreach_packet.md).
The new spotlight bootstrap summaries are now explicit in
[`docs/generated/arbitration_spotlight_t12_bootstrap_v1.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/arbitration_spotlight_t12_bootstrap_v1.md)
and
[`docs/generated/arbitration_spotlight_t3_bootstrap_v1.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/arbitration_spotlight_t3_bootstrap_v1.md).
The new 2x2 killer figure package is now explicit in
[`figures/spotlight_killer/README.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/figures/spotlight_killer/README.md).
The new AdaCAD / CoCoA positioning note is now explicit in
[`docs/generated/adacad_cocoa_positioning_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/adacad_cocoa_positioning_note.md).
The new playbook-completion status note is now explicit in
[`docs/generated/playbook_completion_status.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/playbook_completion_status.md).
The new dedicated `PopQA` / `NQ-Swap` benchmark note is now explicit in
[`docs/generated/popqa_nqswap_real_benchmark_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/popqa_nqswap_real_benchmark_note.md).
The new dedicated `Llama-3.1-8B` five-benchmark note is now explicit in
[`docs/generated/llama_8b_spotlight_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/llama_8b_spotlight_note.md).
The new dedicated `Llama-3.1-70B` frontier note is now explicit in
[`docs/generated/llama_70b_frontier_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/llama_70b_frontier_note.md).
The new empirical-completion audit is now explicit in
[`docs/generated/empirical_completion_audit.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/empirical_completion_audit.md).
The new extended-wave readiness note is now explicit in
[`docs/generated/extended_empirical_wave_ready.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/extended_empirical_wave_ready.md).
That artifact makes the next empirical wave concrete rather than aspirational:
`13` wired models, `10` wired benchmarks, `15` wired baselines, `5` wired
ablations, and explicit three-seed coverage in config, with Delta now
authenticated, `18` extended-wave jobs submitted, and a direct completed
API-slice probe already pulled back locally.
The new spotlight statistical-strength note is now explicit in
[`docs/generated/spotlight_statistical_strength_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/spotlight_statistical_strength_note.md).
That note sharpens the finished headline read:
the theorem-1/theorem-2 spotlight matrix wins `23/25` benchmark-model series
against the heuristic with exact sign-test `p ~= 1e-5`, while the theorem-3
proxy still wins `20/25` with exact sign-test `p ~= 0.0020`.
The new named-comparator spotlight proxy read is now explicit in
[`docs/generated/arbitration_proxy_baseline_t12_v2.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/arbitration_proxy_baseline_t12_v2.md).
The new theorem-3 named-comparator proxy read is now explicit in
[`docs/generated/arbitration_proxy_baseline_t3_v2.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/arbitration_proxy_baseline_t3_v2.md).
That file is now stronger than before: `Qwen2.5-7B` and `Qwen2.5-14B` are
final, and the `32B` job has populated both `ConflictBank` and
`WikiContradict` groups on disk.
Its decision is `not A`:

- the true `closed_book` control also becomes more overconfident with CoT;
- on `ConflictBank`, conflict is worse mainly at larger scale and especially at
  `14B`;
- on `WikiContradict`, the closed-book control is already more overconfident
  than explicit conflict.

## Headline-result checklist

| Item | Needed for paper | Current status |
| --- | --- | --- |
| Theorem 1 written cleanly | yes | drafted in `KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md` |
| Theorem 2 written cleanly | yes | drafted in `KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md` |
| Theorem 3 written cleanly | yes | drafted in `KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md` |
| Synthetic Bayes oracle experiment | yes | done |
| Real benchmark pilot on `PopQA` | yes | done via `docs/generated/knowledge_arbitration_headline_bundle.md` and the dedicated `PopQA` note |
| Real benchmark pilot on `DynamicQA` | yes | done via `docs/generated/knowledge_arbitration_headline_bundle.md` |
| Real benchmark pilot on `ConflictBank` subset | yes | done in compact conflict wave |
| Expanded `5 x 5` benchmark-backed spotlight matrix | strongly preferred | done via `arbitration_spotlight_t12_benchmark_v2` |
| Expanded theorem-3 proxy size-scaling matrix | strongly preferred | done via `arbitration_spotlight_t3_scaling_proxy_v2` |
| Conflict vs no-conflict calibration curves | yes | done for broad pilot and `WikiContradict` focus |
| Checkpoint-family experiment | strongly preferred | not required for the current paper core |
| Real same-family theorem-3 size sweep (`Qwen 7B/14B/32B`) | strongly preferred | done |
| Mitigation experiment | strongly preferred | done as confidence-only eta-tempering intervention read |

## Benchmark coverage

| Benchmark | Closed-book | Aligned context | Conflict context | Multi-context conflict | CoT sweep | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `PopQA` | done | done | not yet supported in built-in loader | n/a | done in broad pilot | broad pilot completed |
| `DynamicQA` | done | done | done | optional | done in broad pilot | broad pilot completed |
| `ConflictBank` | not used | done | done | family-expanded conflicts | done in compact conflict wave | now streamed, not full-download |
| `WikiContradict` | not used | done | done | optional | done in focused report | strongest current theorem-3 signal |
| `NQ-Swap` | done | done | done | n/a | done in broad pilot | clean entity swap |
| `TempLAMA` | missing | optional | optional | n/a | missing | checkpoint analysis |
| `FreshQA` | missing | optional | optional | n/a | missing | freshness analysis |
| `MQuAKE-Remastered` | missing | optional | missing | optional | missing | multi-hop stress test |

## Model coverage

| Family | Pilot coverage | Main coverage target | Status |
| --- | --- | --- | --- |
| `Llama-3.1` | 8B | 8B + optional larger | pilot done |
| `Qwen-2.5` / `Qwen-3` | 7B/8B | 7B/8B + optional 32B | theorem-3 family sweep done through `Qwen2.5-32B` |
| `DeepSeek-R1-Distill` | 7B | 7B + optional 14B | pilot done |
| `Pythia` | 6.9B or nearby | checkpoint sweep | not started |
| `OLMo-2` | 7B | checkpoint sweep | not started |
| `Mistral` | 7B | robustness | not started |
| `Phi-3` | medium | robustness | not started |

The key difference now is that these rows are no longer "missing because we
have not wired them." They are "missing because they require fresh cluster or
API runs on top of the new extended manifest."

## What would count as a real early win

We now have a finished paper core rather than just an early win:

- Synthetic oracle pilot is done and still useful for theorem-shape sanity
  checks.
- Broad real benchmark-backed pilot is now corrected and de-oracled:
  [`docs/generated/knowledge_arbitration_headline_bundle.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_headline_bundle.md)
  on `44,960` parsed examples across `PopQA`, `DynamicQA`, `NQ-Swap`, and
  `WikiContradict`.
- Focused contradiction report is done:
  [`results/arbitration_wikicontradict_focus/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_wikicontradict_focus/report/summary.md)
  and gives the cleanest current theorem-3-style signal.
- Corrected conflict-only wave is done:
  [`docs/generated/knowledge_arbitration_headline_bundle.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_headline_bundle.md)
  and adds `ConflictBank` into the live benchmark path.
- Theorem-3 diagnosis is done:
  [`results/arbitration_conflict_focus_compact_v2/theorem3_diagnosis/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_conflict_focus_compact_v2/theorem3_diagnosis/summary.md)
  with ambiguity filtering and benchmark-family breakdowns.

Current finished headline set:

- In the corrected broad real wave, `bayes_proxy` now beats the generic
  heuristic on regret:
  `-0.0461` versus `-0.0233`, while still crushing `fixed_50` at `0.3650`,
  `always_context` at `7.2237`, and `always_parametric` at `5.9356`.
- In the corrected conflict-heavy wave, the ordering is even cleaner:
  `bayes_proxy = -0.1256`, `heuristic_adaptive = -0.0752`,
  `simulated_model = 0.1104`, `fixed_50 = 0.3037`,
  `always_context = 5.9037`, `always_parametric = 7.1329`.
- In the expanded benchmark-backed spotlight matrix
  ([`results/arbitration_spotlight_t12_benchmark_v2/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_spotlight_t12_benchmark_v2/report/summary.md)),
  the theorem-1/theorem-2 story gets stronger and broader:
  `bayes_proxy = -0.1722`, `heuristic_adaptive = -0.0889`,
  `fixed_50 = 0.4035`, `always_parametric = 5.2420`,
  `always_context = 7.9943` across `174,080` examples on
  `ConflictBank`, `FaithEval`, `MemoTrap`, `NQ-Swap`, and `PopQA`.
- The spotlight-matrix headline is now statistically cleaner:
  Bayes beats the generic heuristic by `0.0833` regret with bootstrap CI
  `[0.0371, 0.1112]`.
- The spotlight-matrix benchmark-family read is now also explicit:
  `ConflictBank`, `FaithEval`, `MemoTrap`, and `NQ-Swap` are unanimous `5/5`
  Bayes-over-heuristic wins across the five model families, while `PopQA`
  remains the lone mixed family because of the Llama-70B outlier slice.
- The dedicated `PopQA` read is now explicit too:
  Bayes beats the generic heuristic by `0.0950` regret with benchmark-level
  bootstrap CI `[0.0440, 0.1460]`, and the gain remains positive across low,
  mid, and high popularity bins.
- The dedicated `NQ-Swap` read is now explicit too:
  Bayes beats the generic heuristic by `0.1038` regret with benchmark-level
  bootstrap CI `[0.0829, 0.1250]`, while also beating `CoCoA` there by
  `0.0540`.
- The dedicated `Llama-3.1-8B` coverage read is now explicit too:
  on the completed five-benchmark Llama slice, Bayes beats the generic
  heuristic by `0.1108` regret with bootstrap CI `[0.0895, 0.1220]`.
- The dedicated `Llama-3.1-70B` frontier read is now explicit too:
  on the completed five-benchmark frontier Llama slice, Bayes beats the
  generic heuristic by `0.0602` regret on the count-weighted aggregate,
  while still beating `CoCoA` and `AdaCAD` in aggregate and exposing `PopQA`
  as the single visible outlier rather than a hidden failure.
- In the updated named-comparator read on that same matrix
  ([`docs/generated/arbitration_proxy_baseline_t12_v2.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/arbitration_proxy_baseline_t12_v2.md)),
  Bayes also beats the strongest named comparator:
  `Self-RAG = -0.1456`, `Astute RAG = -0.1396`, `MADAM-RAG = -0.1033`,
  `NWCAD = -0.0716`, `JuICE = -0.0800`, `CoCoA = -0.1278`,
  `AdaCAD = -0.1063`, and `CAD = -0.0790`, with a Bayes advantage of
  `0.0266` over `Self-RAG`.
- In the expanded theorem-3 proxy size-scaling matrix
  ([`results/arbitration_spotlight_t3_scaling_proxy_v2/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_spotlight_t3_scaling_proxy_v2/report/summary.md)),
  `bayes_proxy = -0.0774` versus `heuristic_adaptive = -0.0189`
  across `65,190` examples on `AmbigDocs`, `ConflictBank`, `FaithEval`,
  `RAMDocs`, and `WikiContradict`.
- That theorem-3 proxy matrix is also now statistically clean on the main
  comparison:
  Bayes beats the generic heuristic by `0.0585` regret with bootstrap CI
  `[0.0155, 0.0961]`.
- The theorem-3 proxy benchmark-family read is now explicit too:
  `AmbigDocs`, `ConflictBank`, `FaithEval`, and `RAMDocs` are unanimous `5/5`
  Bayes-over-heuristic wins, while `WikiContradict` is a unanimous negative
  exception on the proxy regret layer.
- The added optional baselines now have explicit theorem-3 proxy numbers too:
  `MADAM-RAG = -0.0232`, `NWCAD = -0.0290`, and `JuICE = -0.0595`,
  all still trailing Bayes even though `CoCoA = -0.0795` remains the honest
  near-tie baseline on that matrix.
- The live same-family Qwen theorem-3 read is stronger than the old mixed
  proxy stack on controlled conflict:
  final `Qwen2.5-7B` `ConflictBank` conflict reads
  `0.9856 -> 0.9849 -> 0.9693` versus
  no-conflict `0.0868 -> 0.0723 -> 0.0537`,
  while final `Qwen2.5-14B` now shows
  `0.9776 -> 0.9731 -> 0.9584` versus
  `0.0639 -> 0.0679 -> 0.0476`.
- The same completed Qwen sweep also gives the first same-family evidence for the
  rewritten two-regime story on `WikiContradict`:
  final `Qwen2.5-32B` conflict now reads
  `0.0945 -> 0.3520 -> 0.2635`, indicating long-CoT self-correction.
- The explicit cross-family verdict is now also settled:
  DeepSeek replicates the `7B -> 14B` `ConflictBank` asymmetry, but Qwen does
  not, so the universal asymmetry claim is false.
- The same final `Qwen2.5-32B` run still shows persistent controlled-conflict
  failure on `ConflictBank`:
  `0.9484 -> 0.9307 -> 0.8871`.
- The size-threshold read is now sharp enough to cite directly:
  `s* ~= 32B` for same-family `Qwen2.5` recovery on `WikiContradict` conflict,
  but no recovery threshold has appeared through `32B` on `ConflictBank`
  conflict.
- The new theorem-3 mitigation read is now also sharp enough to cite directly:
  on the finished 14B real-generation summary, conflict slices tolerate only
  about `0.52x` the do-no-harm `eta` of no-conflict slices. Confidence-only
  tempering can nearly recalibrate `WikiContradict` conflict
  (best proxy gap `0.0034`), but it cannot rescue `ConflictBank` conflict,
  whose best attainable proxy gap still bottoms out at `0.4820`.
- The theorem-3 wording itself is now sharpened too:
  the cleanest statement is an RLVR-conditioned misspecification law rather
  than a universal scale law.
- The corrected broad-wave oracle-vs-model arbitration gap remains visibly
  nontrivial: mean absolute gap `0.1969`, mean KL `1.2288`.
- The expanded spotlight matrix still shows a much larger conflict-vs-no-conflict
  calibration movement in the proxy stack:
  `-0.1321` versus `-0.0212`.
- The theorem-3 claim should now be written in its finished revised form:
  long-CoT calibration failure is benchmark-dependent, with naturalistic
  contradiction showing partial recovery and controlled conflict showing
  persistent large-model failure.

So the current status is:

- theorem-1/theorem-2-style arbitration evidence: **landed**
- theorem-3 original monotone conflict-only claim: **rejected**
- theorem-3 rewritten two-regime claim: **landed**

Current blocker:

- there is no remaining headline blocker inside the current benchmark-backed
  paper core;
- the six-week playbook is now complete at the paper-core level;
- what remains are optional scope expansions rather than missing core results:
  checkpoint-family sweeps, broader external replications, and additional
  mitigation variants.

What is now in place:

- real-generation theorem-3 backend:
  [`src/knowledge_arbitration/real_generation.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/knowledge_arbitration/real_generation.py)
- focused runner:
  [`scripts/run_theorem3_real_generation.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_real_generation.py)
- theorem-3-specific report:
  [`scripts/report_theorem3_real_generation.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/report_theorem3_real_generation.py)
- local smoke artifact:
  [`results/theorem3_real_generation_mock_smoke/theorem3_report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/theorem3_real_generation_mock_smoke/theorem3_report/summary.md)
- focused Delta job submitted successfully:
  `2185966` `theorem3_real`

That gate is now closed by the finished 7B/14B DeepSeek traces and the
completed same-family Qwen sweep. The current paper headline is therefore live
rather than provisional.

## Real-generation update

The first real DeepSeek theorem-3 run (`2185966`) failed after `01:39:34`, but
it did enough work to give us partial real evidence.

Completed artifacts on Delta:

- `results/theorem3_real_generation_r1_7b/conflictbank_screening.jsonl`
- `results/theorem3_real_generation_r1_7b/conflictbank_screening_summary.json`
- `results/theorem3_real_generation_r1_7b/theorem3_generation_rows.jsonl`

What those partial rows already show:

- `WikiContradict` completed across `cot=0`, `128`, and `1024`
- `ConflictBank` screening completed
- `ConflictBank` generations are still incomplete

Current `WikiContradict` real-generation picture:

| Split | CoT | Accuracy | Mean confidence |
| --- | ---: | ---: | ---: |
| conflict | `0` | `0.2299` | `0.5492` |
| conflict | `128` | `0.2299` | `0.7264` |
| conflict | `1024` | `0.2011` | `0.6522` |
| no_conflict | `0` | `0.3143` | `0.5783` |
| no_conflict | `128` | `0.2171` | `0.7223` |
| no_conflict | `1024` | `0.2126` | `0.6677` |

That means:

- there is a real CoT-induced overconfidence effect;
- but on the completed partial slice it is **not** conflict-specific;
- so theorem 3 remains unproven in its original form.

The current honest strategy is:

1. finish `ConflictBank` real generations;
2. decide whether theorem 3 survives only as a sharper qualified claim or
   should be dropped entirely;
3. if `ConflictBank` also lacks a conflict-specific effect, freeze the paper
   around theorem 1 + theorem 2.

The active recovery job is now:

- `2190333` `theorem3_resume`

That job is intended to resume from the existing JSONL outputs rather than
restarting the finished `WikiContradict` rows.

## Theorem 3 landing update

The resumed real-generation run shifted theorem 3 away from the original
monotone-long-CoT framing and toward a stronger empirical variant:

- overconfidence peaks at an **intermediate** CoT budget;
- very long CoT partially self-corrects relative to that peak;
- the effect is real on actual `DeepSeek-R1-Distill-Qwen-7B` traces.

Completed `DeepSeek-R1-Distill-Qwen-7B` real-trace picture (`4200` rows):

| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap |
| --- | --- | ---: | ---: | ---: |
| WikiContradict | conflict | `0.2923` | `0.4825` | `0.4429` |
| WikiContradict | no-conflict | `0.2643` | `0.5038` | `0.4331` |
| ConflictBank | conflict | `0.5505` | `0.7531` | `0.5308` |
| ConflictBank | no-conflict | `0.0996` | `0.2754` | `-0.3724` |

Most important final deltas:

- `ConflictBank` conflict, `0 -> 128`: overconfidence-gap delta `+0.2026`
- `ConflictBank` conflict, `128 -> 1024`: overconfidence-gap delta `-0.2223`
- `WikiContradict` conflict, `0 -> 128`: overconfidence-gap delta `+0.1902`
- `WikiContradict` conflict, `128 -> 1024`: overconfidence-gap delta `-0.0396`

This is enough to say:

1. The original monotone theorem-3 headline is not the right one.
2. A revised theorem-3 headline is landing:
   `intermediate CoT causes the largest calibration failure, with partial
   long-CoT recovery`.
3. `ConflictBank` is the clearest support for this new statement so far.

Mechanism note from the finished 7B run:

- on `ConflictBank` conflict rows, context-match rate goes
  `0.4780 -> 0.5200 -> 0.8660`
- on `ConflictBank` no-conflict rows, context-match rate goes
  `0.4740 -> 0.4960 -> 0.9060`

So medium CoT is where **verbal overconfidence** peaks, while very long CoT is
where **source adoption** becomes most extreme. This separation is important:
theorem 3 is about the dynamics of calibration failure, not just monotone
context-following.

## 14B replication outcome

The first 14B theorem-3 replication attempt failed operationally because the
run wrote screening output into quota-limited home storage. The rerouted Delta
run completed successfully.

- job `2193155`
- model `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- failure reason: `OSError: [Errno 122] Disk quota exceeded`
- partial artifact preserved:
  `results/theorem3_real_generation_r1_14b/conflictbank_screening.jsonl`

Successful rerun:

- job `2193269`
- working tree:
  `/work/nvme/bgvi/adas17/tts-falsification`
- output root:
  `/work/nvme/bgvi/adas17/tts_results/theorem3_real_generation_r1_14b_v3`

Final completed 14B read (`4200` rows):

- `ConflictBank` conflict gap:
  `0.5876 -> 0.9449 -> 0.9513`
- `ConflictBank` no-conflict gap:
  `0.0691 -> 0.3108 -> 0.1032`
- `WikiContradict` conflict gap:
  `0.2717 -> 0.4516 -> 0.3750`
- `WikiContradict` no-conflict gap:
  `0.2963 -> 0.4229 -> 0.4164`

This locks in the theorem-3 scaling picture:

- the non-monotone intermediate-CoT peak still holds on `WikiContradict`;
- the 14B `ConflictBank` conflict slice is even harsher than the 7B run,
  showing a near-total confidence blow-up by `cot=128` that does not meaningfully
  recover by `cot=1024`.
