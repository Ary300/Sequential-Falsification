# Theorem 3 Qwen Family Sweep: Live Delta Read

As of `2026-04-26`, the live Delta same-family Qwen theorem-3 sweep has
already produced paper-usable evidence:

Jobs:

- `2196739` `Qwen2.5-7B-Instruct`
- `2196740` `Qwen2.5-14B-Instruct`
- `2196741` `Qwen2.5-32B-Instruct`

Status:

- `7B`: completed with final report written
- `14B`: completed with final report written
- `32B`: all `12` benchmark/split/CoT groups are now populated, but the
  `ConflictBank` slice is still partial while the job runs

## Current group means

| Model | Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `Qwen2.5-7B` | `ConflictBank` | conflict | `0.9856` | `0.9849` | `0.9693` | final run; explicit conflict stays near-maximally overconfident |
| `Qwen2.5-7B` | `ConflictBank` | no-conflict | `0.0868` | `0.0723` | `0.0537` | final run; small gap and steady improvement with longer CoT |
| `Qwen2.5-7B` | `WikiContradict` | conflict | `0.1327` | `0.5917` | `0.6710` | strong hard-QA overconfidence growth |
| `Qwen2.5-7B` | `WikiContradict` | no-conflict | `0.1315` | `0.5612` | `0.6545` | similar growth without clean conflict separation |
| `Qwen2.5-14B` | `ConflictBank` | conflict | `0.9776` | `0.9731` | `0.9584` | final run; controlled conflict remains catastrophic |
| `Qwen2.5-14B` | `ConflictBank` | no-conflict | `0.0639` | `0.0679` | `0.0476` | final run; gap stays much smaller than conflict |
| `Qwen2.5-14B` | `WikiContradict` | conflict | `0.1222` | `0.4182` | `0.4572` | intermediate-CoT blow-up without recovery yet |
| `Qwen2.5-14B` | `WikiContradict` | no-conflict | `0.0952` | `0.3745` | `0.4660` | again closer to hard-QA than conflict-only |
| `Qwen2.5-32B` | `ConflictBank` | conflict | `0.9448` | `0.9312` | `0.8829` | partial live read; conflict remains huge even at 32B |
| `Qwen2.5-32B` | `ConflictBank` | no-conflict | `0.0594` | `0.0456` | `0.0532` | partial live read; still far below conflict gap |
| `Qwen2.5-32B` | `WikiContradict` | conflict | `0.0945` | `0.3520` | `0.2635` | first same-family long-CoT self-correction signal |
| `Qwen2.5-32B` | `WikiContradict` | no-conflict | `0.0837` | `0.3422` | `0.3232` | similar but weaker recovery in no-conflict |

## Current read

- The controlled `ConflictBank` family is now the cleanest same-family support
  for the rewritten theorem-3 story anywhere in the repo.
- Within `Qwen2.5`, explicit conflict on `ConflictBank` remains massively more
  overconfident than `no-conflict` at final `7B`, final `14B`, and the
  currently-landed `32B` rows.
- `WikiContradict` still behaves more like a hard-QA overconfidence task than a
  pure conflict-only task at `7B` and `14B`, but `32B` is the first same-family
  model to show genuine long-CoT recovery on the conflict slice
  (`0.3520 -> 0.2635`).
- The emerging same-family scale story is therefore sharper than the old
  monotone theorem: controlled conflict can stay locked into catastrophic
  overconfidence, while naturalistic contradiction begins to recover only at
  larger scale.

## Honest caveat

The `Qwen2.5-7B` and `Qwen2.5-14B` numbers above are final. The
`Qwen2.5-32B` numbers are still live reads from `theorem3_generation_rows.jsonl`,
so the exact `ConflictBank` means may move slightly before the final theorem-3
report artifacts are written.
