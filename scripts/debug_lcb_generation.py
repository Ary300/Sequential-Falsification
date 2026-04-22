"""Debug one LiveCodeBench generation/evaluation path against a vLLM server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.generate import GenerationConfig, generate_candidates
from src.utils.data_loading import load_benchmark
from src.utils.sandbox import evaluate_candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
    parser.add_argument("--problem-index", type=int, default=0)
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=768)
    parser.add_argument("--output-file", default="results/livecodebench_debug/debug.json")
    args = parser.parse_args()

    problems = load_benchmark("livecodebench_v6")
    problem = problems[args.problem_index]
    cfg = GenerationConfig(
        backend="openai",
        model=args.model,
        api_base=args.api_base,
        max_tokens=args.max_tokens,
        request_timeout=60.0,
        temperature=0.7,
        seed=42,
    )
    candidates = generate_candidates(problem, n=args.n, config=cfg)
    rows = []
    for candidate in candidates:
        public_eval = evaluate_candidate(problem, candidate["text"], use_hidden=False)
        hidden_eval = evaluate_candidate(problem, candidate["text"], use_hidden=True)
        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "raw_text": candidate["raw_text"],
                "text": candidate["text"],
                "public_eval": public_eval,
                "hidden_eval": hidden_eval,
            }
        )

    payload = {
        "problem_id": problem["id"],
        "entry_point": problem.get("entry_point"),
        "public_tests": problem.get("public_tests", [])[:2],
        "hidden_tests": problem.get("hidden_tests", [])[:2],
        "candidates": rows,
    }
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"output_file": str(output_path), "problem_id": problem["id"]}, indent=2))


if __name__ == "__main__":
    main()
