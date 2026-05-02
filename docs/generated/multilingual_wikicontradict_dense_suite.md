# Multilingual WikiContradict Dense Retrieval Suite

This suite keeps live target-language Wikipedia search but replaces the weak lexical ranking with multilingual dense reranking.

## Headline

- Languages run: `2`
- Languages with any top-k gold hit: `1`
- Languages with any top-k conflict hit: `0`
- Mean top-k gold-hit rate across completed languages: `0.0625`
- Mean top-k conflict-hit rate across completed languages: `0.0`

| Language | Completed | Failed | Top-1 Gold | Top-1 Conflict | Top-k Gold | Top-k Conflict | Top-k Both |
|---|---:|---:|---:|---:|---:|---:|---:|
| French | 8 | 2 | 0.0000 | 0.0000 | 0.1250 | 0.0000 | 0.0000 |
| Portuguese | 6 | 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

This is still a small transfer probe, but it directly tests whether stronger multilingual reranking rescues the weakest retrieval-only languages.
