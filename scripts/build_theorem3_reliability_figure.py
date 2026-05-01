#!/usr/bin/env python3
"""Build Yoon-style reliability diagrams plus frequency histograms for theorem-3 slices."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 reliability diagrams from theorem3_summary.json.")
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--benchmark", default="conflictbank")
    parser.add_argument("--split", default="conflict")
    parser.add_argument("--cot-lengths", default="0,128,1024")
    parser.add_argument("--title", default="")
    return parser.parse_args()


def _matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore

        return plt
    except ModuleNotFoundError:
        return None


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _slice_lookup(summary: dict[str, Any]) -> dict[tuple[str, str, int], dict[str, Any]]:
    lookup: dict[tuple[str, str, int], dict[str, Any]] = {}
    for row in summary.get("slice_rows", []):
        lookup[(str(row["benchmark"]), str(row["split"]), int(row["cot_length"]))] = row
    return lookup


def _payload(summary: dict[str, Any], *, benchmark: str, split: str, cot_lengths: list[int], title: str) -> dict[str, Any]:
    lookup = _slice_lookup(summary)
    series = []
    for cot_length in cot_lengths:
        row = lookup.get((benchmark, split, cot_length))
        if not row:
            continue
        bins = row.get("calibration_bins", [])
        total = sum(int(item.get("count", 0)) for item in bins) or 1
        series.append(
            {
                "label": f"cot={cot_length}",
                "cot_length": cot_length,
                "bins": [
                    {
                        "bin": int(item.get("bin", 0)),
                        "avg_confidence": float(item.get("avg_confidence", 0.0)),
                        "avg_accuracy": float(item.get("avg_accuracy", 0.0)),
                        "count": int(item.get("count", 0)),
                        "frequency": float(item.get("count", 0)) / total,
                    }
                    for item in bins
                ],
            }
        )
    return {
        "benchmark": benchmark,
        "split": split,
        "title": title or f"{benchmark} / {split} reliability",
        "series": series,
        "perfect": [{"x": i / 10, "y": i / 10} for i in range(11)],
    }


def _render(payload: dict[str, Any], output_prefix: Path) -> str:
    plt = _matplotlib()
    dump_json(payload, output_prefix.with_suffix(".json"))
    if plt is None:
        return "json"

    series = payload.get("series", [])
    if not series:
        return "json"

    fig, axes = plt.subplots(
        2,
        len(series),
        figsize=(4.0 * len(series), 6.0),
        squeeze=False,
        gridspec_kw={"height_ratios": [3.0, 1.35]},
    )

    for col, item in enumerate(series):
        bins = item["bins"]
        top = axes[0][col]
        bottom = axes[1][col]
        xs = [float(entry["avg_confidence"]) for entry in bins]
        ys = [float(entry["avg_accuracy"]) for entry in bins]
        freqs = [float(entry["frequency"]) for entry in bins]
        top.plot([0.0, 1.0], [0.0, 1.0], linestyle="--", color="black", linewidth=1.0)
        top.plot(xs, ys, marker="o", linewidth=1.5, color="#0b6e4f")
        top.set_xlim(0, 1)
        top.set_ylim(0, 1)
        top.set_title(item["label"])
        top.set_xlabel("Predicted confidence")
        top.set_ylabel("Observed accuracy")

        bottom.bar(range(len(freqs)), freqs, color="#6c8ebf", width=0.8)
        bottom.set_xticks(range(len(freqs)), [str(entry["bin"]) for entry in bins], rotation=0)
        bottom.set_xlabel("Confidence bin")
        bottom.set_ylabel("Frequency")
        bottom.set_ylim(0, max(freqs) * 1.2 if freqs else 1.0)

    fig.suptitle(payload["title"])
    fig.tight_layout()
    fig.savefig(output_prefix.with_suffix(".png"))
    plt.close(fig)
    return "plot"


def _markdown(payload: dict[str, Any], render_mode: str) -> str:
    lines = [
        "# Theorem 3 Reliability Figure Note",
        "",
        f"- Benchmark: `{payload['benchmark']}`",
        f"- Split: `{payload['split']}`",
        f"- Render mode: `{render_mode}`",
        "",
        "## Included CoT Series",
        "",
    ]
    for item in payload.get("series", []):
        bins = item.get("bins", [])
        total = sum(int(entry.get("count", 0)) for entry in bins)
        lines.append(
            f"- `{item['label']}`: `{len(bins)}` bins, `{total}` examples, "
            f"peak frequency `{max((entry['frequency'] for entry in bins), default=0.0):.4f}`"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    cot_lengths = [int(item.strip()) for item in args.cot_lengths.split(",") if item.strip()]
    summary = _load(Path(args.summary_json))
    payload = _payload(
        summary,
        benchmark=args.benchmark,
        split=args.split,
        cot_lengths=cot_lengths,
        title=args.title,
    )
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    render_mode = _render(payload, output_prefix)
    output_prefix.with_suffix(".md").write_text(_markdown(payload, render_mode), encoding="utf-8")
    print(json.dumps({"output_prefix": str(output_prefix), "render_mode": render_mode}, indent=2))


if __name__ == "__main__":
    main()
