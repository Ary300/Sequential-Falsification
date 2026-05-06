# Theorem 3 Same-Family Threshold Summary

## Headline Read

- Same-family `Qwen2.5` naturalistic-contradiction recovery first appears at approximately `32B` on `WikiContradict` conflict.
- Same-family `Qwen2.5` controlled-conflict recovery has **not** appeared through the currently observed `32B` scale on `ConflictBank` conflict: threshold = `None`.
- Same-family `Qwen2.5` controlled-conflict persistence above `0.85` long-CoT gap holds at scales `[7, 14, 32]`.
- `DeepSeek-R1-Distill-Qwen` recovers on `WikiContradict` by `7B`, but the `ConflictBank` family splits by scale: recovery at `7B`, persistence at `[14]`.

## Per-Slice Shapes

| Family | Model | Benchmark | Split | `cot=0` | `cot=128` | `cot=1024` | Shape | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-7B | conflictbank | conflict | 0.5505 | 0.7531 | 0.5308 | peak_then_full_recovery | final |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-14B | conflictbank | conflict | 0.5876 | 0.9449 | 0.9513 | persistent_or_saturating | final |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-7B | conflictbank | no_conflict | 0.0996 | 0.2754 | -0.3724 | peak_then_full_recovery | final |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-14B | conflictbank | no_conflict | 0.0691 | 0.3108 | 0.1032 | peak_then_partial_recovery | final |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-7B | wikicontradict | conflict | 0.2923 | 0.4825 | 0.4429 | peak_then_partial_recovery | final |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-14B | wikicontradict | conflict | 0.2717 | 0.4516 | 0.3750 | peak_then_partial_recovery | final |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-7B | wikicontradict | no_conflict | 0.2643 | 0.5038 | 0.4331 | peak_then_partial_recovery | final |
| DeepSeek-R1-Distill-Qwen | DeepSeek-R1-Distill-Qwen-14B | wikicontradict | no_conflict | 0.2963 | 0.4229 | 0.4164 | peak_then_partial_recovery | final |
| Qwen2.5 | Qwen2.5-7B | conflictbank | conflict | 0.9856 | 0.9849 | 0.9693 | monotone_improving | final |
| Qwen2.5 | Qwen2.5-14B | conflictbank | conflict | 0.9776 | 0.9731 | 0.9584 | monotone_improving | final |
| Qwen2.5 | Qwen2.5-32B | conflictbank | conflict | 0.9484 | 0.9307 | 0.8871 | monotone_improving | final |
| Qwen2.5 | Qwen2.5-7B | conflictbank | no_conflict | 0.0868 | 0.0723 | 0.0537 | monotone_improving | final |
| Qwen2.5 | Qwen2.5-14B | conflictbank | no_conflict | 0.0639 | 0.0679 | 0.0476 | peak_then_full_recovery | final |
| Qwen2.5 | Qwen2.5-32B | conflictbank | no_conflict | 0.0977 | 0.0609 | 0.0710 | mixed | final |
| Qwen2.5 | Qwen2.5-7B | wikicontradict | conflict | 0.1327 | 0.5917 | 0.6710 | persistent_or_saturating | final |
| Qwen2.5 | Qwen2.5-14B | wikicontradict | conflict | 0.1222 | 0.4182 | 0.4572 | persistent_or_saturating | final |
| Qwen2.5 | Qwen2.5-32B | wikicontradict | conflict | 0.0945 | 0.3520 | 0.2635 | peak_then_partial_recovery | final |
| Qwen2.5 | Qwen2.5-7B | wikicontradict | no_conflict | 0.1315 | 0.5612 | 0.6545 | persistent_or_saturating | final |
| Qwen2.5 | Qwen2.5-14B | wikicontradict | no_conflict | 0.0952 | 0.3745 | 0.4660 | persistent_or_saturating | final |
| Qwen2.5 | Qwen2.5-32B | wikicontradict | no_conflict | 0.0837 | 0.3422 | 0.3232 | peak_then_partial_recovery | final |
