# Theorem 3 Multi-Seed Headline Note

This note records the theorem-3 dense-grid headline read extracted from the near-complete row files of the resumed Delta audit wave. Even though several long jobs timed out before writing their final packaged summaries, the row-level outputs were sufficiently complete to render stable theorem-3 reports directly.

## DeepSeek-R1-Distill-Qwen-7B

Across seeds `42`, `43`, and `44`, the dense-grid theorem-3 report is highly stable:

| Seed | Conflict ECE delta | No-conflict ECE delta | Conflict minus no-conflict | Conflict gap delta | No-conflict gap delta | Rows |
|---|---:|---:|---:|---:|---:|---:|
| `42` | `-0.0116` | `0.0628` | `-0.0743` | `0.0243` | `-0.1142` | `24678` |
| `43` | `-0.0116` | `0.0641` | `-0.0757` | `0.0243` | `-0.1143` | `24667` |
| `44` | `-0.0115` | `0.0628` | `-0.0743` | `0.0244` | `-0.1140` | `24703` |

Seed-average read:

- Mean conflict ECE delta: `-0.0116`
- Mean no-conflict ECE delta: `0.0632`
- Conflict minus no-conflict ECE delta: `-0.0748`
- Mean conflict overconfidence-gap delta: `0.0243`
- Mean no-conflict overconfidence-gap delta: `-0.1142`

Interpretation:

- At `7B`, the dense-grid aggregate does not support a strong conflict-amplified monotone-collapse story.
- This matches the revised theorem-3 framing: the low-scale regime is mixed and benchmark-dependent rather than uniformly pathological.

## DeepSeek-R1-Distill-Qwen-14B

Across seeds `42`, `43`, and `44`, the dense-grid theorem-3 report is again extremely consistent:

| Seed | Conflict ECE delta | No-conflict ECE delta | Conflict minus no-conflict | Conflict gap delta | No-conflict gap delta | Rows |
|---|---:|---:|---:|---:|---:|---:|
| `42` | `0.1953` | `0.0224` | `0.1729` | `0.1943` | `0.0398` | `17404` |
| `43` | `0.1953` | `0.0227` | `0.1726` | `0.1943` | `0.0403` | `17296` |
| `44` | `0.1953` | `0.0226` | `0.1727` | `0.1943` | `0.0401` | `17391` |

Seed-average read:

- Mean conflict ECE delta: `0.1953`
- Mean no-conflict ECE delta: `0.0226`
- Conflict minus no-conflict ECE delta: `0.1727`
- Mean conflict overconfidence-gap delta: `0.1943`
- Mean no-conflict overconfidence-gap delta: `0.0401`

Interpretation:

- At `14B`, the theorem-3 pattern is strong and clean.
- Long CoT increases calibration error substantially more in conflict slices than in no-conflict slices.
- The seed stability makes this a legitimate headline result, not a one-run artifact.

## Qwen2.5-14B Control

The partially timed-out `Qwen2.5-14B` control still yields a readable aggregate:

- Conflict ECE delta: `0.0760`
- No-conflict ECE delta: `0.0966`
- Conflict minus no-conflict ECE delta: `-0.0207`
- Conflict overconfidence-gap delta: `0.0846`
- No-conflict overconfidence-gap delta: `0.2717`
- Rows: `15207`

Interpretation:

- The Qwen control does not replicate the DeepSeek-R1 14B conflict amplification pattern.
- This remains consistent with the RLVR-conditioned theorem-3 story rather than a universal scale law.

## Headline Read

- `DeepSeek-R1-Distill-Qwen-14B` now has a seed-stable theorem-3 headline: conflict-minus-no-conflict ECE delta is about `+0.173` across all three seeds.
- `DeepSeek-R1-Distill-Qwen-7B` does not show the same aggregate conflict amplification, supporting the two-regime scale story.
- `Qwen2.5-14B` control remains non-replicating, which supports the training-type-dependent framing.
- These summaries were rendered directly from the row-level outputs of the dense-grid audit wave, so the theorem-3 headline read is available now even before every queued mop-up job finishes packaging.
