# Powered Baseline Head-to-Head Note

This note expands the Bayes-vs-baseline comparison from the smaller spotlight table to the full completed three-seed extended model wave.
The resulting comparison has 7 benchmarks x 10 models x 3 seeds = 210 seeded series per baseline, which is the direct high-power answer to the earlier CoCoA paragraph weakness.

## Headline

- Seeds: `[42, 43, 44]`
- Benchmarks per seed: `7`
- Models per seed: `10`
- Series per baseline after seeding: `210`

## adacad

- Overall mean Bayes-vs-adacad regret gap: `0.0639`
- 95% bootstrap CI: `[0.0598, 0.0677]`
- Positive seeded cells: `201/210`
- One-sided sign `p`: `0.0`

| Benchmark | Mean gap | 95% CI | Wins | One-sided sign p |
|---|---:|---:|---:|---:|
| conflictbank | 0.0819 | [0.0818, 0.0821] | 30/30 | 0.000000 |
| faitheval | 0.0760 | [0.0745, 0.0773] | 30/30 | 0.000000 |
| hotpotqa | 0.0709 | [0.0689, 0.0728] | 30/30 | 0.000000 |
| nq_swap | 0.0757 | [0.0742, 0.0770] | 30/30 | 0.000000 |
| popqa | 0.0115 | [-0.0063, 0.0284] | 21/30 | 0.021387 |
| tabmwp | 0.0752 | [0.0737, 0.0767] | 30/30 | 0.000000 |
| triviaqa | 0.0564 | [0.0552, 0.0576] | 30/30 | 0.000000 |

Model-level read:

| Model | Mean gap | 95% CI | Wins |
|---|---:|---:|---:|
| Qwen/Qwen2.5-14B-Instruct | 0.0650 | [0.0558, 0.0727] | 21/21 |
| Qwen/Qwen2.5-32B-Instruct | 0.0487 | [0.0266, 0.0667] | 18/21 |
| Qwen/Qwen2.5-7B-Instruct | 0.0714 | [0.0660, 0.0761] | 21/21 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B | 0.0487 | [0.0267, 0.0673] | 18/21 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | 0.0714 | [0.0660, 0.0762] | 21/21 |
| google/gemma-2-27b-it | 0.0714 | [0.0660, 0.0759] | 21/21 |
| google/gemma-2-9b-it | 0.0714 | [0.0663, 0.0761] | 21/21 |
| meta-llama/Llama-3.1-70B-Instruct | 0.0487 | [0.0280, 0.0670] | 18/21 |
| meta-llama/Llama-3.1-8B-Instruct | 0.0714 | [0.0659, 0.0761] | 21/21 |
| mistralai/Mistral-7B-Instruct-v0.3 | 0.0714 | [0.0662, 0.0762] | 21/21 |

## cocoa

- Overall mean Bayes-vs-cocoa regret gap: `0.0426`
- 95% bootstrap CI: `[0.0405, 0.0445]`
- Positive seeded cells: `201/210`
- One-sided sign `p`: `0.0`

| Benchmark | Mean gap | 95% CI | Wins | One-sided sign p |
|---|---:|---:|---:|---:|
| conflictbank | 0.0539 | [0.0526, 0.0552] | 30/30 | 0.000000 |
| faitheval | 0.0502 | [0.0480, 0.0522] | 30/30 | 0.000000 |
| hotpotqa | 0.0465 | [0.0441, 0.0488] | 30/30 | 0.000000 |
| nq_swap | 0.0495 | [0.0474, 0.0514] | 30/30 | 0.000000 |
| popqa | 0.0149 | [0.0088, 0.0209] | 21/30 | 0.021387 |
| tabmwp | 0.0483 | [0.0462, 0.0503] | 30/30 | 0.000000 |
| triviaqa | 0.0349 | [0.0334, 0.0362] | 30/30 | 0.000000 |

Model-level read:

| Model | Mean gap | 95% CI | Wins |
|---|---:|---:|---:|
| Qwen/Qwen2.5-14B-Instruct | 0.0416 | [0.0361, 0.0463] | 21/21 |
| Qwen/Qwen2.5-32B-Instruct | 0.0323 | [0.0236, 0.0394] | 18/21 |
| Qwen/Qwen2.5-7B-Instruct | 0.0480 | [0.0434, 0.0520] | 21/21 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B | 0.0323 | [0.0237, 0.0396] | 18/21 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | 0.0480 | [0.0434, 0.0520] | 21/21 |
| google/gemma-2-27b-it | 0.0480 | [0.0433, 0.0518] | 21/21 |
| google/gemma-2-9b-it | 0.0480 | [0.0436, 0.0520] | 21/21 |
| meta-llama/Llama-3.1-70B-Instruct | 0.0323 | [0.0239, 0.0394] | 18/21 |
| meta-llama/Llama-3.1-8B-Instruct | 0.0480 | [0.0433, 0.0519] | 21/21 |
| mistralai/Mistral-7B-Instruct-v0.3 | 0.0480 | [0.0435, 0.0520] | 21/21 |

