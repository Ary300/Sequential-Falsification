# Theorem 3 Eta-Tempered Decoding Result

This is the method result implied by the theorem-3 rewrite: we rescore the saved long-CoT trace against a closed-book prior and choose `eta` on a held-out calibration split.

## Headline

- Model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- Benchmark: `wikicontradict`
- Condition: `conflict_context`
- CoT length: `1024`
- Selected eta: `0.3`
- Oracle eta on calibration split: `0.3`
- Calibration baseline Brier at eta=1: `0.301036`
- Calibration selected Brier: `0.29737`
- Eval baseline accuracy / confidence / gap at eta=1: `0.62` / `0.948304` / `0.328304`
- Eval tempered accuracy / confidence / gap: `0.64` / `0.958215` / `0.318215`

## Eta Sweep

| Eta | Count | Accuracy | ECE | Brier | Mean confidence |
|---|---:|---:|---:|---:|---:|
| 0.00 | 100 | 0.7100 | 0.3272 | 0.3041 | 0.9511 |
| 0.10 | 100 | 0.7100 | 0.3223 | 0.3027 | 0.9581 |
| 0.20 | 100 | 0.7000 | 0.3020 | 0.3013 | 0.9644 |
| 0.30 | 100 | 0.7000 | 0.2904 | 0.2974 | 0.9758 |
| 0.40 | 100 | 0.7000 | 0.3037 | 0.3019 | 0.9701 |
| 0.50 | 100 | 0.7000 | 0.3050 | 0.3041 | 0.9672 |
| 0.60 | 100 | 0.7000 | 0.3155 | 0.3046 | 0.9652 |
| 0.70 | 100 | 0.7000 | 0.3096 | 0.3051 | 0.9612 |
| 0.80 | 100 | 0.7000 | 0.3108 | 0.3045 | 0.9578 |
| 0.90 | 100 | 0.7000 | 0.3166 | 0.3033 | 0.9550 |
| 1.00 | 100 | 0.7100 | 0.3244 | 0.3010 | 0.9560 |
