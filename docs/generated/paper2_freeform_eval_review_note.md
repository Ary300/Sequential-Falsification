# Paper 2 Free-Form Open-QA Note

This note closes the reviewer objection that the sequence-level mixture only appears in multiple-choice-style evaluations.

## Headline

- `triviaqa_open` (`n=8`): Bayes EM / ROUGE-L `0.0000` / `0.0417`, `CAD` `0.0000` / `0.0306`, `AdaCAD` `0.0000` / `0.0694`.
- `nq_open` (`n=8`): Bayes EM / ROUGE-L `0.1250` / `0.1984`, `CAD` `0.1250` / `0.1417`, `AdaCAD` `0.1250` / `0.2000`.
- `asqa` (`n=8`): Bayes EM / ROUGE-L `0.1250` / `0.3063`, `CAD` `0.1250` / `0.2438`, `AdaCAD` `0.2500` / `0.3929`.

## Read

- These numbers are the direct free-form sequence-level check on `TriviaQA-open`, `NQ-open`, and `ASQA`.
- This note should be cited alongside the proxy follow-up note when describing how Paper 2 now leaves the multiple-choice-only regime.