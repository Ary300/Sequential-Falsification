# Knowledge Arbitration Scope and Status

This file is a scope ledger for the repo as of `2026-04-29`. It distinguishes what is already finished, what exists locally but is not yet pushed, what is still running on Delta, and what remains outside the current empirical package.

## 1. What Is Already Finished

The following are complete and already summarized in the repo:

- Theorem 1 headline package
- Theorem 2 headline package
- Theorem 3 rewritten two-regime package
- eta-tempered decoding method result
- synthetic oracle experiment
- Bayes component ablation
- confidence-head pilot
- post-hoc calibration baseline comparison
- MQuAKE multi-hop proxy note
- retrieval-backed WikiContradict BM25 demo
- extended Delta wave completion summary
- RLVR validation note
- Yoon contrast note

The best single summary artifact is:

- [knowledge_arbitration_headline_bundle.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_headline_bundle.md)

## 2. Current Empirical Scope

### 2.1 Model-family coverage

Completed current package:

- Llama
- Qwen
- DeepSeek
- Mistral
- Gemma
- closed-model API slice

Playbook status row:

| Item | Target | Current | Status |
|---|---|---|---|
| Model families | `5` | `13` wired models across Llama / Qwen / DeepSeek / Mistral / Gemma plus closed-model API slice | `done` |

### 2.2 Benchmark coverage

Completed current package covers:

- `ConflictBank`
- `WikiContradict`
- `PopQA`
- `NQ-Swap`
- DynamicQA-family extensions
- `HotpotQA`
- `TriviaQA`
- `TabMWP`
- `GPQA`
- `CLIMATEX`
- `MQuAKE-Remastered` for the auxiliary multi-hop note

Playbook status row:

| Item | Target | Current | Status |
|---|---|---|---|
| Benchmarks | `8-10` | `10` wired benchmarks including the conflict, QA, and calibration stack | `done` |

### 2.3 Baseline coverage

Completed user-facing baseline panel includes:

- `CAD`
- `AdaCAD`
- `CoCoA`
- `Self-RAG`
- `Astute RAG`
- `JuICE`
- `NWCAD`
- `MADAM-RAG`
- `CRAG`
- heuristic adaptive
- simulated model
- fixed-trust policies

Playbook status row:

| Item | Target | Current | Status |
|---|---|---|---|
| Baselines | `11-12` | `15` wired baselines, with all headline comparators surfaced in notes | `done` |

### 2.4 Seed coverage

| Item | Target | Current | Status |
|---|---|---|---|
| Seeds | `3` | Explicit seeds `[42, 43, 44]` in the completed extended wave | `done` |

## 3. Current Live Delta Status

### 3.1 Running theorem-3 audit wave

As of the latest check, these jobs are still active:

Running:

- `2215664`
- `2215665`
- `2215666`
- `2215667`
- `2215668`
- `2215669`
- `2215670`
- `2215671`
- `2215672`
- `2215673`
- `2215674`
- `2215677`
- `2215678`
- `2215679`
- `2215680`

Pending:

- `2215675`
- `2215676`
- `2215681`

Pending reason:

- `QOSGrpBillingMinutes`

Interpretation:

- these jobs are submitted correctly
- many are running normally and writing partial row files
- none of these Tier A/B/C audit runs has yet produced a final completed theorem-3 summary artifact

### 3.2 What the live wave is meant to add

The running audit wave is not the core theorem-1/2 package. It is a theorem-3 strengthening wave intended to add:

- denser CoT grids
- more seeds at theorem-3 scale
- stronger Qwen controls
- 70B length sweeps
- temperature sensitivity
- pending higher-scale or alternate-family checks

Until these jobs finish, they should be treated as in-progress scope rather than completed headline evidence.

## 4. Artifact Inventory

### 4.1 Core paper-facing summaries

- [knowledge_arbitration_headline_bundle.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_headline_bundle.md)
- [PAPER_HEADLINE_DRAFT.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/PAPER_HEADLINE_DRAFT.md)
- [KNOWLEDGE_ARBITRATION_RESULTS_TRACKER.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/KNOWLEDGE_ARBITRATION_RESULTS_TRACKER.md)

### 4.2 Detailed support artifacts already on disk

- [theorem3_eta_tempered_method_result.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_eta_tempered_method_result.md)
- [theorem3_confidence_head_pilot_result.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_confidence_head_pilot_result.md)
- [theorem3_calibration_baselines.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_calibration_baselines.md)
- [synthetic_oracle_convergence.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/synthetic_oracle_convergence.md)
- [bayes_component_ablation_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/bayes_component_ablation_note.md)
- [mquake_multihop_compounding_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/mquake_multihop_compounding_note.md)
- [wikicontradict_bm25_rag_demo.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/wikicontradict_bm25_rag_demo.md)
- [yoon_real_contrast_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/yoon_real_contrast_note.md)
- [delta_extended_wave_completion_summary.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/delta_extended_wave_completion_summary.md)

### 4.3 This pass’s additional scope files

- [knowledge_arbitration_results_detailed.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_results_detailed.md)
- [knowledge_arbitration_methodology_detailed.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_methodology_detailed.md)
- [knowledge_arbitration_scope_detailed.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_scope_detailed.md)

## 5. Git and Publish Scope

### 5.1 Local branch status

At the time of this pass:

- branch: `main`
- local branch was already `51` commits ahead of `origin/main` before adding the three new markdown files

That means pushing now is not just today’s documentation change. It updates GitHub with the whole local result-history that has accumulated on `main`.

### 5.2 Large-file audit

The repo contains several very large tracked result files, including files at approximately:

- `56M`
- `70M`
- `75M`
- `549M`
- `1.8G`

Important nuance:

- those files exist in the repo
- but the unpublished commit range `origin/main..HEAD` did **not** show any newly introduced >`100 MB` blobs during the object audit

That means:

- a normal `git push` may still succeed
- if it fails, the likely reason would be remote history policy or pre-existing oversized content handling, not a brand-new giant blob added in this final documentation pass

If push fails due to large-object policy, the fallback is to move the blocked artifact set to Hugging Face or another artifact store and keep the repo on compact summaries.

## 6. Honest Remaining Work

### 6.1 Empirical work that is still in progress

- the live theorem-3 Tier A/B/C audit wave

### 6.2 Empirical work not yet run

- full RLCR-style retraining, if we want a stronger training-time fix beyond the current confidence-head pilot

### 6.3 Non-empirical work not covered by this scope file

- proof write-up and appendix polishing
- external outreach emails
- arXiv submission packaging

## 7. Practical Read

If the question is “what can we claim right now without bluffing,” the answer is:

- the theorem-1/2 package is complete and strong
- the rewritten theorem-3 package is real and paper-usable
- the method story exists and has a real result
- the auxiliary deployment-style additions are done
- the only major unfinished empirical block is the still-running theorem-3 audit expansion on Delta
