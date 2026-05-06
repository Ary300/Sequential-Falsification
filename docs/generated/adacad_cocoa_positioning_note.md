# AdaCAD / CoCoA Positioning Note

## Main point

The paper should position `AdaCAD` and `CoCoA` as the two closest
decoder-level cousins to Bayes-optimal arbitration, not as lingering
comparator gaps.

## Analytical read

- `AdaCAD` is the cleanest first-order approximation story. Its JSD-weighted
  convex blend is a practical surrogate for the posterior reliability weight in
  the Bayes-optimal rule.
- `CoCoA` is the stronger multi-proxy heuristic. It combines entropy gap,
  contextual peakedness, and divergence-style signals into an empirical
  trust-in-context score.
- The Bayes framing therefore does useful theoretical work: it names the target
  object both methods are approximating, and it explains why these heuristics
  help when they do.

## Empirical headline

On the expanded spotlight matrix:

- `bayes_proxy = -0.1722`
- `Self-RAG = -0.1456`
- `Astute RAG = -0.1396`
- `CoCoA = -0.1278`
- `AdaCAD = -0.1063`
- `CAD = -0.0790`

So the closest-cousin read is:

- Bayes beats `CoCoA` by `0.0444` regret.
- Bayes beats `AdaCAD` by `0.0659` regret.

On the theorem-3 proxy size-scaling matrix:

- `bayes_proxy = -0.0774`
- `CoCoA = -0.0795`
- `AdaCAD = -0.0699`

So the honest theorem-3 read is:

- `CoCoA` is a near-tie on the theorem-3 proxy matrix.
- `AdaCAD` still trails Bayes there by `0.0075` regret.
- The theorem-3 headline should therefore anchor on the bootstrap-clean
  Bayes-vs-heuristic win plus the real-trace two-regime evidence, not on a
  fake named-comparator blowout.

## Paper-facing wording

Recommended phrasing:

`AdaCAD can be interpreted as a first-order approximation to the posterior
reliability weight in Bayes-optimal arbitration, while CoCoA combines multiple
confidence proxies into a stronger heuristic trust score. Our contribution is
to identify the decision-theoretic target these methods approximate and to show
that a Bayes-style rule matches or exceeds them on the completed benchmark
matrix.`
