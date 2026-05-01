# Theorem 3 Scope And Framing Note

This note records the paper-side fix for the main reviewer-risk on theorem 3.

## Core Reframing

Theorem 3 should not be presented as having the same formal status as
theorems 1 and 2.

- Theorem 1 is a direct Bayes-optimality statement inside a defined decision
  family.
- Theorem 2 is a direct fixed-policy minimax lower-bound statement.
- Theorem 3 is best read as a structurally motivated misspecification account
  for reasoning-time calibration under endogenous evidence.

The operative language now used in the paper is:

- generalized-Bayes and Berk--Nash machinery provide a structural analogy for
  autoregressive decoding under endogenous evidence
- the theorem-3 value comes from combining that structural account with real
  trace diagnostics
- the empirical proxy `\hat{\eta}_{eff}` is directional rather than
  point-identifying

## Explicit Scope Limits

The body and appendix now state three practical boundaries directly:

1. No completed head-to-head RLCR number yet.
   Current evidence includes confidence-only `\eta`-tempering and lighter
   training-time calibration pilots, but not a finished Damani-style
   reward-redesign comparison in the paper body.

2. Retrieval evidence is deployment-motivated, not production-scale.
   The current demo uses bounded Wikipedia-backed retrieval rather than a live
   continuously refreshed retrieval stack.

3. The theorem-3 package is English-only.
   Benchmarks, prompts, and calibration artifacts are all English-only in the
   current paper.

## Cross-Family Caution

The paper now also states the cross-family caution explicitly:

- DeepSeek-R1-Distill provides the clearest saturated-conflict evidence
- the same 7B-to-14B asymmetry does not replicate cleanly in Qwen through 32B
- the stable claim is therefore benchmark-dependent and training-family-
  conditioned, not a universal scale law
- R1-Distill is a distillation product, so this is not oversold as a clean
  GRPO-versus-DPO causal isolation

## Where The Fix Landed

- [main.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/main.tex)
- [introduction.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/introduction.tex)
- [method.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/method.tex)
- [experiments.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/experiments.tex)
- [conclusion.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/conclusion.tex)
- [appendix.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/appendix.tex)
