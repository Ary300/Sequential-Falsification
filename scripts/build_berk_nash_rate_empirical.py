#!/usr/bin/env python3
"""Build an empirical Berk--Nash / tail-rate note from dense theorem-3 trajectories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs/generated"

EPS = 1e-8


def _clip01(value: Any, default: float = 0.5) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = default
    return min(max(numeric, 0.0), 1.0)


def _row_state(row: dict[str, Any]) -> np.ndarray:
    confidence = _clip01(row.get("confidence"), default=0.5)
    features = row.get("features") or {}
    matched_parametric = bool(features.get("matched_parametric_answer"))
    matched_context = bool(features.get("matched_context_answer"))

    if matched_parametric and matched_context:
        p_parametric = 0.5 * confidence
        p_context = 0.5 * confidence
    elif matched_parametric:
        p_parametric = confidence
        p_context = 0.0
    elif matched_context:
        p_parametric = 0.0
        p_context = confidence
    else:
        p_parametric = 0.0
        p_context = 0.0
    p_other = max(0.0, 1.0 - p_parametric - p_context)
    state = np.asarray([p_parametric, p_context, p_other], dtype=float)
    total = float(state.sum())
    if total <= 0.0:
        return np.asarray([0.0, 0.0, 1.0], dtype=float)
    return state / total


def _load_rows(path: Path, model_filter: str | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if model_filter and str(row.get("model")) != model_filter:
                continue
            rows.append(row)
    return rows


def _tv_distance(lhs: np.ndarray, rhs: np.ndarray) -> float:
    return 0.5 * float(np.abs(lhs - rhs).sum())


def _group_cell(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[int, list[dict[str, Any]]]]:
    grouped: dict[tuple[str, str], dict[int, list[dict[str, Any]]]] = {}
    for row in rows:
        benchmark = str(row.get("benchmark"))
        split = str(row.get("split") or row.get("condition"))
        cot_length = int(row.get("cot_length", 0))
        grouped.setdefault((benchmark, split), {}).setdefault(cot_length, []).append(row)
    return grouped


def _fit_local_jacobian(states: np.ndarray, tail_steps: np.ndarray) -> dict[str, Any]:
    if len(states) < 3:
        return {}
    x_star = states[-1, :2]
    X = states[:-1, :2] - x_star
    Y = states[1:, :2] - x_star
    if X.shape[0] < 2:
        return {}
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    jacobian = beta.T
    eigvals = np.linalg.eigvals(jacobian)
    spectral_radius = float(np.max(np.abs(eigvals)))
    return {
        "jacobian": [[round(float(value), 6) for value in row] for row in jacobian.tolist()],
        "eigenvalues": [[round(float(value.real), 6), round(float(value.imag), 6)] for value in eigvals],
        "spectral_radius": round(spectral_radius, 6),
    }


def _fit_exponential(tv_values: np.ndarray, steps: np.ndarray) -> dict[str, Any]:
    mask = tv_values > EPS
    if int(mask.sum()) < 3:
        return {}
    y = np.log(tv_values[mask])
    X = np.column_stack([np.ones(int(mask.sum())), steps[mask]])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    intercept, slope = [float(item) for item in beta]
    fitted = X @ beta
    ss_res = float(np.sum((y - fitted) ** 2))
    ss_tot = float(np.sum((y - float(y.mean())) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    rho_hat = float(np.exp(slope))
    return {
        "intercept": round(intercept, 6),
        "slope": round(slope, 6),
        "rho_star": round(rho_hat, 6),
        "r2_log_tv": round(r2, 6),
    }


def _fit_polynomial(tv_values: np.ndarray, steps: np.ndarray) -> dict[str, Any]:
    mask = tv_values > EPS
    if int(mask.sum()) < 3:
        return {}
    inv_tv = 1.0 / tv_values[mask]
    X = np.column_stack([steps[mask], np.ones(int(mask.sum()))])
    beta, *_ = np.linalg.lstsq(X, inv_tv, rcond=None)
    slope, intercept = [float(item) for item in beta]
    predicted_inv = X @ beta
    predicted_tv = 1.0 / np.clip(predicted_inv, 1e-6, None)
    actual_tv = tv_values[mask]
    ss_res = float(np.sum((actual_tv - predicted_tv) ** 2))
    ss_tot = float(np.sum((actual_tv - float(actual_tv.mean())) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    payload: dict[str, Any] = {
        "inverse_slope": round(slope, 6),
        "inverse_intercept": round(intercept, 6),
        "r2_tv": round(r2, 6),
    }
    if slope > EPS:
        c_value = 1.0 / slope
        q1_value = intercept / slope
        payload["C"] = round(float(c_value), 6)
        payload["q1"] = round(float(q1_value), 6)
    return payload


def _select_analysis_window(
    steps: np.ndarray,
    states: np.ndarray,
    tv_values: np.ndarray,
    *,
    analysis_mode: str,
    window_size: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if len(steps) <= window_size:
        return steps, states, tv_values
    if analysis_mode == "early":
        window_slice = slice(0, window_size)
    else:
        window_slice = slice(-window_size, None)
    return steps[window_slice], states[window_slice], tv_values[window_slice]


def _analyze_cell(
    benchmark: str,
    split: str,
    rows_by_cot: dict[int, list[dict[str, Any]]],
    *,
    analysis_mode: str,
    window_size: int,
) -> dict[str, Any]:
    steps = np.asarray(sorted(rows_by_cot), dtype=int)
    states = np.asarray(
        [
            np.mean([_row_state(row) for row in rows_by_cot[int(step)]], axis=0)
            for step in steps
        ],
        dtype=float,
    )
    final_state = states[-1]
    tv_values = np.asarray([_tv_distance(state, final_state) for state in states], dtype=float)
    window_steps, window_states, window_tv = _select_analysis_window(
        steps,
        states,
        tv_values,
        analysis_mode=analysis_mode,
        window_size=window_size,
    )

    jacobian = _fit_local_jacobian(window_states, window_steps)

    fit_steps = window_steps
    fit_tv = window_tv
    # In tail mode the final point is the fixed point itself, so its TV is exactly zero.
    if analysis_mode == "tail" and len(window_tv) > 1 and int(window_steps[-1]) == int(steps[-1]):
        fit_steps = window_steps[:-1]
        fit_tv = window_tv[:-1]

    exponential = _fit_exponential(fit_tv, fit_steps) if len(fit_tv) > 1 else {}
    polynomial = _fit_polynomial(fit_tv, fit_steps) if len(fit_tv) > 1 else {}

    return {
        "benchmark": benchmark,
        "split": split,
        "num_cot_points": int(len(steps)),
        "analysis_mode": analysis_mode,
        "analysis_window_target": int(window_size),
        "analysis_window_used": int(len(window_steps)),
        "analysis_steps": [int(step) for step in window_steps.tolist()],
        "analysis_start_cot": int(window_steps[0]),
        "analysis_end_cot": int(window_steps[-1]),
        "tail_window_used": int(len(window_steps)),
        "tail_steps": [int(step) for step in window_steps.tolist()],
        "mean_state_final": {
            "parametric": round(float(final_state[0]), 6),
            "context": round(float(final_state[1]), 6),
            "other": round(float(final_state[2]), 6),
        },
        "tv_to_final": [
            {"cot_length": int(step), "tv": round(float(tv), 6)}
            for step, tv in zip(steps.tolist(), tv_values.tolist())
        ],
        "local_jacobian": jacobian,
        "log_linear_crosscheck": exponential,
        "polynomial_tail_fit": polynomial,
    }


def build_payload(
    rows: list[dict[str, Any]],
    *,
    analysis_mode: str,
    window_size: int,
) -> dict[str, Any]:
    grouped = _group_cell(rows)
    cells = []
    for (benchmark, split), rows_by_cot in sorted(grouped.items()):
        if len(rows_by_cot) < 3:
            continue
        cells.append(
            _analyze_cell(
                benchmark,
                split,
                rows_by_cot,
                analysis_mode=analysis_mode,
                window_size=window_size,
            )
        )
    return {
        "headline": {
            "num_rows": len(rows),
            "num_cells": len(cells),
            "analysis_mode": analysis_mode,
            "window_size": window_size,
            "tail_window": window_size,
        },
        "cells": cells,
    }


def build_markdown(payload: dict[str, Any], *, source_path: Path, model_filter: str | None) -> str:
    headline = payload["headline"]
    analysis_mode = headline.get("analysis_mode", "tail")
    mode_label = "tail" if analysis_mode == "tail" else "early/non-asymptotic"
    lines = [
        "# Berk-Nash Rate Empirical Note",
        "",
        "This note computes the empirical Berk--Nash rate diagnostics requested for the theorem-3 appendix using dense CoT-budget trajectories.",
        "The state is the coarse answer-state simplex implied by each row: probability mass on the parametric answer state, the context-backed answer state, and residual mass on all other answers.",
        "",
        "## Source",
        "",
        f"- Rows JSONL: `{source_path}`",
        f"- Model filter: `{model_filter or 'none'}`",
        f"- Rows loaded: `{headline['num_rows']}`",
        f"- Cells analyzed: `{headline['num_cells']}`",
        f"- Analysis mode: `{analysis_mode}` ({mode_label})",
        f"- Analysis window target: `{headline['window_size']}`",
        "",
        "## Per-cell rates",
        "",
        "| Benchmark | Split | Window | Spectral radius | `rho*` from log-TV | log-TV R² | Polynomial TV R² | `q1` |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for cell in payload["cells"]:
        jac = cell.get("local_jacobian") or {}
        exp_fit = cell.get("log_linear_crosscheck") or {}
        poly_fit = cell.get("polynomial_tail_fit") or {}
        window_label = f"{cell['analysis_start_cot']}→{cell['analysis_end_cot']} ({cell['analysis_window_used']})"
        lines.append(
            f"| {cell['benchmark']} | {cell['split']} | {window_label} | "
            f"{jac.get('spectral_radius', 'NA')} | {exp_fit.get('rho_star', 'NA')} | "
            f"{exp_fit.get('r2_log_tv', 'NA')} | {poly_fit.get('r2_tv', 'NA')} | {poly_fit.get('q1', 'NA')} |"
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- `Spectral radius` comes from a least-squares local Jacobian fit on the selected analysis window.",
            "- `rho* from log-TV` is the cross-check implied by fitting `log TV(p_t, p_K)` linearly in `t` on the same window.",
            "- The polynomial fit reports the `C / (q1 + t)` approximation from the inverse-TV regression; higher TV-space `R²` means the slow-tail story is quantitatively more plausible on that window.",
            "- In `tail` mode, the script uses the last `W` CoT-budget steps and drops the exact fixed-point endpoint from the log-TV and polynomial fits.",
            "- In `early` mode, the script uses the first `W` CoT-budget steps so the same diagnostics can be evaluated before the tail regime.",
            "- If a cell has fewer than `W` dense steps, the script uses the full available window and reports that directly.",
            "",
            "## JSON",
            "",
            "- `docs/generated/berk_nash_rate_empirical.json`",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build empirical Berk-Nash tail-rate diagnostics.")
    parser.add_argument("--rows-jsonl", required=True)
    parser.add_argument("--model", default="")
    parser.add_argument("--analysis-mode", choices=("tail", "early"), default="tail")
    parser.add_argument("--tail-window", type=int, default=100)
    parser.add_argument("--window-size", type=int, default=None)
    parser.add_argument("--json-out", default=str(GENERATED / "berk_nash_rate_empirical.json"))
    parser.add_argument("--md-out", default=str(GENERATED / "berk_nash_rate_empirical.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows_path = Path(args.rows_jsonl)
    rows = _load_rows(rows_path, args.model or None)
    window_size = args.window_size if args.window_size is not None else args.tail_window
    payload = build_payload(rows, analysis_mode=args.analysis_mode, window_size=window_size)

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_out.write_text(build_markdown(payload, source_path=rows_path, model_filter=args.model or None), encoding="utf-8")
    print(json.dumps({"json": str(json_out), "md": str(md_out), "cells": payload["headline"]["num_cells"]}, indent=2))


if __name__ == "__main__":
    main()
