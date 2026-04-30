# Theorem 3 Confidence-Head Pilot

This note summarizes the lightweight RLCR-style confidence-head pilot trained on frozen `DeepSeek-R1-Distill-Qwen-14B` theorem-3 traces.

## Setup

- Eval slice: `conflictbank` / `conflict_context` / `cot=1024`
- Source rows: `4200`
- Train / val / eval rows: `1200 / 200 / 500`
- Epochs / lr / weight decay: `12 / 0.002 / 0.0001`

## Eval Metrics

| Model | Accuracy | ECE | Brier | AUROC | Mean conf | Gap |
|---|---:|---:|---:|---:|---:|---:|
| Baseline confidence | 0.018 | 0.9513 | 0.927365 | 0.298484 | 0.9693 | 0.9513 |
| Confidence-head pilot | 0.018 | 0.374669 | 0.215942 | 0.436524 | 0.392669 | 0.374669 |

## Headline

- Accuracy is unchanged at `0.018`.
- ECE drops by `0.576631`.
- Brier drops by `0.711423`.
- AUROC rises by `0.13804`.
- Overconfidence gap drops by `0.576631`.
