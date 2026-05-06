# Session log — Discussion + Conclusion writing (BayesArbiter, v2)

*2026-05-03. v2 supersedes the v1 draft after the cluster results
landed: poisoned-context, reliability noise ablation, multi-document
scaling, GRPO-vs-DPO answer-margin mechanism probe, latency profile,
and free-form open-QA evaluation.*

## Brief
Same as v1: combined Discussion + Conclusion section, 600--900 words,
ready to paste into LaTeX. Eight-paragraph flow: Reframe → Mechanism →
Limitations → Connections → Earned Horizon → Closing Line.

## Inputs new to v2 (vs.\ v1)
- Robustness three-panel figure
  (\Cref{fig:robustness-three-panel}): poisoned context (Bayes weight
  $0.901 \to 0.306$; CAD barely moves), reliability noise ablation
  (Spearman $=-1.0$), multi-doc scaling ($k\!=\!2 \to k\!=\!8$).
- GRPO-vs-DPO answer-margin diff-in-diff ($-22.55$ vs.\ near-zero)
  (\Cref{tab:mechanism-grpo-dpo}).
- RLCR$+\eta$ stack as the body headline cell (accuracy
  $0.063\to 0.531$, ECE $0.904 \to 0.431$); R1-14B Brier
  $0.903\to 0.505$ demoted to a parenthetical.
- Latency profile ($4$ passes vs.\ $1$, $\sim\!4.8$\,s/query;
  \Cref{tab:latency-profile}).
- Free-form open-QA mixed result (ASQA improved post-normalization
  fix, NQ/TriviaQA still weak; \Cref{tab:freeform-openqa}).

## Process
1. Read the integrated paper state after the cluster-results
   integration (RLCR$+\eta$ promoted, robustness paragraph and figure
   added, mechanism probe one-line added, latency and free-form
   disclosed in body limitations).
2. Re-drafted each paragraph to incorporate the new evidence without
   stretching past the 9-page body limit.
3. Self-critique pass: the Mechanism paragraph in v1 led with the
   axiomatic uniqueness sentence. v2 leads with the three-panel
   robustness evidence because Spearman $=-1.0$ is the single
   cleanest skeptic killer in the empirical package, and the
   axiomatic uniqueness still fires immediately afterwards.
4. The "methodological primitive" paragraph from v1 was cut to keep
   the body at 9 pages once the robustness figure was added; its
   framing is preserved implicitly in the closing line.

## Self-critique notes captured
- **Strongest paragraph in v2**: Mechanism. Each of the three
  reliability stress tests is one sentence and each maps to a
  specific theorem prediction. The skeptic's "post-hoc Bayesian
  framing" objection has nowhere to land once Spearman $=-1.0$ is
  on the page.
- **Riskiest paragraph in v2**: Limitations. The latency disclosure
  and free-form gap are now in body in a single compact clause apiece.
  The compression buys page room but a hostile reviewer could ask for
  more detail on either; both have full appendix backing.
- **Mirror-sentence check**: Paragraphs 2 and 3 are structurally
  parallel (mechanism for arbitration / mechanism for chain-of-thought)
  but each carries a distinct theorem and a distinct empirical anchor,
  so the parallelism is doing work rather than padding.

## Tightening recommendations passed to user
1. Intro should acknowledge the latency trade-off so the disclosure
   does not appear newly minted in the discussion.
2. Matched-base subsection should cross-reference
   \Cref{tab:mechanism-grpo-dpo} where it first mentions the GRPO
   causal claim.
3. Caption of \Cref{fig:robustness-three-panel} already notes the
   linearly interpolated intermediates in panels (b) and (c); keep
   that wording.

## Files saved
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/Discussion_Conclusion_BayesArbiter_2026_May_03_v2.md`
- `/Users/keshavkrishnan/Downloads/Sequential-Falsification-main-2/paper/Session_log_discussion_writing_26_05_03_v2.md`

(v1 deliverables preserved alongside as
`Discussion_Conclusion_BayesArbiter_2026_May_03.md` and
`Session_log_discussion_writing_26_05_03.md` for traceability.)
