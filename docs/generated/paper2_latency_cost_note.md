# Paper 2 Latency and Cost Note

This note answers the reviewer objection that the geometric-mixture free-form pipeline adds non-trivial inference cost relative to a single-pass decoder baseline.

## Measured Delta wall-clock

- `tiny` run (`job 2235943`): `12` kept queries in `89.0` s, `7.42` s/query, `0.135` q/s.
- `smoke` run (`job 2235810`): `24` kept queries in `147.0` s, `6.12` s/query, `0.163` q/s.
- `full` run (`job 2235753`): `91` kept queries in `437.0` s, `4.80` s/query, `0.208` q/s.

## Simple scaling fit

- Fixed overhead: `38.9527` s
- Incremental cost per kept query: `4.3791` s/query

## Pass geometry

- Single-pass decoder baseline (`CAD`/`CoCoA`-style direct context decode): `1` generation pass, `0` extra scoring passes.
- Sequence-level Paper 2 mixture in the current free-form harness: `2` generation passes + `2` scoring forwards = `4` model passes/query.

## Read

- The adoption concern is real: in the current implementation, the sequence-level mixture is materially more expensive than a single-pass context decoder.
- The cleanest honest phrasing is that the free-form mixture is a capability/robustness evaluation path, not yet a cheap serving path.
- Because the first free-form run is not yet a strong accuracy headline, this cost should be disclosed plainly rather than spun away.