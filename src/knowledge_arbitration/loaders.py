"""Dataset loading helpers for knowledge arbitration experiments."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Callable

from huggingface_hub import hf_hub_download, hf_hub_url
import pandas as pd
import requests


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _parse_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if item is not None and str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = ast.literal_eval(stripped)
            except (SyntaxError, ValueError):
                parsed = None
            if isinstance(parsed, list):
                return [str(item) for item in parsed if item is not None and str(item).strip()]
        return [stripped]
    return [str(value)]


def _numeric_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _limit_rows(rows: list[dict[str, Any]], max_examples: int | None) -> list[dict[str, Any]]:
    if max_examples is None or max_examples <= 0:
        return rows
    return rows[: max_examples]


def normalize_arbitration_example(row: dict[str, Any], index: int = 0) -> dict[str, Any]:
    """Normalize one local QA/conflict example into a stable schema."""

    question = row.get("question") or row.get("query") or row.get("prompt") or ""
    answers = _ensure_list(
        row.get("answers")
        if "answers" in row
        else row.get("gold_answers")
        if "gold_answers" in row
        else row.get("gold")
        if "gold" in row
        else row.get("answer")
        if "answer" in row
        else row.get("target")
    )
    contexts = _ensure_list(
        row.get("contexts")
        if "contexts" in row
        else row.get("retrieved_contexts")
        if "retrieved_contexts" in row
        else row.get("evidence")
        if "evidence" in row
        else row.get("context")
    )
    return {
        "id": row.get("id") or row.get("question_id") or row.get("uid") or f"example_{index}",
        "question": question,
        "answers": [str(item) for item in answers if item is not None],
        "contexts": [str(item) if not isinstance(item, dict) else json.dumps(item, sort_keys=True) for item in contexts],
        "condition": row.get("condition") or row.get("conflict_type") or row.get("label") or "unknown",
        "metadata": {
            key: value
            for key, value in row.items()
            if key
            not in {
                "id",
                "question_id",
                "uid",
                "question",
                "query",
                "prompt",
                "answers",
                "gold_answers",
                "gold",
                "answer",
                "target",
                "contexts",
                "retrieved_contexts",
                "evidence",
                "context",
                "condition",
                "conflict_type",
                "label",
            }
        },
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rows.append(json.loads(stripped))
    return rows


def _load_local_dataset(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        raw_rows = _load_jsonl(path)
    elif path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            raw_rows = raw
        elif isinstance(raw, dict) and isinstance(raw.get("data"), list):
            raw_rows = raw["data"]
        else:
            raise ValueError(f"Unsupported JSON structure for arbitration dataset: {path}")
    else:
        raise ValueError(f"Unsupported arbitration dataset format: {path}")
    return [normalize_arbitration_example(row, index=index) for index, row in enumerate(raw_rows)]


def _load_popqa(max_examples: int | None = None) -> list[dict[str, Any]]:
    path = hf_hub_download(repo_id="akariasai/PopQA", filename="test.tsv", repo_type="dataset")
    frame = pd.read_csv(path, sep="\t")
    rows = []
    for _, row in frame.iterrows():
        possible_answers = _parse_string_list(row.get("possible_answers"))
        popularity = _numeric_or_none(row.get("s_pop")) or 0.0
        rows.append(
            {
                "id": str(row["id"]),
                "question": str(row["question"]),
                "answers": possible_answers,
                "contexts": [],
                "condition": "closed_book",
                "metadata": {
                    "benchmark": "popqa",
                    "parametric_answers": possible_answers,
                    "aligned_context_answers": possible_answers,
                    "conflict_context_answers": [],
                    "supports_conditions": ["closed_book", "aligned_context"],
                    "popularity_score": popularity,
                    "dynamicity_score": 0.05,
                    "conflict_strength": 0.12,
                    "subject": str(row.get("subj", "")),
                    "relation": str(row.get("prop", "")),
                    "object": str(row.get("obj", "")),
                    "subject_popularity": popularity,
                    "object_popularity": _numeric_or_none(row.get("o_pop")) or 0.0,
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _dynamicqa_partition_rows(partition: str) -> list[dict[str, Any]]:
    filename = f"{partition}.csv"
    path = hf_hub_download(repo_id="copenlu/dynamicqa", filename=filename, repo_type="dataset")
    frame = pd.read_csv(path)
    partition_strength = {"static": 0.18, "temporal": 0.72, "disputable": 0.66}[partition]
    rows = []
    for _, row in frame.iterrows():
        question = str(row["question"])
        template = str(row["context"])
        gold_answer = str(row["obj"])
        conflict_answer = str(row["replace_name"])
        rows.append(
            {
                "id": f"{partition}_{row['id']}",
                "question": question,
                "answers": [gold_answer],
                "contexts": [template.replace("[ENTITY]", gold_answer)],
                "condition": partition,
                "metadata": {
                    "benchmark": "dynamicqa",
                    "partition": partition,
                    "parametric_answers": [gold_answer],
                    "aligned_context_answers": [gold_answer],
                    "conflict_context_answers": [conflict_answer],
                    "aligned_context_text": template.replace("[ENTITY]", gold_answer),
                    "conflict_context_text": template.replace("[ENTITY]", conflict_answer),
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context", "irrelevant_noise"],
                    "popularity_score": _numeric_or_none(row.get("s_pop")) or 0.0,
                    "dynamicity_score": _numeric_or_none(row.get("num_edits")) or 0.0,
                    "conflict_strength": partition_strength,
                    "subject": str(row.get("subj", "")),
                },
            }
        )
    return rows


def _load_dynamicqa(max_examples: int | None = None) -> list[dict[str, Any]]:
    rows = []
    for partition in ("static", "temporal", "disputable"):
        rows.extend(_dynamicqa_partition_rows(partition))
    rows.sort(key=lambda item: (str(item["metadata"].get("partition")), str(item["id"])))
    return _limit_rows(rows, max_examples)


def _load_nq_swap(max_examples: int | None = None) -> list[dict[str, Any]]:
    path = hf_hub_download(repo_id="younanna/NQ-Swap", filename="data/dev-00000-of-00001.parquet", repo_type="dataset")
    frame = pd.read_parquet(path)
    rows = []
    for _, row in frame.iterrows():
        original_answers = _parse_string_list(row.get("original_answers"))
        substituted_answers = _parse_string_list(row.get("substituted_answers"))
        substitution_type = str(row.get("substitution_type", "unknown"))
        conflict_strength = {"alias": 0.48, "entity": 0.72, "corpus": 0.82}.get(substitution_type, 0.65)
        rows.append(
            {
                "id": str(row["id"]),
                "question": str(row["question"]),
                "answers": original_answers,
                "contexts": [str(row.get("original_context", ""))],
                "condition": "entity_swap",
                "metadata": {
                    "benchmark": "nq_swap",
                    "parametric_answers": original_answers,
                    "aligned_context_answers": original_answers,
                    "conflict_context_answers": substituted_answers,
                    "aligned_context_text": str(row.get("original_context", "")),
                    "conflict_context_text": str(row.get("substituted_context", "")),
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.55,
                    "dynamicity_score": 0.2,
                    "conflict_strength": conflict_strength,
                    "substitution_type": substitution_type,
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _load_wikicontradict(max_examples: int | None = None) -> list[dict[str, Any]]:
    path = hf_hub_download(
        repo_id="ibm-research/Wikipedia_contradict_benchmark",
        filename="WikiContradict_dataset_v1_rag_qa.csv",
        repo_type="dataset",
    )
    frame = pd.read_csv(path)
    rows = []
    for _, row in frame.iterrows():
        ref_answers = [part.strip() for part in str(row.get("ref_answer", "")).split("|") if part.strip()]
        answer1 = str(row.get("answer1", "")).strip()
        answer2 = str(row.get("answer2", "")).strip()
        contradict_type = str(row.get("contradictType", "unknown"))
        conflict_strength = 0.85 if "explicit" in contradict_type.lower() else 0.68
        rows.append(
            {
                "id": str(row["question_ID"]),
                "question": str(row["question"]),
                "answers": ref_answers or [answer1, answer2],
                "contexts": [str(row.get("context1", "")), str(row.get("context2", ""))],
                "condition": "contradiction",
                "metadata": {
                    "benchmark": "wikicontradict",
                    "parametric_answers": [answer1] if answer1 else [],
                    "aligned_context_answers": [answer1] if answer1 else [],
                    "conflict_context_answers": [answer2] if answer2 else [],
                    "aligned_context_text": str(row.get("context1", "")),
                    "conflict_context_text": str(row.get("context2", "")),
                    "supports_conditions": ["aligned_context", "conflict_context"],
                    "popularity_score": 0.5,
                    "dynamicity_score": 0.35,
                    "conflict_strength": conflict_strength,
                    "contradict_type": contradict_type,
                    "same_passage": str(row.get("samepassage", "")),
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _stream_conflictbank_rows(max_examples: int | None = None) -> list[dict[str, Any]]:
    url = hf_hub_url(repo_id="Warrieryes/CB_qa", filename="QA_dataset.json", repo_type="dataset")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    raw_rows = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        raw_rows.append(json.loads(line))
        if max_examples is not None and len(raw_rows) >= max_examples:
            break
    return raw_rows


def _load_conflictbank(max_examples: int | None = None) -> list[dict[str, Any]]:
    raw = _stream_conflictbank_rows(max_examples=max_examples)
    rows = []
    for index, row in enumerate(raw):
        correct_option = str(row.get("correct_option", "")).strip()
        replace_option = str(row.get("replace_option", "")).strip()
        uncertain_option = str(row.get("uncertain_option", "")).strip()
        options = _parse_string_list(row.get("options"))
        option_map = {}
        for option_index, option_value in enumerate(options):
            option_map[chr(ord("A") + option_index)] = option_value
        gold_answer = option_map.get(correct_option, correct_option)
        conflict_answer = option_map.get(replace_option, replace_option)
        conflict_specs = [
            (
                "misinformation",
                str(row.get("misinformation_conflict_evidence_evidence", "")),
                str(row.get("misinformation_conflict_claim", "")),
                0.92,
            ),
            (
                "temporal",
                str(row.get("temporal_conflict_evidence", "")),
                str(row.get("temporal_conflict_claim", "")),
                0.76,
            ),
            (
                "semantic",
                str(row.get("semantic_conflict_evidence", "")),
                str(row.get("semantic_conflict_claim", "")),
                0.68,
            ),
        ]
        for conflict_family, conflict_context, conflict_claim, conflict_strength in conflict_specs:
            if not conflict_context.strip():
                continue
            rows.append(
                {
                    "id": f"{index}_{conflict_family}",
                    "question": str(row.get("question", "")),
                    "answers": [gold_answer] if gold_answer else [],
                    "contexts": [str(row.get("default_evidence", "")), conflict_context],
                    "condition": f"conflictbank_{conflict_family}",
                    "metadata": {
                        "benchmark": "conflictbank",
                        "conflict_family": conflict_family,
                        "parametric_answers": [gold_answer] if gold_answer else [],
                        "aligned_context_answers": [gold_answer] if gold_answer else [],
                        "conflict_context_answers": [conflict_answer] if conflict_answer else [],
                        "aligned_context_text": str(row.get("default_evidence", "")),
                        "conflict_context_text": conflict_context,
                        "supports_conditions": ["aligned_context", "conflict_context"],
                        "popularity_score": 0.5,
                        "dynamicity_score": 0.5 if conflict_family != "temporal" else 0.9,
                        "conflict_strength": conflict_strength,
                        "relation": str(row.get("relation", "")),
                        "default_claim": str(row.get("default_claim", "")),
                        "conflict_claim": conflict_claim,
                        "uncertain_answer": option_map.get(uncertain_option, uncertain_option),
                    },
                }
            )
    return rows


BUILTIN_LOADERS: dict[str, Callable[[int | None], list[dict[str, Any]]]] = {
    "conflictbank": _load_conflictbank,
    "dynamicqa": _load_dynamicqa,
    "nq_swap": _load_nq_swap,
    "popqa": _load_popqa,
    "wikicontradict": _load_wikicontradict,
}


def load_arbitration_dataset(
    dataset_name: str,
    dataset_path: str | Path | None = None,
    *,
    max_examples: int | None = None,
) -> list[dict[str, Any]]:
    """Load an arbitration dataset from a built-in connector or local JSON/JSONL."""

    if dataset_path is not None:
        return _limit_rows(_load_local_dataset(Path(dataset_path)), max_examples)

    loader = BUILTIN_LOADERS.get(dataset_name)
    if loader is None:
        raise ValueError(
            f"Dataset '{dataset_name}' does not yet have a built-in connector. "
            "Pass a local JSON or JSONL path explicitly."
        )
    return loader(max_examples)
