# Berk-Nash Rate Empirical Note: Early Window

This note records the finalized early-window empirical Berk--Nash diagnostic
computed from the same dense `R1-14B` theorem-3 trajectory dump on Delta.

## Source

- Rows JSONL:
  `/work/hdd/bgvi/adas17/tts_results/results/theorem3_r1_14b_tail_trajectory_hdd_v1/theorem3_generation_rows.jsonl`
- Rows loaded: `16186`
- Cells analyzed: `4`
- Analysis mode: `early`
- Analysis window: first `W=100` CoT-budget steps
- Delta follow-up jobs:
  - `2251744` `bn14htail`
  - `2251745` `bn14hearly`
  - both completed successfully on `2026-05-06`

## Per-cell Rates

| Benchmark | Split | Window | Spectral radius | `rho*` from log-TV | log-TV `R^2` | Polynomial TV `R^2` | `q1` |
|---|---|---|---:|---:|---:|---:|---:|
| `conflictbank` | `conflict` | `0→1018 (100)` | `0.329985` | `0.996233` | `0.231948` | `0.007175` | `171.187962` |
| `conflictbank` | `no_conflict` | `0→1018 (100)` | `0.246460` | `0.996508` | `0.135461` | `0.015392` | `69.153099` |
| `wikicontradict` | `conflict` | `0→1018 (100)` | `0.815676` | `0.997877` | `0.210934` | `-7728548797681.422000` | `-184.265934` |
| `wikicontradict` | `no_conflict` | `0→1018 (100)` | `0.358969` | `0.997175` | `0.158155` | `-2972867550161.152300` | `-74.393983` |

## Read

- The early-window `rho*` values also stay very close to `1.0` on all four
  analyzable cells rather than collapsing away from the tail regime.
- This is the strongest empirical answer to the early-`t` reviewer question:
  the spectral diagnostic remains informative even before a clean asymptotic
  tail approximation should be expected.
- The early polynomial fits are unstable on the `WikiContradict` cells, so the
  robust signal is again the near-unit `rho*` behavior rather than the
  polynomial surrogate.

