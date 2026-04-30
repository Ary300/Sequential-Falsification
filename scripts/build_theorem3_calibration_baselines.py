#!/usr/bin/env python3
"""Compare eta-tempering against standard post-hoc calibration baselines."""

from __future__ import annotations

import argparse
import json
from math import log
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402
from utils.metrics import accuracy, brier_score, expected_calibration_error, roc_auc_binary  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 calibration baseline comparisons.")
    parser.add_argument("--rows-jsonl", default="results/theorem3_real_generation_r1_14b_v3/theorem3_generation_rows.jsonl")
    parser.add_argument("--eta-result-json", default="docs/generated/theorem3_eta_tempered_method_result.json")
    parser.add_argument("--output-prefix", default="docs/generated/theorem3_calibration_baselines")
    parser.add_argument("--benchmark", default="conflictbank")
    parser.add_argument("--condition", default="conflict_context")
    parser.add_argument("--cot-length", type=int, default=1024)
    parser.add_argument("--calibration-size", type=int, default=200)
    return parser.parse_args()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _clip(prob: float) -> float:
    return min(max(float(prob), 1e-6), 1.0 - 1e-6)


def _logit(prob: float) -> float:
    p = _clip(prob)
    return log(p / (1.0 - p))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = pow(2.718281828459045, -value)
        return 1.0 / (1.0 + z)
    z = pow(2.718281828459045, value)
    return z / (1.0 + z)


def _metrics(confidences: list[float], outcomes: list[int]) -> dict[str, float]:
    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0
    mean_acc = accuracy(bool(item) for item in outcomes)
    return {
        "count": len(confidences),
        "accuracy": round(mean_acc, 6),
        "ece": round(expected_calibration_error(confidences, outcomes), 6),
        "brier": round(brier_score(confidences, outcomes), 6),
        "auroc": round(roc_auc_binary(confidences, outcomes), 6),
        "mean_confidence": round(mean_conf, 6),
        "overconfidence_gap": round(mean_conf - mean_acc, 6),
    }


def _fit_temperature(cal_conf: list[float], cal_outcomes: list[int]) -> float:
    best_t = 1.0
    best_brier = float("inf")
    for idx in range(5, 501):
        temperature = idx / 100.0
        scaled = [_sigmoid(_logit(conf) / temperature) for conf in cal_conf]
        score = brier_score(scaled, cal_outcomes)
        if score < best_brier:
            best_brier = score
            best_t = temperature
    return best_t


def _fit_platt(cal_conf: list[float], cal_outcomes: list[int]) -> tuple[float, float]:
    try:
        from sklearn.linear_model import LogisticRegression
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"scikit-learn required for Platt scaling: {exc}")

    x = [[_logit(conf)] for conf in cal_conf]
    model = LogisticRegression(random_state=0, max_iter=1000).fit(x, cal_outcomes)
    return float(model.coef_[0][0]), float(model.intercept_[0])


def _fit_isotonic(cal_conf: list[float], cal_outcomes: list[int]):
    try:
        from sklearn.isotonic import IsotonicRegression
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"scikit-learn required for isotonic scaling: {exc}")

    model = IsotonicRegression(out_of_bounds="clip")
    model.fit(cal_conf, cal_outcomes)
    return model


