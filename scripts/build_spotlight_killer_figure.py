#!/usr/bin/env python3
"""Build a self-contained SVG 2x2 killer figure for the arbitration paper."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.experiment import _benchmark_profile  # noqa: E402
from utils.io import dump_json  # noqa: E402


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fmt(value: float) -> str:
    return f"{value:.2f}"


def _top_left_payload(report: dict[str, Any]) -> dict[str, Any]:
    pretty = {
        "bayes_proxy": "Bayes",
        "heuristic_adaptive": "Heuristic",
        "self_rag": "Self-RAG",
        "cocoa": "CoCoA",
        "adacad": "AdaCAD",
        "cad": "CAD",
        "fixed_50": "Fixed 50",
        "always_context": "Always ctx",
        "always_parametric": "Always param",
    }
    wanted = list(pretty.keys())
    overall = {row["policy"]: float(row["mean_regret"]) for row in report["regret"]["overall"]}
    return {
        "title": "Spotlight Matrix Regret",
        "categories": [pretty[key] for key in wanted],
        "values": [overall[key] for key in wanted],
        "policy_keys": wanted,
    }


def _top_right_payload(report: dict[str, Any]) -> dict[str, Any]:
    rows = report["regret"]["rows"]
    benchmark_to_values: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        series = str(row["series"])
        benchmark = series.split("::", 1)[0]
        policy = str(row["policy"])
        if policy not in {"bayes_proxy", "heuristic_adaptive", "self_rag"}:
            continue
        bucket = benchmark_to_values.setdefault(benchmark, {"bayes_proxy": [], "heuristic_adaptive": [], "self_rag": []})
        bucket[policy].append(float(row["mean_regret"]))

    points = []
    for benchmark, bucket in benchmark_to_values.items():
        profile = _benchmark_profile(benchmark)
        points.append(
            {
                "benchmark": benchmark,
                "conflict_density": float(profile["conflict"]),
                "bayes_proxy": sum(bucket["bayes_proxy"]) / max(1, len(bucket["bayes_proxy"])),
                "heuristic_adaptive": sum(bucket["heuristic_adaptive"]) / max(1, len(bucket["heuristic_adaptive"])),
                "self_rag": sum(bucket["self_rag"]) / max(1, len(bucket["self_rag"])),
            }
        )
    points.sort(key=lambda item: item["conflict_density"])
    return {"title": "Conflict Density Sweep", "points": points}


def _bottom_left_payload(results_payload: dict[str, Any]) -> dict[str, Any]:
    summary = results_payload["summary"]
    return {
        "title": "Reliability Diagram",
        "perfect": [{"x": i / 10.0, "y": i / 10.0} for i in range(11)],
        "series": [
            {
                "label": "Bayes",
                "bins": [
                    {"x": float(row["avg_confidence"]), "y": float(row["avg_accuracy"])}
                    for row in summary["bayes_proxy"]["calibration_bins"]
                ],
            },
            {
                "label": "Heuristic",
                "bins": [
                    {"x": float(row["avg_confidence"]), "y": float(row["avg_accuracy"])}
                    for row in summary["heuristic_adaptive"]["calibration_bins"]
                ],
            },
        ],
    }


def _bottom_right_payload(real7: dict[str, Any], real14: dict[str, Any]) -> dict[str, Any]:
    def _rows(payload: dict[str, Any], benchmark: str) -> list[dict[str, Any]]:
        return [row for row in payload["rows"] if row["benchmark"] == benchmark]

    def _series(payload: dict[str, Any], label: str, benchmark: str, size_label: str) -> list[dict[str, Any]]:
        out = []
        for row in _rows(payload, benchmark):
            split = str(row["split"])
            out.append(
                {
                    "label": f"{size_label} {split}",
                    "split": split,
                    "x": [0.0, 128.0, 1024.0],
                    "y": [float(row["gap_cot_0"]), float(row["gap_cot_128"]), float(row["gap_cot_1024"])],
                }
            )
        return out

    return {
        "title": "Two-Regime Curves",
        "panels": [
            {
                "benchmark": "ConflictBank",
                "series": _series(real7, "7B", "conflictbank", "7B") + _series(real14, "14B", "conflictbank", "14B"),
            },
            {
                "benchmark": "WikiContradict",
                "series": _series(real7, "7B", "wikicontradict", "7B") + _series(real14, "14B", "wikicontradict", "14B"),
            },
        ],
    }


def _minmax(values: list[float], *, pad: float = 0.0) -> tuple[float, float]:
    lo = min(values)
    hi = max(values)
    if lo == hi:
        return lo - 1.0, hi + 1.0
    span = hi - lo
    return lo - span * pad, hi + span * pad


def _line_path(points: list[tuple[float, float]]) -> str:
    return " ".join(
        ("M" if idx == 0 else "L") + f" {x:.2f} {y:.2f}"
        for idx, (x, y) in enumerate(points)
    )


def _draw_axes(x: float, y: float, w: float, h: float, *, y_ticks: list[float], x_ticks: list[tuple[float, str]], y_min: float, y_max: float) -> list[str]:
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="#222" stroke-width="1"/>'
    ]
    for tick in y_ticks:
        tick_y = y + h - (tick - y_min) / max(1e-9, (y_max - y_min)) * h
        parts.append(f'<line x1="{x}" y1="{tick_y:.2f}" x2="{x + w}" y2="{tick_y:.2f}" stroke="#e5e7eb" stroke-width="1"/>')
        parts.append(f'<text x="{x - 6}" y="{tick_y + 4:.2f}" text-anchor="end" font-size="10" fill="#444">{_escape(_fmt(tick))}</text>')
    for tick_x, label in x_ticks:
        parts.append(f'<line x1="{tick_x:.2f}" y1="{y + h}" x2="{tick_x:.2f}" y2="{y + h + 5}" stroke="#222" stroke-width="1"/>')
        parts.append(f'<text x="{tick_x:.2f}" y="{y + h + 18}" text-anchor="middle" font-size="10" fill="#444">{_escape(label)}</text>')
    return parts


def _render_top_left(payload: dict[str, Any], x: float, y: float, w: float, h: float) -> str:
    values = list(payload["values"])
    categories = list(payload["categories"])
    y_min, y_max = _minmax(values, pad=0.15)
    zero_y = y + h - (0.0 - y_min) / (y_max - y_min) * h
    colors = {
        "Bayes": "#0f766e",
        "Heuristic": "#b45309",
        "Self-RAG": "#2563eb",
        "CoCoA": "#7c3aed",
        "AdaCAD": "#9333ea",
        "CAD": "#64748b",
        "Fixed 50": "#dc2626",
        "Always ctx": "#ef4444",
        "Always param": "#f97316",
    }
    inner_x, inner_y, inner_w, inner_h = x + 44, y + 28, w - 56, h - 56
    parts = [f'<text x="{x + 8}" y="{y + 16}" font-size="13" font-weight="700">{_escape(payload["title"])}</text>']
    y_ticks = [round(v, 1) for v in [y_min, (y_min + y_max) / 2.0, y_max]]
    slot = inner_w / len(values)
    x_ticks = [(inner_x + slot * (idx + 0.5), categories[idx]) for idx in range(len(categories))]
    parts.extend(_draw_axes(inner_x, inner_y, inner_w, inner_h, y_ticks=y_ticks, x_ticks=x_ticks, y_min=y_min, y_max=y_max))
    parts.append(f'<line x1="{inner_x}" y1="{zero_y:.2f}" x2="{inner_x + inner_w}" y2="{zero_y:.2f}" stroke="#111827" stroke-width="1"/>')
    for idx, value in enumerate(values):
        bar_w = slot * 0.66
        bx = inner_x + slot * idx + slot * 0.17
        by = y + h - (max(value, 0.0) - y_min) / (y_max - y_min) * inner_h - (inner_y - y)
        if value >= 0.0:
            rect_y = zero_y
            rect_h = by - zero_y
        else:
            rect_y = by
            rect_h = zero_y - by
        rect_h = max(1.0, rect_h)
        color = colors.get(categories[idx], "#64748b")
        parts.append(f'<rect x="{bx:.2f}" y="{rect_y:.2f}" width="{bar_w:.2f}" height="{rect_h:.2f}" fill="{color}" opacity="0.9"/>')
    return "".join(parts)


def _render_top_right(payload: dict[str, Any], x: float, y: float, w: float, h: float) -> str:
    points = list(payload["points"])
    inner_x, inner_y, inner_w, inner_h = x + 44, y + 28, w - 56, h - 56
    xs = [float(point["conflict_density"]) for point in points]
    ys = [float(point[key]) for point in points for key in ("bayes_proxy", "heuristic_adaptive", "self_rag")]
    x_min, x_max = _minmax(xs, pad=0.05)
    y_min, y_max = _minmax(ys, pad=0.15)
    series_meta = [
        ("bayes_proxy", "Bayes", "#0f766e"),
        ("heuristic_adaptive", "Heuristic", "#b45309"),
        ("self_rag", "Self-RAG", "#2563eb"),
    ]
    parts = [f'<text x="{x + 8}" y="{y + 16}" font-size="13" font-weight="700">{_escape(payload["title"])}</text>']
    y_ticks = [round(v, 2) for v in [y_min, (y_min + y_max) / 2.0, y_max]]
    x_ticks = [
        (inner_x + (tick - x_min) / (x_max - x_min) * inner_w, _fmt(tick))
        for tick in [x_min, (x_min + x_max) / 2.0, x_max]
    ]
    parts.extend(_draw_axes(inner_x, inner_y, inner_w, inner_h, y_ticks=y_ticks, x_ticks=x_ticks, y_min=y_min, y_max=y_max))
    for key, label, color in series_meta:
        pts = []
        for point in points:
            px = inner_x + (float(point["conflict_density"]) - x_min) / (x_max - x_min) * inner_w
            py = inner_y + inner_h - (float(point[key]) - y_min) / (y_max - y_min) * inner_h
            pts.append((px, py))
        parts.append(f'<path d="{_line_path(pts)}" fill="none" stroke="{color}" stroke-width="2"/>')
        for (px, py), point in zip(pts, points):
            parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3" fill="{color}"/>')
            if key == "bayes_proxy":
                parts.append(f'<text x="{px + 4:.2f}" y="{py - 6:.2f}" font-size="9" fill="#374151">{_escape(point["benchmark"])}</text>')
    legend_x = inner_x + inner_w - 92
    legend_y = inner_y + 10
    for idx, (_, label, color) in enumerate(series_meta):
        ly = legend_y + idx * 14
        parts.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x + 14}" y2="{ly}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<text x="{legend_x + 18}" y="{ly + 4}" font-size="10">{_escape(label)}</text>')
    return "".join(parts)


def _render_bottom_left(payload: dict[str, Any], x: float, y: float, w: float, h: float) -> str:
    inner_x, inner_y, inner_w, inner_h = x + 44, y + 28, w - 56, h - 56
    parts = [f'<text x="{x + 8}" y="{y + 16}" font-size="13" font-weight="700">{_escape(payload["title"])}</text>']
    y_ticks = [0.0, 0.5, 1.0]
    x_ticks = [(inner_x + t * inner_w, _fmt(t)) for t in [0.0, 0.5, 1.0]]
    parts.extend(_draw_axes(inner_x, inner_y, inner_w, inner_h, y_ticks=y_ticks, x_ticks=x_ticks, y_min=0.0, y_max=1.0))
    perfect = [(inner_x + item["x"] * inner_w, inner_y + inner_h - item["y"] * inner_h) for item in payload["perfect"]]
    parts.append(f'<path d="{_line_path(perfect)}" fill="none" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4 3"/>')
    colors = {"Bayes": "#0f766e", "Heuristic": "#b45309"}
    for item in payload["series"]:
        pts = []
        for row in item["bins"]:
            px = inner_x + float(row["x"]) * inner_w
            py = inner_y + inner_h - float(row["y"]) * inner_h
            pts.append((px, py))
        color = colors[item["label"]]
        parts.append(f'<path d="{_line_path(pts)}" fill="none" stroke="{color}" stroke-width="2"/>')
        for px, py in pts:
            parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3" fill="{color}"/>')
    legend_x = inner_x + inner_w - 92
    legend_y = inner_y + 10
    for idx, (label, color) in enumerate([("Bayes", "#0f766e"), ("Heuristic", "#b45309"), ("Perfect", "#9ca3af")]):
        ly = legend_y + idx * 14
        dash = ' stroke-dasharray="4 3"' if label == "Perfect" else ""
        parts.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x + 14}" y2="{ly}" stroke="{color}" stroke-width="2"{dash}/>')
        parts.append(f'<text x="{legend_x + 18}" y="{ly + 4}" font-size="10">{_escape(label)}</text>')
    return "".join(parts)


def _render_small_curve(panel: dict[str, Any], x: float, y: float, w: float, h: float) -> str:
    inner_x, inner_y, inner_w, inner_h = x + 30, y + 18, w - 40, h - 32
    ys = [float(v) for series in panel["series"] for v in series["y"]]
    y_min, y_max = _minmax(ys, pad=0.08)
    x_min, x_max = 0.0, 1024.0
    parts = [f'<text x="{x + 4}" y="{y + 12}" font-size="11" font-weight="700">{_escape(panel["benchmark"])}</text>']
    y_ticks = [round(v, 2) for v in [y_min, (y_min + y_max) / 2.0, y_max]]
    x_ticks = [(inner_x + t / x_max * inner_w, str(int(t))) for t in [0.0, 128.0, 1024.0]]
    parts.extend(_draw_axes(inner_x, inner_y, inner_w, inner_h, y_ticks=y_ticks, x_ticks=x_ticks, y_min=y_min, y_max=y_max))
    color_map = {"7B": "#0f766e", "14B": "#dc2626"}
    for series in panel["series"]:
        size_label = "14B" if series["label"].startswith("14B") else "7B"
        dash = ' stroke-dasharray="5 3"' if series["split"] == "no_conflict" else ""
        pts = []
        for xv, yv in zip(series["x"], series["y"]):
            px = inner_x + float(xv) / x_max * inner_w
            py = inner_y + inner_h - (float(yv) - y_min) / (y_max - y_min) * inner_h
            pts.append((px, py))
        color = color_map[size_label]
        parts.append(f'<path d="{_line_path(pts)}" fill="none" stroke="{color}" stroke-width="2"{dash}/>')
        for px, py in pts:
            parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2.5" fill="{color}"/>')
    return "".join(parts)


def _render_bottom_right(payload: dict[str, Any], x: float, y: float, w: float, h: float) -> str:
    parts = [f'<text x="{x + 8}" y="{y + 16}" font-size="13" font-weight="700">{_escape(payload["title"])}</text>']
    sub_w = (w - 22) / 2.0
    for idx, panel in enumerate(payload["panels"]):
        px = x + 8 + idx * (sub_w + 6)
        py = y + 22
        parts.append(_render_small_curve(panel, px, py, sub_w, h - 28))
    legend_x = x + w - 122
    legend_y = y + h - 34
    for idx, (label, color, dash) in enumerate(
        [("7B conflict", "#0f766e", ""), ("7B no-conflict", "#0f766e", "5 3"), ("14B conflict", "#dc2626", ""), ("14B no-conflict", "#dc2626", "5 3")]
    ):
        ly = legend_y + idx * 12
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x + 14}" y2="{ly}" stroke="{color}" stroke-width="2"{dash_attr}/>')
        parts.append(f'<text x="{legend_x + 18}" y="{ly + 4}" font-size="9">{_escape(label)}</text>')
    return "".join(parts)


def build_svg(payloads: dict[str, Any]) -> str:
    width = 1180
    height = 820
    panels = {
        "tl": (24, 24, 552, 360),
        "tr": (604, 24, 552, 360),
        "bl": (24, 420, 552, 360),
        "br": (604, 420, 552, 360),
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="24" y="18" font-size="16" font-weight="700" fill="#0f172a">Bayes-Optimal Knowledge Arbitration: Spotlight Figure Suite</text>',
    ]
    parts.append(_render_top_left(payloads["top_left"], *panels["tl"]))
    parts.append(_render_top_right(payloads["top_right"], *panels["tr"]))
    parts.append(_render_bottom_left(payloads["bottom_left"], *panels["bl"]))
    parts.append(_render_bottom_right(payloads["bottom_right"], *panels["br"]))
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    t12_report = _load_json(ROOT / "results/arbitration_spotlight_t12_benchmark_v2/report/arbitration_summary.json")
    t12_results = _load_json(ROOT / "results/arbitration_spotlight_t12_benchmark_v2/arbitration_spotlight_t12_matrix_benchmark_results.json")
    real7 = _load_json(ROOT / "docs/generated/theorem3_real_7b_final.json")
    real14 = _load_json(ROOT / "docs/generated/theorem3_real_14b_final.json")

    payloads = {
        "top_left": _top_left_payload(t12_report),
        "top_right": _top_right_payload(t12_report),
        "bottom_left": _bottom_left_payload(t12_results),
        "bottom_right": _bottom_right_payload(real7, real14),
    }

    out_dir = ROOT / "figures" / "spotlight_killer"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        dump_json(payload, out_dir / f"{name}_payload.json")

    svg = build_svg(payloads)
    svg_path = out_dir / "spotlight_killer_figure.svg"
    svg_path.write_text(svg, encoding="utf-8")

    md_lines = [
        "# Spotlight Killer Figure",
        "",
        f"- Main SVG: `{svg_path}`",
        f"- Top-left: overall spotlight-matrix regret bars from `arbitration_spotlight_t12_benchmark_v2`.",
        f"- Top-right: benchmark conflict-density sweep using benchmark conflict priors and mean regret by benchmark.",
        f"- Bottom-left: reliability diagram comparing Bayes proxy vs heuristic adaptive on the spotlight matrix.",
        f"- Bottom-right: theorem-3 real-trace two-regime curves for DeepSeek `7B` and `14B` on `ConflictBank` and `WikiContradict`.",
        "",
        "## Headline Read",
        "",
        "- Bayes dominates the main theorem-1/theorem-2 comparison against the generic heuristic and fixed policies.",
        "- The reliability diagram shows Bayes is closer to the diagonal than the heuristic across confidence bins.",
        "- The theorem-3 panel shows benchmark-dependent structure rather than a universal monotone law: `ConflictBank` remains pathological at `14B`, while `WikiContradict` shows peak-then-partial-recovery.",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(md_lines), encoding="utf-8")

    manifest = {
        "output_dir": str(out_dir),
        "svg": str(svg_path),
        "payloads": {name: str(out_dir / f"{name}_payload.json") for name in payloads},
    }
    dump_json(manifest, out_dir / "manifest.json")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
