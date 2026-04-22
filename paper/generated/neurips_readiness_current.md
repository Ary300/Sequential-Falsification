# NeurIPS Readiness Audit

This audit is intentionally conservative. It flags missing rows, partial results, thin seed coverage, and weak headline comparisons so the paper does not over-claim.

## Headline Metrics

| Model | Benchmark | MV | Falsification | Self-debug | Gen-test filter | Oracle | F recovery | F-SD | F-GTF |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen/Qwen2.5-Coder-14B-Instruct | humaneval_plus | 23.2 | 43.9 | 43.9 | 39.7 | 45.7 | 92.0% | 0.0 | 4.2 |
| Qwen/Qwen2.5-Coder-14B-Instruct | mbpp_plus | 71.6 | 75.1 | 75.2 | 79.0 | 80.3 | 40.2% | -0.1 | -3.9 |
| Qwen/Qwen2.5-Coder-14B-Instruct | livecodebench_v6 | 50.0 | 87.5 | 87.5 | 50.0 | 87.5 | 100.0% | 0.0 | 37.5 |
| Qwen/Qwen2.5-Coder-14B-Instruct | math500 | 24.1 | 34.3 | 34.3 | 34.3 | 34.3 | 100.0% | 0.0 | 0.0 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | humaneval_plus | 29.9 | 82.9 | 82.3 | 67.0 | 84.8 | 96.5% | 0.6 | 15.9 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | mbpp_plus | 30.8 | 64.4 | 64.6 | -- | 66.8 | 93.3% | -0.2 | -- |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | humaneval_plus | 32.9 | 70.7 | 72.6 | 69.2 | 74.4 | 91.1% | -1.9 | 1.5 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | mbpp_plus | 10.8 | 33.8 | 33.8 | 39.4 | 34.8 | 95.8% | 0.0 | -5.6 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | livecodebench_v6 | 3.0 | 8.0 | -- | -- | 8.0 | 100.0% | -- | -- |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | math500 | 23.0 | 33.7 | -- | -- | 33.7 | 100.0% | -- | -- |

## Issues

- `partial` Qwen/Qwen2.5-Coder-14B-Instruct :: humaneval_plus: At least one best-available row is progress-derived/partial.
- `seeds` Qwen/Qwen2.5-Coder-14B-Instruct :: humaneval_plus: Only 2 complete seed runs; target is 3.
- `partial` Qwen/Qwen2.5-Coder-14B-Instruct :: mbpp_plus: At least one best-available row is progress-derived/partial.
- `proxy` Qwen/Qwen2.5-Coder-14B-Instruct :: mbpp_plus: Missing local proxy baselines: code_t_proxy, s_star_proxy
- `headline` Qwen/Qwen2.5-Coder-14B-Instruct :: mbpp_plus: Falsification recovers only 40.2% of majority-to-oracle gap.
- `gtf` Qwen/Qwen2.5-Coder-14B-Instruct :: mbpp_plus: Falsification trails generated-test filtering by 3.9 points.
- `partial` Qwen/Qwen2.5-Coder-14B-Instruct :: livecodebench_v6: At least one best-available row is progress-derived/partial.
- `seeds` Qwen/Qwen2.5-Coder-14B-Instruct :: livecodebench_v6: Only 0 complete seed runs; target is 3.
- `seeds` Qwen/Qwen2.5-Coder-14B-Instruct :: math500: Only 0 complete seed runs; target is 3.
- `partial` deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: humaneval_plus: At least one best-available row is progress-derived/partial.
- `seeds` deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: humaneval_plus: Only 2 complete seed runs; target is 3.
- `proxy` deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: humaneval_plus: Missing local proxy baselines: code_t_proxy, s_star_proxy
- `baseline` deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: mbpp_plus: Missing core methods: generated_test_filter
- `proxy` deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: mbpp_plus: Missing local proxy baselines: code_t_proxy, s_star_proxy
- `missing` deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: livecodebench_v6: No row for target benchmark/model pair.
- `missing` deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: math500: No row for target benchmark/model pair.
- `partial` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: humaneval_plus: At least one best-available row is progress-derived/partial.
- `seeds` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: humaneval_plus: Only 1 complete seed runs; target is 3.
- `self_debug` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: humaneval_plus: Falsification trails self-debug by 1.9 points.
- `partial` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: mbpp_plus: At least one best-available row is progress-derived/partial.
- `proxy` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: mbpp_plus: Missing local proxy baselines: code_t_proxy, s_star_proxy
- `gtf` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: mbpp_plus: Falsification trails generated-test filtering by 5.6 points.
- `coverage` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: livecodebench_v6: Only 100 problems; target is 400.
- `seeds` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: livecodebench_v6: Only 1 complete seed runs; target is 3.
- `baseline` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: livecodebench_v6: Missing core methods: generated_test_filter, self_debug
- `coverage` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: math500: Only 100 problems; target is 500.
- `baseline` deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: math500: Missing core methods: generated_test_filter, self_debug
