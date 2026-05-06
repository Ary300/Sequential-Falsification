# Introduction — BayesArbiter

*Drafted 2026-05-03. 770 words. Continuous prose, ready to paste into `introduction.tex`. The Elon-Musk opener is preserved as the Hook per user request.*

---

A 2023 language model that memorized ``Twitter's CEO is Elon Musk'' will see a 2024 article saying ``Linda Yaccarino.'' A medical assistant will be asked about a drug whose label changed since training. A retrieval pipeline will inject a poisoned passage. In each case the model carries a parametric prior $p_\theta(y\mid q)$ baked in at training, conditions on a retrieved context $p_{\ctx}(y\mid q,c)$, and if it produces a chain of thought, also listens to itself across $K$ reasoning steps before emitting an answer. Any of these voices can be wrong, and they often disagree. The system has to arbitrate, and the rule it uses is a major lever on what the user sees. Today that rule is set by hand.

The arbitration rule silently fixes hallucination rate, calibration on the slice where sources disagree, and worst-case behaviour under poisoned or stale retrieval. The same rule fires on every query in a deployed RAG stack. Production systems either trust retrieval unconditionally, trust the parametric model unconditionally, or interpolate via tuned thresholds and learned controllers~\citep{mallen2023popqa,asai2024selfrag,yan2024crag}. Decoder-side methods like Context-Aware Decoding~\citep{shi2024cad} and its variants AdaCAD~\citep{wang2025adacad} and CoCoA~\citep{khandelwal2025cocoa} are sharper but heuristic. The calibration literature on reasoning models has split into two camps that look contradictory: longer chain-of-thought makes models better calibrated on standard QA~\citep{yoon2025confidence} and worse on harder or misspecified tasks~\citep{halawi2024overthinking,damani2025rlcr}.

None of the existing methods is derived from a posterior over how reliable the context actually is. CAD and AdaCAD weight the context-conditional distribution against the prior using fixed or first-order-corrected exponents that the authors do not interpret as a Bayes-optimal action. CoCoA averages reliability proxies but provides no consistency guarantee for the expected reliability. Survey work~\citep{xu2024knowledgeconflicts} flags that fixed trust in either source is suboptimal but stops short of identifying the optimal rule. The calibration tension above shares this root cause: no theory tells the practitioner which regime they are in, so the same chain-of-thought scaling argument supports both ``reasoning helps calibration'' and ``reasoning hurts calibration'' depending on which slice of the literature you read.

BayesArbiter treats knowledge arbitration as parameter estimation (\Cref{fig:architecture}). We introduce a latent reliability $r\in[0,1]$ with prior $\pi(r)$ informed by observable signals (BM25, entity popularity, semantic entropy). Within the log-linear answer family, the risk-minimizing predictive distribution is the geometric mixture $p_\theta^{1-w^\star}p_{\ctx}^{w^\star}$ with $w^\star=\E[r\mid q,c]$, and a four-axiom characterization shows this combiner is unique among admissible two-distribution rules even without the log-linear assumption. For chain-of-thought, BayesArbiter models the trace as endogenous Bayesian evidence and shows that when the effective update rate exceeds the Grünwald--van~Ommen safe rate, the post-trace distribution overshoots and creates the conflict-slice overconfidence observed in RL-trained reasoners. Tempering at the readout reverses the overshoot with one inference-time scalar.

On a 75-cell spotlight matrix across five conflict benchmarks and thirteen models, the geometric-mixture plug-in beats CoCoA, Astute~RAG, and Self-RAG by $+0.043$, $+0.032$, and $+0.022$ regret on a powered $n=210$ matched design, all CIs strictly above zero. At matched-base Llama-3.1-8B, varying the post-training recipe from SFT to GRPO separates the conflict-slice ECE by $+0.315$, which isolates the failure to the RL recipe rather than to extra training tokens. One held-out tempering scalar drops Brier from $0.903$ to $0.505$ and accuracy from $0.037$ to $0.440$ on the worst slice, with a $+0.043$ pooled Brier improvement across all conflict cells. The overshoot mechanism turns out to be a Berk--Nash equilibrium of the expected gen-Bayes update, which connects RLVR overconfidence to a result in misspecified Bayesian learning studied in econometrics for two decades.

\textbf{(1)} The geometric mixture is the unique two-distribution combiner under four general axioms (\Cref{thm:t1-axiomatic}); within the log-linear family the optimal weight is $\E[r\mid q,c]$ (\Cref{thm:bayes-arbitration}). CAD, AdaCAD, CoCoA, Self-RAG, Astute~RAG, and JuICE fall out as approximations of the same target. \textbf{(2)} An information-theoretic minimax floor (\Cref{thm:t2-info}): any non-adaptive policy pays $\Omega(\sigma_r^2)$ excess regret, matched by the plug-in upper bound. \textbf{(3)} A closed-form Brier improvement for $\eta$-tempering (\Cref{thm:t3-intervention}) holding on every cell, with the safe-rate result (\Cref{thm:eta-bayes}) reduced to a corollary explaining when the optimum is interior. \textbf{(4)} A matched-base SFT/DPO/GRPO causal anchor at Llama-3.1-8B with eight cross-family controls, and three pre-registered held-out predictions of which P1 and P2 replicate as registered.

