# DeepSeek-Llama-8B Failure Diagnosis Note

Status date: `2026-05-05`

This note summarizes what we can already diagnose about the weak / negative
matched-base `DeepSeek-R1-Distill-Llama-8B` result without pretending the
family replicated cleanly.

## Observed matched-base result

Finished matched-family numbers:

- matched `DPO`: `+0.0258`
- matched `GRPO`: `-0.1239`
- DeepSeek-native theorem-3 rerun: `+0.0760`
- curriculum-audit `DPO`: `-0.0699`
- curriculum-audit `GRPO`: `-0.0795`

So the clean second matched-base `8B` replication did **not** land.

## What we can already rule out

### 1. Raw context-window truncation is unlikely

Official model-card facts:

- `DeepSeek-R1-Distill-Llama-8B` is distilled from `Llama-3.1-8B` and belongs
  to a `128K`-context family:
  <https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B>
- `Llama-3.1-8B` itself is a `128k`-context model:
  <https://huggingface.co/meta-llama/Llama-3.1-8B>

Our theorem runner uses much smaller limits:

- prompt-style max tokens top out at `4096`:
  [real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/knowledge_arbitration/real_generation.py#L66)
- the real-generation launcher defaults to `MAX_MODEL_LEN=16384`, and the
  DeepSeek eval recoveries used `12288`:
  [theorem3_real_generation_delta.sbatch](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/slurm/delta/theorem3_real_generation_delta.sbatch)
  [submit_delta_theorem3_deepseek_llama8_grpo_eval_recovery.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_grpo_eval_recovery.sh)

Read:

- the current DeepSeek failure is not well explained by hitting the context
  ceiling.

### 2. The family is not universally broken

Existing DeepSeek lineage results are mixed rather than uniformly bad:

- `DeepSeek-Llama-70B` is strongly positive:
  conflict-minus-no-conflict `+0.3881`
- the `DeepSeek` family sweep over Qwen distills is also not uniformly flat:
  [theorem3_deepseek_family_sweep.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/theorem3_deepseek_family_sweep.md)

Read:

- the `8B` failure is probably configuration-sensitive, not a simple
  “DeepSeek lineage disproves theorem 3” story.

## What now looks like the real failure mode

### 1. Prompt / protocol mismatch with DeepSeek guidance

The official DeepSeek model card says:

- the distill models “slightly change their configs and tokenizers”
- “Please use our setting to run these models”
- recommended temperature is `0.5–0.7`
- “Avoid adding a system prompt”
- for reasoning, enforce the response to start with `<think>\n`

Source:
<https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B>

But our generic theorem-3 stack was using:

- `request_format=chat`
- an explicit `system` role
- deterministic `temperature=0.0`
- a generic XML-style reasoning scaffold

Code path:

- chat + system prompt:
  [real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/src/knowledge_arbitration/real_generation.py#L522)
- generic system prompt template:
  [real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/src/knowledge_arbitration/real_generation.py#L35)
- real-generation defaults:
  [run_theorem3_real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/run_theorem3_real_generation.py#L20)

Read:

- this is a plausible, concrete explanation for why the `DeepSeek-Llama-8B`
  result under our generic theorem harness diverged from the clean `Llama-8B`
  matched-base story.
- the completed DeepSeek-native rerun supports that diagnosis:
  conflict-minus-no-conflict `+0.0760` is modestly positive instead of
  strongly negative, which means some of the original failure really was
  protocol-sensitive.

### 2. Objective-surrogate mismatch

The current `DeepSeek-Llama-8B GRPO` row came from the local matched-objective
`GRPO`-style surrogate plus an eval-recovery path, not a byte-for-byte replay
of DeepSeek’s original training stack.

That is why the active redo wave exists:

- [deepseek_llama8_refresh_wave.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_refresh_wave.md)

Read:

- even if the rerun stays weak, the repo should distinguish “the theorem fails”
  from “our local surrogate did not reproduce a family-specific effect.”

## What the completed diagnostics now say

### Intermediate-checkpoint / curriculum audit

This is no longer a staged-only path; the curriculum audits completed.

Results:

- curriculum-audit `DPO`: conflict-minus-no-conflict `-0.0699`
- curriculum-audit `GRPO`: conflict-minus-no-conflict `-0.0795`

Read:

- the audit does not rescue the matched-base `8B` claim
- it strengthens the case that the weak DeepSeek `8B` story is a real
  family-specific failure mode rather than just one unlucky headline number

Status / launcher:

- [deepseek_llama8_curriculum_audit_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/deepseek_llama8_curriculum_audit_status.md)
- [submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh)

### Mechanism probe

The answer-margin mechanism probe also completed.

Result:

- answer-margin diff-in-diff: `-14.6593`

Read:

- this is consistent with a margin-reallocation failure mode
- it is not the kind of clean positive mechanism story we would need to call
  DeepSeek `8B` a strong replication

## Remediation now wired

Two concrete follow-ups are now in the repo:

1. DeepSeek mechanism probe on the matched `DPO/GRPO` pair:
   [submit_delta_deepseek_llama8_objective_followups.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_deepseek_llama8_objective_followups.sh)

2. DeepSeek-native eval rerun that matches the model-card guidance better:
   - completion-style prompts
   - no system prompt
   - `temperature=0.6`
   - explicit `<think>`-leading prompt

   Launcher:
   [submit_delta_theorem3_deepseek_llama8_native_eval.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_eval.sh)

## Bottom line

The strongest current diagnosis is:

- not a context-limit problem
- not a whole-lineage collapse
- probably a combination of:
  - generic theorem-harness prompting that is not DeepSeek-native
  - objective-surrogate mismatch at `8B`
- with the completed reruns now adding:
  - a modestly positive DeepSeek-native rerun (`+0.0760`)
  - a still-negative curriculum path (`-0.0699`, `-0.0795`)
  - a negative answer-margin mechanism signal (`-14.6593`)

That is a much cleaner and more actionable failure story than just saying
“DeepSeek didn’t replicate.”
