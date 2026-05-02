# Multilingual WikiContradict Transfer Suite

This suite expands the earlier single-language transfer spot-check into a small multi-language probe using translated WikiContradict queries and target-language Wikipedia search.

## Headline

- Languages run: `5`
- Languages with any top-k gold hit: `3`
- Languages with any top-k conflict hit: `3`
- Mean top-k gold-hit rate across completed languages: `0.08`
- Mean top-k conflict-hit rate across completed languages: `0.08`

| Language | Completed | Failed | Top-1 Gold | Top-1 Conflict | Top-k Gold | Top-k Conflict | Top-k Both |
|---|---:|---:|---:|---:|---:|---:|---:|
| Spanish | 10 | 0 | 0.2000 | 0.1000 | 0.2000 | 0.2000 | 0.2000 |
| French | 10 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| German | 10 | 0 | 0.1000 | 0.1000 | 0.1000 | 0.1000 | 0.1000 |
| Italian | 10 | 0 | 0.1000 | 0.1000 | 0.1000 | 0.1000 | 0.1000 |
| Portuguese | 10 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

This remains a transfer probe, not a multilingual theorem-3 replacement benchmark. It does, however, materially weaken the claim that the current evidence is purely English-only.
