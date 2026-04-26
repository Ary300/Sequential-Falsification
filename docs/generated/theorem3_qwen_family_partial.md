# Theorem 3 Qwen Family Sweep: Partial Live Read

As of `2026-04-26`, the live Delta same-family Qwen theorem-3 sweep has
already produced usable partial evidence.

Jobs:

- `2196739` `Qwen2.5-7B-Instruct`
- `2196740` `Qwen2.5-14B-Instruct`
- `2196741` `Qwen2.5-32B-Instruct`

Status:

- `7B`: all `12` benchmark/split/CoT groups are already populated
- `14B`: all `12` benchmark/split/CoT groups are already populated, but
  `ConflictBank` counts are still partial
- `32B`: `WikiContradict` groups are populated; `ConflictBank` has not landed
  yet

## Partial group means

| Model | Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `Qwen2.5-7B` | `ConflictBank` | conflict | `0.9839` | `0.9818` | `0.9674` | near-maximal overconfidence under explicit conflict |
| `Qwen2.5-7B` | `ConflictBank` | no-conflict | `0.0982` | `0.0725` | `0.0628` | small gap and mild improvement with longer CoT |
| `Qwen2.5-7B` | `WikiContradict` | conflict | `0.1327` | `0.5917` | `0.6710` | strong hard-QA overconfidence growth |
| `Qwen2.5-7B` | `WikiContradict` | no-conflict | `0.1315` | `0.5612` | `0.6545` | similar growth without clean conflict separation |
| `Qwen2.5-14B` | `ConflictBank` | conflict | `0.9838` | `0.9811` | `0.9792` | same qualitative separation as 7B |
| `Qwen2.5-14B` | `ConflictBank` | no-conflict | `0.1811` | `0.1784` | `0.1108` | gap remains much smaller than conflict |
| `Qwen2.5-14B` | `WikiContradict` | conflict | `0.1222` | `0.4182` | `0.4572` | intermediate-CoT blow-up without recovery yet |
| `Qwen2.5-14B` | `WikiContradict` | no-conflict | `0.0952` | `0.3745` | `0.4660` | again closer to hard-QA than conflict-only |
| `Qwen2.5-32B` | `WikiContradict` | conflict | `0.1139` | `0.3636` | `0.2486` | partial long-CoT self-correction appears |
| `Qwen2.5-32B` | `WikiContradict` | no-conflict | `0.1312` | `0.4028` | `0.3421` | similar partial recovery in no-conflict |

## Current partial read

- The controlled `ConflictBank` family now looks much stronger for the rewritten
  theorem-3 story than the earlier mixed proxy stack did.
- Within the same `Qwen2.5` family, explicit conflict on `ConflictBank`
  already produces near-maximal overconfidence at `7B` and `14B`, while the
  corresponding `no-conflict` slice stays much smaller.
- `WikiContradict` still behaves more like a hard-QA overconfidence task than a
  clean conflict-only task.
- The partial `Qwen2.5-32B` `WikiContradict` trace shows the first same-family
  sign of long-CoT self-correction (`0.3636 -> 0.2486` on conflict), which is
  exactly the kind of two-regime shape the rewritten theorem-3 wants.

## Honest caveat

These are live partial reads from `theorem3_generation_rows.jsonl`, not final
post-job reports. They should be treated as provisional until the Delta jobs
finish and the final theorem-3 report artifacts are written.
