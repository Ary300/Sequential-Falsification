# Multilingual WikiContradict Transfer Suite

This suite expands the earlier single-language transfer spot-check into a five-language probe using translated WikiContradict queries and target-language Wikipedia search.

## Headline

- Languages run: `5`
- Languages with any top-k gold hit: `3`
- Languages with any top-k conflict hit: `3`
- Mean top-k gold-hit rate across languages: `0.1`
- Mean top-k conflict-hit rate across languages: `0.1`

| Language | Completed | Failed | Top-1 Gold | Top-1 Conflict | Top-k Gold | Top-k Conflict | Top-k Both |
|---|---:|---:|---:|---:|---:|---:|---:|
| Spanish | 10 | 0 | 0.2000 | 0.1000 | 0.2000 | 0.2000 | 0.2000 |
| French | 10 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| German | 10 | 0 | 0.1000 | 0.1000 | 0.1000 | 0.1000 | 0.1000 |
| Italian | 5 | 0 | 0.2000 | 0.2000 | 0.2000 | 0.2000 | 0.2000 |
| Portuguese | 5 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

This remains a transfer probe rather than a multilingual theorem-3 benchmark, but it materially weakens the claim that the empirical package is English-only.
