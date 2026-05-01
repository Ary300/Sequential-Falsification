# Spotlight Comparator Strength Note

This note answers the review concern that the strongest headline may be inflated by comparing primarily against the generic heuristic.

## Headline

- Bayes vs `AdaCAD`: mean regret gap `0.0659`, CI `[0.0521, 0.0756]`, wins `24/25`
- Bayes vs `CoCoA`: mean regret gap `0.0444`, CI `[0.0376, 0.0501]`, wins `24/25`
- Bayes vs `Self-RAG`: mean regret gap `0.0266`, CI `[-0.0379, 0.0686]`, wins `20/25`

## Read

- The AdaCAD comparison is real and materially stronger than the Self-RAG comparison; if the paper wants one body-facing decoder-level comparator, AdaCAD is the cleanest choice.
- The Self-RAG comparison is positive overall but clearly the weakest of the powered head-to-heads, largely because of the known PopQA reversal.