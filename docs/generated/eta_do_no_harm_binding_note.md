# Eta Do-No-Harm Binding Note

This note answers the reviewer question about why the worst theorem-3 cell selects `eta=0` while accuracy improves sharply.

## Headline

- Selected eta: `0.0`
- Baseline accuracy / Brier / gap at `eta=1`: `0.036667` / `0.903275` / `0.937239`
- Tempered accuracy / Brier / gap at selected eta: `0.44` / `0.504515` / `0.520508`

## Read

- On this cell the do-no-harm constraint does not bind against a better-Brier-but-worse-accuracy eta. Instead, the best point is already `eta=0`, which improves both accuracy and Brier.
- The correct interpretation is therefore not that the fallback protected accuracy from an aggressive calibration fix; it is that the conflict-conditioned long-CoT posterior is so bad that collapsing toward the closed-book prior is simultaneously a better answer policy and a better calibration policy.