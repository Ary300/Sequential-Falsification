# Paper 2 Submission Polish Status

Status date: `2026-05-05` (late)

This note tracks the non-compute submission-polish items that can be closed
locally while the remaining Delta jobs are still blocked on cluster access.

## Done in the manuscript

- Added an explicit matched-base objective paragraph to the body:
  [paper/sections/experiments.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/experiments.tex)
  - now explains that the clean anchor is `Llama-8B`
  - states plainly that `DeepSeek-Llama-8B` is mixed
  - cites DPO inline rather than leaving the objective family unnamed

- Added the missing DPO citation:
  [paper/references.bib](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/references.bib)
  - `rafailov2024dpo`

- Updated the architecture presentation to include a real post-trace
  `\eta`-tempering flow figure:
  [paper/sections/method.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/method.tex)

- Added explicit appendix sections for:
  - reproducibility checklist
  - anonymization sweep
  - broader impact
  in [paper/appendix.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/appendix.tex)

- Tightened the conclusion slightly to reduce repeated forward-work prose:
  [paper/sections/conclusion.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/conclusion.tex)

- Trimmed repeated theorem-3 appendix prose and fixed the appendix compile
  issue caused by a raw `\rightarrow` outside math mode:
  [paper/appendix.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/appendix.tex)
- Fixed the local TikZ compile path by adding the missing `calc` library in
  [paper/main.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/main.tex)

## Local compile status

- local compile now succeeds with `tectonic`
- total PDF pages: `13`
- page layout from the local compile log:
  - main body sections occupy pages `1–8`
  - references occupy pages `9–10`
  - appendix occupies pages `11–13`

Read:

- This means the current paper is no longer failing to compile locally.
- It also means the body itself is not spilling deep into the appendix; the
  remaining page-budget question is about venue policy on whether references
  count toward the strict cap, not about a broken manuscript build.

## Already closed outside the manuscript

- positive-subset `\hat{\Delta}_+` reaggregation:
  [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)
- eta-pool distribution summary:
  [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)
- curvature proxy for the `C_{\mathrm{rob}}` shift story:
  [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)

## Still compute-blocked

- third independent matched-base RL pair beyond Llama lineage:
  `Mistral-7B` HDD trio is now actively running; `Gemma-2-9B` is additionally
  staged but blocked by gated-model access on Delta
- early-`t` `\hat{\rho}^\star` / polynomial-tail diagnostics:
  partial dense-window read is already recovered from the failed NVMe run, and
  the corrected HDD tail rerun is now actively running
- DeepSeek native rerun, mechanism probe, and curriculum audit:
  all are now live or queued on HDD-backed outputs
- larger-sample free-form `n=200` runs:
  completed, with Bayes tying `AdaCAD` on EM across `TriviaQA-open`,
  `NQ-open`, and `ASQA` while clearly beating plain `CAD`

## Bottom line

The paper-facing polish work is no longer the bottleneck. The remaining gaps
are the live compute completions and model-access constraints, not missing
citations, missing appendix sections, placeholder figures, or unclear
manuscript framing.
