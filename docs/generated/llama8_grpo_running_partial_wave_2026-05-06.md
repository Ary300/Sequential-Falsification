# Llama-8B GRPO Running Partial Wave Snapshot

Status date: `2026-05-06`

This note records a live partial theorem-3 read from the currently running
`Llama-8B GRPO` seed block after the completed `6`-seed checkpoint through
seeds `42–46,48`.

## Partial seeds with synced theorem-3 rows

- valid partial seeds: `12`
- seeds: `47`, `49`, `50`, `51`, `52`, `53`, `54`, `55`, `56`, `57`, `59`, `61`
- total synced rows across valid partials: `7431`
- unweighted mean conflict-minus-no-conflict ECE delta: `+0.0275`
- row-weighted mean conflict-minus-no-conflict ECE delta: `+0.0319`
- positive partial seeds: `6`
- negative partial seeds: `6`

## Per-seed partial headlines

| Seed | Synced rows | Conflict minus no-conflict |
|---|---:|---:|
| 47 | 706 | +0.0334 |
| 49 | 464 | +0.0910 |
| 50 | 596 | +0.1495 |
| 51 | 860 | -0.0395 |
| 52 | 1064 | +0.0596 |
| 53 | 1120 | +0.0493 |
| 54 | 311 | -0.0073 |
| 55 | 599 | -0.0351 |
| 56 | 451 | +0.1472 |
| 57 | 422 | -0.0087 |
| 59 | 470 | -0.0155 |
| 61 | 368 | -0.0941 |

## Still too early to read

- seeds `58` and `60` have started but had `0` synced theorem-3 rows at the
  time of this snapshot
- seeds `62–71` are still pending on `QOSGrpBillingMinutes`

## Read

- The running block is mixed, but the live partial wave is not collapsing
  negative overall.
- The best current real-time summary is a small positive drift:
  row-weighted mean `+0.0319` across `7431` synced rows.
- This is still a provisional read, not a replacement for the finished
  multiseed aggregate, because the per-seed theorem-3 rows are incomplete for
  all active jobs.
