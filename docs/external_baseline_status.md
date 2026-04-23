# External Baseline Status

This project now has two baseline layers.

## Runnable inside this repository

- `greedy`: first sample.
- `majority_vote`: execution-output clustering on code tasks and normalized
  answer clustering on math tasks.
- `generated_test_filter`: compute-matched one-shot generated-test filtering.
- `self_debug`: lightweight public-test repair/selection proxy.
- `s_star`: local adaptive-elimination proxy, not the original SkyThought S*.
- `code_t`: local agreement-scoring proxy, not the original Microsoft CodeT.
- `oracle`: pass@N upper bound using hidden tests or reference answers.

These are appropriate for continuous regression and reviewer-facing internal
ablations. Proxy rows must be labeled as proxies in paper tables.

## External implementations to stage

Run:

```bash
bash scripts/setup_external_baselines.sh
```

This stages:

- SkyThought / S*: `https://github.com/NovaSky-AI/SkyThought`
- Microsoft CodeT: `https://github.com/microsoft/CodeT`
- ThinkPRM: `https://github.com/mukhal/thinkprm`
- AceCoder: `https://github.com/TIGER-AI-Lab/AceCoder`
- OpenR PRM/search framework: `https://github.com/openreasoner/openr`

## Baselines not yet claimable

- SAGA: we found the paper/source description, but not a stable public repo in
  the current quick pass. Do not report a SAGA number until an official or
  author-confirmed implementation is wired.
- DVTS/verifier-guided tree search: no single canonical code-generation
  implementation is wired yet. It should be treated as a future external
  baseline, not as a completed row.
- ThinkPRM/PRM rows: these require a math-verifier adapter. Until then, math
  benchmark rows remain consensus-based scope checks.

## Adapter requirements before a row is publishable

Every external baseline needs:

- a pinned commit hash;
- a command line in `scripts/` or `slurm/`;
- an input converter from this repo's problem/candidate format;
- an output converter back to `results.json`;
- a smoke run on `synthetic_demo` or a 5-problem benchmark slice;
- a table label that distinguishes original external code from local proxy.
