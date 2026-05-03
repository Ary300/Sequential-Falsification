# Theorem 3 Review Follow-Ups

This note closes the review-facing analysis gaps around theorem-3 uncertainty, conflict severity, and RLCR+eta tradeoffs.

## Bootstrap CIs On Headline Deltas

| Model | Conflict delta | 95% CI | No-conflict delta | 95% CI | Conflict-minus-no-conflict | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| llama8_dpo | -0.1051 | [-0.1744, -0.0340] | -0.1499 | [-0.2211, -0.0801] | 0.0448 | [-0.0504, 0.1477] |
| llama8_grpo | 0.2640 | [0.1862, 0.3404] | -0.0796 | [-0.1754, 0.0090] | 0.3436 | [0.2297, 0.4757] |
| mistral7b | 0.0161 | [-0.0312, 0.0635] | 0.0012 | [-0.0528, 0.0547] | 0.0150 | [-0.0584, 0.0870] |
| gemma9b | 0.0064 | [-0.0208, 0.0394] | -0.0289 | [-0.0508, -0.0109] | 0.0352 | [0.0030, 0.0732] |
| gemma27b | -0.0010 | [-0.0273, 0.0273] | 0.0159 | [-0.0101, 0.0433] | -0.0168 | [-0.0519, 0.0214] |
| qwen14_dpo | 0.1838 | [0.1087, 0.2574] | 0.1186 | [0.0416, 0.1900] | 0.0652 | [-0.0405, 0.1707] |
| qwen14_grpo | 0.0108 | [-0.0181, 0.0442] | 0.0026 | [-0.0314, 0.0384] | 0.0082 | [-0.0362, 0.0557] |
| phi3_dpo | -0.0507 | [-0.1052, -0.0045] | -0.0537 | [-0.1033, -0.0045] | 0.0030 | [-0.0659, 0.0701] |
| phi3_grpo | -0.1000 | [-0.1576, -0.0407] | -0.3087 | [-0.3817, -0.2415] | 0.2088 | [0.1208, 0.3051] |
| olmo2_dpo | 0.0952 | [0.0357, 0.1549] | 0.0469 | [-0.0170, 0.1168] | 0.0483 | [-0.0444, 0.1350] |
| olmo2_grpo | 0.0027 | [-0.0691, 0.0772] | -0.0227 | [-0.1044, 0.0519] | 0.0254 | [-0.0811, 0.1270] |
| deepseek_llama8 | 0.0080 | [-0.0405, 0.0528] | -0.0695 | [-0.1184, -0.0267] | 0.0775 | [0.0147, 0.1435] |
| rlcr | 0.1455 | [0.0796, 0.2101] | -0.1456 | [-0.2088, -0.0824] | 0.2910 | [0.1999, 0.3827] |

## Conflict Severity Dose Response

- Source rows: `/work/nvme/bgvi/adas17/tts_results/results/e1_llama8b_grpo/theorem3_eval_retry/theorem3_generation_rows.jsonl`
- Paired prompts: `128`
- Spearman(conflict strength, gap delta): `-0.0272`

| Bin | Count | Mean conflict strength | Mean gap delta | 95% CI | Mean ECE-proxy delta | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| low | 42 | 0.6800 | 0.5085 | [0.3851, 0.6263] | 0.5085 | [0.3851, 0.6263] |
| mid | 42 | 0.7581 | 0.5352 | [0.3714, 0.6862] | 0.5590 | [0.4045, 0.7014] |
| high | 44 | 0.9127 | 0.4702 | [0.3350, 0.5930] | 0.4702 | [0.3350, 0.5930] |

## RLCR + Eta Per-Benchmark Breakdown

| Benchmark | Mean accuracy delta | 95% CI | Mean ECE delta | 95% CI | Mean Brier delta | 95% CI | Aligned-context accuracy delta | Selected eta values |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| conflictbank | 0.3125 | [0.1016, 0.5260] | -0.3325 | [-0.5648, -0.1058] | -0.3201 | [-0.5466, -0.1009] | 0.0000 | 0.0, 1.0 |
| wikicontradict | 0.0260 | [0.0104, 0.0417] | 0.0051 | [-0.0085, 0.0178] | -0.0237 | [-0.0394, -0.0076] | 0.0312 | 0.2, 1.0 |

## Trace Separation Shuffled Control

- Records: `25`
- Observed win fraction: `0.76`
- Shuffled-label mean win fraction: `0.6545`
- Shuffled-label 95% interval: `[0.56, 0.76]`

## Read

- The bootstrap table makes the ranking uncertainty explicit instead of implying that all small point differences are meaningful.
- The dose-response cut checks whether conflict blowup scales with conflict strength instead of looking like pure noise.
- The RLCR+eta table shows whether the global gain is broad or mostly carried by `ConflictBank`.
- The shuffled-label trace control checks whether the 0.81 self-confirmation rate is an artifact of the scoring setup.
