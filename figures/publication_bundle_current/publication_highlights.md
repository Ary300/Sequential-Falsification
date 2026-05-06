# Publication Highlights

This file summarizes the most reviewer-relevant patterns in the current publication bundle.

## Majority-vote failure cases

- deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: humaneval_plus (45.4 vs 34.5)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: humaneval_plus (35.4 vs 32.3)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: mbpp_plus (11.2 vs 10.8)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: mbpp_plus (31.0 vs 30.8)

## Falsification vs self-debug

- +0.0: deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: mbpp_plus (33.8 vs 33.8)
- +0.0: Qwen/Qwen2.5-Coder-14B-Instruct :: math500 (34.3 vs 34.3)
- +0.0: Qwen/Qwen2.5-Coder-14B-Instruct :: livecodebench_v6 (87.5 vs 87.5)
- +0.0: Qwen/Qwen2.5-Coder-14B-Instruct :: humaneval_plus (42.4 vs 42.4)
- -0.1: Qwen/Qwen2.5-Coder-14B-Instruct :: mbpp_plus (75.1 vs 75.2)
- -0.2: deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: mbpp_plus (64.4 vs 64.6)
- -1.2: deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: humaneval_plus (79.6 vs 80.8)
- -4.9: deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: humaneval_plus (65.2 vs 70.1)

## Oracle-gap recovery by falsification

- deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: math500 (100.0\%)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: livecodebench_v6 (100.0\%)
- Qwen/Qwen2.5-Coder-14B-Instruct :: math500 (100.0\%)
- Qwen/Qwen2.5-Coder-14B-Instruct :: livecodebench_v6 (100.0\%)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: mbpp_plus (95.8\%)
- Qwen/Qwen2.5-Coder-14B-Instruct :: humaneval_plus (93.9\%)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: mbpp_plus (93.3\%)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-32B :: humaneval_plus (92.0\%)
- deepseek-ai/DeepSeek-R1-Distill-Qwen-7B :: humaneval_plus (81.6\%)
- Qwen/Qwen2.5-Coder-14B-Instruct :: mbpp_plus (40.2\%)
