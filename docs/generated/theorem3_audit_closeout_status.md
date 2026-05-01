# Theorem 3 Audit Closeout Status

This note tracks the last audit-driven theorem-3 items that remained after the multi-seed headline extraction.

## Closed

- Multi-seed theorem-3 headline extraction:
  see [theorem3_multiseed_headline_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_multiseed_headline_note.md)
- Answer-stability diagnostic:
  see [theorem3_answer_stability_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_answer_stability_note.md)
- Assumption 3.2 trace-separation verification:
  see [theorem3_trace_separation_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_trace_separation_note.md)
- Reliability-diagram generation path:
  see [build_theorem3_reliability_figure.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_theorem3_reliability_figure.py)

## Generated on Delta

The explicit Yoon-style reliability-diagram plus frequency-histogram figures have been generated on Delta for:

- `R1-Qwen-14B` `ConflictBank` conflict:
  `/work/nvme/bgvi/adas17/tts_results/results/theorem3_tierA_r1_qwen14_seed42/theorem3_report_from_rows/conflictbank_conflict_reliability.png`
- `Qwen2.5-14B` `ConflictBank` conflict:
  `/work/nvme/bgvi/adas17/tts_results/results/theorem3_tierA_Qwen2.5-14B_seed42/theorem3_report_from_rows/conflictbank_conflict_reliability.png`

These were rendered from the row-derived theorem-3 summaries so the visual-standard gap is no longer conceptual.

## Still Queue-Dependent

- `Llama-3.1-70B-Instruct` sparse control run remains queued.
- `QwQ-32B` second RLVR-family run remains queued in resumed form.
- `Qwen2.5-32B-Instruct` Yoon-style reconciliation run remains queued in resumed form.
- `Qwen2.5-32B` base control is now additionally queued to strengthen the non-RL baseline story.

## Honest Read

- The theorem-3 headline argument is already supported by committed results.
- The remaining Delta jobs are best understood as strengthening and completion work, not as the only source of a usable theorem-3 story.
