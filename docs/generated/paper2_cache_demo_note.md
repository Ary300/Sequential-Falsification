# Paper 2 Cache Demo Note

This note answers the deployment-side reviewer question about whether the arbitration weight can be precomputed offline for a stable retrieval distribution.

## Headline

- Cached queries covered: `91` / `91` (`cache hit rate = 1.0`)
- Measured Python cache lookup cost: `2.3e-05` ms/query
- Measured current 4-pass incremental cost: `4.3791` s/query
- Estimated per-model-pass cost from the measured run: `1.0948` s/pass
- Projected online cost with `1` decoder pass + cached weight lookup: `1.0948` s/query
- Conservative projected online cost with `2` passes + cached lookup: `2.1896` s/query

## Read

- On a stable retrieval distribution, the arbitration weight itself can be cached offline and looked up online at negligible cost.
- That does not make the full sequence-mixture free-form path free, but it does cut the online geometry from `4` model passes to about `1.5–2` effective passes depending on whether a second contextual scoring pass is retained.
- On the current measured free-form timing, that translates to roughly halving online latency from the `4`-pass baseline into the `~1.1–2.2 s/query` range.
