# Paper 2 Submission Polish Status

Status date: `2026-05-04`

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

- Updated the architecture presentation to include the post-trace
  `\eta`-tempering box:
  [paper/sections/method.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/method.tex)

- Added explicit appendix sections for:
  - reproducibility checklist
  - anonymization sweep
  - broader impact
  in [paper/appendix.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/appendix.tex)

- Tightened the conclusion slightly to reduce repeated forward-work prose:
  [paper/sections/conclusion.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/conclusion.tex)

## Already closed outside the manuscript

- positive-subset `\hat{\Delta}_+` reaggregation:
  [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)
- eta-pool distribution summary:
  [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)
- curvature proxy for the `C_{\mathrm{rob}}` shift story:
  [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)

## Still compute-blocked

- third independent matched-base RL pair beyond Llama lineage:
  `Mistral-7B` trio is launched but needs live Delta results
- early-`t` `\hat{\rho}^\star` / polynomial-tail diagnostics:
  dense tail jobs are staged but not harvested
- DeepSeek native rerun, mechanism probe, and curriculum audit:
  all launchers exist, but cluster access is still blocked by Delta login
- larger-sample free-form `n=200` runs:
  staged and previously submitted, but final results still depend on Delta

## Bottom line

The paper-facing polish work is no longer the bottleneck. The remaining gaps
are the live compute items, not missing citations, missing appendix sections,
or unclear manuscript framing.
