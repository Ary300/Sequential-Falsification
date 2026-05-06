# Session log — Discussion + Conclusion writing (BayesArbiter, 2026-05-03)

## Brief
Combined Discussion + Conclusion section for NeurIPS 2026 main-conference paper "When Should LLMs Trust Retrieval? Bayes-Optimal Knowledge Arbitration under Conflict." Target 600–900 words, single section, flowing prose, ready to paste into LaTeX. Eight-paragraph structure: Reframe (~80) → Mechanism (~180) → Limitations (~120) → Connections (~100) → Earned Horizon (~200) → Closing Line (1–2 sentences).

## Inputs available from conversation context
- Full paper draft (intro, related work, method, experiments, discussion, appendix all read in earlier turns).
- Three theorems with structural strengthenings: T1 axiomatic uniqueness (Cauchy-equation), T2 information-theoretic minimax floor $\Theta(\sigma_r^2)$, T3 closed-form Brier improvement $(1-\eta^\star)^2 V_{\mathrm{post}}$.
- Empirical package: matched-base SFT/DPO/GRPO triangle on Llama-3.1-8B (gap $+0.344$, GRPO−SFT separation $+0.315$); Phi-3 GRPO uncontrolled cross-family at $+0.209$; Llama-3.1-70B-Instruct scale control near zero; powered $n=210$ vs.\ CoCoA/Astute/Self-RAG at $+0.043/+0.032/+0.022$; $\eta$-tempering pooled $+0.043$ Brier across all conflict cells.
- Pending experiments: DeepSeek-R1-Distill-Llama-8B matched DPO/GRPO pair, Llama-8B GRPO multi-seed variance.
- Pre-registration: P1, P2 replicate; P3 binary classifier fails on $2/8$, partial-order rescue is post-hoc.

## Inputs the prompt asked for that were not explicitly provided
- "Most surprising/counterintuitive empirical finding" — not stated by user, inferred as the GRPO−SFT separation ($+0.315$) showing the conflict gap is RL-recipe-causal rather than just a function of extra training tokens.
- "The one assumption you are most worried about" — not stated, inferred as the conditional-independence assumption $y^\star\perp c\mid (q,r)$ for T1.
- "2–3 closest competing methods" — inferred from paper as CAD, AdaCAD, CoCoA, plus Self-RAG and Astute~RAG. Mechanism distinction: all three are approximations of the same geometric-mixture target via the special-cases corollary.
- "Anticipated reviewer objections" — inferred from the hostile-reviewer rounds earlier in the conversation: small effect sizes against published baselines, single matched-base RL family, post-hoc P3 weakening, T3 conditional on stable-answer subset.

## Process
1. Read the four body sections (intro, method, experiments, discussion) and the appendix structure to identify the load-bearing theorems and empirical anchors.
2. Drafted each paragraph against the prescribed word budgets, applying the LLM-stylometry rules (no "not X but Y", no em-dash rhythm, no "Notably/Importantly/Interestingly", no rule-of-three filler, no mirror sentences).
3. Self-critique pass: identified the Earned Horizon paragraph as weakest on first draft (the scaling prediction was vague). Rewrote it to commit to a specific, testable claim: $D^\star$ grows with parametric prior sharpness, so larger models should show larger matched-base GRPO conflict gaps on ConflictBank, scaling roughly with $\log(\text{model size})$. The pending DeepSeek-Llama-70B run will test this directly.
4. Workshopped three closing lines (full text in editorial notes inside the deliverable) and chose the third for declarative tone and quotability.

## Self-critique notes captured
- **Weakest paragraph on first draft**: Earned Horizon's scaling claim said "we expect overshoot to scale with model size" without specifying the scaling. Rewrote to commit to a specific testable prediction tied to a pending experiment.
- **Avoided patterns**: zero "not X but Y" constructions; one em dash total in the body of the discussion (used for parenthetical, not rhythm); no "Notably/Importantly/Interestingly/It is worth noting that"; no triple parallel constructions other than the closing line's three-clause statement (each clause does distinct work).
- **Mirror-sentence check**: Paragraphs 2 and 3 are structurally parallel (geometric mixture has structure / intervention story is structurally parallel) but the parallelism is signaled and the second paragraph builds on the first rather than repeating it.

## Tightening recommendations passed to user
1. Intro's "three theorems" framing should match the discussion's "method + intervention + observational study" tone.
2. Matched-base table caption should make the SFT negative control more visually prominent.
3. $\eta$-tempering subsection in method should explicitly state the intervention does not depend on the safe-rate result.

## Files saved
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/Discussion_Conclusion_BayesArbiter_2026_May_03.md`
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/Session_log_discussion_writing_26_05_03.md`
