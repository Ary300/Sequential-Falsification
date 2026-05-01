# Closed-Model API Breakdown

This note makes the closed-model slice explicit instead of leaving it as a thin appendix claim.

## Methodology

- Current slice type: `benchmark-backed proxy scaffold`, not direct API-native token logprobs.
- Closed models covered: `GPT-4o-mini`, `Claude-3.5-Haiku`, `Gemini-1.5-Flash`.
- Benchmarks covered in the slice: `conflictbank`, `faitheval`, `popqa`, `triviaqa`.

## Per-Model Regret

- `anthropic/claude-3.5-haiku`: Bayes `0.0093`, heuristic `0.0312`, CoCoA `0.0545`, best policy `always_parametric`
- `google/gemini-1.5-flash`: Bayes `0.0093`, heuristic `0.0312`, CoCoA `0.0545`, best policy `always_parametric`
- `openai/gpt-4o-mini`: Bayes `0.0093`, heuristic `0.0312`, CoCoA `0.0545`, best policy `always_parametric`

## Conflict Oracle-vs-Model Rows

- `anthropic/claude-3.5-haiku | conflict_context | cot=0`: oracle `P(context)=0.02`, model `P(context)=0.1943`, abs gap `0.1743`, count `384`
- `anthropic/claude-3.5-haiku | conflict_context | cot=1024`: oracle `P(context)=0.02`, model `P(context)=0.0431`, abs gap `0.0231`, count `384`
- `anthropic/claude-3.5-haiku | conflict_context | cot=128`: oracle `P(context)=0.02`, model `P(context)=0.156`, abs gap `0.136`, count `384`
- `google/gemini-1.5-flash | conflict_context | cot=0`: oracle `P(context)=0.02`, model `P(context)=0.1943`, abs gap `0.1743`, count `384`
- `google/gemini-1.5-flash | conflict_context | cot=1024`: oracle `P(context)=0.02`, model `P(context)=0.0431`, abs gap `0.0231`, count `384`
- `google/gemini-1.5-flash | conflict_context | cot=128`: oracle `P(context)=0.02`, model `P(context)=0.156`, abs gap `0.136`, count `384`
- `openai/gpt-4o-mini | conflict_context | cot=0`: oracle `P(context)=0.02`, model `P(context)=0.1943`, abs gap `0.1743`, count `384`
- `openai/gpt-4o-mini | conflict_context | cot=1024`: oracle `P(context)=0.02`, model `P(context)=0.0431`, abs gap `0.0231`, count `384`
- `openai/gpt-4o-mini | conflict_context | cot=128`: oracle `P(context)=0.02`, model `P(context)=0.156`, abs gap `0.136`, count `384`

## Read

- This slice is useful as a deployment-adjacent proxy sanity check, but it should not be described as if we had direct access to closed-model posterior factors.
- The strongest empirical fact here is actually negative: on this proxy scaffold, `always_parametric` is the best policy overall, which means the slice is not a clean headline win for the geometric mixture.