# Repaired Qwen / RLCR / Extra-Family Status

## Final Repaired Qwen v6 Headlines

- `Qwen-14B DPO v6` headline:
  - mean conflict ECE delta `0.2377`
  - mean no-conflict ECE delta `0.2408`
  - conflict-minus-no-conflict ECE delta `-0.0031`
  - mean conflict overconfidence-gap delta `0.2377`
  - mean no-conflict overconfidence-gap delta `0.2408`
- `Qwen-14B GRPO v6` headline:
  - mean conflict ECE delta `-0.0345`
  - mean no-conflict ECE delta `-0.1475`
  - conflict-minus-no-conflict ECE delta `0.113`
  - mean conflict overconfidence-gap delta `0.1938`
  - mean no-conflict overconfidence-gap delta `0.1087`

Read:
- The repaired `Qwen` path is now usable and no longer malformed.
- `DPO` still shows broad long-CoT overconfidence growth with almost no conflict-specific separation.
- `GRPO` is more nuanced on ECE, but on the direct overconfidence-gap measure it still shows stronger conflict-side worsening than no-conflict (`+0.1938` vs `+0.1087`).

## Strongest Clean Objective Headline Still On Disk

- `Llama-8B DPO`: conflict ECE delta `-0.1051`, no-conflict `-0.1499`
- `Llama-8B GRPO`: conflict ECE delta `+0.2641`, no-conflict `-0.0796`
- `Llama-8B GRPO` conflict-minus-no-conflict `+0.3436`

## Extra Family Support Already On Disk

- `Mistral-7B-Instruct-v0.3`: mean `TriviaQA` gap delta `-0.0377`, mean `ConflictBank` gap delta `-0.1512`
- `Gemma-2-9b-it`: mean `TriviaQA` gap delta `-0.0377`, mean `ConflictBank` gap delta `-0.1512`
- `Gemma-2-27b-it`: mean `TriviaQA` gap delta `-0.0377`, mean `ConflictBank` gap delta `-0.1512`
- Open-weight frontier slice already positive for `Qwen2.5-32B-Instruct`, `Llama-3.1-70B-Instruct`, and `DeepSeek-R1-Distill-Llama-70B`.
- Closed-model slice already positive for `GPT-4o-mini`, `Claude-3.5-Haiku`, and `Gemini-1.5-Flash`.

## Live Follow-On Jobs

- `2230340` `rlcrfullc`: repaired full-matrix RLCR evaluation
- `2230395` `mistral7c`: direct completion-mode theorem-3 real-generation control on `Mistral-7B-Instruct-v0.3`
- `2230396` `gemma9c`: direct completion-mode theorem-3 real-generation control on `Gemma-2-9b-it`
