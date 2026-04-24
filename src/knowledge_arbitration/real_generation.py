"""Real-generation utilities for theorem-3 knowledge-arbitration experiments."""

from __future__ import annotations

from dataclasses import dataclass
import json
from math import log
from pathlib import Path
import random
import re
from typing import Any

from utils.io import dump_json

from .loaders import load_arbitration_dataset


_ANSWER_RE = re.compile(r"<answer>\s*(.*?)\s*</answer>", flags=re.IGNORECASE | re.DOTALL)
_CONFIDENCE_RE = re.compile(r"<confidence>\s*(.*?)\s*</confidence>", flags=re.IGNORECASE | re.DOTALL)
_THINK_RE = re.compile(r"<think>\s*(.*?)\s*</think>", flags=re.IGNORECASE | re.DOTALL)
_NUMBER_RE = re.compile(r"(?<!\d)(?:0(?:\.\d+)?|1(?:\.0+)?)(?!\d)|(?<!\d)(\d{1,3}(?:\.\d+)?)\s*%")


@dataclass(frozen=True)
class PromptStyle:
    label: str
    cot_length: int
    max_tokens: int
    system_prompt: str


PROMPT_STYLES: dict[str, PromptStyle] = {
    "no_cot": PromptStyle(
        label="no_cot",
        cot_length=0,
        max_tokens=192,
        system_prompt=(
            "Answer the question immediately. Do not include reasoning, explanation, or analysis. "
            "Respond using exactly this format:\n"
            "<answer>your answer</answer>\n"
            "<confidence>0.00 to 1.00</confidence>"
        ),
    ),
    "short_cot": PromptStyle(
        label="short_cot",
        cot_length=128,
        max_tokens=768,
        system_prompt=(
            "Think briefly and then answer. Keep your reasoning concise. "
            "Respond using exactly this format:\n"
            "<think>brief reasoning</think>\n"
            "<answer>your answer</answer>\n"
            "<confidence>0.00 to 1.00</confidence>"
        ),
    ),
    "long_cot": PromptStyle(
        label="long_cot",
        cot_length=1024,
        max_tokens=2048,
        system_prompt=(
            "Think step by step very carefully, consider conflicting evidence explicitly, and then answer. "
            "Respond using exactly this format:\n"
            "<think>detailed reasoning</think>\n"
            "<answer>your answer</answer>\n"
            "<confidence>0.00 to 1.00</confidence>"
        ),
    ),
}


@dataclass(frozen=True)
class GenerationConfig:
    backend: str = "openai"
    model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    api_base: str = "http://127.0.0.1:8000/v1"
    api_key: str = "none"
    request_timeout: float = 180.0
    temperature: float = 0.0
    seed: int = 42


