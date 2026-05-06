# Compute Budget Notes

## Core suite

- Models: DeepSeek-R1-Distill-Qwen-7B, Qwen2.5-Coder-14B-Instruct, DeepSeek-R1-Distill-Qwen-32B
- Benchmarks: HumanEval+, MBPP+, LiveCodeBench v6, MATH-500
- Candidate counts: N in {1, 4, 8, 16, 32, 64}
- Falsification rounds: T in {0, 1, 2, 3, 4}
- Seeds: {42, 43, 44}

## Approximate resource estimate

- Per-model token volume: about 185M tokens for the full main-suite run at N=64 with 4 falsification rounds.
- Three-model main suite: about 174 A100 GPU-hours.
- With ablations and safety margin: roughly 522 A100 GPU-hours.
- With remaining baselines: roughly 650 A100 GPU-hours total.

## Current Anvil status

- CPU allocation `bio260046`: sufficient for setup, preprocessing, and reporting.
- GPU allocation `bio260046-gpu`: current remaining balance is too small for the full experimental program.
- Practical implication: use CPU/shared for environment setup and benchmark staging, and preserve GPU balance for the smallest-possible pilot runs until more GPU time is available.