def _build_payload(rows: list[dict[str, Any]], eta_payload: dict[str, Any], *, benchmark: str, condition: str, cot_length: int, calibration_size: int) -> dict[str, Any]:
    target_rows = [
        row
        for row in rows
        if str(row.get("benchmark")) == benchmark
        and str(row.get("condition")) == condition
        and int(row.get("cot_length", 0)) == cot_length
    ]
    target_rows.sort(key=lambda row: str(row.get("id")))
    calibration_rows = target_rows[:calibration_size]
    eval_rows = target_rows[calibration_size:]
    if not calibration_rows or not eval_rows:
        raise SystemExit("Need non-empty calibration and eval splits for theorem-3 calibration baselines.")

    cal_conf = [float(row.get("confidence", 0.5)) for row in calibration_rows]
    cal_outcomes = [int(row.get("outcome", 0)) for row in calibration_rows]
    eval_conf = [float(row.get("confidence", 0.5)) for row in eval_rows]
    eval_outcomes = [int(row.get("outcome", 0)) for row in eval_rows]

    temperature = _fit_temperature(cal_conf, cal_outcomes)
    platt_weight, platt_bias = _fit_platt(cal_conf, cal_outcomes)
    isotonic = _fit_isotonic(cal_conf, cal_outcomes)

    per_method = []

    identity_eval = eval_conf
    per_method.append({"method": "identity", "eval": _metrics(identity_eval, eval_outcomes)})

    temp_eval = [_sigmoid(_logit(conf) / temperature) for conf in eval_conf]
    per_method.append(
        {
            "method": "temperature_scaling",
            "temperature": round(temperature, 6),
            "eval": _metrics(temp_eval, eval_outcomes),
        }
    )

    platt_eval = [_sigmoid((platt_weight * _logit(conf)) + platt_bias) for conf in eval_conf]
    per_method.append(
        {
            "method": "platt_scaling",
            "weight": round(platt_weight, 6),
            "bias": round(platt_bias, 6),
            "eval": _metrics(platt_eval, eval_outcomes),
        }
    )

    isotonic_eval = [float(item) for item in isotonic.predict(eval_conf)]
    per_method.append({"method": "isotonic", "eval": _metrics(isotonic_eval, eval_outcomes)})

    eta_summary = {
        "method": "eta_tempering",
        "selected_eta": eta_payload.get("selection", {}).get("selected_eta"),
        "eval": (
            eta_payload.get("evaluation", {}).get("selected")
            or eta_payload.get("eval_selected")
            or {}
        ),
    }
    per_method.append(eta_summary)

    best_by_brier = min(
        (entry for entry in per_method if entry.get("eval")),
        key=lambda entry: float(entry["eval"].get("brier", 1e9)),
    )

    return {
        "metadata": {
            "benchmark": benchmark,
            "condition": condition,
            "cot_length": cot_length,
            "calibration_size": calibration_size,
            "num_target_rows": len(target_rows),
            "num_eval_rows": len(eval_rows),
        },
        "methods": per_method,
        "headline": {
            "best_brier_method": best_by_brier["method"],
            "eta_brier": eta_summary["eval"].get("brier"),
            "identity_brier": per_method[0]["eval"].get("brier"),
            "temperature_brier": per_method[1]["eval"].get("brier"),
            "platt_brier": per_method[2]["eval"].get("brier"),
            "isotonic_brier": per_method[3]["eval"].get("brier"),
        },
    }


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Theorem 3 Calibration Baselines",
        "",
        "This note compares eta-tempering against standard post-hoc confidence calibration baselines on the headline theorem-3 slice.",
        "",
        "## Setup",
        "",
        f"- Benchmark / condition / CoT: `{payload['metadata']['benchmark']}` / `{payload['metadata']['condition']}` / `cot={payload['metadata']['cot_length']}`",
        f"- Calibration rows: `{payload['metadata']['calibration_size']}`",
        f"- Eval rows: `{payload['metadata']['num_eval_rows']}`",
        "",
        "## Methods",
        "",
        "| Method | Accuracy | ECE | Brier | AUROC | Mean conf | Gap |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for entry in payload["methods"]:
        metrics = entry.get("eval", {})
        lines.append(
            f"| {entry['method']} | {metrics.get('accuracy', 'n/a')} | {metrics.get('ece', 'n/a')} | "
            f"{metrics.get('brier', 'n/a')} | {metrics.get('auroc', 'n/a')} | "
            f"{metrics.get('mean_confidence', 'n/a')} | {metrics.get('overconfidence_gap', 'n/a')} |"
        )
    lines.extend(
        [
            "",
            "## Headline",
            "",
            f"- Best Brier method: `{payload['headline']['best_brier_method']}`",
            f"- Identity vs eta Brier: `{payload['headline']['identity_brier']}` -> `{payload['headline']['eta_brier']}`",
            f"- Temperature / Platt / Isotonic Brier: `{payload['headline']['temperature_brier']}` / `{payload['headline']['platt_brier']}` / `{payload['headline']['isotonic_brier']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rows = _load_rows(ROOT / args.rows_jsonl)
    eta_payload = json.loads((ROOT / args.eta_result_json).read_text(encoding="utf-8"))
    payload = _build_payload(
        rows,
        eta_payload,
        benchmark=args.benchmark,
        condition=args.condition,
        cot_length=args.cot_length,
        calibration_size=args.calibration_size,
    )
    output_prefix = ROOT / args.output_prefix
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, output_prefix.with_suffix(".json"))
    output_prefix.with_suffix(".md").write_text(_build_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_prefix": str(output_prefix), "headline": payload["headline"]}, indent=2))


if __name__ == "__main__":
    main()
