# Pre-Registered Held-Out Conflict-Family Test

This note freezes three predictions before inspecting the held-out results on two conflict families that were not part of the main spotlight matrix: `ClashEval` and `RAMDocs`.
The goal is to turn a piece of the empirical story from post-hoc validation into an explicit out-of-sample test.

## Pre-Registered Predictions

- `P1`: On held-out conflict families, Bayes proxy will beat heuristic adaptive, CoCoA, Astute RAG, and Self-RAG on mean regret.
- `P2`: Always-context and always-parametric will remain catastrophically suboptimal on held-out conflict families.
- `P3`: The simulated theorem-3 model will show a larger long-CoT ECE change on conflict slices than on aligned-context slices.

## Headline

- Held-out benchmarks: `['clasheval', 'ramdocs']`
- Seeds: `[42, 43, 44]`
- All pre-registered predictions supported: `False`

## Results

- `P1` supported: `True`
| Baseline | Mean regret gap vs Bayes | Seed gaps | All seeds positive |
|---|---:|---|---:|
| heuristic_adaptive | 0.1390 | `[0.139, 0.139, 0.139]` | True |
| cocoa | 0.0539 | `[0.0539, 0.0539, 0.0539]` | True |
| astute_rag | 0.0406 | `[0.0406, 0.0406, 0.0406]` | True |
| self_rag | 0.0891 | `[0.0891, 0.0891, 0.0891]` | True |

- `P2` supported: `True`
| Policy | Mean regret gap vs Bayes | Seed gaps | All seeds positive |
|---|---:|---|---:|
| always_context | 6.8231 | `[6.8231, 6.8231, 6.8231]` | True |
| always_parametric | 6.8231 | `[6.8231, 6.8231, 6.8231]` | True |

- `P3` supported: `False`
| Model | Mean conflict ECE delta | Mean no-conflict ECE delta | Mean conflict-minus-no-conflict | Positive on all seeded held-out cells |
|---|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | -0.1615 | -0.0215 | -0.1400 | False |
| Qwen/Qwen2.5-14B-Instruct | -0.1125 | -0.0323 | -0.0802 | False |
| meta-llama/Llama-3.1-8B-Instruct | -0.1438 | -0.0215 | -0.1223 | False |

## Read

- This is still a proxy-family test, not a gold-standard preregistration filed in advance with an external timestamped registry.
- It is much better than pure post-hoc narration: the predictions are explicit, the held-out families are different from the main spotlight families, and the outcomes are reported against those predictions directly.
