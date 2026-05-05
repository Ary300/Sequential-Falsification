# DeepSeek-Llama-8B Tokenizer / Context Sanity Check

Status date: `2026-05-04`

This note documents the local-first sanity checker added for the
`DeepSeek-R1-Distill-Llama-8B` failure diagnosis:

- script:
  [check_deepseek_llama8_tokenizer_context_sanity.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/check_deepseek_llama8_tokenizer_context_sanity.py)

## What it checks

The script is meant to rule out simple setup mistakes before we interpret the
weak `DeepSeek-Llama-8B` theorem-3 result as a substantive model-family
failure.

It checks:

1. Local metadata resolution
   - resolves either:
     - a direct local model directory, or
     - a locally cached Hugging Face snapshot
   - reports clearly when neither is available

2. Raw model/tokenizer metadata
   - reads local JSON metadata when present:
     - `config.json`
     - `tokenizer_config.json`
     - `special_tokens_map.json`
     - `generation_config.json`
   - extracts context-window candidates such as:
     - `max_position_embeddings`
     - `rope_scaling.original_max_position_embeddings`
     - `tokenizer_config.model_max_length`

3. Rerun-budget versus context-limit sanity
   - compares the theorem-3 rerun bounds against the locally visible context
     limits
   - defaults are aligned with the current DeepSeek rerun discussion:
     - `run_max_model_len=12288`
     - `run_max_prompt_tokens=4096`

4. Optional `transformers` enrichment
   - if `transformers` is available, it performs a local-only
     `AutoConfig` / `AutoTokenizer` probe
   - this adds:
     - tokenizer class
     - tokenizer `model_max_length`
     - pad / BOS / EOS token ids
     - `<think>` token-id lookup
     - a sample token-count smoke test
     - whether the chat template appears to mention a `system` role

5. Prompt-format risk signals
   - flags whether local tokenizer metadata suggests a system-role template
   - checks whether local metadata confirms `<think>` support
   - snapshots local generation defaults like `temperature` and `do_sample`

## Failure-safe behavior

This checker is intentionally defensive:

- if `transformers` is unavailable, it reports that fact instead of crashing
- if the model is not present locally, it reports that it could not resolve a
  local path instead of pretending to validate the tokenizer
- if only some metadata files exist, it still writes a partial report

So this is a diagnosis helper, not a brittle environment-dependent test.

## Example usage

```bash
python3 scripts/check_deepseek_llama8_tokenizer_context_sanity.py \
  --model deepseek-ai/DeepSeek-R1-Distill-Llama-8B
```

Against a local merged checkpoint:

```bash
python3 scripts/check_deepseek_llama8_tokenizer_context_sanity.py \
  --model /work/nvme/bgvi/adas17/tts_results/results/e1_deepseek_llama8_grpo/merged_model
```

## Why this helps the failure diagnosis

The existing diagnosis note already argued that the `DeepSeek-Llama-8B`
failure is probably:

- not a raw context-window problem
- more likely a prompt/protocol mismatch plus objective-surrogate mismatch

This checker makes the first part concrete by giving us a reproducible way to
inspect:

- whether the local model/tokenizer snapshot exposes an obviously too-small
  context limit
- whether the tokenizer metadata looks compatible with the DeepSeek-native
  `<think>` prompting path
- whether the local chat-template metadata suggests system-prompt risk
