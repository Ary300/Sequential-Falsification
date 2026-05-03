#!/usr/bin/env python3
"""Prewarm the Paper 2 free-form retrieval cache without loading a model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.run_paper2_freeform_eval import (  # noqa: E402
    _load_asqa,
    _load_cache,
    _load_nq_open,
    _load_triviaqa_open,
    _save_cache,
    _wiki_search,
)


LOADERS = {
    "triviaqa_open": _load_triviaqa_open,
    "nq_open": _load_nq_open,
    "asqa": _load_asqa,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prewarm retrieval cache for Paper 2 free-form evaluation.")
    parser.add_argument("--datasets", default="triviaqa_open,nq_open,asqa")
    parser.add_argument("--max-examples", type=int, default=32)
    parser.add_argument("--search-limit", type=int, default=6)
    parser.add_argument(
        "--cache-file",
        default=str(ROOT / "docs" / "generated" / "paper2_freeform_retrieval_cache.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cache_path = Path(args.cache_file)
    cache = _load_cache(cache_path)
    dataset_names = [item.strip() for item in args.datasets.split(",") if item.strip()]
    for dataset_name in dataset_names:
        if dataset_name not in LOADERS:
            raise ValueError(f"Unsupported dataset: {dataset_name}")
        rows = LOADERS[dataset_name](args.max_examples)
        print(f"dataset {dataset_name} rows {len(rows)}", flush=True)
        for idx, row in enumerate(rows, start=1):
            hits = _wiki_search(
                row["question"],
                search_limit=args.search_limit,
                cache_path=cache_path,
                cache=cache,
            )
            if idx % 4 == 0:
                print(f"prefetched {dataset_name} {idx} contexts {len(hits)}", flush=True)
    _save_cache(cache_path, cache)
    print(f"done {cache_path}", flush=True)


if __name__ == "__main__":
    main()
