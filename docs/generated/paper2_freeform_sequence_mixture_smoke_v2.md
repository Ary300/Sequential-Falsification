# Paper 2 Free-Form Sequence-Mixture Note

This note records the strongest Paper 2 free-form open-QA result obtained from the sequence-mixture branch after switching retrieval from intro-only Wikipedia extracts to fuller page extracts.

## Setup

- Model: `DeepSeek-R1-Distill-Llama-8B`
- Decode mode: `sequence_mixture`
- Retrieval: Wikipedia search + full-page extracts (`v2_full_extract`)
- Datasets: `ASQA`, `NQ-open`, `TriviaQA-open`
- Max examples per dataset: `8`

## Headline

| Dataset | Bayes EM | Bayes ROUGE-L | AdaCAD EM | AdaCAD ROUGE-L | CAD EM | CAD ROUGE-L | Closed-book EM | Closed-book ROUGE-L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `asqa` | `0.1250` | `0.3063` | `0.2500` | `0.3929` | `0.1250` | `0.2438` | `0.0000` | `0.3083` |
| `nq_open` | `0.1250` | `0.1984` | `0.1250` | `0.2000` | `0.1250` | `0.1417` | `0.2500` | `0.3125` |
| `triviaqa_open` | `0.0000` | `0.0417` | `0.0000` | `0.0694` | `0.0000` | `0.0306` | `0.0000` | `0.0681` |

## Read

- This branch materially improves the earlier all-zero free-form picture.
- `NQ-open` moves from `0.0000` Bayes EM in the rescoring harness to `0.1250` under the retrieval+sequence-mixture variant.
- `ASQA` remains the cleanest free-form win: both Bayes and AdaCAD beat closed-book on EM, and `AdaCAD` is the strongest method on this small slice.
- `TriviaQA-open` remains weak, so the honest claim is still that free-form generalization is mixed rather than a universal headline win.
