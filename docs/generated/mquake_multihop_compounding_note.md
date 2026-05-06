# MQuAKE Multi-Hop Compounding Note

This note treats MQuAKE-Remastered as an edited-world multi-hop arbitration stress test: the updated chain is the gold world, while parametric memory still points to the stale chain.

## Setup

- Benchmark: `mquake_remastered`
- Condition: `aligned_context`
- Max examples: `256`
- Depths evaluated: `[1, 2, 3]`

## Headline

- Reference model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- Bayes depth-2 chain error: `0.089011`
- Heuristic depth-2 chain error: `0.38785`
- Fixed-50 depth-2 chain error: `0.75`
- Always-parametric depth-2 chain error: `1.0`
- Always-context depth-2 chain error: `0.0`

## deepseek-ai/DeepSeek-R1-Distill-Qwen-14B

| Policy | Mean p(correct source) | Depth-1 error | Depth-2 error | Depth-3 error |
|---|---:|---:|---:|---:|
| bayes_proxy | 0.954458 | 0.045542 | 0.089011 | 0.130499 |
| heuristic_adaptive | 0.7824 | 0.2176 | 0.38785 | 0.521054 |
| fixed_50 | 0.5 | 0.5 | 0.75 | 0.875 |
| always_context | 1.0 | 0.0 | 0.0 | 0.0 |
| always_parametric | 0.0 | 1.0 | 1.0 | 1.0 |

## Qwen/Qwen2.5-14B-Instruct

| Policy | Mean p(correct source) | Depth-1 error | Depth-2 error | Depth-3 error |
|---|---:|---:|---:|---:|
| bayes_proxy | 0.954458 | 0.045542 | 0.089011 | 0.130499 |
| heuristic_adaptive | 0.7824 | 0.2176 | 0.38785 | 0.521054 |
| fixed_50 | 0.5 | 0.5 | 0.75 | 0.875 |
| always_context | 1.0 | 0.0 | 0.0 | 0.0 |
| always_parametric | 0.0 | 1.0 | 1.0 | 1.0 |

## deepseek-ai/DeepSeek-R1-Distill-Llama-70B

| Policy | Mean p(correct source) | Depth-1 error | Depth-2 error | Depth-3 error |
|---|---:|---:|---:|---:|
| bayes_proxy | 0.926406 | 0.073594 | 0.141772 | 0.204932 |
| heuristic_adaptive | 0.7124 | 0.2876 | 0.492486 | 0.638447 |
| fixed_50 | 0.5 | 0.5 | 0.75 | 0.875 |
| always_context | 1.0 | 0.0 | 0.0 | 0.0 |
| always_parametric | 0.0 | 1.0 | 1.0 | 1.0 |

## meta-llama/Llama-3.1-70B-Instruct

| Policy | Mean p(correct source) | Depth-1 error | Depth-2 error | Depth-3 error |
|---|---:|---:|---:|---:|
| bayes_proxy | 0.926406 | 0.073594 | 0.141772 | 0.204932 |
| heuristic_adaptive | 0.7124 | 0.2876 | 0.492486 | 0.638447 |
| fixed_50 | 0.5 | 0.5 | 0.75 | 0.875 |
| always_context | 1.0 | 0.0 | 0.0 | 0.0 |
| always_parametric | 0.0 | 1.0 | 1.0 | 1.0 |

## Read

- This is a proxy compounding analysis rather than a full token-level edited-model evaluation.
- It is still useful for the paper because it shows the qualitative prediction cleanly: once the correct source must be chosen repeatedly through a chain, conservative fixed policies degrade multiplicatively.
