# Theorem 3 Family Sweep: deepseek_r1_distill_family

| Model | Benchmark | Split | `cot=0` | `cot=128` | `cot=1024` | `0->128` | `128->1024` |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | conflictbank | conflict | 0.5505 | 0.7531 | 0.5308 | 0.2026 | -0.2223 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | conflictbank | no_conflict | 0.0996 | 0.2754 | -0.3724 | 0.1758 | -0.6478 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | wikicontradict | conflict | 0.2923 | 0.4825 | 0.4429 | 0.1902 | -0.0396 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | wikicontradict | no_conflict | 0.2643 | 0.5038 | 0.4331 | 0.2395 | -0.0707 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | conflictbank | conflict | 0.5876 | 0.9449 | 0.9513 | 0.3573 | 0.0064 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | conflictbank | no_conflict | 0.0691 | 0.3108 | 0.1032 | 0.2417 | -0.2076 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | wikicontradict | conflict | 0.2717 | 0.4516 | 0.3750 | 0.1799 | -0.0766 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | wikicontradict | no_conflict | 0.2963 | 0.4229 | 0.4164 | 0.1266 | -0.0065 |
