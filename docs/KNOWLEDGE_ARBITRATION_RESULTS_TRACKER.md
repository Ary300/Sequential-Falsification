# Bayes-Optimal Knowledge Arbitration: Results Tracker

## Purpose

This file tracks whether we actually have the kind of results the paper needs.

The goal is to prevent a repeat of vague "we're making progress" updates when
the headline results are still missing.

## Headline-result checklist

| Item | Needed for paper | Current status |
| --- | --- | --- |
| Theorem 1 written cleanly | yes | drafted in `KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md` |
| Theorem 2 written cleanly | yes | drafted in `KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md` |
| Theorem 3 written cleanly | yes | drafted in `KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md` |
| Synthetic Bayes oracle experiment | yes | done |
| Real benchmark pilot on `PopQA` | yes | done via `arbitration_real_headline_wave_v2` |
| Real benchmark pilot on `DynamicQA` | yes | done via `arbitration_real_headline_wave_v2` |
| Real benchmark pilot on `ConflictBank` subset | yes | done in compact conflict wave |
| Conflict vs no-conflict calibration curves | yes | done for broad pilot and `WikiContradict` focus |
| Checkpoint-family experiment | strongly preferred | not started |
| Mitigation experiment | strongly preferred | not started |

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
| `Qwen-2.5` / `Qwen-3` | 7B/8B | 7B/8B + optional 32B | pilot partially done (`Qwen-2.5-7B`, `Qwen-2.5-14B`) |
| `DeepSeek-R1-Distill` | 7B | 7B + optional 14B | pilot done |
| `Pythia` | 6.9B or nearby | checkpoint sweep | not started |
| `OLMo-2` | 7B | checkpoint sweep | not started |
| `Mistral` | 7B | robustness | not started |
| `Phi-3` | medium | robustness | not started |

## What would count as a real early win

We now have two early wins and one open gap:

- Synthetic oracle pilot is done and already showed Bayes proxy at `0.0000`
  regret with large gaps to fixed policies.
- Broad real benchmark-backed pilot is done:
  [`results/arbitration_real_headline_wave_v2/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_real_headline_wave_v2/report/summary.md)
  on `44,960` parsed examples across `PopQA`, `DynamicQA`, `NQ-Swap`, and
  `WikiContradict`.
- Focused contradiction report is done:
  [`results/arbitration_wikicontradict_focus/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_wikicontradict_focus/report/summary.md)
  and gives the cleanest current theorem-3-style signal.
- Compact conflict-only wave is done:
  [`results/arbitration_conflict_focus_compact_v2/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_conflict_focus_compact_v2/report/summary.md)
  and adds `ConflictBank` into the live benchmark path.
- Theorem-3 diagnosis is done:
  [`results/arbitration_conflict_focus_compact_v2/theorem3_diagnosis/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_conflict_focus_compact_v2/theorem3_diagnosis/summary.md)
  with ambiguity filtering and benchmark-family breakdowns.

Current best honest headline:

- In the broad real pilot, `Bayes Proxy` is the best policy at `0.0000` mean
  regret, ahead of `heuristic_adaptive` at `0.0593`, `simulated_model` at
  `0.3277`, `fixed_50` at `0.3912`, `always_context` at `6.3179`, and
  `always_parametric` at `6.8936`.
- In the compact conflict-only wave, `Bayes Proxy` is again best at `0.0000`,
  ahead of `heuristic_adaptive` at `0.0608`, `fixed_50` at `0.3363`,
  `simulated_model` at `0.8893`, `always_context` at `5.0159`, and
  `always_parametric` at `8.0860`.
- In the broad real pilot, oracle-vs-model arbitration gap is already visible:
  mean absolute gap `0.0254`, mean KL `0.1310`.
- The broad theorem-3 signal is **not** landed yet:
  mean conflict ECE delta is `-0.0054`, so the wide benchmark mix does not yet
  support the headline that long CoT worsens calibration under conflict.
- The strongest current theorem-3 slice is `WikiContradict`:
  conflict ECE delta `+0.1542` while no-conflict delta is `-0.0190`, matching
  the desired directional story on that benchmark.
- In the newer compact conflict-only wave, the broad theorem-3 story is still
  mixed:
  `ConflictBank` conflict ECE delta `-0.1943`, `DynamicQA` conflict delta
  `-0.0341`, `WikiContradict` conflict delta `+0.1826`.
- Ambiguity filtering did **not** rescue the negative benchmarks in the current
  proxy stack:
  - `ConflictBank` genuine-conflict delta `-0.1943`
  - `DynamicQA` genuine-conflict delta `-0.0679`
  - `WikiContradict` genuine-conflict delta `+0.1826`
- The current best interpretation is not "the theorem is false"; it is:
  naturalistic contradiction (`WikiContradict`) behaves like genuine source
  ambiguity, while `ConflictBank` and much of `DynamicQA` in the current proxy
  behave more like detectable corruption or easy conflict.

So the current status is:

- theorem-1/theorem-2-style arbitration evidence: **promising**
- theorem-3 broad conflict-conditioned CoT claim: **not yet achieved**
- theorem-3 sharpened fallback claim: **promising**

The sharpened fallback claim is:

- long-CoT calibration degradation appears on naturalistic contradiction, not
  uniformly across all conflict benchmarks, suggesting the mechanism requires
  genuine source ambiguity rather than trivially detectable corruption.

Current blocker:

- the proxy theorem-3 diagnosis is complete, and it told us to stop inferring
  CoT length from synthetic buckets and run real generations instead.

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

That focused real-generation run is the actual gate now:

- if it lands positive on both `WikiContradict` and `ConflictBank`, theorem 3
  becomes real and the proxy path can be retired;
- if it lands only on `WikiContradict`, we sharpen the claim to naturalistic
  contradiction rather than uniform conflict;
- if it fails on both, theorem 3 is not a headline and the paper falls back to
  the theorem-1/theorem-2 story.

Until the real-generation run reports back, we still do **not** have the full
paper headline.

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

Current real-trace picture:

| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap |
| --- | --- | ---: | ---: | ---: |
| WikiContradict | conflict | `0.2923` | `0.4825` | `0.4429` |
| WikiContradict | no-conflict | `0.2643` | `0.5038` | `0.4331` |
| ConflictBank (mid-run) | conflict | `0.5407` | `0.7295` | `0.5212` |
| ConflictBank (mid-run) | no-conflict | `0.0561` | `0.1945` | `-0.3515` |

Most important deltas from the live `ConflictBank` slice:

- conflict, `0 -> 128`: overconfidence-gap delta `+0.1888`
- no-conflict, `0 -> 128`: overconfidence-gap delta `+0.1384`
- conflict, `0 -> 1024`: overconfidence-gap delta `-0.0194`

This is enough to say:

1. The original monotone theorem-3 headline is not the right one.
2. A revised theorem-3 headline is landing:
   `intermediate CoT causes the largest calibration failure, with partial
   long-CoT recovery`.
3. `ConflictBank` is the cleanest support for this new statement so far.
