# Theorem 3 Eta-Tempered Decoding Result

This is the method result implied by the theorem-3 rewrite: we rescore the saved long-CoT trace against a closed-book prior and choose `eta` on a held-out calibration split.

## Headline

- Model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- Benchmark: `conflictbank`
- Condition: `conflict_context`
- CoT length: `1024`
- Selected eta: `0.0`
- Oracle eta on calibration split: `0.0`
- Calibration baseline Brier at eta=1: `0.903275`
- Calibration selected Brier: `0.504515`
- Eval baseline accuracy / confidence / gap at eta=1: `0.036667` / `0.973905` / `0.937239`
- Eval tempered accuracy / confidence / gap: `0.44` / `0.960508` / `0.520508`

## Eta Sweep

| Eta | Count | Accuracy | ECE | Brier | Mean confidence |
|---|---:|---:|---:|---:|---:|
| 0.00 | 200 | 0.4700 | 0.5012 | 0.5045 | 0.9712 |
| 0.10 | 200 | 0.4000 | 0.5586 | 0.5579 | 0.9586 |
| 0.20 | 200 | 0.3550 | 0.6155 | 0.6134 | 0.9705 |
| 0.30 | 200 | 0.3100 | 0.6631 | 0.6667 | 0.9724 |
| 0.40 | 200 | 0.2550 | 0.7115 | 0.7214 | 0.9656 |
| 0.50 | 200 | 0.1950 | 0.7750 | 0.7735 | 0.9700 |
| 0.60 | 200 | 0.1400 | 0.8276 | 0.8246 | 0.9676 |
| 0.70 | 200 | 0.1100 | 0.8742 | 0.8667 | 0.9784 |
| 0.80 | 200 | 0.0950 | 0.8832 | 0.8801 | 0.9782 |
| 0.90 | 200 | 0.0750 | 0.8967 | 0.8912 | 0.9717 |
| 1.00 | 200 | 0.0500 | 0.9198 | 0.9033 | 0.9698 |
