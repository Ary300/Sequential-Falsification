#!/usr/bin/env python3
"""Smoke-test the stronger falsification selector on the synthetic demo benchmark."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "results" / "tmp_headline_selector_check"


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    subprocess.run(
        [
            sys.executable,
            "src/evaluate.py",
            "--benchmark",
            "synthetic_demo",
            "--methods",
            "greedy,majority_vote,self_debug,generated_test_filter,code_t,s_star,falsification,oracle",
            "--backend",
            "mock",
            "--model",
            "mock-model",
            "--n-candidates",
            "4",
            "--n-falsification-rounds",
            "2",
            "--max-tiebreak-rounds",
            "2",
            "--output-dir",
            str(OUTPUT_DIR),
        ],
        check=True,
        cwd=ROOT,
    )

    payload = json.loads((OUTPUT_DIR / "results.json").read_text(encoding="utf-8"))
    benchmark = payload["benchmarks"][0]
    rows = benchmark["results"]
    assert rows, "Synthetic benchmark produced no per-problem results."

    saw_selection_metadata = False
    for row in rows:
        selected = row["methods"]["falsification"].get("selected")
        assert selected is not None, "Falsification selected no candidate."
        assert "public_score" in selected, "Falsification selector is missing public_score."
        assert "trace_strength" in selected, "Falsification selector is missing trace_strength."
        saw_selection_metadata = True

    assert saw_selection_metadata, "Expected to validate at least one falsification selection."

    summary = benchmark["summary"]["methods"]
    falsification_acc = float(summary["falsification"]["accuracy"])
    majority_acc = float(summary["majority_vote"]["accuracy"])
    assert falsification_acc >= majority_acc, "Headline selector regressed below majority vote on synthetic demo."

    print(
        json.dumps(
            {
                "checked_benchmark": benchmark["benchmark"],
                "falsification_accuracy": falsification_acc,
                "majority_accuracy": majority_acc,
                "output_dir": str(OUTPUT_DIR),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
