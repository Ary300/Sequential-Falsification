# Self-RAG Power Breakout Note

This note isolates why the powered `Self-RAG` comparison is weaker than the other named baseline head-to-heads.

## Overall

From [powered_baseline_headtohead.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/powered_baseline_headtohead.md):

- overall mean Bayes-vs-Self-RAG gap: `0.0219`
- 95% bootstrap CI: `[0.0019, 0.0395]`
- positive seeded cells: `180/210`

## Benchmark Breakdown

- `conflictbank`: `+0.1072`, `30/30`
- `faitheval`: `+0.0545`, `30/30`
- `hotpotqa`: `+0.0284`, `30/30`
- `nq_swap`: `+0.0538`, `30/30`
- `tabmwp`: `+0.0510`, `30/30`
- `triviaqa`: `+0.0638`, `30/30`
- `popqa`: `-0.2053`, `0/30`

## Read

- The weaker aggregate `Self-RAG` result is not diffuse.
- It is overwhelmingly a `PopQA` reversal.
- Outside `PopQA`, the powered comparison is cleanly positive in every benchmark family.

## Implication

The right empirical framing is not:

- "Self-RAG nearly ties everywhere"

It is:

- "Self-RAG is the closest named baseline overall because of one strong `PopQA` exception, while the rest of the matrix remains solidly positive."
