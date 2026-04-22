"""Metrics used by the evaluation pipeline."""

from __future__ import annotations

from math import comb
from statistics import mean
from typing import Iterable
import random


def accuracy(results: Iterable[bool]) -> float:
    values = [1.0 if x else 0.0 for x in results]
    return mean(values) if values else 0.0


def pass_at_k(num_samples: int, num_correct: int, k: int) -> float:
    if num_correct <= 0:
        return 0.0
    if num_samples - num_correct < k:
        return 1.0
    return 1.0 - comb(num_samples - num_correct, k) / comb(num_samples, k)


def expected_calibration_error(confidences: list[float], outcomes: list[int], n_bins: int = 10) -> float:
    if not confidences:
        return 0.0
    bins = [[] for _ in range(n_bins)]
    for conf, outcome in zip(confidences, outcomes):
        idx = min(n_bins - 1, max(0, int(conf * n_bins)))
        bins[idx].append((conf, outcome))
    total = len(confidences)
    ece = 0.0
    for bucket in bins:
        if not bucket:
            continue
        avg_conf = sum(c for c, _ in bucket) / len(bucket)
        avg_acc = sum(o for _, o in bucket) / len(bucket)
        ece += (len(bucket) / total) * abs(avg_conf - avg_acc)
    return ece


def maximum_calibration_error(confidences: list[float], outcomes: list[int], n_bins: int = 10) -> float:
    bins = [[] for _ in range(n_bins)]
    for conf, outcome in zip(confidences, outcomes):
        idx = min(n_bins - 1, max(0, int(conf * n_bins)))
        bins[idx].append((conf, outcome))
    errors = []
    for bucket in bins:
        if not bucket:
            continue
        avg_conf = sum(c for c, _ in bucket) / len(bucket)
        avg_acc = sum(o for _, o in bucket) / len(bucket)
        errors.append(abs(avg_conf - avg_acc))
    return max(errors) if errors else 0.0


def brier_score(confidences: list[float], outcomes: list[int]) -> float:
    if not confidences:
        return 0.0
    return sum((c - o) ** 2 for c, o in zip(confidences, outcomes)) / len(confidences)


def standard_error(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    avg = sum(values) / len(values)
    variance = sum((x - avg) ** 2 for x in values) / (len(values) - 1)
    return (variance ** 0.5) / (len(values) ** 0.5)


def bootstrap_confidence_interval(
    values: list[float],
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    samples = []
    for _ in range(n_resamples):
        draw = [values[rng.randrange(len(values))] for _ in range(len(values))]
        samples.append(sum(draw) / len(draw))
    samples.sort()
    lo_idx = max(0, int((alpha / 2) * len(samples)) - 1)
    hi_idx = min(len(samples) - 1, int((1 - alpha / 2) * len(samples)) - 1)
    return samples[lo_idx], samples[hi_idx]


def calibration_bins(confidences: list[float], outcomes: list[int], n_bins: int = 10) -> list[dict[str, float]]:
    bins = [[] for _ in range(n_bins)]
    for conf, outcome in zip(confidences, outcomes):
        idx = min(n_bins - 1, max(0, int(conf * n_bins)))
        bins[idx].append((conf, outcome))
    payload = []
    for idx, bucket in enumerate(bins):
        if bucket:
            avg_conf = sum(c for c, _ in bucket) / len(bucket)
            avg_acc = sum(o for _, o in bucket) / len(bucket)
            count = len(bucket)
        else:
            avg_conf = (idx + 0.5) / n_bins
            avg_acc = 0.0
            count = 0
        payload.append({"bin": idx, "avg_confidence": avg_conf, "avg_accuracy": avg_acc, "count": count})
    return payload


def selective_prediction_curve(
    confidences: list[float],
    outcomes: list[int],
    thresholds: list[float] | None = None,
) -> list[dict[str, float]]:
    if thresholds is None:
        thresholds = [i / 10 for i in range(11)]
    curve: list[dict[str, float]] = []
    total = len(confidences)
    for threshold in thresholds:
        kept = [(conf, outcome) for conf, outcome in zip(confidences, outcomes) if conf >= threshold]
        coverage = (len(kept) / total) if total else 0.0
        selective_accuracy = (sum(outcome for _, outcome in kept) / len(kept)) if kept else 0.0
        curve.append(
            {
                "threshold": float(threshold),
                "coverage": coverage,
                "accuracy": selective_accuracy,
                "count": len(kept),
            }
        )
    return curve


def roc_auc_binary(scores: list[float], labels: list[int]) -> float:
    positives = [(score, label) for score, label in zip(scores, labels) if label == 1]
    negatives = [(score, label) for score, label in zip(scores, labels) if label == 0]
    if not positives or not negatives:
        return 0.0
    ranked = sorted(zip(scores, labels), key=lambda item: item[0])
    rank_sum = 0.0
    for idx, (_, label) in enumerate(ranked, start=1):
        if label == 1:
            rank_sum += idx
    n_pos = len(positives)
    n_neg = len(negatives)
    return (rank_sum - (n_pos * (n_pos + 1) / 2)) / (n_pos * n_neg)
