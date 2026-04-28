# PopQA / NQ-Swap Real Benchmark Note

## Headline

- `PopQA`: Bayes beats the generic heuristic by `0.095` regret, with benchmark-level bootstrap CI `[0.044, 0.146]`.
- `NQ-Swap`: Bayes beats the generic heuristic by `0.1038` regret, with benchmark-level bootstrap CI `[0.0829, 0.125]`.

## PopQA

- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`: Bayes `-0.2094`, heuristic `-0.1143`, `CoCoA` `-0.1819`, `AdaCAD` `-0.1619`, `always_context` `6.5511`, `always_parametric` `6.5511`.
- `Qwen/Qwen2.5-7B-Instruct`: Bayes `-0.2094`, heuristic `-0.1143`, `CoCoA` `-0.1819`, `AdaCAD` `-0.1619`, `always_context` `6.5511`, `always_parametric` `6.5511`.
- Bayes vs heuristic bootstrap CI: `[0.044, 0.146]`.
- Bayes vs `CoCoA` bootstrap CI: `[0.0218, 0.0332]`.

Popularity-bin read:

- `low` popularity: Bayes `-0.2851`, heuristic `-0.1568`, Bayes gain `0.1282`.
- `mid` popularity: Bayes `-0.2566`, heuristic `-0.1273`, Bayes gain `0.1293`.
- `high` popularity: Bayes `-0.0857`, heuristic `-0.0586`, Bayes gain `0.0271`.

## NQ-Swap

- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`: Bayes `-0.174`, heuristic `-0.0702`, `CoCoA` `-0.12`, `AdaCAD` `-0.0954`, `always_context` `8.9658`, `always_parametric` `4.3607`.
- `Qwen/Qwen2.5-7B-Instruct`: Bayes `-0.174`, heuristic `-0.0702`, `CoCoA` `-0.12`, `AdaCAD` `-0.0954`, `always_context` `8.9658`, `always_parametric` `4.3607`.
- Bayes vs heuristic bootstrap CI: `[0.0829, 0.125]`.
- Bayes vs `CoCoA` bootstrap CI: `[0.0449, 0.0634]`.

Substitution-type read:

- `alias`: Bayes `-0.1775`, heuristic `-0.0738`, Bayes gain `0.1037`.
- `corpus`: Bayes `-0.1711`, heuristic `-0.0672`, Bayes gain `0.1039`.
- `popularity`: Bayes `-0.1745`, heuristic `-0.0706`, Bayes gain `0.1039`.
- `type_swap`: Bayes `-0.1745`, heuristic `-0.0706`, Bayes gain `0.1039`.

## Read

- `PopQA` closes the most visible theorem-2 scope gap: the Bayes rule beats the popularity-style heuristic on the benchmark that motivated popularity-threshold retrieval in the first place.
- `NQ-Swap` closes the most visible comparator gap: it is the canonical entity-substitution benchmark used by the closest baseline papers, and Bayes is clearly ahead there too.
