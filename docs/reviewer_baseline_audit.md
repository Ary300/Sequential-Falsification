# Reviewer Baseline Audit

This note tracks what a NeurIPS/ICLR-style reviewer is likely to expect for a
paper on test-time scaling for code generation, and how the current repository
meets or misses those expectations.

## Current recommendation

The strongest current paper framing is:

1. Agreement-based test-time scaling can fail badly on reasoning-oriented code
   models.
2. Execution-grounded falsification can recover most of the majority-vote to
   oracle gap.
3. The current system produces useful confidence diagnostics, but does not yet
   cleanly beat self-debugging across the full matrix.

That framing is more defensible with the current evidence than a stronger claim
that falsification universally dominates all sequential baselines.

## Baselines reviewers are most likely to ask for

### Must-have

1. `greedy`
2. `majority_vote`
3. `self_debug`
4. `oracle`
5. `generated_test_filter`
6. `CodeT`
7. `S*`

### Nice-to-have / discussion baselines

1. PRM-based best-of-N selection
2. self-debugging with self-generated tests
3. broader non-code test-time scaling references for framing, not direct table comparison
4. reward-model or verifier-model selectors such as CodeScaler / GenPRM as discussion points, not mandatory main-table rows

## Literature-driven audit

### S*: Test Time Scaling for Code Generation

- Paper: https://arxiv.org/abs/2502.14382
- Why it matters: this is the most obvious code-generation TTS comparison and
  the first one a reviewer is likely to name.
- Current repo state:
  - `s_star` exists in `src/baselines.py`
  - it is an executable local adaptive-elimination proxy
  - it is **not** the external SkyThought implementation
- Submission risk:
  - acceptable as an engineering proxy during development
  - not sufficient as the final comparison in a paper that claims strong SOTA relevance

### CodeT: Code Generation with Generated Tests

- Paper: https://arxiv.org/abs/2207.10397
- Why it matters: classic execution-based test-generation selector baseline.
- Current repo state:
  - `code_t` exists in `src/baselines.py`
  - it is an executable local agreement-scoring proxy
  - it is **not** the external Microsoft implementation
- Submission risk:
  - useful for internal ablations
  - still needs an external-faithful comparison for a strong final paper

### Teaching Large Language Models to Self-Debug

- Paper: https://arxiv.org/abs/2304.05128
- Why it matters: this is the baseline currently most dangerous to the paper.
- Current repo state:
  - `self_debug` is implemented and already included in the main benchmark runs
  - current MBPP+ and monitored HumanEval+ rows show self-debug is often tied with
    or slightly above falsification
- Scientific consequence:
  - the paper must address this directly, not bury it
  - calibration + failure-diagnosis framing is more credible than a pure
    "falsification beats everything" framing today

### Inference Scaling fLaws

- Paper: https://arxiv.org/abs/2411.17501
- Why it matters: strongest narrative hook for the project.
- Current repo state:
  - paper and docs already use the resampling-ceiling framing
  - current HumanEval+ 32B numbers support the "recover the oracle gap" story well
- Best use:
  - motivation and interpretation
  - not a direct baseline row

### CodeMonkeys

- Paper: https://arxiv.org/abs/2501.14723
- Why it matters: strong test-time compute paper in software engineering.
- Current repo state:
  - not directly comparable to HumanEval+/MBPP+/LiveCodeBench code-generation tables
  - useful in related work, especially for multi-turn test-guided selection
- Best use:
  - related-work discussion, not main table

### Revisit Self-Debugging with Self-Generated Tests

- Paper: https://arxiv.org/abs/2501.12793
- Why it matters: shows the self-debug family is still evolving and may absorb
  some of the same benefits as generated-test falsification.
- Current repo state:
  - not implemented as a distinct baseline
- Best use:
  - discussion baseline
  - motivation for why "why not just self-debug?" remains the core review question

### CodeScaler / verifier-model selection references

- CodeScaler: https://arxiv.org/abs/2602.17684
- GenPRM: https://arxiv.org/abs/2504.00891
- Why they matter: they strengthen the discussion around verifier-based or reward-model-based test-time scaling, which makes it easier to justify why the paper compares against execution-based selectors first and leaves PRM-style selectors as future work unless a faithful code-domain implementation is added.
- Best use:
  - related work and discussion of missing verifier-model baselines
  - not required as direct main-table comparisons unless the paper explicitly claims broad verifier superiority

## Current repo status by baseline

| Baseline | In repo | In paper-quality runs | External-faithful |
| --- | --- | --- | --- |
| Greedy | yes | yes | yes |
| Majority vote | yes | yes | yes |
| Self-debug | yes | yes | approximate local implementation |
| Oracle | yes | yes | yes |
| Generated-test filter | yes | not yet in paper bundle | local |
| CodeT | yes | not yet in paper bundle | no |
| S* | yes | not yet in paper bundle | no |
| PRM best-of-N | placeholder only | no | no |

## What is strong right now

1. HumanEval+ 32B monitored row is genuinely strong:
   - majority vote `34.5 ± 0.3`
   - falsification `79.6 ± 1.5`
   - oracle `83.5 ± 0.6`
2. MBPP+ completed rows are strong against majority vote and greedy.
3. LiveCodeBench and math are present, which helps keep the paper from looking
   single-domain.
