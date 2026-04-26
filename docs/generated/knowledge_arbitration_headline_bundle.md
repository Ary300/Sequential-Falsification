# Knowledge Arbitration Headline Bundle

## Headline Claims

- Theorem 1: A Bayes-style reliability-aware arbitration rule beats the generic heuristic and sharply beats fixed trust policies, and the result gets stronger on the expanded `5 x 5` benchmark-backed spotlight matrix.
- Theorem 2: Fixed trust policies are minimax-bad in practice: in both the conflict-heavy wave and the expanded spotlight matrix, they incur much larger regret than the principled Bayes proxy.
- Theorem 3: Reasoning amplifies overconfidence on hard knowledge QA, and
  explicit conflict further worsens the effect on controlled conflict families
  at larger scale.

## Expanded Spotlight Matrix

- Wave: `arbitration_spotlight_t12_benchmark_v1` on `174,080` examples across
  `5` benchmarks x `5` models
- Benchmarks: `ConflictBank`, `FaithEval`, `MemoTrap`, `NQ-Swap`, `PopQA`
- `bayes_proxy` mean regret: `-0.1722`
- `heuristic_adaptive` mean regret: `-0.0889`
- Bayes minus heuristic regret gap: `0.0833`
- `simulated_model` mean regret: `-0.2046`
- `fixed_50` mean regret: `0.4035`
- `always_context` mean regret: `7.9943`
- `always_parametric` mean regret: `5.2420`
- Mean oracle-model absolute gap: `0.1932`
- Mean oracle-model KL: `1.4680`
- Mean conflict / no-conflict ECE deltas: `-0.1321` / `-0.0212`

This is now the strongest theorem-1/theorem-2 benchmark-backed result in the
repo.

## Theorem 1

- Wave: `broad_real_headline_wave_reestimated_v3` across `176` series
- `bayes_proxy` mean regret: `-0.04607070194023072`
- `bayes_proxy` accuracy / ECE: `0.8866` / `0.1354`
- `heuristic_adaptive` mean regret: `-0.023349765237714086`
- Bayes minus heuristic regret gap: `0.0227`
- `simulated_model` mean regret: `0.1407719311984596`
- `fixed_50` mean regret: `0.3650119290428605`
- `always_context` mean regret: `7.223688766628678`
- `always_parametric` mean regret: `5.935552288286208`
- Mean oracle-model absolute gap: `0.1969`
- Mean oracle-model KL: `1.2288`
- Mean conflict / no-conflict ECE deltas: `-0.0054` / `-0.0238`

Per-model read:

- `Qwen/Qwen2.5-14B-Instruct`: Bayes `0.0098`, heuristic `0.0050`, simulated `0.2546`
- `Qwen/Qwen2.5-7B-Instruct`: Bayes `-0.0647`, heuristic `-0.0328`, simulated `-0.0638`
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`: Bayes `-0.0647`, heuristic `-0.0328`, simulated `0.4362`
- `meta-llama/Llama-3.1-8B-Instruct`: Bayes `-0.0647`, heuristic `-0.0328`, simulated `-0.0638`

## Theorem 2

- Wave: `conflict_headline_wave_reestimated_v3` across `175` series
- `bayes_proxy` mean regret: `-0.12557343144995242`
- `bayes_proxy` accuracy / ECE: `0.9028` / `0.0724`
- `heuristic_adaptive` mean regret: `-0.07515526270093635`
- Bayes minus heuristic regret gap: `0.0504`
- `simulated_model` mean regret: `0.11035460812956133`
- `fixed_50` mean regret: `0.303704532192305`
- `always_context` mean regret: `5.903744200087245`
- `always_parametric` mean regret: `7.132882061129149`
- Mean oracle-model absolute gap: `0.2768`
- Mean oracle-model KL: `2.1393`
- Mean conflict / no-conflict ECE deltas: `-0.0191` / `-0.0383`

Per-model read:

- `EleutherAI/pythia-6.9b`: Bayes `-0.1510`, heuristic `-0.1193`, simulated `-0.1534`
- `Qwen/Qwen2.5-7B-Instruct`: Bayes `-0.1192`, heuristic `-0.0641`, simulated `0.0789`
- `Qwen/Qwen3-8B`: Bayes `-0.1192`, heuristic `-0.0641`, simulated `0.0789`
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`: Bayes `-0.1192`, heuristic `-0.0641`, simulated `0.4686`
- `meta-llama/Llama-3.1-8B-Instruct`: Bayes `-0.1192`, heuristic `-0.0641`, simulated `0.0789`

