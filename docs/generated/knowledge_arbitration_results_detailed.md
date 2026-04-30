# Knowledge Arbitration Detailed Results

As of `2026-04-29`, this file summarizes the current finished empirical package in detail. It separates completed, paper-usable results from still-running theorem-3 audit jobs on Delta.

## 1. Finished Headline Results

### 1.1 Theorem 1: Broad Real Wave

Source wave: `broad_real_headline_wave_reestimated_v3`

| Policy | Mean Regret | Accuracy | ECE |
|---|---:|---:|---:|
| Bayes proxy | `-0.0461` | `0.8866` | `0.1354` |
| Heuristic adaptive | `-0.0233` | — | — |
| Simulated model | `0.1408` | — | — |
| Fixed 50/50 | `0.3650` | — | — |
| Always context | `7.2237` | — | — |
| Always parametric | `5.9356` | — | — |

Additional diagnostics:

| Measure | Value |
|---|---:|
| Bayes minus heuristic regret gap | `0.0227` |
| Mean oracle-model absolute gap | `0.1969` |
| Mean oracle-model KL | `1.2288` |
| Mean conflict ECE delta | `-0.0054` |
| Mean no-conflict ECE delta | `-0.0238` |

Per-model read reported in the main bundle:

| Model | Bayes Proxy | Heuristic | Simulated Model |
|---|---:|---:|---:|
| `Qwen/Qwen2.5-14B-Instruct` | `0.0098` | `0.0050` | `0.2546` |
| `Qwen/Qwen2.5-7B-Instruct` | `-0.0647` | `-0.0328` | `-0.0638` |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | `-0.0647` | `-0.0328` | `0.4362` |
| `meta-llama/Llama-3.1-8B-Instruct` | `-0.0647` | `-0.0328` | `-0.0638` |

### 1.2 Theorem 1: Spotlight Matrix

This is the strongest poster-to-spotlight result layer.

| Quantity | Value |
|---|---:|
| Bayes vs heuristic regret gain | `0.0833` |
| 95% bootstrap CI | `[0.0371, 0.1112]` |
| Bayes wins vs heuristic | `23/25` series |
| Exact one-sided sign test | `p = 0.000010` |
| Fixed-lambda e-value | `2805.6854` |

Named comparator panel on the spotlight matrix:

| Comparator | Mean Regret | Bayes Advantage |
|---|---:|---:|
| `MADAM-RAG` | `-0.1033` | `0.0689` |
| `NWCAD` | `-0.0716` | `0.1006` |
| `JuICE` | `-0.0800` | `0.0922` |
| `CoCoA` | `-0.1278` | `0.0444` |
| `AdaCAD` | `-0.1063` | `0.0659` |
| `CAD` | `-0.0790` | `0.0932` |
| `Astute RAG` | `-0.1396` | `0.0326` |
| `CRAG` | `-0.0449` | `0.1273` |
| `Self-RAG` | `-0.1456` | `0.0266` |
| Heuristic adaptive | `-0.0889` | `0.0833` |
| Simulated model | `-0.2046` | `-0.0324` |

Finished benchmark/model spotlights:

| Slice | Result |
|---|---|
| `PopQA` | Bayes beats heuristic by `0.0950`, CI `[0.0440, 0.1460]` |
| `NQ-Swap` | Bayes beats heuristic by `0.1038`, CI `[0.0829, 0.1250]` |
| `Llama-3.1-8B` | Bayes beats heuristic by `0.1108`, CI `[0.0895, 0.1220]` |
| `Llama-3.1-70B` | Bayes beats heuristic by `0.0602` |

### 1.3 Theorem 2: Conflict-Heavy Wave

Source wave: `conflict_headline_wave_reestimated_v3`

| Policy | Mean Regret | Accuracy | ECE |
|---|---:|---:|---:|
| Bayes proxy | `-0.1256` | `0.9028` | `0.0724` |
| Heuristic adaptive | `-0.0752` | — | — |
| Simulated model | `0.1104` | — | — |
| Fixed 50/50 | `0.3037` | — | — |
| Always context | `5.9037` | — | — |
| Always parametric | `7.1329` | — | — |

Additional diagnostics:

| Measure | Value |
|---|---:|
| Bayes minus heuristic regret gap | `0.0504` |
| Mean oracle-model absolute gap | `0.2768` |
| Mean oracle-model KL | `2.1393` |
| Mean conflict ECE delta | `-0.0191` |
| Mean no-conflict ECE delta | `-0.0383` |

