# Yoon Real Contrast Note

This note compares the finished no-conflict QA control (`TriviaQA` closed-book) against the existing explicit-conflict 14B slice (`ConflictBank` conflict) on the real theorem-3 generation path.

## Headline

- `TriviaQA` gap: `0.2512` -> `0.4944` -> `0.483`
- `TriviaQA` gap delta (`cot 128 - cot 0`): `0.2432`
- `TriviaQA` gap delta (`cot 1024 - cot 0`): `0.2318`
- `ConflictBank` conflict gap: `0.5876` -> `0.9449` -> `0.9513`
- `ConflictBank` conflict gap delta (`cot 128 - cot 0`): `0.3573`
- `ConflictBank` conflict gap delta (`cot 1024 - cot 0`): `0.3637`
- `ConflictBank` closed-book gap: `0.4917` -> `0.8168` -> `0.789`
- `ConflictBank` closed-book gap delta (`cot 128 - cot 0`): `0.3251`
- `ConflictBank` closed-book gap delta (`cot 1024 - cot 0`): `0.2973`
- Strict Yoon-style sign flip achieved: `False`
- Conflict worse than `TriviaQA` at short CoT: `True`
- Conflict worse than `TriviaQA` at long CoT: `True`
- Conflict worse than closed-book at long CoT: `True`

Interpretation:
- The strongest reviewer-facing outcome would be a strict sign flip, but the more realistic target is a conflict-amplification figure: explicit conflict should show substantially larger overconfidence than the no-conflict QA control at the same CoT budget.
- In this run, `ConflictBank` conflict is already much worse than `TriviaQA` by `cot=128`, which is the main practical Yoon-contrast figure for the paper.
