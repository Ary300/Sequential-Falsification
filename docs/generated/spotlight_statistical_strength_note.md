# Spotlight Statistical Strength Note

This note consolidates the strongest already-finished statistical support for the spotlight-scale matrices.

## T1/T2 Matrix

- Series wins vs heuristic: `23/25`
- Exact one-sided sign-test p vs heuristic: `0.000010`
- Fixed-lambda e-value vs heuristic: `2805.6854`
- Bootstrap Bayes-vs-heuristic CI: `[0.0371, 0.1112]`
- Series wins vs strongest named comparator: `20/25`
- Exact one-sided sign-test p vs strongest named comparator: `0.002039`
- Fixed-lambda e-value vs strongest named comparator: `103.9143`
- Sequential e-value crosses `10` after `6` series, `20` after `8` series, and `100` after `12` series against the heuristic.

## T3 Proxy Matrix

- Series wins vs heuristic: `20/25`
- Exact one-sided sign-test p vs heuristic: `0.002039`
- Fixed-lambda e-value vs heuristic: `103.9143`
- Bootstrap Bayes-vs-heuristic CI: `[0.0155, 0.0961]`
- Series wins vs strongest named comparator: `20/25`
- Exact one-sided sign-test p vs strongest named comparator: `0.002039`
- Fixed-lambda e-value vs strongest named comparator: `103.9143`
- Sequential e-value crosses `10` after `6` series, `20` after `8` series, and `100` after `12` series against the heuristic.

## Read

- The theorem-1/theorem-2 spotlight matrix is not just a positive mean-gap result; it is directionally positive on almost every benchmark-model series and crosses strong e-value thresholds quickly.
- The theorem-3 proxy matrix is weaker than the theorem-1/theorem-2 matrix, but it still reaches a clean positive bootstrap interval and decisive series-level directional support against the heuristic.
- The strongest named-comparator story remains more mixed than the heuristic story, which is exactly why the paper should headline Bayes-vs-heuristic plus benchmark-family consistency rather than over-selling every comparator.
- This note complements, rather than replaces, the benchmark-family Holm-Bonferroni tables in the family-consistency artifact.
