# Conditional-Independence Diagnostic

This note puts numbers on the reviewer concern that some conflict passages may contain the answer verbatim, making a scalar reliability variable do more work than advertised.

These are bounded diagnostic samples rather than the full corpora, but they are large enough to show the benchmark geometry cleanly.

## Headline

- `WikiContradict` sampled rows: `253`
- `WikiContradict` gold-answer verbatim rate in conflict context: `0.5336`
- `WikiContradict` conflict-answer verbatim rate in conflict context: `0.4111`
- `ConflictBank` sampled rows: `768`
- `ConflictBank` gold-answer verbatim rate in conflict context: `0.0391`
- `ConflictBank` conflict-answer verbatim rate in conflict context: `0.9466`

## Read

- `WikiContradict` is mixed: the gold answer appears verbatim in the conflict passage often enough that scalar-reliability-only assumptions should be read cautiously there.
- `ConflictBank` shows the opposite geometry: the conflicting answer is almost always written explicitly in the conflict evidence, while the gold answer is rarely verbatim. That makes the benchmark a particularly strong stress test of whether the arbitration rule can discount high-salience but wrong contextual evidence.