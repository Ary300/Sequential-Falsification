# Playbook Target Matrix Update

This is the corrected current-vs-target matrix after the extended Delta wave and the eta-decoding method run.

| Item | Target | Current | Status |
|---|---|---|---|
| Model families | 5 | 13 wired models across Llama / Qwen / DeepSeek / Mistral / Gemma plus closed-model API slice | done |
| Benchmarks | 8-10 | 10 wired benchmarks including ConflictBank / WikiContradict / PopQA / NQ-Swap / DynamicQA-family extensions / HotpotQA / TriviaQA / TabMWP / GPQA / CLIMATEX | done |
| Baselines | 11-12 | 15 wired baselines, with CAD / AdaCAD / CoCoA / Self-RAG / Astute RAG / JuICE / NWCAD / MADAM-RAG all surfaced in the spotlight notes | done |
| Seeds | 3 | Explicit seeds `[42, 43, 44]` in the completed extended wave | done |
| Theorem 3 reframe | RLVR-driven Berk-Nash with R1-Distill-Llama validation | Reframing note is on disk, and the completed theorem-3 calibration wave now includes `DeepSeek-R1-Distill-Llama-70B`; its `ConflictBank` conflict `cot=1024` Bayes-vs-heuristic gain is `0.0518`. | done |
| Eta-tempered decoding | Implemented and ablated with real 14B ConflictBank run | Real post-trace method run on `ConflictBank` conflict at `14B` selects `eta = 0.0` and moves eval gap from `0.937239` to `0.520508`. | done |
