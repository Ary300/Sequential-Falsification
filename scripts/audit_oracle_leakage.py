"""Fast guardrails against benchmark-answer leakage in deployable methods."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from falsify import FalsificationConfig, sequential_falsify_candidates
from utils.data_loading import load_benchmark
from utils.sandbox import evaluate_candidate


def main() -> None:
    math_problem = next(problem for problem in load_benchmark("synthetic_demo") if problem.get("type") == "math")
    public_eval = evaluate_candidate(math_problem, "56", use_hidden=False)
    if public_eval.get("num_tests") != 0 or public_eval.get("passed"):
        raise SystemExit(f"math public evaluation leaked answer access: {public_eval}")

    candidates = [
        {"text": "56", "candidate_id": "correct"},
        {"text": "57", "candidate_id": "wrong_a"},
        {"text": "57", "candidate_id": "wrong_b"},
    ]
    payload = sequential_falsify_candidates(
        candidates,
        math_problem,
        FalsificationConfig(n_rounds=4, max_tiebreak_rounds=2),
    )
    records = payload["records"]
    if any(record.get("trace") for record in records):
        raise SystemExit("math falsification unexpectedly created answer-check traces")
    if any(float(record.get("confidence", 0.0)) > 0.0 for record in records):
        raise SystemExit("math no-probe fallback should not emit calibrated confidence")
    print("oracle_leakage_audit_ok")


if __name__ == "__main__":
    main()
