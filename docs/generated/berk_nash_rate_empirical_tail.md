# Berk-Nash Rate Empirical Note: Tail Window

This note records the finalized tail-window empirical Berk--Nash diagnostic
computed from the dense `R1-14B` theorem-3 trajectory dump on Delta.

## Source

- Rows JSONL:
  `/work/hdd/bgvi/adas17/tts_results/results/theorem3_r1_14b_tail_trajectory_hdd_v1/theorem3_generation_rows.jsonl`
- Rows loaded: `16186`
- Cells analyzed: `4`
- Analysis mode: `tail`
- Analysis window: last `W=100` CoT-budget steps
- Delta follow-up jobs:
  - `2251744` `bn14htail`
  - `2251745` `bn14hearly`
  - both completed successfully on `2026-05-06`

## Per-cell Rates

| Benchmark | Split | Window | Spectral radius | `rho*` from log-TV | log-TV `R^2` | Polynomial TV `R^2` | `q1` |
|---|---|---|---:|---:|---:|---:|---:|
| `conflictbank` | `conflict` | `925→1024 (100)` | `0.139590` | `0.999575` | `0.000122` | `-0.372912` | `-113.363951` |
| `conflictbank` | `no_conflict` | `925→1024 (100)` | `0.117242` | `0.997495` | `0.002827` | `-0.279419` | `-3.413658` |
| `wikicontradict` | `conflict` | `925→1024 (100)` | `0.387669` | `0.998071` | `0.007068` | `-0.471740` | `-831.574155` |
| `wikicontradict` | `no_conflict` | `925→1024 (100)` | `0.483948` | `1.002431` | `0.004304` | `-0.951908` | `NA` |

## Read

- The tail-window `rho*` values stay extremely close to `1.0` on all four
  analyzable cells.
- The local spectral radii are all well below `1`, which is consistent with a
  stable local linearization even though the fitted log-TV rates are very slow.
- The polynomial inverse-TV fits are weak or unstable on this dump, so the
  strongest empirical story is the near-unit `rho*` cross-check rather than a
  quantitatively clean `C / (q1 + t)` law.

