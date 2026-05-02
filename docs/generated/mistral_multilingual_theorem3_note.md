# Mistral Multilingual Theorem-3 Note

This note summarizes the first completed multilingual theorem-3 transfer run.

## Setup

- Model: `mistralai/Mistral-7B-Instruct-v0.3`
- Benchmarks:
  - `wikicontradict_de`
  - `wikicontradict_es`
  - `wikicontradict_fr`
  - `wikicontradict_it`
  - `wikicontradict_pt`
- Rows: `300`
- Conditions: `aligned_context`, `conflict_context`
- CoT budgets: `0`, `128`, `1024`

## Headline

- mean conflict ECE delta: `+0.0012`
- mean no-conflict ECE delta: `+0.0014`
- conflict-minus-no-conflict ECE delta: `-0.0002`
- mean conflict overconfidence-gap delta: `+0.0012`
- mean no-conflict overconfidence-gap delta: `+0.0014`
- mean conflict reasoning-word delta: `+21.86`

## Read

This is a strong multilingual control result.

- Across five languages, long CoT does not produce a large conflict-specific calibration blow-up.
- The aggregate multilingual theorem-3 pattern is essentially flat rather than pathological.
- That is useful because it shows the multilingual story is not being driven by retrieval failure alone.

## Per-Language Trend Rows

- `wikicontradict_de`
  - conflict ECE delta: `+0.1100`
  - no-conflict ECE delta: `+0.1100`
  - conflict-minus-no-conflict: `0.0000`
- `wikicontradict_es`
  - conflict ECE delta: `+0.0570`
  - no-conflict ECE delta: `+0.0570`
  - conflict-minus-no-conflict: `0.0000`
- `wikicontradict_fr`
  - conflict ECE delta: `-0.1620`
  - no-conflict ECE delta: `-0.1620`
  - conflict-minus-no-conflict: `0.0000`
- `wikicontradict_it`
  - conflict ECE delta: `-0.0280`
  - no-conflict ECE delta: `-0.0280`
  - conflict-minus-no-conflict: `0.0000`
- `wikicontradict_pt`
  - conflict ECE delta: `+0.0290`
  - no-conflict ECE delta: `+0.0300`
  - conflict-minus-no-conflict: `-0.0010`

## Interpretation

- French and Italian actually improve with longer CoT.
- German, Spanish, and Portuguese worsen a bit, but not in a conflict-specific way.
- The multilingual theorem-3 transfer evidence therefore looks much more like family- and benchmark-sensitive stability than like a broad multilingual failure mode.
