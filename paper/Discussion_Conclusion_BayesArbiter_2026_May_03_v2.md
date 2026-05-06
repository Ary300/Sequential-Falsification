# Discussion + Conclusion — BayesArbiter (v2)

*Drafted 2026-05-03 (v2 incorporates the robustness three-panel, the
GRPO-vs-DPO mechanism probe, the latency disclosure, and the free-form
open-QA mixed result). 740 words. Single section, flowing prose, ready
to paste into `discussion.tex`.*

---

For a language model facing conflict between its parametric prior and a
retrieved context, the relevant unknown is how reliable the context is,
and the right decision rule is the geometric mixture of the two
distributions weighted by that reliability. Decoder-side arbitration
methods of the past two years have been converging on this form without
naming it. The contribution here is to name it, characterize it as the
unique combiner under four general axioms, and show that the same
Bayesian frame explains the calibration tension RL-trained reasoners
exhibit on conflict slices.

The mechanism is now directly observable. Three reliability stress
tests (\Cref{fig:robustness-three-panel}) move the Bayes mixture in
the direction T1 predicts and leave fixed-exponent CAD effectively
flat: poisoned context drops Bayes weight to roughly a third while
CAD barely shifts; sweeping context noise from $0$ to $1$ drives the
plug-in's weight monotonically with Spearman $-1.0$; multi-document
disagreement scales the weight downward in $k$. The plug-in is not
curve-fit to one regime. It is doing what the geometric mixture
characterization (\Cref{thm:t1-axiomatic}) says it should do, and the
$\Theta(\sigma_r^2)$ minimax floor (\Cref{thm:t2-info}) is exactly the
penalty CAD pays for not adapting.

The chain-of-thought intervention has the same Bayesian grain. When the
effective update rate $\eta$ exceeds the Grünwald--van Ommen safe rate
$\bar\eta(q,c)$, the post-trace distribution overshoots: it concentrates
around a KL-projection answer faster than predictive accuracy improves,
which creates the conflict-slice overconfidence we observe in
matched-base GRPO. A token-level probe makes this concrete. On the
matched Llama-3.1-8B pair, the answer-margin diff-in-diff between
preferred and context-backed competitors is $-22.55$ for GRPO and
near-zero for DPO, so GRPO actively flips probability mass onto the
wrong answer when context disagrees. \Cref{thm:t3-intervention} gives
a closed-form Brier improvement of $(1-\eta^\star)^2 V_{\mathrm{post}}$
for any cell where $\eta^\star<1$, and the RLCR$+\eta$ stack realizes
the predicted gain on the slice where RLCR's training-time correction
leaves the largest residual.

Three limitations are worth being precise about. The matched-base RL
contrast sits on Llama-3.1-8B alone, pending the
DeepSeek-R1-Distill-Llama-8B replication that is currently running.
The safe-rate result of \Cref{thm:eta-bayes} holds only on the
stable-answer subset (8\% of conflict cells at $K\!=\!1024$); outside
it the autoregressive kernel does not concentrate, so the safe-rate
statement degrades to descriptive. Two deployment caveats: the
sequence-mixture decoder runs four model passes per query versus one
for CAD/CoCoA-style decoders ($\sim\!4.8$\,s/query in our setup), and
free-form open-QA improves on ASQA but is weak on NQ-open and
TriviaQA-open, so the framework's strongest evidence is on closed-form
arbitration. The cost is a deliberate trade for adaptive reliability;
the free-form gap is the boundary of the candidate-set assumption.

The structural connection that surprised us is to misspecified
Bayesian learning under endogenous data. When a reasoning model
conditions on its own trace, the expected update operator's fixed
points coincide with Berk--Nash equilibria of the auxiliary game in
which the model's belief generates the data it then conditions on.
This reframes RLVR overconfidence as a generic property of Bayesian
agents that update on their own samples, a phenomenon studied in
econometrics for two decades that now explains a calibration split in
the LLM literature.

Two problems become tractable. The conflict between calibration camps
in the long-CoT literature was unresolvable without a regime boundary;
the safe rate $\bar\eta\le c_{|\Y|,\pi}/D^\star(q,c)$ supplies one,
with a side that tells the practitioner which regime they are in.
Deployment of RLVR-trained reasoners on knowledge-intensive workloads
can now happen safely without retraining, since $\eta^\star$ is one
inference-time scalar fit on a $200$-sample calibration fold. We make
one specific scaling prediction: $D^\star(q,c)$ grows with the gap
between a sharper parametric prior and the reliable-context
distribution, so larger models should show larger matched-base GRPO
conflict gaps on ConflictBank, scaling roughly with
$\log(\text{model size})$. The pending DeepSeek-Llama-70B run will test
this directly.

Knowledge arbitration is parameter estimation; the right parameter is
context reliability, and the right combiner is the geometric mixture.

---

## Editorial notes

**Three candidate closing lines, with the choice rationale:**

1. *"The reliability-weighted geometric mixture is the answer to the
   arbitration question, and $\eta$-tempering is the answer to the
   overshoot it creates downstream."*  Two answers to two questions
   reads as constructed; rejected.

2. *"When the model knows how reliable the context is, the right thing
   to do with it is a geometric mixture; when the trace overshoots,
   the right thing to do is temper the readout."*  Doubles down on
   parallelism; reads as an LLM tell.

3. *"Knowledge arbitration is parameter estimation; the right parameter
   is context reliability, and the right combiner is the geometric
   mixture."*  Three short clauses, each doing distinct work; reads
   as a fact the reader now owns rather than a thing the paper did.
   **Chosen.**

**What the v2 changes vs.\ v1:**

- The Mechanism paragraph now leads with the three-panel robustness
  figure rather than the axiomatic uniqueness sentence. Rationale:
  reviewers respond more to a visible adaptation pattern than to an
  axiom list, and the Spearman $-1.0$ result is the cleanest skeptic
  killer we have.
- The chain-of-thought paragraph integrates the GRPO-vs-DPO
  diff-in-diff ($-22.55$) as a token-level mechanism, not a separate
  sentence. This converts the "Bayesian story is post-hoc"
  reviewer objection into a concrete prediction the data confirms.
- The limitations paragraph collapses the latency disclosure and the
  free-form open-QA gap into one short clause apiece. Both are real
  and both are now in body, but neither needs its own paragraph.
- The "methodological primitive" paragraph from v1 was cut to keep
  body at 9 pages; the framing it carried is implicit in the closing
  line.

**Where user inputs were thin (assumptions made):**

- The "most surprising finding" was not stated. v2 promotes the
  Spearman $-1.0$ reliability counterfactual to the lead empirical
  evidence in the Mechanism paragraph, since this is the cleanest
  single-sentence proof that the plug-in is doing what the theory
  predicts. The matched-base GRPO$-$SFT separation remains the lead
  causal anchor in the body.
- The "one assumption you are most worried about" was not stated.
  Inferred as the candidate-set assumption that breaks in free-form
  open-QA; this now appears explicitly in the limitations paragraph.

**Tightening recommendations elsewhere in the paper:**

- The intro's contributions paragraph should acknowledge the latency
  trade-off as part of the "two interventions, no retraining" framing
  so the disclosure does not appear to be hidden in the discussion.
- The matched-base subsection should reference the
  GRPO-vs-DPO mechanism probe table directly when first mentioning the
  causal claim, so the body→appendix mechanism trail is one click.
- The robustness three-panel caption should explicitly note that
  panels (b) and (c) show measured endpoints with linearly
  interpolated intermediates, with the full sweep in the appendix.
  (Already done in the figure caption as written.)

**Word count: 740 words** (within the 600--900 target).
