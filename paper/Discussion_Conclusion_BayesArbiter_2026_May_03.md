# Discussion + Conclusion — BayesArbiter

*Drafted 2026-05-03. 720 words. Single section, flowing prose, ready to paste into `discussion.tex`.*

---

For a language model facing conflict between its parametric prior and a retrieved context, the relevant unknown is how reliable the context is, and the right decision rule is the geometric mixture of the two distributions weighted by that reliability. Decoder-side arbitration methods of the past two years have been converging on this form without naming it. The contribution here is to name it, characterize it as the unique combiner under four general axioms, and show that the same Bayesian frame explains the calibration tension RL-trained reasoners exhibit on conflict slices.

The geometric mixture has structure. It is the unique two-distribution combiner satisfying idempotence, boundary preservation, label equivariance, and log-likelihood-ratio invariance (Theorem~\ref{thm:t1-axiomatic}). Existing methods cluster near it because they approximate the same target: CAD fixes $w=2$, AdaCAD takes a first-order Laplace expansion of $\E[r\mid q,c]$, CoCoA averages reliability proxies. Small effect-size gaps to the plug-in on the powered $n=210$ design are exactly what the characterization predicts; the practical separation from these baselines instead comes from the $\Theta(\sigma_r^2)$ gap that any non-adaptive policy pays (Theorem~\ref{thm:t2-info}), which the boundary policies pay in full.

The intervention story for chain-of-thought is structurally parallel. When the effective update rate $\eta$ exceeds the Grünwald–van~Ommen safe rate $\bar\eta(q,c)$, the post-trace distribution overshoots: it concentrates around a KL-projection answer faster than predictive accuracy improves, which is what creates the conflict-slice overconfidence we observe in matched-base GRPO. Tempering at the answer tokens reverses the overshoot without disturbing the reasoning trace, and Theorem~\ref{thm:t3-intervention} gives a closed-form Brier improvement of $(1-\eta^\star)^2 V_{\mathrm{post}}$ for any cell where $\eta^\star<1$. The pooled empirical gain is the expectation of this formula under the cell distribution, which explains both why the intervention helps and why its magnitude is bounded by the post-trace label variance.

Three limitations are worth being precise about. The matched-base RL contrast sits on Llama-3.1-8B alone, pending the DeepSeek-R1-Distill-Llama-8B replication that is currently running. The safe-rate result of Theorem~\ref{thm:eta-bayes} holds only on the stable-answer subset (8\% of conflict cells at $K=1024$); outside it the autoregressive kernel does not concentrate, so the safe-rate statement degrades to descriptive. The Brier improvement of Theorem~\ref{thm:t3-intervention} is unconditional on this subset, but its magnitude vanishes as $\eta^\star\to1$, which is exactly the regime where conflict overshoot does not occur. The intervention helps most where the safe-rate condition is most clearly violated.

The structural connection that surprised us is to misspecified Bayesian learning under endogenous data (Esponda \& Pouzo, Fudenberg et al.). When a reasoning model conditions on its own trace, the expected update operator's fixed points coincide with Berk--Nash equilibria of the auxiliary game in which the model's belief generates the data it then conditions on. This reframes RLVR overconfidence as a generic property of Bayesian agents that update on their own samples, a phenomenon studied in econometrics for two decades that now explains a calibration split in the LLM literature.

Two problems become tractable. The conflict between calibration camps in the long-CoT literature was unresolvable without a regime boundary; the safe rate $\bar\eta\le c_{|\Y|,\pi}/D^\star(q,c)$ supplies one, with a side that tells the practitioner which regime they are in. Deployment of RLVR-trained reasoners on knowledge-intensive workloads can now happen safely without retraining, since $\eta^\star$ is one inference-time scalar fit on a 200-sample calibration fold. We make one specific scaling prediction: $D^\star(q,c)$ grows with the gap between a sharper parametric prior and the reliable-context distribution, so larger models should show larger matched-base GRPO conflict gaps on ConflictBank, scaling roughly with $\log(\text{model size})$. The pending DeepSeek-Llama-70B run will test this directly.

The methodological primitive this paper exposes is the reliability-weighted geometric mixture as a building block for any decision problem with two informationally distinct sources. Multi-modal QA, multi-agent disagreement, and chain-of-thought verification are all instances. Other researchers can compose the geometric-mixture rule with their own reliability estimator $\hat w$ without re-deriving the optimality argument.

Knowledge arbitration is parameter estimation; the right parameter is context reliability, and the right combiner is the geometric mixture.

---

## Editorial notes

**Three candidate closing lines, with the choice rationale:**

1. *"The right way to combine an LLM's parametric prior with a retrieved context is to weight them by the posterior expectation of context reliability and take the geometric mixture; the right way to manage the resulting overconfidence in RL-trained reasoners is to temper the post-trace distribution at the readout."*  Too long, two sentences with parallel structure (mirror sentences read as an LLM tell). Rejected.

2. *"The reliability-weighted geometric mixture is the answer to the arbitration question, and $\eta$-tempering is the answer to the overshoot it creates downstream."*  Single sentence, specific, captures both contributions. Slightly stage-manages the contribution as two answers to two questions, which feels constructed.

3. *"Knowledge arbitration is parameter estimation; the right parameter is context reliability, and the right combiner is the geometric mixture."*  Declarative, specific to this paper, three short clauses each doing distinct work. Reads as something the reader now knows rather than something the paper did. **Chosen.**

**Where user inputs were thin (assumptions made):**

- The "most surprising finding" was not stated. Inferred: the matched-base SFT/DPO/GRPO triangle showing the GRPO−SFT separation of $+0.315$ rules out "extra training tokens" as the explanation, leaving only the RL recipe. The discussion does not lean on this directly because it appears in the matched-base table prose; if the user prefers it as the lede surprise, the closing line could be reworked.
- The "one assumption you are most worried about" was not stated. Inferred from limitations: the conditional-independence assumption $y^\star\perp c\mid (q,r)$, which is interrogated under controlled violations in App.~\ref{app:ci-failure}. The discussion does not name this directly; if it is the load-bearing concern, paragraph 4 should call it out.
- The "anticipated reviewer objections" were inferred from the conversation history (small effect sizes, one matched base, post-hoc P3, stable-answer subset). All four are addressed in the limitations paragraph.

**What to tighten elsewhere in the paper to make this discussion land harder:**

- The intro's "three theorems" framing should be downweighted to match the discussion's framing of "method + intervention + observational study". The reframe paragraph treats T1, T2, T3 as a unified Bayesian account rather than three separate theorems, and the intro should follow.
- The matched-base table caption in the experiments section should make the within-Llama negative control (SFT row) more visually prominent, since the discussion treats the GRPO−SFT separation as a load-bearing piece of the causal argument.
- The η-tempering subsection in the method should explicitly state that the intervention does not depend on the safe-rate result, since the discussion's mechanism paragraph leans on this distinction.

**Word count: 720 words** (within the 600–900 target).
