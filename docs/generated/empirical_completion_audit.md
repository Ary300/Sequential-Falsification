# Empirical Completion Audit

## Headline

- The finished empirical core is real and headline-worthy: the spotlight matrix already covers `5` models x `5` benchmarks on `174080` parsed rows.
- On that matrix, Bayes beats the generic heuristic by `0.0833` with bootstrap CI `[0.0371, 0.1112]`.
- The theorem-3 proxy matrix is also statistically clean on its main comparison: Bayes beats the generic heuristic by `0.0585` with bootstrap CI `[0.0155, 0.0961]`.
- The repo now contains both an `8B` and a frontier `70B` Llama spotlight slice with Bayes-vs-heuristic gains `0.1108` and `0.0602`.
- The strongest theorem-3 same-family result is also complete: `Qwen2.5` recovery first appears at about `32B` on `WikiContradict`, with no recovery threshold yet visible on controlled `ConflictBank` conflict.

## Done With Good / Headline Results

- `spotlight_matrix_5x5`: `done_with_headline_result`. 5 models x 5 benchmarks x 174,080 rows.
- `frontier_open_weight_model`: `done_with_headline_result`. Llama-3.1-70B five-benchmark slice on disk.
- `closest_cousin_baselines`: `done_with_headline_result`. AdaCAD, CoCoA, MADAM-RAG, NWCAD, JuICE, Self-RAG, CAD surfaced in spotlight summaries.
- `popqa_benchmark`: `done_with_headline_result`. Bayes vs heuristic 0.0950 [0.0440, 0.1460].
- `nq_swap_benchmark`: `done_with_headline_result`. Bayes vs heuristic 0.1038 [0.0829, 0.1250].
- `same_family_qwen_theorem3_sweep`: `done_with_headline_result`. Qwen2.5 7B/14B/32B complete with 32B recovery on WikiContradict only.
- `cross_family_theorem3_check`: `done_with_honest_negative`. DeepSeek asymmetry true, Qwen asymmetry false.
- `eta_tempering_intervention`: `done_with_mechanism_result`. conflict/no-conflict eta shrink factor 0.52.
- `killer_figure_package`: `done`. scripted SVG package built from finished artifacts.

## Finished Empirical Story

- Dedicated real-benchmark wins are already on disk for `PopQA` (`0.095`) and `NQ-Swap` (`0.1038`).
- Spotlight family consistency is strong: `conflictbank, faitheval, memotrap, nq_swap` are unanimous `5/5` Bayes-over-heuristic wins across model families.
- The theorem-3 cross-family audit is now honest and complete rather than over-claimed: DeepSeek asymmetry = `True`, Qwen asymmetry = `False`.
- The eta intervention gives a real mechanism result rather than just a conjecture: conflict slices tolerate only `0.52x` the do-no-harm eta of no-conflict slices.

## Genuinely Still Missing Compute

- Mistral family runs are not on disk.
- Gemma family runs are not on disk.
- DeepSeek-R1-Distill-Llama frontier sweep is not on disk.
- Closed-model API comparison is not on disk.
- HotpotQA is not on disk as a finished paper artifact.
- TriviaQA is not on disk as a finished paper artifact.
- TabMWP is not on disk as a finished paper artifact.
- GPQA / CLIMATEX / MATH-500 theorem-3 calibration extensions are not on disk as finished paper artifacts.

## Decision

- The finished empirical core is not the blocker anymore; the remaining missing pieces are genuinely new model / benchmark runs, not hidden completed results.
- If we want to extend beyond the current paper-strong package, the next honest empirical step is new Delta compute for the missing families and benchmarks above.
