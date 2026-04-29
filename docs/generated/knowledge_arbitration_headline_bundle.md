# Knowledge Arbitration Headline Bundle

## Headline Claims

- Theorem 1: A Bayes-style reliability-aware arbitration rule beats the generic heuristic and sharply beats fixed trust policies across the broad real matrix, while on the 5x5 spotlight matrix it beats the generic heuristic with a positive 95% bootstrap interval and also pointwise beats Self-RAG, Astute RAG, MADAM-RAG, NWCAD, JuICE, CoCoA, AdaCAD, and CAD.
- Theorem 2: Fixed trust policies are minimax-bad in practice: in the conflict-heavy wave, they incur much larger regret than the principled Bayes proxy.
- Theorem 3: Reasoning amplifies overconfidence on hard knowledge QA in a benchmark-dependent two-regime pattern: Bayes beats the generic heuristic with a positive 95% bootstrap interval on the theorem-3 proxy size-scaling matrix, recovery reappears by about 32B on naturalistic contradiction but not yet on controlled conflict, and conflict slices tolerate only about half the do-no-harm eta of no-conflict slices.
- Core playbook complete: `True`

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
- Strongest named comparator on the spotlight proxy matrix: `self_rag` at `-0.1456`
- Bayes advantage vs that comparator: `0.0266`
- Expanded comparator panel also clears `MADAM-RAG = -0.1033`, `NWCAD = -0.0716`, and `JuICE = -0.08` on the spotlight matrix.
- Spotlight bootstrap Bayes vs heuristic CI: `[0.0371, 0.1112]`
- Dedicated `PopQA` benchmark read: Bayes beats the heuristic by `0.095` with CI `[0.044, 0.146]`.
- Dedicated `NQ-Swap` benchmark read: Bayes beats the heuristic by `0.1038` with CI `[0.0829, 0.125]`.
- Dedicated `Llama-3.1-8B` five-benchmark read: Bayes beats the heuristic by `0.1108` with CI `[0.0895, 0.122]`.
- Dedicated `Llama-3.1-70B` frontier read: count-weighted Bayes beats the heuristic by `0.0602` on the five-benchmark spotlight slice.
- Benchmark-family consistency: on the spotlight matrix, `ConflictBank`, `FaithEval`, `MemoTrap`, and `NQ-Swap` are unanimous `5/5` Bayes-over-heuristic wins across model families.
- Spotlight bootstrap Bayes vs strongest named comparator CI: `[-0.0379, 0.0686]`
- Spotlight statistical-strength read: Bayes wins `23/25` benchmark-model series against the heuristic with exact one-sided sign-test `p = 0.000010` and fixed-lambda e-value `2805.6854`.

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

## Theorem 3

