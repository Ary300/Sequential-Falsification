"""Plotting helpers with graceful fallback when matplotlib is unavailable."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _ensure_parent(path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def _matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore

        return plt
    except ModuleNotFoundError:
        return None


def save_plot_payload(payload: dict[str, Any], output_path: str | Path) -> None:
    path = _ensure_parent(output_path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def maybe_plot_grouped_bars(payload: dict[str, Any], output_path: str | Path) -> str:
    plt = _matplotlib()
    if plt is None:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    categories = payload.get("categories", [])
    series = payload.get("series", [])
    if not categories or not series:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    fig, ax = plt.subplots(figsize=payload.get("figsize", (6.5, 3.8)))
    width = 0.8 / max(1, len(series))
    x = list(range(len(categories)))
    for idx, item in enumerate(series):
        offset = (idx - (len(series) - 1) / 2) * width
        values = item.get("values", [])
        ax.bar([value + offset for value in x], values, width=width, label=item.get("label", f"series_{idx}"))
    ax.set_xticks(x, categories, rotation=payload.get("rotation", 0))
    ax.set_xlabel(payload.get("x_label", "Category"))
    ax.set_ylabel(payload.get("y_label", "Value"))
    ax.set_title(payload.get("title", "Grouped Bars"))
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(_ensure_parent(output_path))
    plt.close(fig)
    return "plot"


def maybe_plot_scatter(payload: dict[str, Any], output_path: str | Path) -> str:
    plt = _matplotlib()
    if plt is None:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    series = payload.get("series", [])
    if not series:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    fig, ax = plt.subplots(figsize=payload.get("figsize", (5.5, 4.0)))
    for item in series:
        xs = item.get("x", [])
        ys = item.get("y", [])
        ax.scatter(xs, ys, label=item.get("label", "series"))
        if payload.get("annotate_points"):
            annotations = item.get("annotations", [])
            for x, y, text in zip(xs, ys, annotations):
                ax.annotate(str(text), (x, y), fontsize=8, xytext=(4, 4), textcoords="offset points")
    if payload.get("diagonal"):
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        lo = min(x_min, y_min)
        hi = max(x_max, y_max)
        ax.plot([lo, hi], [lo, hi], linestyle="--", color="black", linewidth=1.0)
    ax.set_xlabel(payload.get("x_label", "x"))
    ax.set_ylabel(payload.get("y_label", "y"))
    ax.set_title(payload.get("title", "Scatter"))
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(_ensure_parent(output_path))
    plt.close(fig)
    return "plot"


def maybe_plot_scaling_curve(payload: dict[str, Any], output_path: str | Path) -> str:
    plt = _matplotlib()
    if plt is None:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    series = payload.get("series", [])
    if not series:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"
    plt.figure(figsize=(5.5, 3.5))
    for item in series:
        plt.plot(item["x"], item["y"], marker="o", label=item["label"])
    x_scale = payload.get("x_scale", "log2")
    if x_scale == "log2":
        plt.xscale("log", base=2)
    elif x_scale == "log10":
        plt.xscale("log", base=10)
    plt.xlabel(payload.get("x_label", "N"))
    plt.ylabel(payload.get("y_label", "Accuracy"))
    plt.title(payload.get("title", "Scaling Curve"))
    handles, labels = plt.gca().get_legend_handles_labels()
    if handles:
        plt.legend(frameon=False)
    path = _ensure_parent(output_path)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return "plot"


def maybe_plot_calibration(payload: dict[str, Any], output_path: str | Path) -> str:
    plt = _matplotlib()
    if plt is None:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    panels = payload.get("panels", [])
    if not panels:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    fig, axes = plt.subplots(1, len(panels), figsize=(5.5 * max(1, len(panels)), 3.5), squeeze=False)
    for ax, panel in zip(axes[0], panels):
        perfect = panel.get("perfect_calibration", [])
        dynamic_series = panel.get("series", [])
        def _x(item: dict[str, Any]) -> float:
            return float(item.get("confidence", item.get("avg_confidence", item.get("x", 0.0))))

        def _y(item: dict[str, Any]) -> float:
            return float(item.get("accuracy", item.get("avg_accuracy", item.get("y", 0.0))))

        if perfect:
            ax.plot([_x(item) for item in perfect], [_y(item) for item in perfect], linestyle="--", label="perfect")
        if dynamic_series:
            marker_map = {
                "falsification": "o",
                "s_star": "P",
                "code_t": "v",
                "generated_test_filter": "d",
                "majority_vote": "s",
                "self_debug": "^",
                "greedy": "x",
            }
            label_map = {
                "falsification": "ours",
                "s_star": "S* proxy",
                "code_t": "CodeT proxy",
                "generated_test_filter": "generated-test filter",
                "majority_vote": "majority",
                "self_debug": "self-debug",
                "greedy": "greedy",
            }
            for item in dynamic_series:
                bins = item.get("bins", [])
                method = item.get("method", "method")
                if not bins:
                    continue
                ax.plot(
                    [_x(entry) for entry in bins],
                    [_y(entry) for entry in bins],
                    marker=marker_map.get(method, "o"),
                    label=label_map.get(method, method),
                )
        else:
            falsification = panel.get("falsification_bins", [])
            majority = panel.get("majority_vote_bins", [])
            if falsification:
                ax.plot([_x(item) for item in falsification], [_y(item) for item in falsification], marker="o", label="ours")
            if majority:
                ax.plot([_x(item) for item in majority], [_y(item) for item in majority], marker="s", label="majority")
        ax.set_title(panel.get("benchmark", "benchmark"))
        ax.set_xlabel("Predicted confidence")
        ax.set_ylabel("Observed accuracy")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(_ensure_parent(output_path))
    plt.close(fig)
    return "plot"


def maybe_plot_difficulty(payload: dict[str, Any], output_path: str | Path) -> str:
    plt = _matplotlib()
    if plt is None:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    panels = payload.get("panels", [])
    if not panels:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    fig, axes = plt.subplots(1, len(panels), figsize=(5.5 * max(1, len(panels)), 3.5), squeeze=False)
    for ax, panel in zip(axes[0], panels):
        difficulty = panel.get("difficulty", {})
        if not difficulty:
            continue
        bins = list(difficulty.keys())
        ours = [difficulty[level].get("falsification", 0.0) * 100.0 for level in bins]
        majority = [difficulty[level].get("majority_vote", 0.0) * 100.0 for level in bins]
        x = list(range(len(bins)))
        ax.plot(x, ours, marker="o", label="ours")
        ax.plot(x, majority, marker="s", label="majority")
        ax.set_xticks(x, bins, rotation=20)
        ax.set_ylabel("Accuracy (%)")
        ax.set_title(panel.get("benchmark", "benchmark"))
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(_ensure_parent(output_path))
    plt.close(fig)
    return "plot"


def maybe_plot_wealth(payload: dict[str, Any], output_path: str | Path) -> str:
    plt = _matplotlib()
    if plt is None:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    traces = payload.get("traces", [])
    if not traces:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for trace in traces[:10]:
        wealth = trace.get("wealth", [])
        if not wealth:
            continue
        x = list(range(1, len(wealth) + 1))
        label = f"{trace.get('problem_id')}::{trace.get('candidate_id')}"
        ax.plot(x, wealth, marker="o", alpha=0.7, label=label)
    ax.axhline(payload.get("threshold", 20.0), linestyle="--", color="black", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_xlabel("Falsification round")
    ax.set_ylabel("Wealth")
    ax.set_title(payload.get("title", "Wealth Process"))
    if len(traces) <= 6:
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(_ensure_parent(output_path))
    plt.close(fig)
    return "plot"


def maybe_plot_selective_prediction(payload: dict[str, Any], output_path: str | Path) -> str:
    plt = _matplotlib()
    if plt is None:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    panels = payload.get("panels", [])
    if not panels:
        save_plot_payload(payload, Path(output_path).with_suffix(".json"))
        return "json"

    fig, axes = plt.subplots(1, len(panels), figsize=(5.5 * max(1, len(panels)), 3.5), squeeze=False)
    for ax, panel in zip(axes[0], panels):
        dynamic_series = panel.get("series", [])
        if dynamic_series:
            marker_map = {
                "falsification": "o",
                "s_star": "P",
                "code_t": "v",
                "generated_test_filter": "d",
                "majority_vote": "s",
                "self_debug": "^",
                "greedy": "x",
            }
            label_map = {
                "falsification": "ours",
                "s_star": "S* proxy",
                "code_t": "CodeT proxy",
                "generated_test_filter": "generated-test filter",
                "majority_vote": "majority",
                "self_debug": "self-debug",
                "greedy": "greedy",
            }
            for item in dynamic_series:
                curve = item.get("curve", [])
                method = item.get("method", "method")
                if not curve:
                    continue
                ax.plot(
                    [entry.get("coverage", 0.0) for entry in curve],
                    [entry.get("accuracy", 0.0) for entry in curve],
                    marker=marker_map.get(method, "o"),
                    label=label_map.get(method, method),
                )
        else:
            for key, label, marker in [
                ("ours", "ours", "o"),
                ("majority_vote", "majority", "s"),
                ("self_debug", "self-debug", "^"),
            ]:
                curve = panel.get(key, [])
                if not curve:
                    continue
                ax.plot(
                    [item.get("coverage", 0.0) for item in curve],
                    [item.get("accuracy", 0.0) for item in curve],
                    marker=marker,
                    label=label,
                )
        ax.set_title(panel.get("benchmark", "benchmark"))
        ax.set_xlabel("Coverage")
        ax.set_ylabel("Selective accuracy")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(_ensure_parent(output_path))
    plt.close(fig)
    return "plot"