Per-model read reported in the main bundle:

| Model | Bayes Proxy | Heuristic | Simulated Model |
|---|---:|---:|---:|
| `EleutherAI/pythia-6.9b` | `-0.1510` | `-0.1193` | `-0.1534` |
| `Qwen/Qwen2.5-7B-Instruct` | `-0.1192` | `-0.0641` | `0.0789` |
| `Qwen/Qwen3-8B` | `-0.1192` | `-0.0641` | `0.0789` |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | `-0.1192` | `-0.0641` | `0.4686` |
| `meta-llama/Llama-3.1-8B-Instruct` | `-0.1192` | `-0.0641` | `0.0789` |

## 2. Finished Theorem 3 Results

### 2.1 Real 7B Sweep

| Benchmark | Split | `cot=0` Gap | `cot=128` Gap | `cot=1024` Gap | `0->128` | `128->1024` |
|---|---|---:|---:|---:|---:|---:|
| `conflictbank` | conflict | `0.5505` | `0.7531` | `0.5308` | `0.2026` | `-0.2223` |
| `conflictbank` | no_conflict | `0.0996` | `0.2754` | `-0.3724` | `0.1758` | `-0.6478` |
| `wikicontradict` | conflict | `0.2923` | `0.4825` | `0.4429` | `0.1902` | `-0.0396` |
| `wikicontradict` | no_conflict | `0.2643` | `0.5038` | `0.4331` | `0.2395` | `-0.0707` |

### 2.2 Partial 14B Replication

| Benchmark | Split | `cot=0` Gap | `cot=128` Gap | `cot=1024` Gap | `0->128` | `128->1024` |
|---|---|---:|---:|---:|---:|---:|
| `conflictbank` | conflict | `0.5876` | `0.9449` | `0.9513` | `0.3573` | `0.0064` |
| `conflictbank` | no_conflict | `0.0691` | `0.3108` | `0.1032` | `0.2417` | `-0.2076` |
| `wikicontradict` | conflict | `0.2717` | `0.4516` | `0.3750` | `0.1799` | `-0.0766` |
| `wikicontradict` | no_conflict | `0.2963` | `0.4229` | `0.4164` | `0.1266` | `-0.0065` |

### 2.3 Theorem-3 Proxy Matrix

| Quantity | Value |
|---|---:|
| Bayes vs heuristic gain | `0.0585` |
| 95% bootstrap CI | `[0.0155, 0.0961]` |
| Bayes wins vs heuristic | `20/25` series |
| Exact one-sided sign test | `p = 0.002039` |
| Fixed-lambda e-value | `103.9143` |
| Strongest named comparator | `CoCoA` |
| Strongest named comparator regret | `-0.0795` |
| Bayes advantage vs strongest named comparator | `-0.0021` |

### 2.4 RLVR Validation and Yoon Contrast

RLVR validation:

| Quantity | Value |
|---|---:|
| DeepSeek-Llama all-slice gain | `0.0984` |
| DeepSeek-Llama conflict-only gain | `-0.0439` |
| DeepSeek-Llama `ConflictBank` conflict `cot=1024` gain | `0.0518` |
| DeepSeek-Qwen-7B long-CoT gain | `0.1072` |
| Qwen2.5-32B long-CoT gain | `0.0518` |
| Qwen2.5-14B long-CoT gain | `0.0889` |

Yoon contrast:

| Quantity | Value |
|---|---:|
| `TriviaQA` gap at `cot=0` | `0.2512` |
| `TriviaQA` gap at `cot=128` | `0.4944` |
| `TriviaQA` gap at `cot=1024` | `0.4830` |
| `ConflictBank` conflict gap at `cot=0` | `0.5876` |
| `ConflictBank` conflict gap at `cot=128` | `0.9449` |
| `ConflictBank` conflict gap at `cot=1024` | `0.9513` |
| Strict sign flip | `False` |
| Conflict worse than `TriviaQA` at short CoT | `True` |
| Conflict worse than `TriviaQA` at long CoT | `True` |
| Conflict worse than closed-book at long CoT | `True` |

## 3. Finished Method and Calibration Results

### 3.1 Eta-Tempered Decoding

