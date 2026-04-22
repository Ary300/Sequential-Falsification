"""Benchmark loading utilities with optional local and Hugging Face support."""

from __future__ import annotations

import re
import json
import pickle
import textwrap
import base64
import urllib.request
import zlib
from pathlib import Path
from typing import Any

try:
    from utils.io import load_pickle, normalize_python_value
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from .io import load_pickle, normalize_python_value


def _synthetic_demo() -> list[dict[str, Any]]:
    return [
        {
            "id": "sum_two",
            "benchmark": "synthetic_demo",
            "type": "code",
            "prompt": "Write a Python function solve(a, b) that returns the sum of two integers.",
            "entry_point": "solve",
            "reference_solution": "def solve(a, b):\n    return a + b\n",
            "public_tests": [
                {"input": [1, 2], "output": 3},
                {"input": [0, 0], "output": 0},
            ],
            "hidden_tests": [
                {"input": [-1, 5], "output": 4},
                {"input": [10, -4], "output": 6},
            ],
            "difficulty": "easy",
        },
        {
            "id": "factorial_small",
            "benchmark": "synthetic_demo",
            "type": "code",
            "prompt": "Write a Python function solve(n) that returns n! for n >= 0.",
            "entry_point": "solve",
            "reference_solution": (
                "def solve(n):\n"
                "    out = 1\n"
                "    for i in range(2, n + 1):\n"
                "        out *= i\n"
                "    return out\n"
            ),
            "public_tests": [
                {"input": [0], "output": 1},
                {"input": [4], "output": 24},
            ],
            "hidden_tests": [
                {"input": [1], "output": 1},
                {"input": [5], "output": 120},
            ],
            "difficulty": "medium",
        },
        {
            "id": "math_boxed",
            "benchmark": "synthetic_demo",
            "type": "math",
            "prompt": "Compute the value of 7 * 8 and give only the final answer.",
            "reference_answer": "56",
            "public_tests": [],
            "hidden_tests": [],
            "difficulty": "easy",
        },
    ]


def _load_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    def _restore_json_types(value: Any) -> Any:
        if isinstance(value, list):
            return [_restore_json_types(item) for item in value]
        if isinstance(value, dict):
            if set(value.keys()) == {"__dict_items__"}:
                return {
                    _restore_json_types(item["key"]): _restore_json_types(item["value"])
                    for item in value["__dict_items__"]
                }
            if set(value.keys()) == {"__tuple__"}:
                return tuple(_restore_json_types(item) for item in value["__tuple__"])
            if set(value.keys()) == {"__set__"}:
                return set(_restore_json_types(item) for item in value["__set__"])
            if set(value.keys()) == {"__complex__"}:
                real, imag = value["__complex__"]
                return complex(real, imag)
            if set(value.keys()) == {"__re_match__"}:
                return value
            if set(value.keys()) == {"__python_object__"}:
                return value
            return {key: _restore_json_types(item) for key, item in value.items()}
        return value

    if path.suffix == ".jsonl":
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(_restore_json_types(json.loads(line)))
        return rows
    data = _restore_json_types(json.loads(path.read_text(encoding="utf-8")))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "problems" in data:
        return data["problems"]
    raise ValueError(f"Unsupported data format in {path}")


def _normalize_test_item(test_item: Any) -> dict[str, Any]:
    if isinstance(test_item, dict):
        normalized = {
            "input": test_item.get("input", test_item.get("inputs", [])),
            "output": test_item.get("output", test_item.get("expected_output")),
        }
        if "testtype" in test_item:
            normalized["testtype"] = test_item["testtype"]
        elif isinstance(normalized["input"], str) and isinstance(normalized["output"], str):
            normalized["testtype"] = "stdin"
        return normalized
    return {"input": test_item, "output": None}


def _decode_livecodebench_tests(value: Any) -> list[dict[str, Any]]:
    if not value:
        return []
    if isinstance(value, list):
        raw_tests = value
    elif isinstance(value, str):
        try:
            raw_tests = json.loads(value)
        except json.JSONDecodeError:
            try:
                payload = zlib.decompress(base64.b64decode(value))
                restored = pickle.loads(payload)
                raw_tests = json.loads(restored) if isinstance(restored, str) else restored
            except Exception:
                return []
    else:
        return []

    tests = []
    for item in raw_tests:
        if not isinstance(item, dict):
            continue
        tests.append(
            {
                "input": item.get("input", ""),
                "output": item.get("output", ""),
                "testtype": item.get("testtype", "stdin"),
            }
        )
    return tests


