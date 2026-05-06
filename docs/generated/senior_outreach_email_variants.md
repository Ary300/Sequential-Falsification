# Senior Outreach Email Variants

This packet turns the co-author / advisor step into a ready-to-send set of emails tied to the current headline numbers.

## Shared Headline Numbers

- Spotlight matrix Bayes-vs-heuristic gap: `0.0833` with CI `[0.0371, 0.1112]`.
- Theorem-3 proxy Bayes-vs-heuristic gap: `0.0585` with CI `[0.0155, 0.0961]`.
- Real eta-tempered method result on `ConflictBank` 14B conflict: accuracy `0.0367 -> 0.4400`, gap `0.9372 -> 0.5205`.

## Mohit Bansal

Subject: `Bayes-optimal knowledge arbitration paper: theorem + benchmark package`

```text
Hello Professor Bansal,

I am writing because I now have a finished theorem-and-results draft on knowledge conflict in LLMs, and I think it overlaps closely with your work on AdaCAD / MADAM-RAG / RAMDocs and conflict-aware decoding.

The overlap with AdaCAD / MADAM-RAG / RAMDocs is the main reason I am reaching out: the paper's positioning is that these strong adaptive decoders look like approximations to a common Bayes-optimal arbitration target rather than isolated heuristics.

The main claim is that parametric-vs-context conflict should be treated as a posterior-predictive decision problem. I derive a Bayes-style arbitration rule, prove that fixed-trust policies are minimax-suboptimal in the conflict family, and package a theorem-3 rewrite that frames long-CoT overconfidence as a benchmark-dependent misspecification / endogenous-evidence phenomenon.

Empirically, the current spotlight matrix covers 5 benchmarks x 5 models, with Bayes beating the generic heuristic by 0.0833 regret and 95% bootstrap CI [0.0371, 0.1112]. On the theorem-3 proxy size-scaling matrix, Bayes beats the heuristic by 0.0585 with CI [0.0155, 0.0961]. On the real post-trace method run for DeepSeek-R1-Distill-Qwen-14B on ConflictBank conflict, eta-tempered decoding moves accuracy from 0.0367 to 0.4400 and reduces the overconfidence gap from 0.9372 to 0.5205.

I am attaching the draft, theorem sketch, and headline bundle. If the framing seems interesting, I would be very grateful for either brief feedback or a conversation focused on positioning against adaptive decoding baselines and benchmark scope.

Best,
NAME
```

## Jacob Andreas

Subject: `Bayes-optimal knowledge arbitration paper: theorem + benchmark package`

```text
Hello Professor Andreas,

I am writing because I now have a finished theorem-and-results draft on knowledge conflict in LLMs, and I think it overlaps closely with your work on RLCR, calibration, and reasoning-time uncertainty.

The theorem-3 rewrite is the part I most want your reaction to: it recasts the DeepSeek-vs-Qwen split as an RLVR-conditioned misspecification law and now includes a real eta-tempered decoding method result on the 14B ConflictBank conflict slice.

The main claim is that parametric-vs-context conflict should be treated as a posterior-predictive decision problem. I derive a Bayes-style arbitration rule, prove that fixed-trust policies are minimax-suboptimal in the conflict family, and package a theorem-3 rewrite that frames long-CoT overconfidence as a benchmark-dependent misspecification / endogenous-evidence phenomenon.

Empirically, the current spotlight matrix covers 5 benchmarks x 5 models, with Bayes beating the generic heuristic by 0.0833 regret and 95% bootstrap CI [0.0371, 0.1112]. On the theorem-3 proxy size-scaling matrix, Bayes beats the heuristic by 0.0585 with CI [0.0155, 0.0961]. On the real post-trace method run for DeepSeek-R1-Distill-Qwen-14B on ConflictBank conflict, eta-tempered decoding moves accuracy from 0.0367 to 0.4400 and reduces the overconfidence gap from 0.9372 to 0.5205.

I am attaching the draft, theorem sketch, and headline bundle. If the framing seems interesting, I would be very grateful for either brief feedback or a conversation focused on theorem-3 framing and the eta-method packaging.

Best,
NAME
```

## Yoon Kim

Subject: `Bayes-optimal knowledge arbitration paper: theorem + benchmark package`