## astute-rag

- Overall mean Bayes-vs-astute-rag regret gap: `0.0318`
- 95% bootstrap CI: `[0.0302, 0.0333]`
- Positive seeded cells: `201/210`
- One-sided sign `p`: `0.0`

| Benchmark | Mean gap | 95% CI | Wins | One-sided sign p |
|---|---:|---:|---:|---:|
| conflictbank | 0.0400 | [0.0394, 0.0407] | 30/30 | 0.000000 |
| faitheval | 0.0360 | [0.0357, 0.0362] | 30/30 | 0.000000 |
| hotpotqa | 0.0324 | [0.0317, 0.0330] | 30/30 | 0.000000 |
| nq_swap | 0.0361 | [0.0358, 0.0364] | 30/30 | 0.000000 |
| popqa | 0.0133 | [0.0061, 0.0203] | 21/30 | 0.021387 |
| tabmwp | 0.0363 | [0.0359, 0.0367] | 30/30 | 0.000000 |
| triviaqa | 0.0288 | [0.0286, 0.0291] | 30/30 | 0.000000 |

Model-level read:

| Model | Mean gap | 95% CI | Wins |
|---|---:|---:|---:|
| Qwen/Qwen2.5-14B-Instruct | 0.0320 | [0.0284, 0.0351] | 21/21 |
| Qwen/Qwen2.5-32B-Instruct | 0.0267 | [0.0180, 0.0338] | 18/21 |
| Qwen/Qwen2.5-7B-Instruct | 0.0344 | [0.0328, 0.0359] | 21/21 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B | 0.0267 | [0.0181, 0.0339] | 18/21 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | 0.0344 | [0.0327, 0.0360] | 21/21 |
| google/gemma-2-27b-it | 0.0344 | [0.0327, 0.0359] | 21/21 |
| google/gemma-2-9b-it | 0.0344 | [0.0328, 0.0359] | 21/21 |
| meta-llama/Llama-3.1-70B-Instruct | 0.0267 | [0.0184, 0.0338] | 18/21 |
| meta-llama/Llama-3.1-8B-Instruct | 0.0344 | [0.0327, 0.0359] | 21/21 |
| mistralai/Mistral-7B-Instruct-v0.3 | 0.0344 | [0.0327, 0.0359] | 21/21 |

## self-rag

- Overall mean Bayes-vs-self-rag regret gap: `0.0219`
- 95% bootstrap CI: `[0.0019, 0.0395]`
- Positive seeded cells: `180/210`
- One-sided sign `p`: `0.0`

| Benchmark | Mean gap | 95% CI | Wins | One-sided sign p |
|---|---:|---:|---:|---:|
| conflictbank | 0.1072 | [0.1033, 0.1114] | 30/30 | 0.000000 |
| faitheval | 0.0545 | [0.0519, 0.0572] | 30/30 | 0.000000 |
| hotpotqa | 0.0284 | [0.0253, 0.0315] | 30/30 | 0.000000 |
| nq_swap | 0.0538 | [0.0513, 0.0565] | 30/30 | 0.000000 |
| popqa | -0.2053 | [-0.3033, -0.1120] | 0/30 | 1.000000 |
| tabmwp | 0.0510 | [0.0482, 0.0538] | 30/30 | 0.000000 |
| triviaqa | 0.0638 | [0.0622, 0.0654] | 30/30 | 0.000000 |

Model-level read:

| Model | Mean gap | 95% CI | Wins |
|---|---:|---:|---:|
| Qwen/Qwen2.5-14B-Instruct | 0.0348 | [-0.0018, 0.0634] | 18/21 |
| Qwen/Qwen2.5-32B-Instruct | -0.0302 | [-0.1380, 0.0661] | 18/21 |
| Qwen/Qwen2.5-7B-Instruct | 0.0458 | [0.0326, 0.0591] | 18/21 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B | -0.0302 | [-0.1375, 0.0665] | 18/21 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | 0.0458 | [0.0331, 0.0593] | 18/21 |
| google/gemma-2-27b-it | 0.0458 | [0.0332, 0.0589] | 18/21 |
| google/gemma-2-9b-it | 0.0458 | [0.0327, 0.0591] | 18/21 |
| meta-llama/Llama-3.1-70B-Instruct | -0.0302 | [-0.1344, 0.0662] | 18/21 |
| meta-llama/Llama-3.1-8B-Instruct | 0.0458 | [0.0324, 0.0591] | 18/21 |
| mistralai/Mistral-7B-Instruct-v0.3 | 0.0458 | [0.0330, 0.0589] | 18/21 |

## Read

- This is the powered version of the comparator story: it replaces the fragile 25-series paragraph with 210 seeded series per baseline.
- On this expanded matrix, the Bayes rule is decisively ahead of AdaCAD, CoCoA, and Astute RAG overall.
- Self-RAG remains the closest baseline overall; the PopQA caveat is real, but it is now visibly a benchmark-specific exception rather than a reason to doubt the aggregate head-to-head claim.
