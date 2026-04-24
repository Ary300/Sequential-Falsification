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

- the present theorem-3 pipeline is still a proxy pipeline and does not contain
  raw generated reasoning traces, so it cannot answer the "longer reasoning vs
  padding/filler" question on its own.

Until that broad theorem-3 result lands across more than one hard conflict
benchmark, we still do **not** have the full paper headline.
