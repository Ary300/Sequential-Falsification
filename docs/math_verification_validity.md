# Math Benchmark Validity Guardrail

The current repository treats math benchmarks as evaluation targets, not as
fully verified falsification targets.

## What changed

Earlier experimental code allowed math falsification to use an `answer_check`
probe that compared a candidate against `reference_answer` during selection.
That is oracle leakage: it is valid for the final hidden evaluation or oracle
upper bound, but not for any deployable method.

The pipeline now enforces this guardrail:

- `evaluate_candidate(..., use_hidden=False)` returns an oracle-free
  `no_public_oracle` result for math tasks.
- `_build_probe_bank` returns no math answer-check probes.
- Falsification selection on math uses only non-oracle answer agreement among
  candidates.
- Oracle and final reporting still use `reference_answer`, because benchmark
  scoring and pass@N upper bounds must know the true answer.

## Interpretation

Math rows are scientifically valid after this change, but they should be framed
conservatively until we integrate a real math verifier/PRM. In the paper, do
not claim adversarial math falsification from these rows. Claim only that the
same evaluation harness supports math benchmarks and that current math
selection is an oracle-free consensus fallback.

## What is needed for headline math results

A NeurIPS-strength math story needs at least one non-oracle verifier:

- a process reward model such as ThinkPRM or Math-Shepherd;
- symbolic/numeric substitution checks for problem families where constraints
  are parseable;
- generated related problems with independently known answers;
- verifier-guided search or DVTS-style scoring.

Until one of those exists, code benchmarks remain the primary falsification
evidence and math benchmarks are supporting scope.
