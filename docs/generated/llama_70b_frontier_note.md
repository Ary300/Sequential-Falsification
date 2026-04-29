# Llama-3.1-70B Frontier Note

## Headline

- `Llama-3.1-70B-Instruct` is already present as a real frontier-scale model in the finished five-benchmark spotlight matrix.
- On the count-weighted `Llama-3.1-70B` five-benchmark slice, Bayes beats the generic heuristic by `0.0602` regret.
- On that same frontier slice, Bayes beats `CoCoA` by `0.0373` and `AdaCAD` by `0.0581` regret.
- The single visible weakness is `PopQA`, where the Llama-70B slice is the outlier responsible for the only mixed family on the spotlight benchmark-consistency read.

## Per-Benchmark Read

- `conflictbank`: Bayes `-0.2844`, heuristic `-0.1281`, `CoCoA` `-0.2358`, `AdaCAD` `-0.2021`, `always_context` `6.5511`, `always_parametric` `6.5511`, Bayes gain `0.1563`.
- `faitheval`: Bayes `-0.1908`, heuristic `-0.0905`, `CoCoA` `-0.1492`, `AdaCAD` `-0.1203`, `always_context` `8.9658`, `always_parametric` `4.3607`, Bayes gain `0.1003`.
- `memotrap`: Bayes `-0.1867`, heuristic `-0.087`, `CoCoA` `-0.1468`, `AdaCAD` `-0.1185`, `always_context` `8.9375`, `always_parametric` `4.3863`, Bayes gain `0.0997`.
- `nq_swap`: Bayes `-0.19`, heuristic `-0.0898`, `CoCoA` `-0.149`, `AdaCAD` `-0.1202`, `always_context` `8.9658`, `always_parametric` `4.3607`, Bayes gain `0.1002`.
- `popqa`: Bayes `0.3999`, heuristic `-0.0073`, `CoCoA` `0.3871`, `AdaCAD` `0.3344`, `always_context` `6.5511`, `always_parametric` `6.5511`, Bayes gain `-0.4072`.

## Read

- This closes the most important frontier-scale empirical objection that was still easy to miss in the previous bundle: the repo already contains a real `70B` open-weight main-table slice.
- The resulting read is good enough to headline honestly: strong aggregate five-benchmark performance, strong wins over heuristic / `CoCoA` / `AdaCAD`, and one explicit `PopQA` caveat rather than a hidden failure.