---

## Figure 1 brief

Figure 1 (the BayesArbiter pipeline) shows three inputs (query, retrieved context, chain-of-thought trace) producing three corresponding distributions ($p_\theta$, $p_{\ctx}$, post-trace). A reliability plug-in $\hat w(c)=\widehat{\E}[r\mid s(q,c)]$ drives the geometric mixture that combines $p_\theta$ and $p_{\ctx}$, and the post-trace distribution is $\eta$-tempered for RL-trained reasoners. The takeaway in 10 seconds: BayesArbiter is two inference-time interventions on top of an existing decoder, both fit on small held-out splits with no retraining required. The figure should make it visually obvious that the trace branch is independent of the retrieval branch, since this independence is what the appendix's per-token chain-mixture corollary relies on.

---

## Editorial notes

**Three candidate opening sentences (with chosen rationale):**

1. *"A 2023 language model that memorized ``Twitter's CEO is Elon Musk'' will see a 2024 article saying ``Linda Yaccarino.''"*  Concrete, dated, named entities, sets up the conflict question without abstraction. Forces the reader to engage with a specific case before the formal setup. **Chosen** (and matches the user's stated preference).

2. *"When a language model's training memory contradicts the document just retrieved for it, the rule it uses to arbitrate is set by hand."*  Direct, problem-statement style. Less surprising; reads as the second sentence of someone else's intro. Rejected as Hook because it telegraphs the Stakes paragraph.

3. *"Production retrieval-augmented systems trust their parametric prior, trust their retrieval, or split the difference with tuned thresholds, and the choice silently fixes the hallucination rate."*  Specific to RAG audience but loses the non-specialist; reads as Para 2 material. Rejected as Hook for the same reason as #2.

**Where user inputs were thin (assumptions made):**

- **Seed-crystal sentence** was not explicitly stated. Inferred as: ``Knowledge arbitration is parameter estimation; the right parameter is context reliability, and the right combiner is the geometric mixture.'' The Method Sketch paragraph leans on this implicitly. If the user prefers a different framing (e.g., ``LLM arbitration is endogenous Bayesian inference''), the seed crystal in Para 4 should change.
- **Most surprising finding** was not specified. Two candidates: (a) the matched-base SFT/DPO/GRPO triangle showing the GRPO$-$SFT separation of $+0.315$ rules out ``extra training tokens'' as the explanation; (b) the RLVR-overconfidence-as-Berk--Nash connection. The Results paragraph leads with (a) and ends with (b) for narrative payoff. Either could be promoted to the Hook.
- **Closest competitor mechanism distinction** was inferred from the special-cases corollary: CAD = $w=2$, AdaCAD = first-order Laplace, CoCoA = non-Bayesian ensemble. This appears in Para 3 (Gap) rather than Para 4 (Method) because it is the Gap argument.
- **Audience** assumed: NeurIPS LLM/NLP/RAG primary, Bayesian decision theory and online learning secondary. The connection to misspecified Bayesian learning in econometrics in Para 5 is the bid for the secondary audience.
- **Figure 1**: the existing architecture figure already exists in `figs/fig_architecture.pdf` and is referenced as `\Cref{fig:architecture}`. The Figure 1 brief above describes what the existing figure shows, not a new figure.

**Tightening recommendations for the rest of the paper to make this intro hold up:**

- The contributions paragraph claims that ``CAD, AdaCAD, CoCoA, Self-RAG, Astute~RAG, and JuICE fall out as approximations of the same target.'' The special-cases corollary in `method.tex` should explicitly enumerate this mapping for each method, and the appendix should cite the original paper for each. Currently CoCoA is hand-waved as ``non-Bayesian ensemble of reliability proxies'' without naming which proxies; this could be tightened.
- The Results teaser claims ``the failure to the RL recipe rather than to extra training tokens'' on the basis of the SFT row. The matched-base table in `experiments.tex` should make the SFT row visually distinct from DPO/GRPO (e.g., a header row or separator) since it carries the negative-control argument that the intro relies on.
- The Berk--Nash connection in Para 5 is foreshadowed in `method.tex` (\Cref{prop:berk-nash-reduction}) but not discussed in the Discussion. If the intro promises this connection as a surprise, the Discussion should land it as a Connections paragraph, not just a passing reference.

**Word count: 770 words** (within 600--800 target).
