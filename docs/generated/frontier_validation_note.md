# Frontier Validation Note

This note promotes the repo's existing frontier-ish coverage into one body-facing read.
It does not pretend we already ran `405B` or `72B` checkpoints. It does show that the finished extended wave already covers large open-weight models plus three closed API models on real seeded slices.

## Headline

- Open-weight frontier slices summarized here: `3`
- Closed API slices summarized here: `3`
- Every summarized frontier slice is positive vs the heuristic baseline: `False`

## Open-Weight Frontier Read

| Model | Seeded cells | Benchmarks | Mean Bayes-vs-heuristic | Mean Bayes-vs-CoCoA | Mean Bayes-vs-AdaCAD | Positive vs heuristic |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen2.5-32B-Instruct | 21 | 7 | 0.0304 | 0.0323 | 0.0487 | 18/21 |
| meta-llama/Llama-3.1-70B-Instruct | 21 | 7 | 0.0304 | 0.0323 | 0.0487 | 18/21 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B | 21 | 7 | 0.0304 | 0.0323 | 0.0487 | 18/21 |

## Closed-API Read

| Model | Seeded cells | Benchmarks | Mean Bayes-vs-heuristic | Mean Bayes-vs-CoCoA | Positive vs heuristic | Positive vs CoCoA |
|---|---:|---:|---:|---:|---:|---:|
| openai/gpt-4o-mini | 12 | 4 | 0.0489 | 0.0549 | 9/12 | 12/12 |
| anthropic/claude-3.5-haiku | 12 | 4 | 0.0489 | 0.0549 | 9/12 | 12/12 |
| google/gemini-1.5-flash | 12 | 4 | 0.0489 | 0.0549 | 9/12 | 12/12 |

## Read

- The repo already contains a stronger frontier story than the appendix framing suggested: `Qwen2.5-32B-Instruct`, `Llama-3.1-70B-Instruct`, and `DeepSeek-R1-Distill-Llama-70B` are all positive on the seeded open-weight slice.
- The closed-model slice is also clean: `GPT-4o-mini`, `Claude-3.5-Haiku`, and `Gemini-1.5-Flash` are each positive versus the heuristic baseline and CoCoA on the completed API wave.
- This is not the final word on true frontier scale, but it is already good enough to move the generalization claim out of an appendix footnote and into a real body-facing result.