4. The repository now has a reproducible publication-bundle path and cluster
   recovery path.
5. The Delta HumanEval recovery path is now materially healthier:
   - `2156104 / 2156105` finished for the 14B resume chain
   - `2156126 / 2156127` finished for the 32B single-GPU fallback
   - `2160243 / 2160244` is the longer 18-hour 7B rerun after the earlier timeout
6. The local ready bundle now contains a finished 14B HumanEval+ row:
   - greedy `27.4`
   - majority vote `23.2`
   - falsification `43.9`
   - self-debug `43.9`
   - oracle `45.7`
7. The local ready bundle now also contains a finished 32B HumanEval+ row:
   - greedy `44.5`
   - majority vote `29.9`
   - falsification `82.9`
   - self-debug `82.3`
   - oracle `84.8`
8. The publication bundle now emits explicit reviewer-facing diagnostics rather
   than leaving the core claims implicit:
   - `paper/generated/publication_completion_table_current.tex`
   - `paper/generated/publication_gap_recovery_table_current.tex`
   - `paper/generated/publication_method_coverage_current.md`
   - `paper/generated/publication_highlights_current.md`

## What is still weak

1. The strongest HumanEval+ rows are still in the monitoring bundle, not the
   publication-ready bundle, because the resumed Delta seeds have not finished.
2. The paper-quality main table still lacks external-faithful S* and CodeT.
3. The central comparison to self-debug is still unfavorable or tied on several rows.
4. Full LiveCodeBench and broader math coverage are still incomplete.

## Recommendation for a stronger submission

1. Finish the resumed Delta HumanEval seeds so the strongest HumanEval rows move
   into the publication-ready table.
2. Run `generated_test_filter` in the paper-quality benchmark matrix to isolate
   the value of adaptivity from the value of extra generated tests.
3. Replace local `s_star` and `code_t` proxies with external-faithful runs if possible.
4. Keep the paper framing conservative until falsification clearly separates
   from self-debug on more than one benchmark family.
5. Use the generated publication coverage artifacts to keep the manuscript honest:
   - `paper/generated/publication_completion_table_current.tex`
   - `paper/generated/publication_method_coverage_current.md`

## Live queue follow-up

The repository now has an explicit DeltaAI launcher for the missing
`generated_test_filter` paper baseline:

- `scripts/submit_delta_generated_filter_matrix.sh`

The first queued MBPP+ augmentation jobs are:

- `2157600 / 2157601` for `reviewer_gtf_r1_7b_mbpp_full`
- `2157602 / 2157603` for `reviewer_gtf_qwen14b_mbpp_full`
- `2160266 / 2160267` for `reviewer_gtf_r1_32b_mbpp_full`
- `2160268 / 2160269` for `reviewer_gtf_r1_7b_humaneval_full`
- `2160270 / 2160271` for `reviewer_gtf_qwen14b_humaneval_full`
- `2160272 / 2160273` for `reviewer_gtf_r1_32b_humaneval_full`

This does not solve the larger S*/CodeT fidelity issue, but it does directly
address the cleaner reviewer question: ``does adaptive falsification beat a
non-adaptive generated-test filter on the same benchmark setup?''.

The original broader Delta paper-matrix coverage wave was queued as:

- `2160274 / 2160275` for `paperplus_r1_7b_livecodebench_full`
- `2160276 / 2160277` for `paperplus_r1_7b_math500_full`
- `2160228 / 2160229` for `paperplus_qwen14b_livecodebench_full`
- `2160230 / 2160231` for `paperplus_qwen14b_math500_full`
- `2160232 / 2160233` for `paperplus_r1_32b_livecodebench_full`
- `2160234 / 2160235` for `paperplus_r1_32b_math500_full`

For local appendix-style proxy coverage, the first Delta `paperproxy_*` jobs
were also queued as:

- `2160283 / 2160284` for `paperproxy_r1_7b_humaneval_full`
- `2160285 / 2160286` for `paperproxy_r1_7b_mbpp_full`
- `2160287 / 2160288` for `paperproxy_qwen14b_humaneval_full`
- `2160289 / 2160290` for `paperproxy_qwen14b_mbpp_full`
- `2160291 / 2160292` for `paperproxy_r1_32b_humaneval_full`
- `2160293 / 2160294` for `paperproxy_r1_32b_mbpp_full`

After the Delta billing-minute bottleneck was partially relieved, the active
replacement wave moved to a leaner mix of direct paper and reviewer runs:

- `2165719 / 2165722` for the corrected interactive rerun of
  `reviewer_gtf_r1_7b_mbpp_full`
- `2165724 / 2165725` for `paperplus_qwen14b_livecodebench_full`
- `2165726 / 2165727` for `paperplus_qwen14b_math500_full`
- `2165728 / 2165729` for `reviewer_gtf_qwen14b_mbpp_full`
- `2165730 / 2165731` for `reviewer_gtf_r1_32b_humaneval_full`
- `2165742 / 2165743` for `paperproxy_r1_7b_humaneval_full`
- `2165744 / 2165745` for `paperproxy_r1_7b_mbpp_full`

This replacement wave matters more than the older queued ids, because these
jobs were admitted after the QoS recovery and are the ones currently driving
the remaining baseline-coverage gap toward closure.
