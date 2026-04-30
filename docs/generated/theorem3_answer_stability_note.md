# Theorem 3 Answer-Stability Note

This note quantifies the empirical scope of the answer-stability condition used in theorem 3(a). The source rows are the finished `DeepSeek-R1-Distill-Qwen-14B` real-generation run at `cot={0,128,1024}`.

- Model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- CoT checkpoints: `0`, `128`, `1024`
- Source rows: canonical real-generation theorem-3 14B run

## Headline

- On `ConflictBank` conflict, only `0.08` of examples keep the same predicted answer across all three checkpoints.
- The pre-saturation answer-stable fraction on `ConflictBank` conflict is `0.098` across `0 -> 128`.
- The late-window stable fraction on `ConflictBank` conflict is `0.364` across `128 -> 1024`.
- On the `0 -> 128` stable subset, the mean confidence gap still rises by `+0.0908` with `0.0` mean accuracy change.
- On the fully stable `0 -> 1024` subset, the mean confidence gap rises by `+0.1025` with `0.0` mean accuracy change.

## Per-Slice Detail

| Benchmark | Split | Examples with all checkpoints | Stable `0/128/1024` | Stable `0/128` | Stable `128/1024` |
|---|---|---:|---:|---:|---:|
| `ConflictBank` | `conflict` | `500` | `0.08` | `0.098` | `0.364` |
| `ConflictBank` | `no_conflict` | `500` | `0.052` | `0.084` | `0.348` |
| `WikiContradict` | `conflict` | `200` | `0.05` | `0.095` | `0.3` |
| `WikiContradict` | `no_conflict` | `200` | `0.05` | `0.09` | `0.225` |

## Stable-Subset Gap Read

For the theorem-3 conditional claim, the key question is not whether every example is stable, but whether the stable subset still exhibits the predicted confidence sharpening without matching accuracy growth.

On `ConflictBank` conflict:

- Stable `0 -> 128` subset:
  `mean confidence delta = +0.0908`
  `mean accuracy delta = 0.0`
  `mean gap delta = +0.0908`
- Stable `0 -> 1024` subset:
  `mean confidence delta = +0.1025`
  `mean accuracy delta = 0.0`
  `mean gap delta = +0.1025`

## Interpretation

- The answer-stability condition is empirically narrow, not generic. Most examples do change their predicted answer as CoT grows.
- The clean theorem-3(a) implication should therefore be stated conditionally, on locally stable answer trajectories.
- Within that stable subset, the data behave the way the proof needs: confidence-gap growth appears without corresponding accuracy growth.
- This supports using theorem 3(a) as a mechanism statement about self-reinforcing stable traces rather than as a universal per-example law.
