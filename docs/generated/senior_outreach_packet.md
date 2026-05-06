# Senior Outreach Packet

This packet turns the co-author / advisor step into a concrete deliverable.
It does not send mail automatically, but it removes the remaining writing work.

## Primary Targets

1. `Mohit Bansal`
Reason: AdaCAD / MADAM-RAG / RAMDocs make this the closest conflict-decoding lab.

2. `Jacob Andreas`
Reason: RLCR is the cleanest training-time cousin of the theorem-3 rewrite.

3. `Yoon Kim`
Reason: sits exactly at the Yoon-calibration / RLCR intersection.

4. `Eunsol Choi`
Reason: conflict-centric QA and benchmark framing.

5. `Peter Grünwald`
Reason: strongest theory-side credibility boost for the generalized-Bayes / SafeBayes transport.

## What To Attach

- Main paper draft:
  [`paper/main.tex`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/main.tex)
- Theorem sketch:
  [`docs/KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md)
- Current paper-facing headline bundle:
  [`docs/generated/knowledge_arbitration_headline_bundle.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_headline_bundle.md)
- Theorem-3 RLVR note:
  [`docs/generated/theorem3_rlvr_reframing_note.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_rlvr_reframing_note.md)

## Short Cold Email

Subject:
`Bayes-optimal knowledge arbitration paper: theorem + benchmark package`

Body:

Hello Professor NAME,

I’m writing because I have a draft on knowledge conflict in LLMs that now has a finished theorem-and-results core, and I think it overlaps closely with your work on TOPIC.

The paper’s main claim is that parametric-vs-context conflict should be treated as a posterior-predictive decision problem. I derive a Bayes-style arbitration rule, prove that fixed-trust policies are minimax-suboptimal in the conflict family, and package a theorem-3 rewrite that frames long-CoT overconfidence as a benchmark-dependent misspecification / endogenous-evidence phenomenon. Empirically, the current spotlight matrix covers 5 benchmarks x 5 models, with Bayes beating the generic heuristic by 0.0833 regret and 95% bootstrap CI [0.0371, 0.1112]. On the theorem-3 proxy size-scaling matrix, Bayes beats the heuristic by 0.0585 with CI [0.0155, 0.0961].

I’m attaching the draft, theorem sketch, and the current headline bundle. If the framing seems interesting, I would be grateful for either brief feedback or a conversation about whether the paper’s positioning could be sharpened further.

Best,
NAME

## Bansal Variant

Replace the second paragraph opener with:

`The overlap with AdaCAD / MADAM-RAG / RAMDocs is the reason I’m reaching out specifically: the paper’s main positioning is that these strong adaptive decoders look like approximations to a common Bayes-optimal arbitration target rather than isolated heuristics.`

## Andreas / Kim Variant

Replace the theorem-3 sentence with:

`The theorem-3 rewrite is the part I most want your reaction to: it recasts the DeepSeek-vs-Qwen split as an RLVR-conditioned misspecification law and uses an eta-tempered decoding intervention as the method-level translation.`

## Grünwald Variant

Replace the theorem-3 sentence with:

`The theorem-3 rewrite leans explicitly on generalized Bayes and SafeBayes ideas: the current claim is that conflict lowers the effective safe eta and makes wrong-answer posterior sharpening more persistent under endogenous CoT evidence.`

## What To Ask For

- If the target is `Bansal` or `Choi`: ask primarily about positioning against conflict-decoding baselines and benchmark scope.
- If the target is `Andreas` or `Kim`: ask primarily about theorem-3 framing and eta-method packaging.
- If the target is `Grünwald`: ask primarily whether the transport from generalized Bayes / misspecification to CoT decoding is stated cleanly enough to be defensible.
