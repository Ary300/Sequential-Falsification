# ACCESS Explore Request Draft

## Project Title

Sequential Falsification with Calibrated Confidence for Test-Time Scaling in Code and Mathematical Reasoning

## Project Abstract

We propose a test-time scaling framework for language models that combines parallel candidate generation with sequential falsification and anytime-valid confidence calibration. Prior work shows that best-of-N resampling for code and math reasoning suffers from a false-positive ceiling: as the number of samples grows, incorrect but superficially plausible candidates increasingly dominate naive selection rules. Our approach addresses this directly by allocating inference-time compute to adversarial falsification. Each candidate is subjected to multiple rounds of targeted probes, execution-based checks, and adaptive elimination. The resulting evidence is aggregated through e-values and a wealth process, yielding calibrated confidence scores with anytime-valid guarantees.

The empirical study will evaluate open-weight models on HumanEval+, MBPP+, LiveCodeBench, and MATH-500, with ablations over candidate count, falsification rounds, probe families, temperature, and compute-matched operating points. The project targets an ICLR 2027 submission and a potential NeurIPS workshop paper. Requested resources will be used for benchmark preparation, model serving, and multi-seed inference-time evaluation across 7B, 14B, and 32B models.

## Scientific Merit

- Introduces a novel connection between e-values / anytime-valid inference and test-time scaling.
- Targets a concrete limitation identified by recent TTS literature: false-positive saturation in resampling.
- Produces both empirical benchmarks and a statistical framework for calibrated confidence in LLM selection.

## Resource Request Summary

- Primary accelerator need: GPU time for open-weight model inference.
- CPU time supports benchmark preprocessing, sandboxed execution, and postprocessing.
- Estimated full campaign: roughly 650 A100-equivalent GPU-hours including ablations and baselines.

## Immediate Constraint

The current project GPU balance is insufficient for the full campaign, so an Explore allocation or comparable supplemental GPU access is necessary to execute the complete experimental matrix.
