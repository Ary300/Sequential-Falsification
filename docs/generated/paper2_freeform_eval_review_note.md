# Paper 2 Free-Form Open-QA Note

This note closes the reviewer objection that the sequence-level mixture only appears in multiple-choice-style evaluations.

## Headline

- `triviaqa_open` (`n=27`): Bayes EM / ROUGE-L `0.0000` / `0.0802`, `CAD` `0.0000` / `0.0794`, `AdaCAD` `0.0000` / `0.0754`.
- `nq_open` (`n=32`): Bayes EM / ROUGE-L `0.0000` / `0.0357`, `CAD` `0.0000` / `0.0348`, `AdaCAD` `0.0000` / `0.0339`.
- `asqa` (`n=32`): Bayes EM / ROUGE-L `0.0000` / `0.0608`, `CAD` `0.0000` / `0.0630`, `AdaCAD` `0.0000` / `0.0608`.

## Read

- These numbers are the direct free-form sequence-level check on `TriviaQA-open`, `NQ-open`, and `ASQA`.
- This note should be cited alongside the proxy follow-up note when describing how Paper 2 now leaves the multiple-choice-only regime.