```text
Hello Professor Kim,

I am writing because I now have a finished theorem-and-results draft on knowledge conflict in LLMs, and I think it overlaps closely with your work on reasoning calibration, RLCR, and confidence expression.

The calibration framing now leans on a concrete split between no-conflict QA and explicit knowledge conflict: the theorem-3 rewrite argues that longer CoT can sharpen confidence faster than accuracy specifically in the misspecified conflict regime, and we now have a real post-trace eta-decoding intervention to show that.

The main claim is that parametric-vs-context conflict should be treated as a posterior-predictive decision problem. I derive a Bayes-style arbitration rule, prove that fixed-trust policies are minimax-suboptimal in the conflict family, and package a theorem-3 rewrite that frames long-CoT overconfidence as a benchmark-dependent misspecification / endogenous-evidence phenomenon.

Empirically, the current spotlight matrix covers 5 benchmarks x 5 models, with Bayes beating the generic heuristic by 0.0833 regret and 95% bootstrap CI [0.0371, 0.1112]. On the theorem-3 proxy size-scaling matrix, Bayes beats the heuristic by 0.0585 with CI [0.0155, 0.0961]. On the real post-trace method run for DeepSeek-R1-Distill-Qwen-14B on ConflictBank conflict, eta-tempered decoding moves accuracy from 0.0367 to 0.4400 and reduces the overconfidence gap from 0.9372 to 0.5205.

I am attaching the draft, theorem sketch, and headline bundle. If the framing seems interesting, I would be very grateful for either brief feedback or a conversation focused on theorem-3 framing and how best to contrast the no-conflict vs conflict settings.

Best,
NAME
```

## Eunsol Choi

Subject: `Bayes-optimal knowledge arbitration paper: theorem + benchmark package`

```text
Hello Professor Choi,

I am writing because I now have a finished theorem-and-results draft on knowledge conflict in LLMs, and I think it overlaps closely with your work on knowledge conflict benchmarks and conflict-centric QA.

The benchmark package is now broad enough that I think the paper can be read as a conflict-arbitration paper rather than a narrow decoding note: the current matrix spans ConflictBank, WikiContradict, PopQA, NQ-Swap, HotpotQA, TriviaQA, TabMWP, GPQA, and CLIMATEX-style slices.

The main claim is that parametric-vs-context conflict should be treated as a posterior-predictive decision problem. I derive a Bayes-style arbitration rule, prove that fixed-trust policies are minimax-suboptimal in the conflict family, and package a theorem-3 rewrite that frames long-CoT overconfidence as a benchmark-dependent misspecification / endogenous-evidence phenomenon.

Empirically, the current spotlight matrix covers 5 benchmarks x 5 models, with Bayes beating the generic heuristic by 0.0833 regret and 95% bootstrap CI [0.0371, 0.1112]. On the theorem-3 proxy size-scaling matrix, Bayes beats the heuristic by 0.0585 with CI [0.0155, 0.0961]. On the real post-trace method run for DeepSeek-R1-Distill-Qwen-14B on ConflictBank conflict, eta-tempered decoding moves accuracy from 0.0367 to 0.4400 and reduces the overconfidence gap from 0.9372 to 0.5205.

I am attaching the draft, theorem sketch, and headline bundle. If the framing seems interesting, I would be very grateful for either brief feedback or a conversation focused on benchmark framing and whether the conflict families are positioned cleanly enough.

Best,
NAME
```

## Peter Grünwald

Subject: `Bayes-optimal knowledge arbitration paper: theorem + benchmark package`

```text
Hello Professor Grünwald,

I am writing because I now have a finished theorem-and-results draft on knowledge conflict in LLMs, and I think it overlaps closely with your work on generalized Bayes, SafeBayes, and misspecification.

The theorem-3 rewrite leans explicitly on generalized Bayes and SafeBayes ideas: the current claim is that conflict lowers the effective safe eta and makes wrong-answer posterior sharpening more persistent under endogenous CoT evidence.

The main claim is that parametric-vs-context conflict should be treated as a posterior-predictive decision problem. I derive a Bayes-style arbitration rule, prove that fixed-trust policies are minimax-suboptimal in the conflict family, and package a theorem-3 rewrite that frames long-CoT overconfidence as a benchmark-dependent misspecification / endogenous-evidence phenomenon.

Empirically, the current spotlight matrix covers 5 benchmarks x 5 models, with Bayes beating the generic heuristic by 0.0833 regret and 95% bootstrap CI [0.0371, 0.1112]. On the theorem-3 proxy size-scaling matrix, Bayes beats the heuristic by 0.0585 with CI [0.0155, 0.0961]. On the real post-trace method run for DeepSeek-R1-Distill-Qwen-14B on ConflictBank conflict, eta-tempered decoding moves accuracy from 0.0367 to 0.4400 and reduces the overconfidence gap from 0.9372 to 0.5205.

I am attaching the draft, theorem sketch, and headline bundle. If the framing seems interesting, I would be very grateful for either brief feedback or a conversation focused on whether the generalized-Bayes transport to CoT decoding is stated defensibly.

Best,
NAME
```