def _decode_codecontests_tests(value: Any) -> list[dict[str, Any]]:
    """Normalize CodeContests-style test dictionaries to stdin tests."""

    if not value:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []

    if isinstance(value, dict):
        inputs = value.get("input", value.get("inputs", []))
        outputs = value.get("output", value.get("outputs", []))
        if isinstance(inputs, str):
            inputs = [inputs]
        if isinstance(outputs, str):
            outputs = [outputs]
        tests = []
        for test_input, expected_output in zip(inputs or [], outputs or []):
            tests.append(
                {
                    "input": str(test_input),
                    "output": str(expected_output),
                    "testtype": "stdin",
                }
            )
        return tests

    if isinstance(value, list):
        tests = []
        for item in value:
            if isinstance(item, dict):
                tests.append(
                    {
                        "input": str(item.get("input", item.get("stdin", ""))),
                        "output": str(item.get("output", item.get("stdout", item.get("expected_output", "")))),
                        "testtype": "stdin",
                    }
                )
        return tests

    return []


def _extract_boxed_answer(solution: str) -> str:
    text = (solution or "").strip()
    marker = "\\boxed{"
    start = text.rfind(marker)
    if start != -1:
        index = start + len(marker)
        depth = 1
        pieces: list[str] = []
        while index < len(text) and depth > 0:
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    break
            if depth > 0:
                pieces.append(char)
            index += 1
        answer = "".join(pieces).strip()
        if answer:
            return answer

    fallback_patterns = [
        r"####\s*([^\n]+)",
        r"answer\s+is\s+([^\n\.]+)",
        r"therefore[, ]+([^\n\.]+)$",
    ]
    for pattern in fallback_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            answer = match.group(1).strip().strip(".")
            if answer:
                return answer
    return text


def _build_math500_rows_from_eleutherai(load_dataset: Any) -> list[dict[str, Any]]:
    configs = [
        "algebra",
        "counting_and_probability",
        "geometry",
        "intermediate_algebra",
        "number_theory",
        "prealgebra",
        "precalculus",
    ]
    per_level_target = 100
    buckets: dict[str, list[dict[str, Any]]] = {f"level {level}": [] for level in range(1, 6)}
    leftovers: list[dict[str, Any]] = []

    for config in configs:
        dataset = load_dataset("EleutherAI/hendrycks_math", config, split="test")
        for row in dataset:
            difficulty = str(row.get("level", "unknown")).strip().lower()
            normalized = {
                "id": f"math500_{config}_{len(leftovers) + sum(len(items) for items in buckets.values())}",
                "type": "math",
                "prompt": row.get("problem", ""),
                "reference_answer": _extract_boxed_answer(row.get("solution", "")),
                "difficulty": difficulty,
                "subject": row.get("type", config),
            }
            if difficulty in buckets and len(buckets[difficulty]) < per_level_target:
                buckets[difficulty].append(normalized)
            else:
                leftovers.append(normalized)

    rows: list[dict[str, Any]] = []
    for level in range(1, 6):
        rows.extend(buckets[f"level {level}"])
    if len(rows) < 500:
        rows.extend(leftovers[: 500 - len(rows)])
    return rows[:500]


def _normalize_problem(problem: dict[str, Any], benchmark: str, index: int) -> dict[str, Any]:
    prompt = problem.get("prompt") or problem.get("question") or problem.get("problem") or problem.get("statement") or ""
    normalized = {
        "id": str(problem.get("id") or problem.get("task_id") or problem.get("name") or f"{benchmark}_{index}"),
        "benchmark": benchmark,
        "type": problem.get("type"),
        "prompt": prompt,
        "difficulty": str(problem.get("difficulty", "unknown")).lower(),
        "public_tests": [_normalize_test_item(item) for item in problem.get("public_tests", [])],
        "hidden_tests": [_normalize_test_item(item) for item in problem.get("hidden_tests", [])],
    }

    tests = normalized["public_tests"] + normalized["hidden_tests"]
    is_stdin_task = any(test.get("testtype") == "stdin" for test in tests)
    entry_point = problem.get("entry_point") or problem.get("fn_name") or problem.get("function_name")
    if benchmark.startswith("livecodebench") and is_stdin_task:
        normalized["entry_point"] = None
    elif entry_point:
        normalized["entry_point"] = entry_point

    if "reference_solution" in problem:
        normalized["reference_solution"] = problem["reference_solution"]
    if "canonical_solution" in problem:
        normalized["reference_solution"] = problem["canonical_solution"]

    if "reference_answer" in problem:
        normalized["reference_answer"] = str(problem["reference_answer"]).strip()
    elif "answer" in problem:
        normalized["reference_answer"] = str(problem["answer"]).strip()
    elif "final_answer" in problem:
        normalized["reference_answer"] = str(problem["final_answer"]).strip()

    if not normalized["type"]:
        normalized["type"] = "math" if "reference_answer" in normalized and "entry_point" not in normalized else "code"

    return normalized


