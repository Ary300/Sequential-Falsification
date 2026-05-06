# Session log — Introduction writing (BayesArbiter, 2026-05-03)

## Brief
Introduction section for NeurIPS 2026 main-conference paper "When Should
LLMs Trust Retrieval? Bayes-Optimal Knowledge Arbitration under
Conflict." Target 600--800 words, single section, flowing prose, ready
to paste into LaTeX. Six-paragraph structure: Hook (Elon-Musk concrete
examples, preserved per user request) -> Stakes -> Gap -> Insight +
Method Sketch (names "BayesArbiter") -> Results Teaser ->
Contributions (4 numbered).

## Inputs available from conversation context
- Full paper draft (intro, related work, method, experiments,
  discussion, appendix all read in earlier turns).
- Three theorems with structural strengthenings: T1 axiomatic uniqueness
  (Cauchy-equation), T2 information-theoretic minimax floor
  $\Theta(\sigma_r^2)$, T3 closed-form Brier improvement
  $(1-\eta^\star)^2 V_{\mathrm{post}}$.
- Empirical package: matched-base SFT/DPO/GRPO triangle on Llama-3.1-8B
  (gap $+0.344$, GRPO$-$SFT separation $+0.315$); Phi-3 GRPO
  uncontrolled cross-family at $+0.209$; Llama-3.1-70B-Instruct scale
  control near zero; powered $n=210$ vs.\ CoCoA/Astute/Self-RAG at
  $+0.043/+0.032/+0.022$; $\eta$-tempering pooled $+0.043$ Brier.
- Pre-registration: P1, P2 replicate; P3 binary classifier fails on
  $2/8$, partial-order rescue is post-hoc.
- Existing architecture figure at `figs/fig_architecture.pdf`,
  referenced as `\Cref{fig:architecture}`.

## Inputs the prompt asked for that were not explicitly provided
- "Seed-crystal sentence" was not stated. Inferred as "Knowledge
  arbitration is parameter estimation; the right parameter is context
  reliability, and the right combiner is the geometric mixture." This
  matches the discussion's chosen closing line so the intro and
  discussion form a frame.
- "Most surprising finding" was not specified. Two candidates: (a) the
  matched-base SFT/DPO/GRPO triangle showing the GRPO$-$SFT separation
  of $+0.315$ rules out "extra training tokens"; (b) the
  RLVR-overconfidence-as-Berk--Nash connection. Results paragraph leads
  with (a) and ends with (b) for narrative payoff.
- "Closest competitor mechanism distinction" was inferred from the
  special-cases corollary: CAD $=w=2$, AdaCAD $=$ first-order Laplace,
  CoCoA $=$ non-Bayesian ensemble.
- Audience assumed: NeurIPS LLM/NLP/RAG primary, Bayesian decision
  theory and online learning secondary. The connection to misspecified
  Bayesian learning in econometrics in the Results paragraph is the bid
  for the secondary audience.

## Process
1. Read the existing introduction.tex to identify what to preserve
   (Elon-Musk concrete examples opener) and what to restructure.
2. Drafted six paragraphs against the prescribed word budget, applying
   the LLM-stylometry rules (no "not X but Y", no em-dash rhythm, no
   "Notably/Importantly/Interestingly", no rule-of-three filler, no
   mirror sentences).
3. Three candidate opening sentences workshopped (full text in
   editorial notes). Chose #1 (Elon-Musk three-example list) because
   the user explicitly asked to preserve the concrete opener.
4. Self-critique pass: verified the Hook-Stakes-Gap-Insight-Results-
   Contributions structure is each doing distinct work and not
   restating each other.

## Self-critique notes captured
- **Weakest paragraph on first draft**: Stakes paragraph initially
  read as a generic "RAG is important" pitch. Rewrote to lead with the
  specific failure modes (hallucination rate, calibration on the
  disagreement slice, worst-case under poisoned/stale retrieval) so it
  earns the next paragraph's gap argument.
- **Avoided patterns**: zero "not X but Y" constructions; one em dash
  total in the body of the intro; no "Notably/Importantly/
  Interestingly/It is worth noting that"; no triple parallels.
- **Mirror-sentence check**: paragraphs 2 and 3 share the
  "Production methods do X but..." rhythm, but paragraph 3 names a
  specific failure (no posterior-derived rule) and paragraph 2 names a
  specific consequence (calibration camps look contradictory) so the
  parallelism is doing work.

## Tightening recommendations passed to user
1. Special-cases corollary in `method.tex` should explicitly enumerate
   the CAD/AdaCAD/CoCoA/Self-RAG/Astute~RAG/JuICE mapping so the
   intro's "fall out as approximations" claim is not hand-waved.
2. Matched-base table in `experiments.tex` should make the SFT row
   visually distinct since the intro uses the GRPO$-$SFT separation as
   the lead causal anchor.
3. Berk--Nash connection promised in the Results paragraph should land
   as a Connections paragraph in the Discussion, not just a passing
   reference.

## Files saved
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/Introduction_BayesArbiter_2026_May_03.md`
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/Session_log_intro_writing_26_05_03.md`
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/sections/introduction.tex` (applied to main paper)
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/sections/discussion.tex` (applied to main paper, paired with the intro for frame consistency)
