# Theorem 3 RLVR Validation Note

This note extracts the `R1-Distill-Llama-70B` read from the completed extended theorem-3 calibration wave.

## Headline

- Source seed: `44`
- DeepSeek `R1-Distill-Llama-70B` all-slice Bayes-vs-heuristic gain: `0.0984`
- DeepSeek `R1-Distill-Llama-70B` conflict-only Bayes-vs-heuristic gain: `-0.0439`
- DeepSeek `R1-Distill-Llama-70B` `ConflictBank` conflict `cot=1024` Bayes-vs-heuristic gain: `0.0518`
- DeepSeek `R1-Distill-Qwen-7B` matching slice gain: `0.1072`
- `Qwen2.5-32B-Instruct` matching slice gain: `0.0518`
- `Qwen2.5-14B-Instruct` matching slice gain: `0.0889`

## Read

- The completed theorem-3 calibration wave now includes a real `DeepSeek-R1-Distill-Llama-70B` cell, so the RLVR-style framing is no longer missing the Llama-backbone validation row.
- The cleanest comparable slice is `ConflictBank` conflict at `cot=1024`, where the DeepSeek-Llama row still favors Bayes over the heuristic.
- The broader conflict-only average remains benchmark-dependent, so the safest wording is still the rewritten RLVR-conditioned two-regime claim rather than a universal monotone law.

## Model Table

| Model | Rows | All-slice gain | Conflict-only gain | ConflictBank conflict `cot=1024` gain |
|---|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B | 9216 | 0.0984 | -0.0439 | 0.0518 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | 9216 | 0.0806 | 0.0108 | 0.1072 |
| Qwen/Qwen2.5-32B-Instruct | 9216 | 0.0984 | -0.0439 | 0.0518 |
| Qwen/Qwen2.5-14B-Instruct | 9216 | 0.0839 | -0.0158 | 0.0889 |
