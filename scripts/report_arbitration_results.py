#!/usr/bin/env python3
"""Render knowledge-arbitration result JSON into summary artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.reporting import load_results, write_report  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build summary JSON/Markdown and figure payloads for arbitration results.")
    parser.add_argument("--results-file", required=True, help="Path to an arbitration results JSON file.")
    parser.add_argument("--output-dir", required=True, help="Directory for the rendered report artifacts.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_results(args.results_file)
    report_manifest = write_report(payload, args.output_dir)
    print(json.dumps(report_manifest, indent=2))


if __name__ == "__main__":
    main()
