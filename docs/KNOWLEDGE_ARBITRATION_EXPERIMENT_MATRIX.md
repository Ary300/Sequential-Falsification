# Bayes-Optimal Knowledge Arbitration: Experiment Matrix

## Purpose

This file tracks the concrete experiment matrix for the active knowledge
arbitration project. It is intentionally operational rather than narrative.

## Matrix legend

- `P0`: first pilot, needed immediately
- `P1`: headline result tier
- `P2`: robustness / extension tier
- `open`: not yet run
- `scaffolded`: config/code path exists, results not yet run
- `complete`: results exist and are reportable

## Benchmark priority table

| Benchmark | Main role | Priority | Status |
| --- | --- | --- | --- |
| PopQA | prior strength / popularity | P0 | scaffolded |
| DynamicQA | dynamicity / temporal conflict | P0 | scaffolded |
| ConflictBank | broad conflict coverage | P0 | scaffolded |
| WikiContradict | gold contradiction set | P1 | scaffolded |
| NQ-Swap | clean entity substitution | P1 | scaffolded |
| MQuAKE-Remastered | multi-hop conflict | P1 | scaffolded |
| TempLAMA | temporal staleness | P2 | scaffolded |
| FreshQA | freshness and post-cutoff facts | P2 | scaffolded |

## Model priority table

| Model | Purpose | Priority | Status |
| --- | --- | --- | --- |
| Pythia checkpoint slice | checkpoint-resolved scaling | P0 | scaffolded |
| OLMo checkpoint slice | open-data checkpoint-resolved scaling | P0 | scaffolded |
| Llama-3.1-8B | modern strong base model | P0 | scaffolded |
| Qwen-2.5-7B | strong open model | P0 | scaffolded |
| Qwen-2.5-32B | larger open model | P1 | scaffolded |
| Mistral-7B | family robustness | P1 | scaffolded |
| Phi-3-medium | medium-size robustness | P1 | scaffolded |
| DeepSeek-R1-distill | long-CoT calibration stress test | P1 | scaffolded |

## Condition table

| Condition | Description | Needed for |
| --- | --- | --- |
| `closed_book` | no external context | parametric prior estimate |
| `aligned_context` | correct supportive context | positive control |
| `conflict_context` | contextual evidence conflicts with memory | Theorems 1–3 |
| `dual_conflict` | two contradictory contexts | regret and robustness |
| `noise_context` | irrelevant or low-quality context | reliability sensitivity |

## CoT budget table

| Budget bucket | Tokens / mode | Role |
| --- | --- | --- |
| `none` | no chain-of-thought | baseline |
| `short` | 64–128 tokens | low-depth |
| `medium` | 256–512 tokens | default |
| `long` | 1024–2048 tokens | stress regime |
| `very_long` | 4096+ or thinking mode | theorem stress test |

## Headline figure dependencies

### Figure 1: Bayes oracle vs. model arbitration

Needs:

- PopQA
- DynamicQA
- ConflictBank
- at least 5 models
- closed-book and conflict-context conditions

### Figure 2: fixed-policy regret

Needs:

- synthetic oracle
- PopQA and ConflictBank
- policies:
  - always-context
  - always-parametric
  - fixed interpolation
  - adaptive heuristic
  - Bayes proxy

### Figure 3: conflict-conditioned calibration vs. CoT length

Needs:

- ConflictBank or DynamicQA
- at least one reasoning model and one base model
- deterministic and stochastic decoding
- conflict and no-conflict splits

### Figure 4: checkpoint scaling

Needs:

- Pythia or OLMo checkpoints
- one benchmark from PopQA / DynamicQA / TempLAMA

## Required report tables

### Table A: benchmark/model coverage

Must include:

- benchmark
- model
- condition
- seed count
- completion status

### Table B: arbitration gap

Must include:

- Bayes-oracle arbitration accuracy
- model arbitration accuracy
- regret vs. oracle
- KL gap to oracle

### Table C: calibration by CoT length

Must include:

- conflict split
- no-conflict split
- Brier
- NLL
- ECE
- SmoothECE

## First executable pilot

The first serious pilot should be:

- benchmarks:
  - PopQA
  - DynamicQA
- models:
  - Llama-3.1-8B
  - Qwen-2.5-7B
  - Pythia checkpoint slice
- conditions:
  - closed_book
  - aligned_context
  - conflict_context
- outputs:
  - oracle-vs-model arbitration scatter
  - fixed-policy regret table
  - calibration summary
