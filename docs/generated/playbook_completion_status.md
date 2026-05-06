# Playbook Completion Status

## Verdict

The six-week core playbook is finished at the current paper-core level. What
remains after this point is scope expansion, not a missing headline-result
blocker.

## Week 1-2: Cross-family asymmetry check

- Status: done
- Artifact: `docs/generated/theorem3_cross_family_verdict.md`
- Headline result:
  - DeepSeek replicates the `7B -> 14B` `ConflictBank` asymmetry.
  - Qwen does not.
  - Universal cross-family asymmetry is false.
  - The stronger finished theorem-3 claim is benchmark-dependent two-regime
    behavior.

## Week 2-3: AdaCAD and CoCoA baselines

- Status: done
- Artifacts:
  - `docs/generated/arbitration_proxy_baseline_t12_v2.md`
  - `docs/generated/arbitration_proxy_baseline_t3_v2.md`
  - `docs/generated/adacad_cocoa_positioning_note.md`
- Headline result:
  - On the spotlight matrix, Bayes beats both `CoCoA` and `AdaCAD`.
  - On the theorem-3 proxy matrix, `CoCoA` is a near-tie and `AdaCAD` trails.
  - The paper now has the required closest-cousin comparator coverage.

## Week 3-4: PopQA and NQ-Swap

- Status: done
- Evidence:
  - `PopQA` and `NQ-Swap` are included in the completed spotlight matrix.
  - The expanded spotlight matrix covers `ConflictBank`, `FaithEval`,
    `MemoTrap`, `NQ-Swap`, and `PopQA`.
- Headline result:
  - The Bayes-vs-heuristic regret gap on that completed matrix is `0.0833`
    with bootstrap CI `[0.0371, 0.1112]`.

## Week 4-5: T3 rewrite

- Status: done
- Artifacts:
  - `paper/sections/method.tex`
  - `docs/KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md`
  - `docs/generated/theorem3_eta_tempering_analysis.md`
- Headline result:
  - The theorem is now written as an `eta`-generalized-Bayes /
    Berk-Nash-style transport claim.
  - Conflict slices tolerate only about `0.52x` the do-no-harm `eta` of
    no-conflict slices.

## Week 5-6: Killer figure

- Status: done
- Artifact:
  - `figures/spotlight_killer/spotlight_killer_figure.svg`
- Headline result:
  - The figure package now contains regret bars, conflict-density behavior,
    reliability comparison, and the two-regime theorem-3 curves in one panel.

## Statistical backbone

- Spotlight matrix Bayes-vs-heuristic CI: `[0.0371, 0.1112]`
- Theorem-3 proxy matrix Bayes-vs-heuristic CI: `[0.0155, 0.0961]`

Those are the two non-negotiable confidence intervals from the playbook, and
both exclude zero.

## Honest remaining work

- More external replications can still raise confidence.
- More models and benchmarks can still broaden scope.
- Additional mitigation variants can still improve the theorem-3 mechanism
  section.

None of those are required to say the six-week playbook is finished with
headline results.
