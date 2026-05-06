"""Candidate generation.

Supports three modes:
- `mock`: deterministic local variants for smoke tests.
- `openai`: OpenAI-compatible API endpoint, including vLLM server mode.
- `transformers`: direct local Hugging Face generation without a serving layer.
- `echo`: return the reference solution or answer when present.
"""

from __future__ import annotations

import argparse
import ast
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from utils.io import dump_json
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from .utils.io import dump_json


@dataclass
class GenerationConfig:
    backend: str = "mock"
    model: str = "mock-model"
    api_base: str = "http://localhost:8000/v1"
    api_key: str = "none"
    request_timeout: float = 15.0
    temperature: float = 0.7
    max_tokens: int = 512
    seed: int = 42


_TRANSFORMERS_CACHE: dict[str, tuple[Any, Any]] = {}


def _mock_code_variants(problem: dict[str, Any], n: int, rng: random.Random) -> list[str]:
    reference = problem.get("reference_solution", "").rstrip() + "\n"
    wrong_variants = [
        "def solve(*args):\n    return 0\n",
        "def solve(*args):\n    return args[0] if args else None\n",
        "def solve(*args):\n    raise ValueError('not implemented')\n",
    ]
    variants = []
    for idx in range(n):
        if idx == 0:
            variants.append(reference)
        else:
            variants.append(rng.choice(wrong_variants))
    return variants


def _mock_math_variants(problem: dict[str, Any], n: int, rng: random.Random) -> list[str]:
    answer = str(problem.get("reference_answer", "")).strip()
    variants = [answer]
    for _ in range(max(0, n - 1)):
        jitter = rng.randint(-3, 3) or 1
        if answer.isdigit():
            variants.append(str(int(answer) + jitter))
        else:
            variants.append("0")
    return variants[:n]


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)
    return str(content or "")


def _contains_entry_point(source: str, entry_point: str | None) -> bool:
    if not entry_point:
        return True
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entry_point:
            return True
    return False


def _looks_like_standalone_program(source: str) -> bool:
    """Reject plain problem text that happens to have a parseable prefix."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    structural_nodes = (
        ast.Import,
        ast.ImportFrom,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Assign,
        ast.AnnAssign,
        ast.AugAssign,
        ast.For,
        ast.While,
        ast.If,
        ast.Try,
        ast.With,
    )
    if any(isinstance(node, structural_nodes) for node in ast.walk(tree)):
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in {"input", "print", "range", "map", "int"}:
                return True
            if isinstance(func, ast.Attribute) and func.attr in {"read", "readline", "split", "append"}:
                return True
    return False


def _parseable_prefix(source: str, entry_point: str | None) -> str | None:
    lines = source.splitlines()
    best: str | None = None
    for idx in range(1, len(lines) + 1):
        snippet = "\n".join(lines[:idx]).rstrip()
        if not snippet:
            continue
        try:
            ast.parse(snippet + "\n")
        except SyntaxError:
            continue
        if entry_point:
            valid = _contains_entry_point(snippet + "\n", entry_point)
        else:
            valid = _looks_like_standalone_program(snippet + "\n")
        if valid:
            best = snippet + "\n"
    return best


def _strip_markdown_fences(text: str) -> str:
    stripped = text.strip()
    if "```" not in stripped:
        return text
    matches = re.findall(r"```(?:python)?\s*(.*?)```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if matches:
        return "\n\n".join(matches)
    return stripped.replace("```python", "").replace("```", "")


def _looks_like_code_line(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped:
        return True
    if line.startswith("    ") or line.startswith("\t"):
        return True
    prefixes = (
        "def ",
        "class ",
        "from ",
        "import ",
        "@",
        "if ",
        "elif ",
        "else:",
        "for ",
        "while ",
        "try:",
        "except",
        "finally:",
        "with ",
        "return ",
        "yield ",
        "raise ",
        "assert ",
        "pass",
        "break",
        "continue",
        "#",
        '"""',
        "'''",
        ")",
        "]",
        "}",
    )
    return stripped.startswith(prefixes)


