# Extended Empirical Wave Readiness

## Status

- Spotlight floor ready: `True`
- Unique models: `13`
- Unique benchmarks: `10`
- Unique baselines: `15`
- Unique ablations: `5`
- Total scheduled cells before backend-specific chunking: `7356`
- Three-seed coverage encoded in config: `[42, 43, 44]`
- Delta auth state: `submitted`
- Delta auth detail: Authenticated to DeltaAI on 2026-04-28, repaired the remote knowledge-arbitration loader package under src/, submitted 18 extended-wave jobs (2210217-2210234), and completed a direct API-slice probe locally on Delta while the queue waits at priority.
- Delta submitted jobs captured locally: `18`
- Direct completed Delta probe: `arbitration_spotlight_extended_api_slice__seed=42` with `8064` rows and Bayes-vs-heuristic gain `0.0691`

## Coverage

- Benchmarks wired: `climatex, conflictbank, faitheval, gpqa, hotpotqa, nq_swap, popqa, tabmwp, triviaqa, wikicontradict`
- Models wired: `Qwen/Qwen2.5-14B-Instruct, Qwen/Qwen2.5-32B-Instruct, Qwen/Qwen2.5-7B-Instruct, anthropic/claude-3.5-haiku, deepseek-ai/DeepSeek-R1-Distill-Llama-70B, deepseek-ai/DeepSeek-R1-Distill-Qwen-7B, google/gemini-1.5-flash, google/gemma-2-27b-it, google/gemma-2-9b-it, meta-llama/Llama-3.1-70B-Instruct, meta-llama/Llama-3.1-8B-Instruct, mistralai/Mistral-7B-Instruct-v0.3, openai/gpt-4o-mini`
- Baselines wired: `adacad, always_context, always_parametric, astute_rag, bayes_proxy, cad, cocoa, crag, fixed_50, heuristic_adaptive, juice, madam_rag, nwcad, self_rag, simulated_model`
- Ablations wired: `answer_conditioning_mask, component_drop, conflict_density, eta_tempering, retrieval_quality`

## Experiments

- `arbitration_spotlight_extended_model_wave__seed=42`: `10` models x `7` benchmarks, `15` baselines, `0` ablations, `max_examples=256`, `total_cells=1120`. Extended spotlight model-and-benchmark wave with the full named baseline panel and three-seed coverage.
- `arbitration_spotlight_extended_model_wave__seed=43`: `10` models x `7` benchmarks, `15` baselines, `0` ablations, `max_examples=256`, `total_cells=1120`. Extended spotlight model-and-benchmark wave with the full named baseline panel and three-seed coverage.
- `arbitration_spotlight_extended_model_wave__seed=44`: `10` models x `7` benchmarks, `15` baselines, `0` ablations, `max_examples=256`, `total_cells=1120`. Extended spotlight model-and-benchmark wave with the full named baseline panel and three-seed coverage.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=42__eta_value=0p25`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=42__eta_value=0p5`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=42__eta_value=0p75`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=42__eta_value=1p0`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=43__eta_value=0p25`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=43__eta_value=0p5`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=43__eta_value=0p75`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=43__eta_value=1p0`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=44__eta_value=0p25`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=44__eta_value=0p5`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=44__eta_value=0p75`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_t3_calibration_wave__seed=44__eta_value=1p0`: `7` models x `5` benchmarks, `7` baselines, `5` ablations, `max_examples=192`, `total_cells=315`. Theorem-3 rescue wave targeting RLVR-vs-instruction families and overconfidence calibration benchmarks.
- `arbitration_spotlight_extended_api_slice__seed=42`: `3` models x `4` benchmarks, `7` baselines, `0` ablations, `max_examples=128`, `total_cells=72`. Closed-model headline slice for reviewer-facing generalization claims when API budget is available.
- `arbitration_spotlight_extended_api_slice__seed=43`: `3` models x `4` benchmarks, `7` baselines, `0` ablations, `max_examples=128`, `total_cells=72`. Closed-model headline slice for reviewer-facing generalization claims when API budget is available.
- `arbitration_spotlight_extended_api_slice__seed=44`: `3` models x `4` benchmarks, `7` baselines, `0` ablations, `max_examples=128`, `total_cells=72`. Closed-model headline slice for reviewer-facing generalization claims when API budget is available.

## Interpretation

- The remaining gap is no longer missing code or missing benchmark plumbing.
- The extended wave is now both compute-ready and Delta-submitted; the open remaining gap is job completion, result pullback, and final write-up.
- This note should be read together with the empirical completion audit: the finished core already has headline-grade results, and this extended wave is now an active execution path rather than a dormant plan.
