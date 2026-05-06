"""Helpers for loading, expanding, and filtering experiment configs."""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

from utils.io import load_config


def sanitize_for_name(value: Any) -> str:
    text = str(value)
    return text.replace("/", "_").replace(" ", "").replace(".", "p")


def expand_experiment_grid(experiment: dict[str, Any]) -> list[dict[str, Any]]:
    grid = experiment.get("grid")
    if not grid:
        return [dict(experiment)]

    keys = list(grid.keys())
    values_product = itertools.product(*(grid[key] for key in keys))
    expanded: list[dict[str, Any]] = []
    base_name = experiment.get("name", "unnamed")
    for combo in values_product:
        variant = dict(experiment)
        variant.pop("grid", None)
        sweep_values = dict(zip(keys, combo))
        variant.update(sweep_values)
        variant["sweep_values"] = sweep_values
        suffix = "__".join(f"{key}={sanitize_for_name(value)}" for key, value in sweep_values.items())
        variant["name"] = f"{base_name}__{suffix}"
        variant["expanded_from"] = base_name
        expanded.append(variant)
    return expanded


def load_expanded_experiments(config_path: str | Path) -> list[dict[str, Any]]:
    config = load_config(config_path)
    expanded: list[dict[str, Any]] = []
    for experiment in config.get("experiments", []):
        expanded.extend(expand_experiment_grid(experiment))
    return expanded


def filter_experiments(
    experiments: list[dict[str, Any]],
    names: list[str] | None = None,
    prefixes: list[str] | None = None,
) -> list[dict[str, Any]]:
    names = [item for item in (names or []) if item]
    prefixes = [item for item in (prefixes or []) if item]
    if not names and not prefixes:
        return experiments

    selected: list[dict[str, Any]] = []
    for experiment in experiments:
        experiment_name = str(experiment.get("name", ""))
        expanded_from = str(experiment.get("expanded_from", experiment_name))
        if experiment_name in names or expanded_from in names:
            selected.append(experiment)
            continue
        if any(experiment_name.startswith(prefix) or expanded_from.startswith(prefix) for prefix in prefixes):
            selected.append(experiment)
    return selected