## Theorem 2: Proxy Size-Scaling Support

- Wave: `arbitration_spotlight_t3_scaling_proxy_v1` on `65,190` examples
  across `AmbigDocs`, `ConflictBank`, `FaithEval`, `RAMDocs`, and
  `WikiContradict`
- `bayes_proxy` mean regret: `-0.0774`
- `heuristic_adaptive` mean regret: `-0.0189`
- Bayes minus heuristic regret gap: `0.0585`
- `simulated_model` mean regret: `0.1533`
- `fixed_50` mean regret: `0.3352`
- `always_context` mean regret: `6.5247`
- `always_parametric` mean regret: `6.5751`
- Mean oracle-model absolute gap: `0.2448`
- Mean oracle-model KL: `1.7309`
- Mean conflict / no-conflict ECE deltas: `-0.0736` / `-0.0229`

## Theorem 3

- Source run: `delta_job_2190906` on `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- Total parsed rows: `4200`
- Final 14B follow-on: `delta_job_2193269` on `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` with `4200` rows

| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |
|---|---|---:|---:|---:|---:|---:|
| conflictbank | conflict | 0.5505 | 0.7531 | 0.5308 | 0.2026 | -0.2223 |
| wikicontradict | conflict | 0.2923 | 0.4825 | 0.4429 | 0.1902 | -0.0396 |

Final 14B replication:

| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |
|---|---|---:|---:|---:|---:|---:|
| conflictbank | conflict | 0.5876 | 0.9449 | 0.9513 | 0.3573 | 0.0064 |
| wikicontradict | conflict | 0.2717 | 0.4516 | 0.3750 | 0.1799 | -0.0766 |

Corrected closed-book controls:

| Benchmark | Model | `cot=0` gap | `cot=128` gap | `cot=1024` gap |
|---|---|---:|---:|---:|
| conflictbank | 7B closed-book | 0.4885 | 0.7220 | 0.6235 |
| wikicontradict | 7B closed-book | 0.4950 | 0.6220 | 0.6499 |
| conflictbank | 14B closed-book | 0.4917 | 0.8168 | 0.7890 |
| wikicontradict | 14B closed-book | 0.5044 | 0.5879 | 0.6938 |

## Current Read

- Theorem 1/2 are now paper-strong at the proxy-regret layer and materially
  stronger on the new `5 x 5` spotlight matrix than on the original smaller
  waves.
- Theorem 3 does not support the old monotone or conflict-only sign-flip statement.
- The strongest current theorem-3 claim is hard-QA overconfidence amplification with conflict-sensitive severity on controlled conflict families.
- Broad-wave exception worth writing honestly: `Qwen2.5-14B-Instruct` is the one slice where the heuristic edges the Bayes proxy.
- Conflict-wave near-tie worth noting: `pythia-6.9b` is essentially tied between Bayes proxy and simulated model.
- The finished 14B run plus corrected closed-book control sharpen theorem 3: `ConflictBank` conflict stays catastrophically overconfident through long CoT, while `WikiContradict` looks more like a hard-QA overconfidence task than a clean conflict-specific effect.
- The live same-family theorem-3 gate is now the Delta Qwen sweep:
  `2196739` (`7B`), `2196740` (`14B`), and `2196741` (`32B`), all running
  with successful `vLLM` startup and active generation traffic.