Real post-trace run: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` on `ConflictBank` / `conflict_context`

| Quantity | Value |
|---|---:|
| Selected `eta` | `0.0` |
| Conservative largest no-harm `eta` | `0.9` |
| Brier before | `0.903275` |
| Brier after | `0.504515` |
| Accuracy before | `0.036667` |
| Accuracy after | `0.440000` |
| Overconfidence gap before | `0.937239` |
| Overconfidence gap after | `0.520508` |

### 3.2 Confidence-Head Pilot

| Quantity | Baseline | Pilot | Delta |
|---|---:|---:|---:|
| Accuracy | `0.018000` | `0.018000` | `0.000000` |
| AUROC | `0.298484` | `0.436524` | `0.138040` |
| Brier | `0.927365` | `0.215942` | `-0.711423` |
| ECE | `0.951300` | `0.374669` | `-0.576631` |

Pilot metadata:

| Field | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` |
| Eval benchmark | `conflictbank` |
| Eval condition | `conflict_context` |
| Eval CoT length | `1024` |
| Source rows | `300` |
| Train / val / eval rows | `180 / 60 / 60` |
| Epochs | `20` |
| LR | `0.001` |

### 3.3 Post-hoc Calibration Baselines

Same worst-case slice: `ConflictBank` / `conflict_context` / `cot=1024`

| Method | Brier |
|---|---:|
| Raw identity | `0.924083` |
| Temperature scaling | `0.675480` |
| Eta-tempering | `0.530564` |
| Platt | `0.016660` |
| Isotonic | `0.016379` |

Best Brier method: `isotonic`

## 4. Finished Synthetic and Auxiliary Results

### 4.1 Synthetic Oracle

| Quantity | Value |
|---|---:|
| Held-out `R^2` at calibration size `2048` | `0.9984` |
| Target `R^2 > 0.95` achieved | `True` |

### 4.2 Bayes Component Ablation

| Variant | Mean Regret | Worse-rate |
|---|---:|---:|
| Full Bayes | `-0.1984` | — |
| No prior-strength estimate | `-0.2226` | `0.74` |
| No reliability estimate | `-0.1624` | `0.94` |
| No posterior update | `0.1695` | `0.94` |

### 4.3 MQuAKE Multi-hop Proxy

Reference model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`

| Policy | Depth-1 Error | Depth-2 Error | Depth-3 Error |
|---|---:|---:|---:|
| Bayes proxy | `0.045542` | `0.089011` | `0.130499` |
| Heuristic adaptive | `0.217600` | `0.387850` | `0.521054` |
| Fixed 50/50 | `0.500000` | `0.750000` | `0.875000` |
| Always parametric | `1.000000` | `1.000000` | `1.000000` |
| Always context | `0.000000` | `0.000000` | `0.000000` |

### 4.4 Retrieval-backed WikiContradict Demo

| Quantity | Value |
|---|---:|
| Top-1 aligned retrieval rate | `0.616601` |
| Top-1 conflict retrieval rate | `0.300395` |
| Top-5 contains both aligned and conflicting passages | `0.719368` |

Metadata:

| Field | Value |
|---|---|
| Benchmark | `wikicontradict` |
| Retriever | `bm25` |
| Number of examples | `253` |
| Number of corpus docs | `506` |

## 5. Extended Delta Wave

Completed extended-wave summary:

| Wave | Count | Total Rows | Mean Bayes Regret | Mean Heuristic Regret | Mean Gain |
|---|---:|---:|---:|---:|---:|
| API slice | `3` | `24192` | `0.0801` | `0.1493` | `0.0691` |
| Model wave | `3` | `737280` | `-0.1870` | `-0.0963` | `0.0907` |
| T3 calibration wave | `12` | `774144` | `-0.1542` | `-0.0680` | `0.0862` |

Best single completed extended-wave gain:

| Run | Gain | Rows |
|---|---:|---:|
| `arbitration_spotlight_extended_model_wave__seed=42` | `0.09065076945710755` | `245760` |

## 6. Live Delta Audit Wave Status

These are not finished theorem-3 headline results yet. They are active or queued jobs for the dense-grid Tier A/B/C audit wave.

As of the latest check:

- Running: `2215664`, `2215665`, `2215666`, `2215667`, `2215668`, `2215669`, `2215670`, `2215671`, `2215672`, `2215673`, `2215674`, `2215677`, `2215678`, `2215679`, `2215680`
- Pending: `2215675`, `2215676`, `2215681`
- Pending reason: `QOSGrpBillingMinutes`

Interpretation:

- The theorem-3 audit expansion is submitted and healthy.
- Partial row files exist for some Tier A runs.
- No final completed Tier A/B/C summary artifact exists yet, so these jobs are not counted in the finished headline package above.
