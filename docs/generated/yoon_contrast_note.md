# Yoon Contrast Note

This note tests the reviewer-facing contrast directly: a no-conflict QA control (`TriviaQA` aligned-context) versus explicit conflict (`ConflictBank` conflict-context), measured by how the magnitude of the confidence-accuracy gap changes from `cot=0` to the longest completed budget.

## Headline

- Sign-flip count: `0/30`
- Sign-flip rate: `0.0`
- Mean `TriviaQA` no-conflict gap-magnitude delta (`cot 2048 - cot 0`): `-0.0433`
- Mean `ConflictBank` conflict gap-magnitude delta (`cot 2048 - cot 0`): `-0.1327`

Interpretation:
- Negative delta means calibration improves with longer CoT.
- Positive delta means calibration worsens with longer CoT.
- On the completed proxy wave, this direct `TriviaQA` vs `ConflictBank` control does not produce the clean sign flip by itself, so the stronger theorem-3 contrast should still be written around the real-trace conflict results rather than this proxy alone.

## Per-Model Means

| Model | Mean TriviaQA delta | Mean ConflictBank delta | Count |
|---|---:|---:|---:|
| Qwen/Qwen2.5-14B-Instruct | -0.0399 | -0.1377 | 3 |
| Qwen/Qwen2.5-32B-Instruct | -0.0357 | -0.0796 | 3 |
| Qwen/Qwen2.5-7B-Instruct | -0.0377 | -0.1512 | 3 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B | -0.0952 | -0.0796 | 3 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | -0.0377 | -0.1943 | 3 |
| google/gemma-2-27b-it | -0.0377 | -0.1512 | 3 |
| google/gemma-2-9b-it | -0.0377 | -0.1512 | 3 |
| meta-llama/Llama-3.1-70B-Instruct | -0.0357 | -0.0796 | 3 |
| meta-llama/Llama-3.1-8B-Instruct | -0.0377 | -0.1512 | 3 |
| mistralai/Mistral-7B-Instruct-v0.3 | -0.0377 | -0.1512 | 3 |