def _normalize_answer_text(text: Any) -> str:
    normalized = str(text or "").strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[`\"'“”‘’.,;:!?()\[\]{}]", "", normalized)
    return normalized.strip()


def _answer_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if hasattr(values, "tolist"):
        values = values.tolist()
    if isinstance(values, str):
        values = [values]
    if isinstance(values, tuple):
        values = list(values)
    if isinstance(values, list):
        return {_normalize_answer_text(item) for item in values if _normalize_answer_text(item)}
    normalized = _normalize_answer_text(values)
    return {normalized} if normalized else set()


def _answers_match(prediction: str, answers: set[str]) -> bool:
    normalized_prediction = _normalize_answer_text(prediction)
    if not normalized_prediction or not answers:
        return False
    if normalized_prediction in answers:
        return True
    for answer in answers:
        if len(answer) >= 4 and answer in normalized_prediction:
            return True
        if len(normalized_prediction) >= 4 and normalized_prediction in answer:
            return True
    return False


def _question_block(example: dict[str, Any], condition: str) -> str:
    metadata = example.get("metadata", {})
    question = str(example.get("question", "")).strip()
    if condition == "closed_book":
        return f"Question: {question}"

    if condition == "aligned_context":
        context_text = str(metadata.get("aligned_context_text") or "")
    elif condition == "conflict_context":
        context_text = str(metadata.get("conflict_context_text") or "")
    else:
        raise ValueError(f"Unsupported condition for real theorem-3 generation: {condition}")

    return (
        f"Question: {question}\n\n"
        "Context:\n"
        f"{context_text.strip()}\n\n"
        "Use the context if it is reliable, but answer the question rather than summarizing the passage."
    )


def _extract_confidence(text: str) -> float | None:
    tagged = _CONFIDENCE_RE.search(text)
    if tagged:
        candidate = tagged.group(1).strip()
        try:
            value = float(candidate)
        except ValueError:
            value = None
        if value is not None:
            if value > 1.0:
                value = value / 100.0
            return min(max(value, 0.0), 1.0)

    for match in _NUMBER_RE.finditer(text):
        token = match.group(0).strip()
        try:
            value = float(token.rstrip("%"))
        except ValueError:
            continue
        if token.endswith("%") or value > 1.0:
            value = value / 100.0
        return min(max(value, 0.0), 1.0)
    return None


def _extract_answer(text: str) -> str:
    tagged = _ANSWER_RE.search(text)
    if tagged:
        return tagged.group(1).strip()

    stripped = re.sub(r"</?think>|</?answer>|</?confidence>", "", text, flags=re.IGNORECASE)
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if not lines:
        return ""
    for line in reversed(lines):
        if "confidence" in line.lower():
            continue
        return line
    return lines[-1]


def _extract_reasoning(text: str) -> str:
    tagged = _THINK_RE.search(text)
    if tagged:
        return tagged.group(1).strip()

    answer_match = _ANSWER_RE.search(text)
    if answer_match:
        prefix = text[: answer_match.start()].strip()
        prefix = re.sub(r"</?confidence>.*", "", prefix, flags=re.IGNORECASE | re.DOTALL)
        return prefix.strip()
    return ""


def _count_words(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return len([token for token in re.split(r"\s+", stripped) if token])


def _arbitration_probability(answer: str, *, parametric_answers: set[str], context_answers: set[str], split: str) -> tuple[float | None, float | None]:
    prediction_matches_context = _answers_match(answer, context_answers)
    prediction_matches_parametric = _answers_match(answer, parametric_answers)

    if split == "conflict":
        oracle_context_probability = 0.0
    elif split == "no_conflict":
        oracle_context_probability = 0.5
    else:
        oracle_context_probability = None

    if prediction_matches_context and not prediction_matches_parametric:
        model_context_probability = 1.0
    elif prediction_matches_parametric and not prediction_matches_context:
        model_context_probability = 0.0
    elif prediction_matches_context and prediction_matches_parametric:
        model_context_probability = 0.5
    else:
        model_context_probability = 0.5 if split == "no_conflict" else None

    return oracle_context_probability, model_context_probability


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True))
        handle.write("\n")


def _load_jsonl_map(path: Path, key_fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[tuple[str, ...], dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            key = tuple(str(record.get(field, "")) for field in key_fields)
            out[key] = record
    return out


def _openai_chat(messages: list[dict[str, str]], *, style: PromptStyle, config: GenerationConfig) -> tuple[str, dict[str, Any]]:
    from openai import OpenAI  # type: ignore

    client = OpenAI(
        base_url=config.api_base,
        api_key=config.api_key,
        timeout=config.request_timeout,
        max_retries=1,
    )
    response = client.chat.completions.create(
        model=config.model,
        messages=messages,
        max_tokens=style.max_tokens,
        temperature=config.temperature,
    )
    choice = response.choices[0]
    text = ""
    if getattr(choice, "message", None) is not None:
        content = choice.message.content
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = "".join(item.get("text", "") for item in content if isinstance(item, dict))
    usage = getattr(response, "usage", None)
    usage_payload = {}
    if usage is not None:
        usage_payload = {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    return text, usage_payload


def _mock_chat(example: dict[str, Any], *, style: PromptStyle, condition: str, seed: int) -> tuple[str, dict[str, Any]]:
    rng = random.Random(f"{example.get('id')}::{condition}::{style.label}::{seed}")
    metadata = example.get("metadata", {})
    gold_answers = list(_answer_set(example.get("answers")))
    parametric_answers = list(_answer_set(metadata.get("parametric_answers") or example.get("answers")))
    conflict_answers = list(_answer_set(metadata.get("conflict_context_answers")))

    if condition == "conflict_context" and style.label == "long_cot":
        answer = conflict_answers[0] if conflict_answers else (gold_answers[0] if gold_answers else "unknown")
        confidence = 0.82
        reasoning = (
            "The passage strongly states an answer, and after carefully weighing the evidence I trust the context."
        )
    elif condition == "conflict_context" and style.label == "short_cot":
        answer = gold_answers[0] if gold_answers else "unknown"
        confidence = 0.58
        reasoning = "The context conflicts with what I think I know, so I am uncertain."
    else:
        answer = gold_answers[0] if gold_answers else (parametric_answers[0] if parametric_answers else "unknown")
        confidence = 0.74 if style.label == "no_cot" else 0.69
        reasoning = "I compared the question with the most plausible evidence." if style.label != "no_cot" else ""

    if rng.random() < 0.05 and gold_answers:
        answer = gold_answers[0]
    if style.label == "no_cot":
        response = f"<answer>{answer}</answer>\n<confidence>{confidence:.2f}</confidence>"
    else:
        repeated = reasoning if style.label == "short_cot" else " ".join([reasoning] * 6)
        response = (
            f"<think>{repeated}</think>\n"
            f"<answer>{answer}</answer>\n"
            f"<confidence>{confidence:.2f}</confidence>"
        )
    usage = {"prompt_tokens": 0, "completion_tokens": len(response.split()), "total_tokens": len(response.split())}
    return response, usage


def _generate_response(example: dict[str, Any], *, style: PromptStyle, condition: str, config: GenerationConfig) -> tuple[str, dict[str, Any]]:
    messages = [
        {"role": "system", "content": style.system_prompt},
        {"role": "user", "content": _question_block(example, condition)},
    ]
    if config.backend == "mock":
        return _mock_chat(example, style=style, condition=condition, seed=config.seed)
    if config.backend != "openai":
        raise ValueError(f"Unsupported theorem-3 real-generation backend: {config.backend}")
    return _openai_chat(messages, style=style, config=config)


def _screen_key(example: dict[str, Any]) -> tuple[str, ...]:
    return (str(example.get("benchmark")), str(example.get("id")))


def _generation_key(record: dict[str, Any]) -> tuple[str, ...]:
    return (
        str(record.get("benchmark")),
        str(record.get("id")),
        str(record.get("condition")),
        str(record.get("cot_length")),
        str(record.get("model")),
    )


def screen_conflict_examples(
    *,
    benchmark: str,
    config: GenerationConfig,
    low: float,
    high: float,
    max_examples: int,
    screening_pool: int,
    output_dir: str | Path,
    resume: bool = True,
) -> dict[str, Any]:
    examples = load_arbitration_dataset(benchmark, max_examples=screening_pool)
    output_path = Path(output_dir)
    screening_file = output_path / f"{benchmark}_screening.jsonl"
    existing = _load_jsonl_map(screening_file, ("benchmark", "id"))

    records: list[dict[str, Any]] = []
    for example in examples:
        key = (benchmark, str(example.get("id")))
        cached = existing.get(key)
        if cached is None:
            raw_response, usage = _generate_response(example, style=PROMPT_STYLES["no_cot"], condition="closed_book", config=config)
            answer = _extract_answer(raw_response)
            confidence = _extract_confidence(raw_response)
            if confidence is None:
                confidence = 0.5
            gold_answers = _answer_set(example.get("answers"))
            correct = _answers_match(answer, gold_answers)
            cached = {
                "benchmark": benchmark,
                "id": str(example.get("id")),
                "question": example.get("question"),
                "answer": answer,
                "confidence": confidence,
                "correct": int(correct),
                "raw_response": raw_response,
                "usage": usage,
            }
            _append_jsonl(screening_file, cached)
        records.append(cached)

    ambiguous = [record for record in records if low <= float(record.get("confidence", 0.0)) <= high]
    ambiguous.sort(key=lambda item: abs(float(item.get("confidence", 0.5)) - 0.5))
    if len(ambiguous) < max_examples:
        remaining = [record for record in records if record not in ambiguous]
        remaining.sort(key=lambda item: abs(float(item.get("confidence", 0.5)) - 0.5))
        ambiguous.extend(remaining[: max(0, max_examples - len(ambiguous))])
    selected = ambiguous[:max_examples]
    selected_ids = {str(record["id"]) for record in selected}
    selected_examples = [example for example in examples if str(example.get("id")) in selected_ids]

    summary = {
        "benchmark": benchmark,
        "screening_pool": len(records),
        "selected_examples": len(selected_examples),
        "ambiguity_interval": [low, high],
        "mean_screen_confidence": sum(float(record["confidence"]) for record in selected) / len(selected) if selected else 0.0,
        "mean_screen_accuracy": sum(int(record["correct"]) for record in selected) / len(selected) if selected else 0.0,
        "selected_ids": sorted(selected_ids),
    }
    dump_json(summary, output_path / f"{benchmark}_screening_summary.json")
    return {
        "summary": summary,
        "examples": selected_examples,
        "records_by_id": {str(record["id"]): record for record in records},
    }


def _group_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["benchmark"]), str(row["model"]), str(row["condition"]), str(row["cot_length"]))
        grouped.setdefault(key, []).append(row)
    out = []
    for benchmark, model, condition, cot_length in sorted(grouped):
        out.append(
            {
                "benchmark": benchmark,
                "model": model,
                "condition": condition,
                "cot_length": cot_length,
                "rows": grouped[(benchmark, model, condition, cot_length)],
            }
        )
    return out


def run_real_generation_experiment(
    *,
    config: GenerationConfig,
    benchmarks: list[str],
    output_dir: str | Path,
    wikicontradict_max: int = 200,
    conflictbank_max: int = 500,
    conflictbank_screening_pool: int = 1200,
    ambiguity_low: float = 0.2,
    ambiguity_high: float = 0.8,
    resume: bool = True,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    selection: dict[str, dict[str, Any]] = {}
    if "wikicontradict" in benchmarks:
        wiki_examples = load_arbitration_dataset("wikicontradict", max_examples=wikicontradict_max)
        selection["wikicontradict"] = {
            "summary": {
                "benchmark": "wikicontradict",
                "screening_pool": len(wiki_examples),
                "selected_examples": len(wiki_examples),
                "selection_rule": "first_n",
            },
            "examples": wiki_examples,
            "records_by_id": {},
        }
    if "conflictbank" in benchmarks:
        selection["conflictbank"] = screen_conflict_examples(
            benchmark="conflictbank",
            config=config,
            low=ambiguity_low,
            high=ambiguity_high,
            max_examples=conflictbank_max,
            screening_pool=conflictbank_screening_pool,
            output_dir=output_path,
            resume=resume,
        )

    raw_generations_path = output_path / "theorem3_generation_rows.jsonl"
    existing = _load_jsonl_map(raw_generations_path, ("benchmark", "id", "condition", "cot_length", "model")) if resume else {}

    generated_rows: list[dict[str, Any]] = list(existing.values())
    for benchmark in benchmarks:
        selected = selection.get(benchmark, {})
        examples = list(selected.get("examples", []))
        screening_records = selected.get("records_by_id", {})
        for example in examples:
            metadata = dict(example.get("metadata", {}))
            gold_answers = _answer_set(example.get("answers"))
            parametric_answers = _answer_set(metadata.get("parametric_answers") or example.get("answers"))
            aligned_answers = _answer_set(metadata.get("aligned_context_answers") or example.get("answers"))
            conflict_answers = _answer_set(metadata.get("conflict_context_answers"))
            screening_record = screening_records.get(str(example.get("id")), {})
            for condition in ("aligned_context", "conflict_context"):
                split = "no_conflict" if condition == "aligned_context" else "conflict"
                context_answers = aligned_answers if condition == "aligned_context" else conflict_answers
                context_reliability = 0.84 if condition == "aligned_context" else 0.24
                for style in (PROMPT_STYLES["no_cot"], PROMPT_STYLES["short_cot"], PROMPT_STYLES["long_cot"]):
                    key = (
                        benchmark,
                        str(example.get("id")),
                        condition,
                        str(style.cot_length),
                        config.model,
                    )
                    cached = existing.get(key)
                    if cached is None:
                        raw_response, usage = _generate_response(example, style=style, condition=condition, config=config)
                        answer = _extract_answer(raw_response)
                        confidence = _extract_confidence(raw_response)
                        if confidence is None:
                            confidence = 0.5
                        reasoning = _extract_reasoning(raw_response)
                        correct = _answers_match(answer, gold_answers)
                        oracle_prob, model_prob = _arbitration_probability(
                            answer,
                            parametric_answers=parametric_answers,
                            context_answers=context_answers,
                            split=split,
                        )
                        cached = {
                            "benchmark": benchmark,
                            "model": config.model,
                            "condition": condition,
                            "cot_length": style.cot_length,
                            "cot_label": style.label,
                            "id": str(example.get("id")),
                            "question": example.get("question"),
                            "split": split,
                            "label": int(correct),
                            "outcome": int(correct),
                            "confidence": float(confidence),
                            "answer": answer,
                            "gold_answers": sorted(gold_answers),
                            "raw_response": raw_response,
                            "reasoning_text": reasoning,
                            "reasoning_word_count": _count_words(reasoning),
                            "reasoning_char_count": len(reasoning),
                            "response_word_count": _count_words(raw_response),
                            "response_char_count": len(raw_response),
                            "oracle_context_probability": oracle_prob,
                            "model_context_probability": model_prob,
                            "metadata": {
                                **metadata,
                                "screening_confidence": screening_record.get("confidence"),
                                "screening_correct": screening_record.get("correct"),
                                "screening_answer": screening_record.get("answer"),
                            },
                            "features": {
                                "parametric_score": float(screening_record.get("confidence", 0.5)),
                                "context_reliability": context_reliability,
                                "conflict_strength": float(metadata.get("conflict_strength", 0.5)),
                                "screening_correct": bool(screening_record.get("correct", 0)),
                                "matched_parametric_answer": _answers_match(answer, parametric_answers),
                                "matched_context_answer": _answers_match(answer, context_answers),
                            },
                            "policies": {
                                "simulated_model": {
                                    "probability": float(confidence),
                                    "regret": None,
                                    "kl_gap": None,
                                }
                            },
                            "regret_by_policy": {},
                            "usage": usage,
                        }
                        _append_jsonl(raw_generations_path, cached)
                    generated_rows.append(cached)

    deduped = { _generation_key(record): record for record in generated_rows }
    rows = list(deduped.values())
    payload = {
        "experiment_name": "theorem3_real_generation_r1_7b",
        "metadata": {
            "mode": "real_generation",
            "backend": config.backend,
            "model": config.model,
            "benchmarks": benchmarks,
            "cot_styles": [
                {"label": style.label, "cot_length": style.cot_length, "max_tokens": style.max_tokens}
                for style in PROMPT_STYLES.values()
            ],
            "ambiguity_interval": [ambiguity_low, ambiguity_high],
            "wikicontradict_max": wikicontradict_max,
            "conflictbank_max": conflictbank_max,
            "conflictbank_screening_pool": conflictbank_screening_pool,
            "screening": {benchmark: selection[benchmark]["summary"] for benchmark in selection},
        },
        "experiments": _group_rows(rows),
    }
    dump_json(payload, output_path / "theorem3_real_generation_results.json")
    return payload
