"""Small IO helpers with optional YAML support."""

from __future__ import annotations

import json
import pickle
import re
import sys
from base64 import b64encode
from pathlib import Path
from typing import Any


try:
    # EvalPlus can surface giant integer outputs that exceed Python 3.11+'s
    # conservative string-conversion guard during json.dumps.
    sys.set_int_max_str_digits(0)
except AttributeError:
    pass


def load_config(path: str | Path) -> Any:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore

            return yaml.safe_load(text)
        except ModuleNotFoundError:
            return json.loads(text)
    raise ValueError(f"Unsupported config format: {file_path}")


def normalize_python_value(value: Any) -> Any:
    if isinstance(value, dict):
        if all(isinstance(key, (str, int, float, bool)) or key is None for key in value):
            return {key: normalize_python_value(item) for key, item in value.items()}
        return {
            "__dict_items__": [
                {"key": normalize_python_value(key), "value": normalize_python_value(item)}
                for key, item in value.items()
            ]
        }
    if isinstance(value, list):
        return [normalize_python_value(item) for item in value]
    if isinstance(value, tuple):
        return {"__tuple__": [normalize_python_value(item) for item in value]}
    if isinstance(value, set):
        normalized = [normalize_python_value(item) for item in value]
        return {"__set__": sorted(normalized, key=repr)}
    if isinstance(value, complex):
        return {"__complex__": [value.real, value.imag]}
    if isinstance(value, bytes):
        return {"__bytes__": b64encode(value).decode("ascii")}
    if isinstance(value, re.Match):
        return {
            "__re_match__": {
                "group0": value.group(0),
                "groups": [normalize_python_value(item) for item in value.groups()],
                "groupdict": {key: normalize_python_value(item) for key, item in value.groupdict().items()},
                "span": [value.span()[0], value.span()[1]],
                "pattern": value.re.pattern,
                "string": value.string,
            }
        }
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return {"__python_object__": {"type": type(value).__name__, "repr": repr(value)}}


def dump_pickle(data: Any, path: str | Path) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("wb") as handle:
        pickle.dump(data, handle)


def load_pickle(path: str | Path) -> Any:
    file_path = Path(path)
    with file_path.open("rb") as handle:
        return pickle.load(handle)


def dump_json(data: Any, path: str | Path) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(normalize_python_value(data), indent=2, sort_keys=True), encoding="utf-8")
