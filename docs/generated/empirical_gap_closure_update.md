# Empirical Gap Closure Update

This note records the direct empirical follow-up on three open scope gaps: RLCR comparison, open retrieval, and English-only scope.

## New Local Results

### Open-Wikipedia retrieval probe

A live Wikipedia search-and-extract probe on `10` `WikiContradict` questions gives:

- top-1 gold-answer hit rate: `0.3`
- top-1 conflict-answer hit rate: `0.0`
- top-5 gold-answer hit rate: `0.3`
- top-5 conflict-answer hit rate: `0.1`
- top-5 both-hit rate: `0.1`
- top-5 neither-hit rate: `0.7`

Interpretation: the bounded in-benchmark BM25 demo was not the only place where retrieval conflict appears. Even with open Wikipedia search, the system can surface gold and conflicting evidence in the same retrieval set, though the hit rate is noisier and lower than in the benchmark-contained setting.

### Spanish transfer probe

A small Spanish transfer spot-check on `5` translated `WikiContradict` questions searched against Spanish Wikipedia gives:

- top-1 gold-answer hit rate: `0.4`
- top-1 conflict-answer hit rate: `0.2`
- top-3 gold-answer hit rate: `0.4`
- top-3 conflict-answer hit rate: `0.4`
- top-3 both-hit rate: `0.4`

Interpretation: this is not a multilingual theorem-3 replacement, but it does show that the retrieval-conflict pattern is not obviously confined to English-only search results.

## Fast Delta Jobs Submitted

To avoid waiting only on the heavier queue-blocked jobs, smaller backfill-friendly versions are now in the queue:

- `2224414` `t3r14f`: 1-GPU fast RLCR-style LoRA run
- `2224415` `t3attf`: 1-GPU fast attention-intervention run
- `2224419` `p2r70f`: 2-GPU reduced 70B real-trajectory run

Delta currently estimates all three as eligible for backfill starting on `2026-05-02`.

## Honest Read

- The RLCR head-to-head gap is not fully closed yet because the training-time jobs have not started.
- The production-retrieval limitation is materially improved by the open-Wikipedia probe.
- The English-only limitation is materially improved by the Spanish transfer spot-check, but not eliminated.