def _infer_entry_point(*texts: Any) -> str | None:
    pattern = re.compile(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    for text in texts:
        if not isinstance(text, str):
            continue
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def _compute_expected_outputs_from_inputs(
    solution: str,
    entry_point: str,
    inputs: list[Any],
    fallback_sources: list[str] | None = None,
) -> list[dict[str, Any]]:
    sources = [solution]
    if fallback_sources:
        sources.extend(source for source in fallback_sources if source not in sources)
    namespace: dict[str, Any] | None = None
    last_error: Exception | None = None
    for source in sources:
        try:
            trial_namespace: dict[str, Any] = {}
            exec(source, trial_namespace, trial_namespace)
            if entry_point not in trial_namespace:
                raise KeyError(f"Entry point '{entry_point}' not found after exec")
            namespace = trial_namespace
            break
        except Exception as exc:  # pragma: no cover - fallback path
            last_error = exc
    if namespace is None:
        raise RuntimeError(f"Could not execute canonical solution for entry point {entry_point}: {last_error}")
    fn = namespace[entry_point]
    tests = []
    for inp in inputs:
        if isinstance(inp, (list, tuple)):
            args = list(inp)
        else:
            args = [inp]
        tests.append({"input": args, "output": normalize_python_value(fn(*args))})
    return tests


def _build_executable_solution(prompt: str, solution: str) -> str:
    stripped = (solution or "").lstrip()
    if stripped.startswith("def ") or stripped.startswith("class "):
        return textwrap.dedent(solution)
    prompt_text = prompt or ""
    if "def " in prompt_text:
        prompt_text = textwrap.dedent(prompt_text)
        if not prompt_text.endswith("\n"):
            prompt_text += "\n"
        return prompt_text + solution.lstrip("\n")
    return textwrap.dedent(solution)


def _build_executable_candidates(prompt: str, solution: str) -> list[str]:
    prompt_text = textwrap.dedent(prompt or "")
    body = solution or ""
    stripped_body = textwrap.dedent(body).lstrip("\n")
    candidates = [
        _build_executable_solution(prompt_text, body),
        prompt_text + body.lstrip("\n"),
        prompt_text + textwrap.indent(stripped_body, "    "),
        textwrap.dedent(body),
    ]
    unique = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def _local_candidate_paths(name: str, data_root_path: Path) -> list[Path]:
    return [
        data_root_path / f"{name}.pkl",
        data_root_path / f"{name}.json",
        data_root_path / f"{name}.jsonl",
        data_root_path / name / "problems.pkl",
        data_root_path / name / "problems.json",
        data_root_path / name / "problems.jsonl",
    ]


def _load_local_benchmark(name: str, data_root_path: Path) -> list[dict[str, Any]] | None:
    for path in _local_candidate_paths(name, data_root_path):
        if path.exists():
            try:
                rows = load_pickle(path) if path.suffix == ".pkl" else _load_json_or_jsonl(path)
            except Exception:
                continue
            return [_normalize_problem(row, name, idx) for idx, row in enumerate(rows)]
    return None


def _load_livecodebench_release(version: str = "v6") -> list[dict[str, Any]]:
    file_map = {
        "v1": ["test.jsonl"],
        "v2": ["test2.jsonl"],
        "v3": ["test3.jsonl"],
        "v4": ["test4.jsonl"],
        "v5": ["test5.jsonl"],
        "v6": ["test6.jsonl"],
        "release_v6": ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl", "test6.jsonl"],
    }
    paths = file_map.get(version, file_map["release_v6"])
    base_url = "https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/main"
    rows = []
    for path in paths:
        with urllib.request.urlopen(f"{base_url}/{path}") as response:
            for line in response.read().decode("utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
    return rows


def _hf_rows(name: str) -> list[dict[str, Any]]:
    if name == "humaneval_plus":
        try:
            from evalplus.data.humaneval import get_human_eval, get_human_eval_plus  # type: ignore
        except ModuleNotFoundError as exc:
            raise FileNotFoundError(
                "Benchmark 'humaneval_plus' requires the optional evalplus package."
            ) from exc
        base = get_human_eval()
        plus = get_human_eval_plus()
        rows = []
        for idx, (task_id, task) in enumerate(sorted(plus.items())):
            base_task = base.get(task_id, {})
            entry_point = base_task.get("entry_point") or task.get("entry_point") or _infer_entry_point(
                task.get("prompt"),
                task.get("canonical_solution"),
            )
            candidates = _build_executable_candidates(task.get("prompt", ""), task.get("canonical_solution", ""))
            canonical = candidates[0]
            public_tests = _compute_expected_outputs_from_inputs(
                canonical,
                entry_point,
                task.get("base_input", []),
                fallback_sources=candidates[1:],
            )
            hidden_tests = _compute_expected_outputs_from_inputs(
                canonical,
                entry_point,
                task.get("plus_input", []),
                fallback_sources=candidates[1:],
            )
            rows.append(
                {
                    "id": task_id,
                    "type": "code",
                    "prompt": task.get("prompt", ""),
                    "entry_point": entry_point or "solution",
                    "reference_solution": canonical,
                    "public_tests": public_tests,
                    "hidden_tests": hidden_tests,
                    "difficulty": "unknown",
                }
            )
        return rows

    if name == "mbpp_plus":
        try:
            from evalplus.data.mbpp import get_mbpp, get_mbpp_plus  # type: ignore
        except ModuleNotFoundError as exc:
            raise FileNotFoundError("Benchmark 'mbpp_plus' requires the optional evalplus package.") from exc
        base = get_mbpp()
        plus = get_mbpp_plus()
        rows = []
        for idx, (task_id, task) in enumerate(sorted(plus.items(), key=lambda item: item[0])):
            base_task = base.get(task_id.split("/")[-1], {})
            canonical_candidates = _build_executable_candidates(
                task.get("prompt", base_task.get("prompt", "")),
                task.get("canonical_solution") or base_task.get("code", ""),
            )
            canonical = canonical_candidates[0]
            entry_point = (
                task.get("entry_point")
                or _infer_entry_point(canonical, task.get("prompt"), base_task.get("code", ""))
                or "solution"
            )
            public_tests = _compute_expected_outputs_from_inputs(
                canonical,
                entry_point,
                task.get("base_input", []),
                fallback_sources=canonical_candidates[1:],
            )
            hidden_tests = _compute_expected_outputs_from_inputs(
                canonical,
                entry_point,
                task.get("plus_input", []),
                fallback_sources=canonical_candidates[1:],
            )
            rows.append(
                {
                    "id": task_id,
                    "type": "code",
                    "prompt": task.get("prompt", base_task.get("prompt", "")),
                    "entry_point": entry_point,
                    "reference_solution": canonical,
                    "public_tests": public_tests,
                    "hidden_tests": hidden_tests,
                    "difficulty": "unknown",
                }
            )
        return rows

    try:
        from datasets import load_dataset  # type: ignore
    except ModuleNotFoundError as exc:
        raise FileNotFoundError(
            f"Benchmark '{name}' was not found locally and the optional 'datasets' package is not installed."
        ) from exc

    if name == "math500":
        try:
            dataset = load_dataset("hendrycks/competition_math", split="test")
            rows = []
            for idx, row in enumerate(dataset):
                rows.append(
                    {
                        "id": row.get("problem_id", f"math500_{idx}"),
                        "type": "math",
                        "prompt": row.get("problem", ""),
                        "reference_answer": _extract_boxed_answer(row.get("solution", "")),
                        "difficulty": str(row.get("level", "unknown")).lower(),
                    }
                )
            return rows[:500]
        except Exception:
            return _build_math500_rows_from_eleutherai(load_dataset)

    if name == "gsm8k":
        dataset = load_dataset("openai/gsm8k", "main", split="test")
        return [
            {
                "id": f"gsm8k_{idx}",
                "type": "math",
                "prompt": row.get("question", ""),
                "reference_answer": str(row.get("answer", "")).split("####")[-1].strip(),
                "difficulty": "easy",
            }
            for idx, row in enumerate(dataset)
        ]

    if name == "aime2024":
        dataset = load_dataset("AI-MO/aimo-validation-aime", split="train")
        return [
            {
                "id": row.get("id", f"aime2024_{idx}"),
                "type": "math",
                "prompt": row.get("problem", ""),
                "reference_answer": str(row.get("answer", "")).strip(),
                "difficulty": "competition",
            }
            for idx, row in enumerate(dataset)
        ]

    if name == "aime2025":
        try:
            dataset = load_dataset("test-time-compute/aime_2025", split="train")
        except Exception:
            dataset = load_dataset("math-ai/aime25", split="train")
        return [
            {
                "id": row.get("id", row.get("problem_id", f"aime2025_{idx}")),
                "type": "math",
                "prompt": row.get("question", row.get("problem", "")),
                "reference_answer": str(row.get("answer", row.get("final_answer", ""))).strip(),
                "difficulty": "competition",
                "subject": row.get("metadata", {}).get("problem_type", "unknown")
                if isinstance(row.get("metadata"), dict)
                else "unknown",
            }
            for idx, row in enumerate(dataset)
        ]

    if name == "livecodebench_v6":
        try:
            dataset = load_dataset("livecodebench/code_generation_lite", split="test")
            iterable_rows = list(dataset)
        except Exception:
            iterable_rows = _load_livecodebench_release("release_v6")
        rows = []
        for idx, row in enumerate(iterable_rows):
            public_tests = _decode_livecodebench_tests(
                row.get("public_tests", row.get("public_test_cases", []))
            )
            hidden_tests = _decode_livecodebench_tests(
                row.get("private_tests", row.get("private_test_cases", row.get("hidden_tests", [])))
            )
            is_stdin_task = any(test.get("testtype") == "stdin" for test in public_tests + hidden_tests)
            rows.append(
                {
                    "id": row.get("question_id", f"livecodebench_v6_{idx}"),
                    "type": "code",
                    "prompt": row.get("prompt", row.get("question_content", "")),
                    "entry_point": None if is_stdin_task else row.get("entry_point", "solve"),
                    "public_tests": public_tests,
                    "hidden_tests": hidden_tests,
                    "difficulty": str(row.get("difficulty", "unknown")).lower(),
                }
            )
        return rows

    if name in {"codecontests", "code_contests"}:
        last_error: Exception | None = None
        for dataset_name in ["deepmind/code_contests", "Imandra/code_contests", "prima02/deepmind_code_contests"]:
            try:
                dataset = load_dataset(dataset_name, split="test")
                iterable_rows = list(dataset)
                break
            except Exception as exc:
                last_error = exc
        else:
            raise FileNotFoundError(
                "Could not load CodeContests from Hugging Face. Prepare data/codecontests/problems.json "
                "or install the DeepMind Riegeli release locally."
            ) from last_error

        rows = []
        for idx, row in enumerate(iterable_rows):
            public_tests = _decode_codecontests_tests(row.get("public_tests", row.get("sample_tests", [])))
            hidden_tests = []
            hidden_tests.extend(_decode_codecontests_tests(row.get("private_tests", [])))
            hidden_tests.extend(_decode_codecontests_tests(row.get("generated_tests", [])))
            rows.append(
                {
                    "id": row.get("name", row.get("id", f"codecontests_{idx}")),
                    "type": "code",
                    "prompt": row.get("description", row.get("question", row.get("prompt", ""))),
                    "entry_point": None,
                    "public_tests": public_tests,
                    "hidden_tests": hidden_tests,
                    "difficulty": str(row.get("difficulty", "competition")).lower(),
                    "source": row.get("source", "codecontests"),
                }
            )
        return rows

    raise FileNotFoundError(f"No built-in Hugging Face loader configured for benchmark '{name}'.")


def load_benchmark(name: str, data_root: str | Path = "data") -> list[dict[str, Any]]:
    if name == "synthetic_demo":
        return _synthetic_demo()

    data_root_path = Path(data_root)
    local_rows = _load_local_benchmark(name, data_root_path)
    if local_rows is not None:
        return local_rows

    rows = _hf_rows(name)
    return [_normalize_problem(row, name, idx) for idx, row in enumerate(rows)]
