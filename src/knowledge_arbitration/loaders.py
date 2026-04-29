"""Dataset loading helpers for knowledge arbitration experiments."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Callable

from huggingface_hub import hf_hub_download, hf_hub_url
from datasets import load_dataset
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


def _load_triviaqa(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("trivia_qa", "rc.nocontext")["validation"]
    rows = []
    for row in dataset:
        answer = row.get("answer", {}) or {}
        aliases = _parse_string_list(answer.get("aliases"))
        gold_answer = str(answer.get("value", "")).strip()
        if gold_answer and gold_answer not in aliases:
            aliases = [gold_answer] + aliases
        search_results = row.get("search_results", {}) or {}
        titles = _parse_string_list(search_results.get("title"))
        descriptions = _parse_string_list(search_results.get("description"))
        snippets = []
        for title, description in zip(titles[:2], descriptions[:2]):
            text = " ".join(part for part in [title, description] if part)
            if text.strip():
                snippets.append(text.strip())
        aligned_text = snippets[0] if snippets else ""
        conflict_text = snippets[1] if len(snippets) > 1 else aligned_text
        rows.append(
            {
                "id": str(row.get("question_id", row.get("id", f"triviaqa_{len(rows)}"))),
                "question": str(row.get("question", "")).strip(),
                "answers": aliases or ([gold_answer] if gold_answer else []),
                "contexts": [text for text in [aligned_text, conflict_text] if text],
                "condition": "triviaqa",
                "metadata": {
                    "benchmark": "triviaqa",
                    "parametric_answers": aliases or ([gold_answer] if gold_answer else []),
                    "aligned_context_answers": aliases or ([gold_answer] if gold_answer else []),
                    "conflict_context_answers": [],
                    "aligned_context_text": aligned_text,
                    "conflict_context_text": conflict_text,
                    "supports_conditions": ["closed_book", "aligned_context", "irrelevant_noise"],
                    "popularity_score": 0.62,
                    "dynamicity_score": 0.12,
                    "conflict_strength": 0.22,
                    "question_source": str(row.get("question_source", "")),
                },
            }
        )
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


def _load_hotpotqa(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("hotpot_qa", "distractor")["validation"]
    rows = []
    for row in dataset:
        contexts = row.get("context", {}) or {}
        titles = _parse_string_list(contexts.get("title"))
        sentences = contexts.get("sentences", []) or []
        supporting = row.get("supporting_facts", {}) or {}
        support_titles = set(_parse_string_list(supporting.get("title")))

        aligned_blocks: list[str] = []
        distractor_blocks: list[str] = []
        for title, sentence_list in zip(titles, sentences):
            text = " ".join(str(sentence).strip() for sentence in sentence_list if str(sentence).strip()).strip()
            if not text:
                continue
            block = f"{title}: {text}" if title else text
            if title in support_titles and len(aligned_blocks) < 2:
                aligned_blocks.append(block)
            elif len(distractor_blocks) < 2:
                distractor_blocks.append(block)

        aligned_text = "\n\n".join(aligned_blocks[:2]).strip()
        conflict_text = "\n\n".join(distractor_blocks[:2]).strip() or aligned_text
        answer = str(row.get("answer", "")).strip()
        rows.append(
            {
                "id": str(row.get("id", f"hotpotqa_{len(rows)}")),
                "question": str(row.get("question", "")).strip(),
                "answers": [answer] if answer else [],
                "contexts": [text for text in [aligned_text, conflict_text] if text],
                "condition": "hotpotqa_distractor",
                "metadata": {
                    "benchmark": "hotpotqa",
                    "parametric_answers": [answer] if answer else [],
                    "aligned_context_answers": [answer] if answer else [],
                    "conflict_context_answers": [],
                    "aligned_context_text": aligned_text,
                    "conflict_context_text": conflict_text,
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context", "irrelevant_noise"],
                    "popularity_score": 0.48,
                    "dynamicity_score": 0.18,
                    "conflict_strength": 0.58,
                    "type": str(row.get("type", "")),
                    "level": str(row.get("level", "")),
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _load_tabmwp(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("JiaerX/TabMWP")["train"]
    rows = []
    for row in dataset:
        question = str(row.get("question", "")).strip()
        answer = str(row.get("answer", "")).strip()
        options = _parse_string_list(row.get("options"))
        conflict_answer = ""
        if options:
            for option in options:
                if option != answer:
                    conflict_answer = option
                    break
        aligned_text = f"Table reasoning problem: {question}"
        conflict_text = f"Alternative answer proposal: {conflict_answer}" if conflict_answer else aligned_text
        rows.append(
            {
                "id": str(row.get("id", f"tabmwp_{len(rows)}")),
                "question": question,
                "answers": [answer] if answer else [],
                "contexts": [aligned_text, conflict_text],
                "condition": "tabmwp",
                "metadata": {
                    "benchmark": "tabmwp",
                    "parametric_answers": [answer] if answer else [],
                    "aligned_context_answers": [answer] if answer else [],
                    "conflict_context_answers": [conflict_answer] if conflict_answer else [],
                    "aligned_context_text": aligned_text,
                    "conflict_context_text": conflict_text,
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.30,
                    "dynamicity_score": 0.05,
                    "conflict_strength": 0.52,
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


def _load_gpqa(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("ariaattarml/verified-reasoning-o1-gpqa-mmlu-pro")["train"]
    rows = []
    for index, row in enumerate(dataset):
        question = str(row.get("original_question", "")).strip()
        gold_answer = str(row.get("correct_answer", "")).strip()
        model_answer = str(row.get("model_answer", "")).strip()
        reasoning = str(row.get("assistant_response", "")).strip()
        aligned_text = reasoning
        conflict_text = f"Candidate answer from a competing solver: {model_answer}" if model_answer else reasoning
        rows.append(
            {
                "id": f"gpqa_{index}",
                "question": question,
                "answers": [gold_answer] if gold_answer else [],
                "contexts": [text for text in [aligned_text, conflict_text] if text],
                "condition": "gpqa",
                "metadata": {
                    "benchmark": "gpqa",
                    "parametric_answers": [gold_answer] if gold_answer else [],
                    "aligned_context_answers": [gold_answer] if gold_answer else [],
                    "conflict_context_answers": [model_answer] if model_answer and model_answer != gold_answer else [],
                    "aligned_context_text": aligned_text,
                    "conflict_context_text": conflict_text,
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.18,
                    "dynamicity_score": 0.06,
                    "conflict_strength": 0.61,
                    "source": str(row.get("source", "")),
                    "preferred": bool(row.get("preferred", False)),
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _load_climatex(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("rlacombe/ClimateX")["train"]
    rows = []
    for index, row in enumerate(dataset):
        statement = str(row.get("statement", "")).strip()
        confidence = str(row.get("confidence", "")).strip()
        score = str(row.get("score", "")).strip()
        answer = confidence or score or "supported"
        aligned_text = f"Climate report excerpt: {statement}"
        conflict_text = f"Climate confidence annotation: {confidence}; score: {score}"
        rows.append(
            {
                "id": f"climatex_{index}",
                "question": f"What confidence should we place in the following climate statement? {statement}",
                "answers": [answer],
                "contexts": [aligned_text, conflict_text],
                "condition": "climatex",
                "metadata": {
                    "benchmark": "climatex",
                    "parametric_answers": [answer],
                    "aligned_context_answers": [answer],
                    "conflict_context_answers": [],
                    "aligned_context_text": aligned_text,
                    "conflict_context_text": conflict_text,
                    "supports_conditions": ["closed_book", "aligned_context", "irrelevant_noise"],
                    "popularity_score": 0.12,
                    "dynamicity_score": 0.26,
                    "conflict_strength": 0.44,
                    "report": str(row.get("report", "")),
                    "page_num": int(row.get("page_num", 0) or 0),
                    "split": str(row.get("split", "")),
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _load_memotrap(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("Albertmade/memo-trap")
    split = dataset["train"]
    rows = []
    for index, row in enumerate(split):
        choices = [str(item).strip() for item in row.get("classes", []) if str(item).strip()]
        if len(choices) < 2:
            continue
        answer_index = int(row.get("answer_index", 0))
        answer_index = max(0, min(answer_index, len(choices) - 1))
        gold_answer = choices[answer_index]
        distractors = [choice for idx, choice in enumerate(choices) if idx != answer_index]
        conflict_answer = distractors[0] if distractors else ""
        prompt = str(row.get("prompt", "")).strip()
        rows.append(
            {
                "id": f"memotrap_{index}",
                "question": prompt,
                "answers": [gold_answer],
                "contexts": [f"{prompt}{gold_answer}", f"{prompt}{conflict_answer}"],
                "condition": "memotrap",
                "metadata": {
                    "benchmark": "memotrap",
                    "parametric_answers": [gold_answer],
                    "aligned_context_answers": [gold_answer],
                    "conflict_context_answers": [conflict_answer] if conflict_answer else [],
                    "aligned_context_text": f"{prompt}{gold_answer}",
                    "conflict_context_text": f"{prompt}{conflict_answer}" if conflict_answer else prompt,
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.45,
                    "dynamicity_score": 0.08,
                    "conflict_strength": 0.74,
                    "round": int(row.get("round", 0)),
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _load_faitheval(max_examples: int | None = None) -> list[dict[str, Any]]:
    rows = []

    counterfactual = load_dataset("Salesforce/FaithEval-counterfactual-v1.0")["test"]
    for row in counterfactual:
        choices = row.get("choices", {}) or {}
        labels = [str(item).strip() for item in choices.get("label", [])]
        texts = [str(item).strip() for item in choices.get("text", [])]
        choice_map = {label: text for label, text in zip(labels, texts)}
        gold_answer = str(row.get("answer", "")).strip() or choice_map.get(str(row.get("answerKey", "")).strip(), "")
        distractors = [text for text in texts if text and text != gold_answer]
        rows.append(
            {
                "id": str(row.get("id", f"cf_{len(rows)}")),
                "question": str(row.get("question", "")).strip(),
                "answers": [gold_answer] if gold_answer else [],
                "contexts": [str(row.get("context", "")).strip()],
                "condition": "faitheval_counterfactual",
                "metadata": {
                    "benchmark": "faitheval",
                    "subset": "counterfactual",
                    "parametric_answers": [gold_answer] if gold_answer else [],
                    "aligned_context_answers": [gold_answer] if gold_answer else [],
                    "conflict_context_answers": distractors[:1],
                    "aligned_context_text": str(row.get("context", "")).strip(),
                    "conflict_context_text": str(row.get("context", "")).strip(),
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.5,
                    "dynamicity_score": 0.25,
                    "conflict_strength": 0.72,
                    "justification": str(row.get("justification", "")),
                },
            }
        )

    inconsistent = load_dataset("Salesforce/FaithEval-inconsistent-v1.0")["test"]
    for row in inconsistent:
        answers = _parse_string_list(row.get("answers"))
        if not answers:
            continue
        gold_answer = answers[0]
        conflict_answers = answers[1:] or answers[:1]
        rows.append(
            {
                "id": str(row.get("qid", f"inc_{len(rows)}")),
                "question": str(row.get("question", "")).strip(),
                "answers": [gold_answer],
                "contexts": [str(row.get("context", "")).strip()],
                "condition": "faitheval_inconsistent",
                "metadata": {
                    "benchmark": "faitheval",
                    "subset": "inconsistent",
                    "parametric_answers": [gold_answer],
                    "aligned_context_answers": [gold_answer],
                    "conflict_context_answers": conflict_answers,
                    "aligned_context_text": str(row.get("context", "")).strip(),
                    "conflict_context_text": str(row.get("context", "")).strip(),
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.48,
                    "dynamicity_score": 0.22,
                    "conflict_strength": 0.81,
                    "justification": str(row.get("justification", "")),
                },
            }
        )

    unanswerable = load_dataset("Salesforce/FaithEval-unanswerable-v1.0")["test"]
    for row in unanswerable:
        rows.append(
            {
                "id": str(row.get("qid", f"un_{len(rows)}")),
                "question": str(row.get("question", "")).strip(),
                "answers": _parse_string_list(row.get("answers")) or ["unanswerable"],
                "contexts": [str(row.get("context", "")).strip()],
                "condition": "faitheval_unanswerable",
                "metadata": {
                    "benchmark": "faitheval",
                    "subset": "unanswerable",
                    "parametric_answers": ["unanswerable"],
                    "aligned_context_answers": ["unanswerable"],
                    "conflict_context_answers": [],
                    "aligned_context_text": str(row.get("context", "")).strip(),
                    "conflict_context_text": str(row.get("context", "")).strip(),
                    "supports_conditions": ["closed_book", "aligned_context"],
                    "popularity_score": 0.42,
                    "dynamicity_score": 0.18,
                    "conflict_strength": 0.34,
                    "justification": str(row.get("justification", "")),
                },
            }
        )

    return _limit_rows(rows, max_examples)


def _load_ambigdocs(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("duynht/ambigdocs_answerability")["test"]
    rows = []
    for row in dataset:
        answers = _parse_string_list(row.get("answer"))
        if not answers:
            continue
        gold_answer = answers[0]
        conflict_answers = answers[1:]
        retrieved_documents = row.get("retrieved_documents", []) or []
        aligned_text = ""
        conflict_text = ""
        if retrieved_documents:
            aligned_text = str(retrieved_documents[0].get("text", "")).strip()
        if len(retrieved_documents) > 1:
            conflict_text = str(retrieved_documents[1].get("text", "")).strip()
        elif aligned_text:
            conflict_text = aligned_text
        rows.append(
            {
                "id": str(row.get("qid", f"ambigdocs_{len(rows)}")),
                "question": str(row.get("question", "")).strip(),
                "answers": [gold_answer],
                "contexts": [doc.get("text", "") for doc in retrieved_documents[:2]],
                "condition": "ambigdocs",
                "metadata": {
                    "benchmark": "ambigdocs",
                    "parametric_answers": [gold_answer],
                    "aligned_context_answers": [gold_answer],
                    "conflict_context_answers": conflict_answers[:1],
                    "aligned_context_text": aligned_text,
                    "conflict_context_text": conflict_text,
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.44,
                    "dynamicity_score": 0.12,
                    "conflict_strength": 0.69,
                    "is_disambiguated": bool(row.get("is_disambiguated", False)),
                    "num_documents": int(row.get("num_documents", 0) or 0),
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _load_ramdocs(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("HanNight/RAMDocs")["test"]
    rows = []
    for index, row in enumerate(dataset):
        gold_answers = _parse_string_list(row.get("gold_answers"))
        wrong_answers = _parse_string_list(row.get("wrong_answers"))
        documents = row.get("documents", []) or []
        contexts = [str(doc.get("text", "")).strip() for doc in documents[:3] if str(doc.get("text", "")).strip()]
        aligned_text = contexts[0] if contexts else ""
        conflict_text = contexts[1] if len(contexts) > 1 else aligned_text
        rows.append(
            {
                "id": f"ramdocs_{index}",
                "question": str(row.get("question", "")).strip(),
                "answers": gold_answers,
                "contexts": contexts,
                "condition": "ramdocs",
                "metadata": {
                    "benchmark": "ramdocs",
                    "parametric_answers": gold_answers,
                    "aligned_context_answers": gold_answers,
                    "conflict_context_answers": wrong_answers,
                    "aligned_context_text": aligned_text,
                    "conflict_context_text": conflict_text,
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.41,
                    "dynamicity_score": 0.14,
                    "conflict_strength": 0.77,
                    "disambig_entity": _parse_string_list(row.get("disambig_entity")),
                },
            }
        )
    return _limit_rows(rows, max_examples)


def _load_clasheval(max_examples: int | None = None) -> list[dict[str, Any]]:
    dataset = load_dataset("sagnikrayc/clasheval")["train"]
    rows = []
    for index, row in enumerate(dataset):
        original_answer = str(row.get("answer_original", "")).strip()
        modified_answer = str(row.get("answer_mod", "")).strip()
        rows.append(
            {
                "id": f"clasheval_{index}",
                "question": str(row.get("question", "")).strip(),
                "answers": [original_answer] if original_answer else [],
                "contexts": [str(row.get("context_original", "")).strip(), str(row.get("context_mod", "")).strip()],
                "condition": "clasheval",
                "metadata": {
                    "benchmark": "clasheval",
                    "parametric_answers": [original_answer] if original_answer else [],
                    "aligned_context_answers": [original_answer] if original_answer else [],
                    "conflict_context_answers": [modified_answer] if modified_answer else [],
                    "aligned_context_text": str(row.get("context_original", "")).strip(),
                    "conflict_context_text": str(row.get("context_mod", "")).strip(),
                    "supports_conditions": ["closed_book", "aligned_context", "conflict_context"],
                    "popularity_score": 0.5,
                    "dynamicity_score": 0.2,
                    "conflict_strength": min(max(float(row.get("mod_degree", 3)) / 4.0, 0.45), 0.95),
                    "dataset": str(row.get("dataset", "")),
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
    "ambigdocs": _load_ambigdocs,
    "climatex": _load_climatex,
    "clasheval": _load_clasheval,
    "conflictbank": _load_conflictbank,
    "dynamicqa": _load_dynamicqa,
    "faitheval": _load_faitheval,
    "gpqa": _load_gpqa,
    "hotpotqa": _load_hotpotqa,
    "memotrap": _load_memotrap,
    "nq_swap": _load_nq_swap,
    "popqa": _load_popqa,
    "ramdocs": _load_ramdocs,
    "tabmwp": _load_tabmwp,
    "triviaqa": _load_triviaqa,
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
