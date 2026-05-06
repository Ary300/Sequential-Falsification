"""Export benchmarks into local JSON files under data/ for reproducible runs."""

from __future__ import annotations

import argparse
from pathlib import Path

from utils.data_loading import load_benchmark
from utils.io import dump_json, dump_pickle


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare benchmark exports under a local data directory.")
    parser.add_argument("--benchmarks", required=True, help="Comma-separated benchmark names.")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--prefer-pickle", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    data_root = Path(args.data_root)
    data_root.mkdir(parents=True, exist_ok=True)

    failures: list[tuple[str, str]] = []
    for benchmark in [item.strip() for item in args.benchmarks.split(",") if item.strip()]:
        try:
            rows = load_benchmark(benchmark, data_root=data_root)
        except Exception as exc:
            if not args.continue_on_error:
                raise
            failures.append((benchmark, f"{type(exc).__name__}: {exc}"))
            print(f"Skipping {benchmark}: {type(exc).__name__}: {exc}")
            continue
        out_dir = data_root / benchmark
        out_dir.mkdir(parents=True, exist_ok=True)
        if args.prefer_pickle:
            dump_pickle(rows, out_dir / "problems.pkl")
            print(f"Wrote {len(rows)} problems to {out_dir / 'problems.pkl'}")
            continue
        try:
            dump_json({"problems": rows}, out_dir / "problems.json")
            print(f"Wrote {len(rows)} problems to {out_dir / 'problems.json'}")
        except TypeError:
            dump_pickle(rows, out_dir / "problems.pkl")
            print(f"Wrote {len(rows)} problems to {out_dir / 'problems.pkl'} (pickle fallback)")

    if failures:
        print("Preparation completed with skipped benchmarks:")
        for benchmark, error in failures:
            print(f"  - {benchmark}: {error}")


if __name__ == "__main__":
    main()