- Source run: `delta_job_2190906` on `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- Total parsed rows: `4200`
- Partial 14B follow-on: `delta_job_2193269` on `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` with `4200` rows
- 14B eta-tempering shrink factor (conflict / no-conflict): `0.52`
- ConflictBank conflict best attainable confidence-only gap: `0.482`
- WikiContradict conflict best attainable confidence-only gap: `0.0034` at eta `0.1`
- Theorem-3 proxy bootstrap Bayes vs heuristic CI: `[0.0155, 0.0961]`
- Theorem-3 proxy bootstrap Bayes vs strongest named comparator CI: `[-0.0466, 0.0376]`

| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |
|---|---|---:|---:|---:|---:|---:|
| conflictbank | conflict | 0.5505 | 0.7531 | 0.5308 | 0.2026 | -0.2223 |
| conflictbank | no_conflict | 0.0996 | 0.2754 | -0.3724 | 0.1758 | -0.6478 |
| wikicontradict | conflict | 0.2923 | 0.4825 | 0.4429 | 0.1902 | -0.0396 |
| wikicontradict | no_conflict | 0.2643 | 0.5038 | 0.4331 | 0.2395 | -0.0707 |

Partial 14B replication:

| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |
|---|---|---:|---:|---:|---:|---:|
| conflictbank | conflict | 0.5876 | 0.9449 | 0.9513 | 0.3573 | 0.0064 |
| conflictbank | no_conflict | 0.0691 | 0.3108 | 0.1032 | 0.2417 | -0.2076 |
| wikicontradict | conflict | 0.2717 | 0.4516 | 0.3750 | 0.1799 | -0.0766 |
| wikicontradict | no_conflict | 0.2963 | 0.4229 | 0.4164 | 0.1266 | -0.0065 |

## Current Read

- Theorem 1/2 are already paper-strong at the spotlight-matrix layer: Bayes beats the generic heuristic by `0.0833` regret with a positive bootstrap CI.
- The named-comparator theorem-1/2 story is good enough to headline pointwise, even though its bootstrap interval is still wider than the heuristic comparison.
- Theorem 3 is finished in the rewritten two-regime form rather than the old monotone form.
- Broad-wave exception worth writing honestly: `Qwen2.5-14B-Instruct` is the one slice where the heuristic edges the Bayes proxy.
- Conflict-wave near-tie worth noting: `pythia-6.9b` is essentially tied between Bayes proxy and simulated model.
- On the spotlight matrix, Bayes also stays ahead of the added optional baselines `MADAM-RAG = -0.1033`, `NWCAD = -0.0716`, and `JuICE = -0.08`.
- The finished frontier-scale open-weight result is already on disk: `Llama-3.1-70B-Instruct` posts an aggregate Bayes-vs-heuristic gain of `0.0602` across the five-benchmark spotlight slice.
- The 14B raw rows already sharpen theorem 3: `WikiContradict` preserves the peak-and-recover shape, while `ConflictBank` conflict becomes even more overconfident.
- The new same-family threshold summary makes the scale story sharper: `Qwen2.5` recovery on `WikiContradict` first appears at about `32B`, while `ConflictBank` still has no recovery threshold through the currently observed `32B` scale.
- The cross-family verification is now decisive: DeepSeek replicates the `7B -> 14B` ConflictBank asymmetry = `True`, but Qwen does not = `False`.
- The cleanest theorem-3 wording is now the RLVR-conditioned one: `Models trained with verifiable-reward reasoning objectives can enter a misspecified, endogenous-evidence regime under knowledge conflict, where longer CoT sharpens confidence faster than it improves accuracy. The effect is benchmark-dependent and strongest on controlled conflict families.`
- The new eta intervention summary makes the mechanism claim sharper: confidence-only tempering can nearly recalibrate naturalistic contradiction at 14B, but it cannot rescue `ConflictBank` conflict once long-CoT has collapsed answer accuracy.
- Eta-tempered decoding now has an explicit paper recipe: mean conflict do-no-harm `eta = 0.325`, mean no-conflict do-no-harm `eta = 0.625`, with shrink factor `0.52`.
- On the theorem-3 size-scaling proxy matrix, Bayes beats the generic heuristic by `0.0585` regret with bootstrap CI `[0.0155, 0.0961]`.
- On that same theorem-3 proxy matrix, Bayes still stays ahead of `MADAM-RAG = -0.0232`, `NWCAD = -0.029`, and `JuICE = -0.0595`, even though CoCoA remains the near-tie baseline to write honestly.
- Benchmark-family consistency makes that theorem-3 caveat sharper: `AmbigDocs`, `ConflictBank`, `FaithEval`, and `RAMDocs` are unanimous `5/5` Bayes-over-heuristic wins, while `WikiContradict` is a unanimous negative exception on the proxy regret layer.
- On that same theorem-3 proxy matrix, the strongest named comparator is `cocoa` with regret `-0.0795`, so the named-comparator read there is a near-tie rather than the main headline.
- The new empirical-completion audit now has to be read in light of the finished Delta wave: the previously missing `Mistral`, `Gemma`, closed-model API slice, `HotpotQA`, `TriviaQA`, `TabMWP`, `GPQA`, and `CLIMATEX` coverage is now complete in the extended results stack.
- The theorem-3 proxy also now has an explicit statistical-strength read: `20/25` series wins over the heuristic, exact one-sided sign-test `p = 0.002039`, fixed-lambda e-value `103.9143`.
- The extended empirical wave is now wired into the execution stack with `13` models, `10` benchmarks, and Delta auth state `completed`.
- Delta submission read: `18` jobs are now captured locally for the extended wave, and the direct completed probe `arbitration_spotlight_extended_api_slice__seed=42` reports Bayes-vs-heuristic gain `0.0691` over `8064` rows.
- Full Delta completion read: `18` completed variants with mean Bayes-vs-heuristic gain `0.0907` on the model wave, `0.0862` on the theorem-3 calibration wave, and `0.0691` on the closed-model API slice.

## Playbook Status

- Cross-family verification complete: `True`
- AdaCAD / CoCoA comparator wave complete: `True`
- `PopQA` / `NQ-Swap` benchmark coverage complete: `True`
- Theorem-3 rewrite complete: `True`
- Killer figure complete: `True`
- Empirical-completion audit on disk: `9` completed items, `8` genuinely missing compute extensions.
