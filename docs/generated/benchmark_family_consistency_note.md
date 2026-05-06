# Benchmark-Family Consistency Note

This note summarizes how often Bayes beats the generic heuristic and CoCoA within each benchmark family.
The model-level sign tests are intentionally conservative because each benchmark contributes only five model-family slices.

## Spotlight Matrix (`T1/T2`)

| Benchmark | Mean gap vs heuristic | Positive model slices | One-sided sign p | Holm p | Fixed-lambda e-value | Mean gap vs CoCoA | Positive slices vs CoCoA | One-sided sign p | Holm p | Fixed-lambda e-value |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| conflictbank | 0.1359 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0544 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| faitheval | 0.1024 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0510 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| memotrap | 0.1010 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0495 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| nq_swap | 0.1020 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0502 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| popqa | -0.0246 | 3/5 | 0.8125 | 0.8125 | 0.8438 | 0.0171 | 4/5 | 0.1875 | 0.1875 | 2.5312 |

## Theorem-3 Proxy Matrix

| Benchmark | Mean gap vs heuristic | Positive model slices | One-sided sign p | Holm p | Fixed-lambda e-value | Mean gap vs CoCoA | Positive slices vs CoCoA | One-sided sign p | Holm p | Fixed-lambda e-value |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ambigdocs | 0.1022 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0504 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| conflictbank | 0.1359 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0544 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| faitheval | 0.1024 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0510 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| ramdocs | 0.0970 | 5/5 | 0.0312 | 0.1560 | 7.5938 | 0.0461 | 5/5 | 0.0312 | 0.1560 | 7.5938 |
| wikicontradict | -0.1453 | 0/5 | 0.0312 | 0.1560 | 0.0312 | -0.2125 | 0/5 | 0.0312 | 0.1560 | 0.0312 |

## Read

- On the spotlight matrix, `ConflictBank`, `FaithEval`, `MemoTrap`, and `NQ-Swap` are unanimous `5/5` Bayes-over-heuristic wins across model families, while `PopQA` is the lone mixed family because of the Llama-70B outlier slice.
- On that same matrix, those same four benchmark families are also unanimous `5/5` Bayes-over-CoCoA wins, which is the cleanest benchmark-family version of the theorem-1/theorem-2 headline.
- On the theorem-3 proxy matrix, `AmbigDocs`, `ConflictBank`, `FaithEval`, and `RAMDocs` are unanimous `5/5` Bayes-over-heuristic wins, while `WikiContradict` is a unanimous negative exception. That makes the theorem-3 regret read explicitly benchmark-dependent rather than universally positive.
- The fixed-lambda e-values are exploratory support diagnostics, not replacements for the main bootstrap intervals. They are included to make the cross-model directional consistency easy to see at a glance.
