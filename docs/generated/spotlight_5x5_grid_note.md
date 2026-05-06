# Spotlight 5x5 Grid Note

## Headline

- The completed spotlight matrix already covers `5` models x `5` benchmarks = `25` model-benchmark cells.
- Total parsed rows in the finished matrix: `174080`.

## Model Coverage

- `Qwen/Qwen2.5-14B-Instruct`: `5` benchmarks, Bayes `-0.2029`, heuristic `-0.1008`, `CoCoA` `-0.1568`, `AdaCAD` `-0.1315`, Bayes gain `0.1021`.
- `Qwen/Qwen2.5-7B-Instruct`: `5` benchmarks, Bayes `-0.2073`, heuristic `-0.0965`, `CoCoA` `-0.1554`, `AdaCAD` `-0.1314`, Bayes gain `0.1108`.
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`: `5` benchmarks, Bayes `-0.2073`, heuristic `-0.0965`, `CoCoA` `-0.1554`, `AdaCAD` `-0.1314`, Bayes gain `0.1108`.
- `meta-llama/Llama-3.1-70B-Instruct`: `5` benchmarks, Bayes `-0.1535`, heuristic `-0.0932`, `CoCoA` `-0.1162`, `AdaCAD` `-0.0953`, Bayes gain `0.0602`.
- `meta-llama/Llama-3.1-8B-Instruct`: `5` benchmarks, Bayes `-0.2073`, heuristic `-0.0965`, `CoCoA` `-0.1554`, `AdaCAD` `-0.1314`, Bayes gain `0.1108`.

## Cell Table

| Model | Benchmark | Rows | Bayes | Heuristic | Bayes gain |
|---|---|---:|---:|---:|---:|
| Qwen/Qwen2.5-14B-Instruct | conflictbank | 12288 | -0.2756 | -0.1334 | 0.1423 |
| Qwen/Qwen2.5-14B-Instruct | faitheval | 6144 | -0.1843 | -0.0851 | 0.0992 |
| Qwen/Qwen2.5-14B-Instruct | memotrap | 6144 | -0.1819 | -0.0845 | 0.0975 |
| Qwen/Qwen2.5-14B-Instruct | nq_swap | 6144 | -0.1853 | -0.0871 | 0.0982 |
| Qwen/Qwen2.5-14B-Instruct | popqa | 4096 | -0.0706 | -0.0719 | -0.0013 |
| Qwen/Qwen2.5-7B-Instruct | conflictbank | 12288 | -0.2594 | -0.1324 | 0.1270 |
| Qwen/Qwen2.5-7B-Instruct | faitheval | 6144 | -0.1718 | -0.0677 | 0.1041 |
| Qwen/Qwen2.5-7B-Instruct | memotrap | 6144 | -0.1706 | -0.0680 | 0.1026 |
| Qwen/Qwen2.5-7B-Instruct | nq_swap | 6144 | -0.1740 | -0.0702 | 0.1038 |
| Qwen/Qwen2.5-7B-Instruct | popqa | 4096 | -0.2094 | -0.1143 | 0.0950 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | conflictbank | 12288 | -0.2594 | -0.1324 | 0.1270 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | faitheval | 6144 | -0.1718 | -0.0677 | 0.1041 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | memotrap | 6144 | -0.1706 | -0.0680 | 0.1026 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | nq_swap | 6144 | -0.1740 | -0.0702 | 0.1038 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | popqa | 4096 | -0.2094 | -0.1143 | 0.0950 |
| meta-llama/Llama-3.1-70B-Instruct | conflictbank | 12288 | -0.2844 | -0.1281 | 0.1563 |
| meta-llama/Llama-3.1-70B-Instruct | faitheval | 6144 | -0.1908 | -0.0905 | 0.1002 |
| meta-llama/Llama-3.1-70B-Instruct | memotrap | 6144 | -0.1867 | -0.0870 | 0.0997 |
| meta-llama/Llama-3.1-70B-Instruct | nq_swap | 6144 | -0.1900 | -0.0898 | 0.1002 |
| meta-llama/Llama-3.1-70B-Instruct | popqa | 4096 | 0.3999 | -0.0073 | -0.4072 |
| meta-llama/Llama-3.1-8B-Instruct | conflictbank | 12288 | -0.2594 | -0.1324 | 0.1270 |
| meta-llama/Llama-3.1-8B-Instruct | faitheval | 6144 | -0.1718 | -0.0677 | 0.1041 |
| meta-llama/Llama-3.1-8B-Instruct | memotrap | 6144 | -0.1706 | -0.0680 | 0.1026 |
| meta-llama/Llama-3.1-8B-Instruct | nq_swap | 6144 | -0.1740 | -0.0702 | 0.1038 |
| meta-llama/Llama-3.1-8B-Instruct | popqa | 4096 | -0.2094 | -0.1143 | 0.0950 |