def _candidate_views(problem: dict[str, Any], raw_output: str) -> list[str]:
    prompt = problem.get("prompt", "").rstrip()
    entry_point = problem.get("entry_point")
    cleaned = _strip_markdown_fences(raw_output).replace("\r\n", "\n")
    lines = cleaned.splitlines()
    include_prompt = bool(prompt and entry_point)

    views: list[str] = []
    views.append(cleaned)
    if include_prompt:
        views.append(prompt + "\n" + cleaned.lstrip("\n"))

    for idx, line in enumerate(lines):
        if not _looks_like_code_line(line):
            continue
        snippet = "\n".join(lines[idx:])
        views.append(snippet)
        if include_prompt:
            views.append(prompt + "\n" + snippet.lstrip("\n"))

    unique: list[str] = []
    for view in views:
        normalized = view.strip("\n")
        if normalized and normalized not in unique:
            unique.append(normalized)
    return unique


def _normalize_code_output(problem: dict[str, Any], raw_output: str) -> str:
    entry_point = problem.get("entry_point")
    for candidate in _candidate_views(problem, raw_output):
        parsed = _parseable_prefix(candidate, entry_point)
        if parsed:
            return parsed
    if not entry_point:
        fallback = _strip_markdown_fences(raw_output)
        return fallback.strip("\n") + "\n"
    fallback = problem.get("prompt", "").rstrip() + "\n" + _strip_markdown_fences(raw_output).lstrip("\n")
    return fallback.strip("\n") + "\n"


def _normalize_math_output(raw_output: str) -> str:
    text = _strip_markdown_fences(raw_output).strip()
    boxed = re.findall(r"\\boxed\{([^}]*)\}", text)
    if boxed:
        return boxed[-1].strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        return lines[-1]
    return text


def _normalize_generated_output(problem: dict[str, Any], raw_output: str) -> str:
    if problem.get("type") == "math":
        return _normalize_math_output(raw_output)
    if problem.get("type") == "code":
        return _normalize_code_output(problem, raw_output)
    return raw_output


def _is_stdin_code_problem(problem: dict[str, Any]) -> bool:
    tests = list(problem.get("public_tests", [])) + list(problem.get("hidden_tests", []))
    return problem.get("type") == "code" and any(test.get("testtype") == "stdin" for test in tests)


def _load_transformers_model(model_name: str) -> tuple[Any, Any]:
    if model_name in _TRANSFORMERS_CACHE:
        return _TRANSFORMERS_CACHE[model_name]

    try:
        import torch  # type: ignore
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("transformers backend requires torch, transformers, and accelerate") from exc

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    _TRANSFORMERS_CACHE[model_name] = (tokenizer, model)
    return tokenizer, model


def _transformers_prompt(problem: dict[str, Any]) -> str:
    if problem.get("type") == "code":
        if _is_stdin_code_problem(problem):
            return (
                f"{problem['prompt'].rstrip()}\n\n"
                "Write a complete Python 3 program that solves the problem. "
                "The program must read from stdin and write to stdout. "
                "Return only executable code."
            )
        entry_point = problem.get("entry_point")
        prompt_text = problem["prompt"]
        if entry_point and f"def {entry_point}" not in prompt_text:
            return (
                f"{prompt_text.rstrip()}\n\n"
                f"Write a Python function named `{entry_point}` that solves the task. "
                "Return only executable Python code."
            )
        return prompt_text
    if problem.get("type") == "math":
        return (
            "Solve the problem and return only the final answer, with no explanation.\n\n"
            f"{problem['prompt']}"
        )
    return problem["prompt"]


