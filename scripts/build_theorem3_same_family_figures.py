#!/usr/bin/env python3
"""Build same-family theorem-3 figure payloads and plots."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402
from utils.plotting import maybe_plot_scaling_curve, save_plot_payload  # noqa: E402


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _series(summary: dict[str, Any], *, benchmark: str, split: str) -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in summary["rows"]:
        if row["benchmark"] != benchmark or row["split"] != split:
            continue
        family = str(row["family"])
        bucket = out.setdefault(
            family,
            {
                "label": family,
                "x": [],
                "y": [],
            },
        )
        bucket["x"].append(int(row["model_size_b"]))
        bucket["y"].append(round(float(row["gap_cot_1024"]), 4))
    return [out[key] for key in sorted(out)]


def _payload(summary: dict[str, Any], *, benchmark: str, split: str, title: str) -> dict[str, Any]:
    return {
        "title": title,
        "x_label": "Model size (B params)",
        "y_label": "Long-CoT confidence gap",
        "x_scale": "log2",
        "series": _series(summary, benchmark=benchmark, split=split),
    }


def main() -> None:
    summary = _load_json(ROOT / "docs/generated/theorem3_same_family_threshold_summary.json")
    output_dir = ROOT / "figures" / "theorem3_same_family"
    output_dir.mkdir(parents=True, exist_ok=True)

    payloads = {
        "conflictbank_conflict": _payload(
            summary,
            benchmark="conflictbank",
            split="conflict",
            title="Theorem 3 Same-Family Scaling: ConflictBank Conflict",
        ),
        "wikicontradict_conflict": _payload(
            summary,
            benchmark="wikicontradict",
            split="conflict",
            title="Theorem 3 Same-Family Scaling: WikiContradict Conflict",
        ),
    }

    manifest: dict[str, Any] = {"output_dir": str(output_dir), "figures": {}}
    for name, payload in payloads.items():
        payload_path = output_dir / f"{name}_payload.json"
        pdf_path = output_dir / f"{name}.pdf"
        save_plot_payload(payload, payload_path)
        render_format = maybe_plot_scaling_curve(payload, pdf_path)
        manifest["figures"][name] = {
            "payload": str(payload_path),
            "rendered": str(pdf_path),
            "render_format": render_format,
        }

    dump_json(manifest, output_dir / "manifest.json")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
