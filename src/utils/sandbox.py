"""Execution helpers for candidate programs.

This local version uses subprocess-based Python execution to stay portable.
For HPC runs, replace or wrap this with Apptainer as planned.
"""

from __future__ import annotations

import json
import os
import pickle
import subprocess
import sys
import tempfile
import textwrap
from base64 import b64decode, b64encode
from pathlib import Path
from typing import Any

try:
    from utils.io import normalize_python_value
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from .io import normalize_python_value


def run_code_test(
    code: str,
    entry_point: str,
    test_input: list[Any],
    expected_output: Any,
    timeout: int = 10,
) -> dict[str, Any]:
    execution = execute_code_function(
        code=code,
        entry_point=entry_point,
        test_input=test_input,
        timeout=timeout,
    )
    if execution["status"] != "passed":
        return execution

    observed = execution["observed_output"]
    normalized_expected = normalize_python_value(expected_output)
    return {
        **execution,
        "passed": observed == normalized_expected,
        "status": "passed" if observed == normalized_expected else "failed",
        "expected_output": normalized_expected,
    }


def execute_code_function(
    code: str,
    entry_point: str,
    test_input: list[Any],
    timeout: int = 10,
) -> dict[str, Any]:
    apptainer_image = os.environ.get("SEQFALS_APPTAINER_IMAGE")
    if apptainer_image:
        return execute_code_function_apptainer(
            code=code,
            entry_point=entry_point,
            test_input=test_input,
            timeout=timeout,
            image=apptainer_image,
        )

    encoded_args = b64encode(pickle.dumps(test_input)).decode("ascii")
    harness = textwrap.dedent(
        f"""
        import re
        import pickle
        from base64 import b64decode, b64encode

        def _normalize(value):
            if isinstance(value, dict):
                if all(isinstance(key, (str, int, float, bool)) or key is None for key in value):
                    return {{key: _normalize(item) for key, item in value.items()}}
                return {{
                    "__dict_items__": [
                        {{"key": _normalize(key), "value": _normalize(item)}} for key, item in value.items()
                    ]
                }}
            if isinstance(value, list):
                return [_normalize(item) for item in value]
            if isinstance(value, tuple):
                return {{"__tuple__": [_normalize(item) for item in value]}}
            if isinstance(value, set):
                normalized = [_normalize(item) for item in value]
                return {{"__set__": sorted(normalized, key=repr)}}
            if isinstance(value, complex):
                return {{"__complex__": [value.real, value.imag]}}
            if isinstance(value, bytes):
                return {{"__bytes__": b64encode(value).decode("ascii")}}
            if isinstance(value, re.Match):
                return {{
                    "__re_match__": {{
                        "group0": value.group(0),
                        "groups": [_normalize(item) for item in value.groups()],
                        "groupdict": {{key: _normalize(item) for key, item in value.groupdict().items()}},
                        "span": [value.span()[0], value.span()[1]],
                        "pattern": value.re.pattern,
                        "string": value.string,
                    }}
                }}
            if isinstance(value, (str, int, float, bool)) or value is None:
                return value
            return {{"__python_object__": {{"type": type(value).__name__, "repr": repr(value)}}}}

        namespace = {{}}
        code = {code!r}
        exec(code, namespace, namespace)
        fn = namespace[{entry_point!r}]
        args = pickle.loads(b64decode({encoded_args!r}))
        result = fn(*args)
        print(b64encode(pickle.dumps(_normalize(result))).decode("ascii"))
        """
    )
    with tempfile.TemporaryDirectory(prefix="seqfals_") as tmp_dir:
        script_path = Path(tmp_dir) / "runner.py"
        script_path.write_text(harness, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "status": "timeout",
                "stdout": "",
                "stderr": "Execution timed out",
            }

    if completed.returncode != 0:
        return {
            "passed": False,
            "status": "error",
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    try:
        observed = normalize_python_value(pickle.loads(b64decode(completed.stdout.strip().encode("ascii"))))
    except Exception as exc:  # pragma: no cover - defensive path
        return {
            "passed": False,
            "status": "parse_error",
            "stdout": completed.stdout,
            "stderr": f"Failed to parse execution output: {exc}",
        }

    return {
        "passed": True,
        "status": "passed",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "observed_output": observed,
    }


def run_code_test_apptainer(
    code: str,
    entry_point: str,
    test_input: list[Any],
    expected_output: Any,
    timeout: int,
    image: str,
) -> dict[str, Any]:
    execution = execute_code_function_apptainer(
        code=code,
        entry_point=entry_point,
        test_input=test_input,
        timeout=timeout,
        image=image,
    )
    if execution["status"] != "passed":
        return execution

    observed = execution["observed_output"]
    normalized_expected = normalize_python_value(expected_output)
    return {
        **execution,
        "passed": observed == normalized_expected,
        "status": "passed" if observed == normalized_expected else "failed",
        "expected_output": normalized_expected,
    }


def execute_code_function_apptainer(
    code: str,
    entry_point: str,
    test_input: list[Any],
    timeout: int,
    image: str,
) -> dict[str, Any]:
    encoded_args = b64encode(pickle.dumps(test_input)).decode("ascii")
    harness = textwrap.dedent(
        f"""
        import re
        import pickle
        from base64 import b64decode, b64encode

        def _normalize(value):
            if isinstance(value, dict):
                if all(isinstance(key, (str, int, float, bool)) or key is None for key in value):
                    return {{key: _normalize(item) for key, item in value.items()}}
                return {{
                    "__dict_items__": [
                        {{"key": _normalize(key), "value": _normalize(item)}} for key, item in value.items()
                    ]
                }}
            if isinstance(value, list):
                return [_normalize(item) for item in value]
            if isinstance(value, tuple):
                return {{"__tuple__": [_normalize(item) for item in value]}}
            if isinstance(value, set):
                normalized = [_normalize(item) for item in value]
                return {{"__set__": sorted(normalized, key=repr)}}
            if isinstance(value, complex):
                return {{"__complex__": [value.real, value.imag]}}
            if isinstance(value, bytes):
                return {{"__bytes__": b64encode(value).decode("ascii")}}
            if isinstance(value, re.Match):
                return {{
                    "__re_match__": {{
                        "group0": value.group(0),
                        "groups": [_normalize(item) for item in value.groups()],
                        "groupdict": {{key: _normalize(item) for key, item in value.groupdict().items()}},
                        "span": [value.span()[0], value.span()[1]],
                        "pattern": value.re.pattern,
                        "string": value.string,
                    }}
                }}
            if isinstance(value, (str, int, float, bool)) or value is None:
                return value
            return {{"__python_object__": {{"type": type(value).__name__, "repr": repr(value)}}}}

        namespace = {{}}
        exec({code!r}, namespace, namespace)
        fn = namespace[{entry_point!r}]
        args = pickle.loads(b64decode({encoded_args!r}))
        result = fn(*args)
        print(b64encode(pickle.dumps(_normalize(result))).decode("ascii"))
        """
    )
    with tempfile.TemporaryDirectory(prefix="seqfals_appt_") as tmp_dir:
        script_path = Path(tmp_dir) / "runner.py"
        script_path.write_text(harness, encoding="utf-8")
        command = [
            "apptainer",
            "exec",
            "--contain",
            "--no-home",
            "--bind",
            f"{tmp_dir}:/workspace",
            image,
            "timeout",
            str(timeout),
            "python3",
            "/workspace/runner.py",
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout + 5,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "status": "timeout",
                "stdout": "",
                "stderr": "Apptainer execution timed out",
            }

    if completed.returncode != 0:
        return {
            "passed": False,
            "status": "error",
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    try:
        observed = normalize_python_value(pickle.loads(b64decode(completed.stdout.strip().encode("ascii"))))
    except Exception as exc:
        return {
            "passed": False,
            "status": "parse_error",
            "stdout": completed.stdout,
            "stderr": f"Failed to parse Apptainer output: {exc}",
        }

    return {
        "passed": True,
        "status": "passed",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "observed_output": observed,
        "runtime": "apptainer",
    }


def _normalize_stdout(value: Any) -> str:
    return str(value if value is not None else "").replace("\r\n", "\n").strip()


def run_code_stdin_test(
    code: str,
    stdin: str,
    expected_output: Any,
    timeout: int = 10,
) -> dict[str, Any]:
    execution = execute_stdin_program(code=code, stdin=stdin, timeout=timeout)
    observed = execution["observed_output"]
    expected = _normalize_stdout(expected_output)
    passed = execution["status"] == "passed" and observed == expected
    return {
        **execution,
        "passed": passed,
        "status": "passed" if passed else ("error" if execution["status"] == "error" else "failed"),
        "expected_output": expected,
    }


def execute_stdin_program(
    code: str,
    stdin: str,
    timeout: int = 10,
) -> dict[str, Any]:
    apptainer_image = os.environ.get("SEQFALS_APPTAINER_IMAGE")
    with tempfile.TemporaryDirectory(prefix="seqfals_stdin_") as tmp_dir:
        script_path = Path(tmp_dir) / "solution.py"
        script_path.write_text(code, encoding="utf-8")
        if apptainer_image:
            command = [
                "apptainer",
                "exec",
                "--contain",
                "--no-home",
                "--bind",
                f"{tmp_dir}:/workspace",
                apptainer_image,
                "timeout",
                str(timeout),
                "python3",
                "/workspace/solution.py",
            ]
            effective_timeout = timeout + 5
        else:
            command = [sys.executable, str(script_path)]
            effective_timeout = timeout
        try:
            completed = subprocess.run(
                command,
                input=str(stdin if stdin is not None else ""),
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "status": "timeout",
                "stdout": "",
                "stderr": "Execution timed out",
            }

    observed = _normalize_stdout(completed.stdout)
    return {
        "passed": completed.returncode == 0,
        "status": "passed" if completed.returncode == 0 else "error",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "observed_output": observed,
        "returncode": completed.returncode,
        "runtime": "apptainer" if apptainer_image else "subprocess",
    }


def evaluate_candidate(problem: dict[str, Any], code: str, use_hidden: bool = False, timeout: int = 10) -> dict[str, Any]:
    tests = list(problem.get("public_tests", []))
    if use_hidden:
        tests.extend(problem.get("hidden_tests", []))
    if problem.get("type") != "code":
        prediction = code.strip()
        answer = str(problem.get("reference_answer", "")).strip()
        return {
            "passed": prediction == answer,
            "status": "passed" if prediction == answer else "failed",
            "num_tests": 1,
            "num_passed": 1 if prediction == answer else 0,
            "details": [{"passed": prediction == answer, "prediction": prediction, "answer": answer}],
        }

    details = []
    passed = 0
    for test in tests:
        if test.get("testtype") == "stdin":
            result = run_code_stdin_test(
                code=code,
                stdin=test.get("input", ""),
                expected_output=test.get("output", ""),
                timeout=timeout,
            )
        else:
            result = run_code_test(
                code=code,
                entry_point=problem["entry_point"],
                test_input=test["input"],
                expected_output=test["output"],
                timeout=timeout,
            )
        details.append(result)
        if result["passed"]:
            passed += 1

    return {
        "passed": passed == len(tests),
        "status": "passed" if passed == len(tests) else "failed",
        "num_tests": len(tests),
        "num_passed": passed,
        "details": details,
    }