def _generate_with_transformers(problem: dict[str, Any], n: int, config: GenerationConfig) -> list[str]:
    try:
        import torch  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("transformers backend requires torch") from exc

    tokenizer, model = _load_transformers_model(config.model)
    prompt = _transformers_prompt(problem)
    seed_value = config.seed + hash(problem.get("id", "")) % 10_000
    torch.manual_seed(seed_value)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed_value)

    if problem.get("type") == "math" and hasattr(tokenizer, "apply_chat_template"):
        messages = [
            {"role": "system", "content": "Solve the problem and return only the final answer, with no explanation."},
            {"role": "user", "content": problem["prompt"]},
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    encoded = tokenizer(prompt, return_tensors="pt")
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    generation_kwargs = {
        **encoded,
        "max_new_tokens": config.max_tokens,
        "do_sample": config.temperature > 0,
        "temperature": max(config.temperature, 1e-5),
        "num_return_sequences": n,
        "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }
    with torch.no_grad():
        sequences = model.generate(**generation_kwargs)
    prompt_length = encoded["input_ids"].shape[1]
    generated = sequences[:, prompt_length:]
    return tokenizer.batch_decode(generated, skip_special_tokens=True)


def generate_candidates(problem: dict[str, Any], n: int, config: GenerationConfig) -> list[dict[str, Any]]:
    rng = random.Random(config.seed + hash(problem.get("id", "")) % 10_000)
    if config.backend in {"mock", "echo"}:
        if problem.get("type") == "math":
            outputs = _mock_math_variants(problem, n=n, rng=rng)
        elif config.backend == "echo":
            outputs = [problem.get("reference_solution", "")]
            outputs.extend([""] * max(0, n - 1))
        else:
            outputs = _mock_code_variants(problem, n=n, rng=rng)
    elif config.backend == "openai":
        try:
            from openai import OpenAI  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("openai package is required for backend=openai") from exc
        client = OpenAI(
            base_url=config.api_base,
            api_key=config.api_key,
            timeout=config.request_timeout,
            max_retries=1,
        )
        if problem.get("type") == "code":
            if _is_stdin_code_problem(problem):
                prompt = (
                    f"{problem['prompt'].rstrip()}\n\n"
                    "Write a complete Python 3 program that solves the problem. "
                    "The program must read from stdin and write to stdout. "
                    "Return only executable code.\n"
                    "```python\n"
                )
                response = client.completions.create(
                    model=config.model,
                    prompt=prompt,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    n=n,
                    stop=["```"],
                )
                outputs = [choice.text for choice in response.choices]
            else:
                entry_point = problem.get("entry_point")
                prompt_text = problem["prompt"]
                if entry_point and f"def {entry_point}" not in prompt_text:
                    prompt = (
                        f"{prompt_text.rstrip()}\n\n"
                        f"Write a Python function named `{entry_point}` that solves the task. "
                        "Return only executable Python code.\n"
                        "```python\n"
                    )
                    stop = ["```"]
                else:
                    prompt = prompt_text
                    stop = ["\nWait", "\nThe ", "\nI ", "\nLet ", "\nIn this"]
                response = client.completions.create(
                    model=config.model,
                    prompt=prompt,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    n=n,
                    stop=stop,
                )
                outputs = [choice.text for choice in response.choices]
        elif problem.get("type") == "math":
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Solve the problem and return only the final answer, with no explanation.",
                    },
                    {"role": "user", "content": problem["prompt"]},
                ],
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                n=n,
            )
            outputs = [_message_text(choice.message.content) for choice in response.choices]
        else:
            response = client.completions.create(
                model=config.model,
                prompt=problem["prompt"],
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                n=n,
            )
            outputs = [choice.text for choice in response.choices]
    elif config.backend == "transformers":
        outputs = _generate_with_transformers(problem, n=n, config=config)
    else:
        raise ValueError(f"Unknown generation backend: {config.backend}")

    return [
        {
            "candidate_id": f"{problem.get('id', 'problem')}_cand_{idx}",
            "problem_id": problem.get("id"),
            "text": _normalize_generated_output(problem, output),
            "raw_text": output,
            "backend": config.backend,
            "model": config.model,
            "temperature": config.temperature,
        }
        for idx, output in enumerate(outputs)
    ]


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Generate candidate solutions for a single problem JSON file.")
    parser.add_argument("--problem-file", required=True)
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--backend", default="mock")
    parser.add_argument("--model", default="mock-model")
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()

    problem = json.loads(Path(args.problem_file).read_text(encoding="utf-8"))
    cfg = GenerationConfig(backend=args.backend, model=args.model)
    dump_json(generate_candidates(problem, n=args.n, config=cfg), args.output_file)


if __name__ == "__main__":
    _cli()
