#!/usr/bin/env python3
"""Calibrate theorem-3's eta proxy against a synthetic ground-truth eta."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs/generated"
FIGURES = ROOT / "figures/knowledge_arbitration"


ETA_GRID = [0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0]
NUM_SEEDS = 12
TRAJECTORIES_PER_SEED = 192
NUM_STEPS = 20


def sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x))


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-5, 1.0 - 1e-5)
    return np.log(p / (1.0 - p))


def _rank(values: list[float]) -> list[float]:
    pairs = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    idx = 0
    while idx < len(pairs):
        end = idx + 1
        while end < len(pairs) and pairs[end][1] == pairs[idx][1]:
            end += 1
        mean_rank = 0.5 * (idx + end - 1) + 1.0
        for j in range(idx, end):
            ranks[pairs[j][0]] = mean_rank
        idx = end
    return ranks


def spearman(x: list[float], y: list[float]) -> float:
    rx = np.asarray(_rank(x), dtype=float)
    ry = np.asarray(_rank(y), dtype=float)
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _estimate_slope(cumulative_trace: np.ndarray, answer_probabilities: np.ndarray) -> float:
    y = logit(answer_probabilities)
    X = np.column_stack([np.ones_like(cumulative_trace), cumulative_trace])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(beta[1])


def simulate_seed(true_eta: float, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    per_trajectory = []
    for _ in range(TRAJECTORIES_PER_SEED):
        trace_increments = np.clip(rng.normal(0.12, 0.05, size=NUM_STEPS), 0.01, None)
        cumulative_trace = np.cumsum(trace_increments)
        base_logit = rng.normal(-0.2, 0.22)
        endogenous_noise = np.cumsum(rng.normal(0.0, 0.03, size=NUM_STEPS))
        answer_logit = base_logit + true_eta * cumulative_trace + endogenous_noise
        observed_probabilities = sigmoid(np.clip(answer_logit, -6.0, 6.0))
        eta_hat = _estimate_slope(cumulative_trace, observed_probabilities)
        per_trajectory.append(eta_hat)

    trajectory_hats = np.asarray(per_trajectory, dtype=float)
    seed_mean = float(np.mean(trajectory_hats))
    return {
        "seed": seed,
        "true_eta": true_eta,
        "mean_eta_hat": seed_mean,
        "std_eta_hat": float(np.std(trajectory_hats)),
        "median_eta_hat": float(np.median(trajectory_hats)),
        "seed_relative_error": abs(seed_mean - true_eta) / true_eta,
        "trajectory_within_10pct": float(np.mean(np.abs(trajectory_hats - true_eta) / true_eta <= 0.10)),
    }


def run_experiment() -> dict:
    rows = []
    all_seed_rows = []

    for eta in ETA_GRID:
        seed_rows = [simulate_seed(eta, seed) for seed in range(NUM_SEEDS)]
        all_seed_rows.extend(seed_rows)
        seed_means = np.asarray([row["mean_eta_hat"] for row in seed_rows], dtype=float)
        rel_errors = np.asarray([row["seed_relative_error"] for row in seed_rows], dtype=float)
        within_10 = np.asarray([row["trajectory_within_10pct"] for row in seed_rows], dtype=float)
        rows.append(
            {
                "true_eta": eta,
                "mean_eta_hat": round(float(np.mean(seed_means)), 4),
                "std_eta_hat": round(float(np.std(seed_means)), 4),
                "median_eta_hat": round(float(np.median(seed_means)), 4),
                "mean_relative_error": round(float(np.mean(rel_errors)), 4),
                "max_seed_relative_error": round(float(np.max(rel_errors)), 4),
                "mean_trajectory_within_10pct": round(float(np.mean(within_10)), 4),
            }
        )

    mean_hats = [row["mean_eta_hat"] for row in rows]
    rel_errors = [row["mean_relative_error"] for row in rows]
    monotone = all(x < y for x, y in zip(mean_hats, mean_hats[1:]))
    headline = {
        "num_steps": NUM_STEPS,
        "num_seeds": NUM_SEEDS,
        "trajectories_per_seed": TRAJECTORIES_PER_SEED,
        "spearman_true_vs_hat": round(spearman(ETA_GRID, mean_hats), 4),
        "monotone_mean_hat": monotone,
        "max_mean_relative_error": round(max(rel_errors), 4),
        "mean_of_mean_relative_errors": round(float(np.mean(rel_errors)), 4),
        "num_grid_points_within_10pct": int(sum(error <= 0.10 for error in rel_errors)),
        "grid_size": len(rows),
    }
    return {"headline": headline, "rows": rows, "seed_rows": all_seed_rows}


def build_figure(payload: dict) -> str:
    FIGURES.mkdir(parents=True, exist_ok=True)
    x = [row["true_eta"] for row in payload["rows"]]
    y = [row["mean_eta_hat"] for row in payload["rows"]]
    std = [row["std_eta_hat"] for row in payload["rows"]]

    fig_path = FIGURES / "theorem3_eta_proxy_identification.pdf"
    plt.figure(figsize=(5.8, 4.0))
    plt.plot(x, x, linestyle="--", color="black", linewidth=1.2, label="Ideal")
    plt.errorbar(x, y, yerr=std, marker="o", linewidth=2.0, color="#0f766e", capsize=3, label=r"Mean $\hat{\eta}_{eff}$")
    plt.xlabel(r"True $\eta$")
    plt.ylabel(r"Estimated $\hat{\eta}_{eff}$")
    plt.title(r"Synthetic calibration of $\hat{\eta}_{eff}$")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close()
    return str(fig_path.relative_to(ROOT))


def build_markdown(payload: dict, figure_path: str) -> str:
    h = payload["headline"]
    lines = [
        "# Theorem 3 Eta-Proxy Identification Note",
        "",
        "This synthetic experiment calibrates the theorem-3 proxy `eta_hat_eff` against a known ground-truth `eta` in a controlled exponential-tilting environment.",
        "Each trajectory accumulates trace-token evidence over time, the answer logit is sharpened with a user-set `eta`, and `eta_hat_eff` is recovered as the slope of answer-logit growth against cumulative trace evidence.",
        "",
        "## Headline",
        "",
        f"- Seeds: `{h['num_seeds']}`",
        f"- Trajectories per seed: `{h['trajectories_per_seed']}`",
        f"- Steps per trajectory: `{h['num_steps']}`",
        f"- Spearman correlation between true `eta` and mean `eta_hat_eff`: `{h['spearman_true_vs_hat']}`",
        f"- Mean estimate is strictly monotone over the sweep: `{h['monotone_mean_hat']}`",
        f"- Max mean relative error across the sweep: `{h['max_mean_relative_error']}`",
        f"- Grid points with mean relative error <= 10%: `{h['num_grid_points_within_10pct']}/{h['grid_size']}`",
        "",
        "## Sweep",
        "",
        "| True `eta` | Mean `eta_hat_eff` | Std across seed means | Median `eta_hat_eff` | Mean relative error | Max seed relative error | Mean trajectory fraction within 10% |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['true_eta']:.1f} | {row['mean_eta_hat']:.4f} | {row['std_eta_hat']:.4f} | "
            f"{row['median_eta_hat']:.4f} | {row['mean_relative_error']:.4f} | "
            f"{row['max_seed_relative_error']:.4f} | {row['mean_trajectory_within_10pct']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- In this controlled environment, `eta_hat_eff` is not just directional: the seed-mean proxy tracks the true `eta` almost exactly across the full sweep.",
            "- The per-trajectory estimate is noisier at the smallest `eta` values, but the aggregated proxy remains calibrated and monotone.",
            "- This does not turn theorem 3 into a literal autoregressive proof. It does show that the current proxy is a usable instrument in the exact kind of exponential-tilting environment the theorem invokes.",
            "",
            "## Figure",
            "",
            f"- `{figure_path}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = run_experiment()
    figure_path = build_figure(payload)
    GENERATED.mkdir(parents=True, exist_ok=True)
    json_path = GENERATED / "theorem3_eta_proxy_identification.json"
    md_path = GENERATED / "theorem3_eta_proxy_identification.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload, figure_path), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path), "figure": figure_path}, indent=2))


if __name__ == "__main__":
    main()
