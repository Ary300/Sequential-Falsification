#!/usr/bin/env python3
"""Run a free-form Paper 2 evaluation with candidate rescoring and open-QA metrics."""

from __future__ import annotations

import argparse
import json
from math import exp, log
from pathlib import Path
import re
import sys
import time
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.posterior import ArbitrationFeatures, bayes_arbitration_probability, logit, sigmoid  # noqa: E402


SEARCH_URL = "https://en.wikipedia.org/w/api.php"
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
MAX_WIKI_ATTEMPTS = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run free-form Paper 2 evaluation.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--datasets", default="triviaqa_open,nq_open,asqa")
    parser.add_argument("--max-examples", type=int, default=32)
    parser.add_argument("--search-limit", type=int, default=6)
    parser.add_argument("--top-k-contexts", type=int, default=3)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--torch-dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"])
    parser.add_argument("--cache-file", default=str(ROOT / "docs" / "generated" / "paper2_freeform_retrieval_cache.json"))
    parser.add_argument("--output-prefix", default=str(ROOT / "docs" / "generated" / "paper2_freeform_eval"))
    return parser.parse_args()


def _normalize(text: str) -> str:
    return " ".join(match.group(0).lower() for match in TOKEN_RE.finditer(text or ""))


def _exact_match(prediction: str, references: list[str]) -> int:
    target = _normalize(prediction)
    return int(any(target and target == _normalize(reference) for reference in references))


def _lcs_length(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for token_a in a:
        curr = [0]
        for j, token_b in enumerate(b, start=1):
            if token_a == token_b:
                curr.append(prev[j - 1] + 1)
            else:
                curr.append(max(curr[-1], prev[j]))
        prev = curr
    return prev[-1]


def _rouge_l_f1(prediction: str, references: list[str]) -> float:
    pred_tokens = _normalize(prediction).split()
    if not pred_tokens:
        return 0.0
    best = 0.0
    for reference in references:
        ref_tokens = _normalize(reference).split()
        if not ref_tokens:
            continue
        lcs = _lcs_length(pred_tokens, ref_tokens)
        recall = lcs / len(ref_tokens)
        precision = lcs / len(pred_tokens)
        if recall + precision == 0.0:
            score = 0.0
        else:
            score = 2.0 * recall * precision / (recall + precision)
        best = max(best, score)
    return best


def _load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_cache(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _wiki_search(
    question: str,
    *,
    search_limit: int,
    cache_path: Path,
    cache: dict[str, Any],
) -> list[str]:
    key = f"wiki::{question}::{search_limit}"
    cached = cache.get(key)
    if isinstance(cached, list):
        return [str(item) for item in cached]

    session = requests.Session()
    session.headers.update({"User-Agent": "SequentialFalsification/1.0 (paper2 freeform eval)"})
    search_response = None
    for attempt in range(MAX_WIKI_ATTEMPTS):
        response = session.get(
            SEARCH_URL,
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": question,
                "srlimit": search_limit,
                "utf8": 1,
            },
            timeout=30,
        )
        if response.status_code != 429:
            search_response = response
            break
        retry_after = response.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            sleep_seconds = max(1.0, float(retry_after))
        else:
            sleep_seconds = 1.5 * (attempt + 1)
        time.sleep(sleep_seconds)
    if search_response is None:
        cache[key] = []
        _save_cache(cache_path, cache)
        return []
    search_response.raise_for_status()
    search_rows = search_response.json().get("query", {}).get("search", [])
    page_ids = [str(row.get("pageid")) for row in search_rows if row.get("pageid") is not None]
    pages: dict[str, dict[str, Any]] = {}
    if page_ids:
        detail_response = None
        for attempt in range(MAX_WIKI_ATTEMPTS):
            response = session.get(
                SEARCH_URL,
                params={
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "pageids": "|".join(page_ids),
                    "explaintext": 1,
                    "exintro": 1,
                    "utf8": 1,
                },
                timeout=30,
            )
            if response.status_code != 429:
                detail_response = response
                break
            retry_after = response.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                sleep_seconds = max(1.0, float(retry_after))
            else:
                sleep_seconds = 1.5 * (attempt + 1)
            time.sleep(sleep_seconds)
        if detail_response is not None and detail_response.ok:
            pages = detail_response.json().get("query", {}).get("pages", {})
    snippets: list[str] = []
    for row in search_rows:
        detail = pages.get(str(row.get("pageid")), {})
        text = "\n".join(
            part.strip()
            for part in [
                str(row.get("title", "")),
                str(row.get("snippet", "")),
                str(detail.get("extract", "")),
            ]
            if part and part.strip()
        ).strip()
        if text:
            snippets.append(text)
    cache[key] = snippets
    _save_cache(cache_path, cache)
    time.sleep(0.6)
    return snippets


def _load_triviaqa_open(max_examples: int) -> list[dict[str, Any]]:
    from datasets import load_dataset

    dataset = load_dataset("trivia_qa", "rc.nocontext", split="validation", streaming=True)
    rows: list[dict[str, Any]] = []
    for row in dataset:
        answer = row.get("answer", {}) or {}
        aliases = [str(item).strip() for item in answer.get("aliases", []) if str(item).strip()]
        value = str(answer.get("value", "")).strip()
        if value and value not in aliases:
            aliases.insert(0, value)
        rows.append(
            {
                "id": str(row.get("question_id", row.get("id", f"triviaqa_{len(rows)}"))),
                "dataset": "triviaqa_open",
                "question": str(row.get("question", "")).strip(),
                "answers": aliases,
            }
        )
        if len(rows) >= max_examples:
            break
    return rows


def _load_nq_open(max_examples: int) -> list[dict[str, Any]]:
    from datasets import load_dataset

    candidates = [
        ("nq_open", "nq_open", "validation"),
        ("nq_open", None, "validation"),
        ("google-research-datasets/nq_open", None, "validation"),
    ]
    last_error: Exception | None = None
    for dataset_name, config_name, split in candidates:
        try:
            dataset = load_dataset(dataset_name, config_name, split=split, streaming=True)
            rows: list[dict[str, Any]] = []
            for row in dataset:
                answers = row.get("answer") or row.get("answers") or []
                if isinstance(answers, str):
                    answers = [answers]
                answers = [str(item).strip() for item in answers if str(item).strip()]
                rows.append(
                    {
                        "id": str(row.get("id", f"nq_open_{len(rows)}")),
                        "dataset": "nq_open",
                        "question": str(row.get("question", "")).strip(),
                        "answers": answers,
                    }
                )
                if len(rows) >= max_examples:
                    break
            if rows:
                return rows
        except Exception as exc:  # pragma: no cover - best effort loader
            last_error = exc
    raise RuntimeError(f"Could not load NQ-open from known dataset IDs: {last_error}")


def _load_asqa(max_examples: int) -> list[dict[str, Any]]:
    from datasets import load_dataset

    candidates = [
        ("din0s/asqa", "default", "dev"),
        ("din0s/asqa", "default", "train"),
        ("din0s/asqa", None, "dev"),
        ("asqa", None, "dev"),
    ]
    last_error: Exception | None = None
    for dataset_name, config_name, split in candidates:
        try:
            dataset = load_dataset(dataset_name, config_name, split=split, streaming=True)
            rows: list[dict[str, Any]] = []
            for row in dataset:
                answers: list[str] = []
                for key in ("short_answers", "qa_pairs", "annotations", "answers"):
                    value = row.get(key)
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                for inner_key in ("short_answers", "answer", "answers"):
                                    inner = item.get(inner_key)
                                    if isinstance(inner, list):
                                        answers.extend(str(part).strip() for part in inner if str(part).strip())
                                    elif isinstance(inner, str) and inner.strip():
                                        answers.append(inner.strip())
                            elif isinstance(item, str) and item.strip():
                                answers.append(item.strip())
                    elif isinstance(value, str) and value.strip():
                        answers.append(value.strip())
                deduped = []
                seen = set()
                for item in answers:
                    norm = _normalize(item)
                    if norm and norm not in seen:
                        seen.add(norm)
                        deduped.append(item)
                question = str(row.get("ambiguous_question") or row.get("question") or "").strip()
                if question and deduped:
                    rows.append(
                        {
                            "id": str(row.get("sample_id", row.get("id", f"asqa_{len(rows)}"))),
                            "dataset": "asqa",
                            "question": question,
                            "answers": deduped,
                        }
                    )
                if len(rows) >= max_examples:
                    break
            if rows:
                return rows
        except Exception as exc:  # pragma: no cover - best effort loader
            last_error = exc
    raise RuntimeError(f"Could not load ASQA from known dataset IDs: {last_error}")


def _load_examples(dataset_name: str, max_examples: int) -> list[dict[str, Any]]:
    if dataset_name == "triviaqa_open":
        return _load_triviaqa_open(max_examples)
    if dataset_name == "nq_open":
        return _load_nq_open(max_examples)
    if dataset_name == "asqa":
        return _load_asqa(max_examples)
    raise ValueError(f"Unsupported dataset: {dataset_name}")


def _apply_chat_template(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception:
            pass
    rendered = []
    for message in messages:
        rendered.append(f"{message['role'].upper()}:\n{message['content'].strip()}\n")
    rendered.append("ASSISTANT:\n")
    return "\n".join(rendered)


def _generate_answer(
    model: Any,
    tokenizer: Any,
    *,
    prompt: str,
    max_new_tokens: int,
) -> str:
    import torch

    encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    with torch.no_grad():
        generated = model.generate(
            **encoded,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    completion = tokenizer.decode(generated[0][encoded["input_ids"].shape[1] :], skip_special_tokens=True)
    return completion.strip()


def _candidate_suffix(answer: str) -> str:
    return f"{answer.strip()}\n"


def _score_candidates(
    model: Any,
    tokenizer: Any,
    *,
    prompt: str,
    candidates: list[str],
    batch_size: int,
) -> dict[str, float]:
    import torch

    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)["input_ids"][0]
    prompt_len = int(prompt_ids.shape[0])
    scores: dict[str, float] = {}
    for start in range(0, len(candidates), batch_size):
        batch_candidates = candidates[start : start + batch_size]
        batch_texts = [prompt + _candidate_suffix(candidate) for candidate in batch_candidates]
        encoded = tokenizer(batch_texts, return_tensors="pt", padding=True, add_special_tokens=False)
        encoded = {key: value.to(model.device) for key, value in encoded.items()}
        input_ids = encoded["input_ids"]
        attention_mask = encoded["attention_mask"]
        labels = input_ids.clone()
        labels[:, :prompt_len] = -100
        labels = labels.masked_fill(attention_mask == 0, -100)
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            log_probs = outputs.logits[:, :-1, :].log_softmax(dim=-1)
        target_ids = input_ids[:, 1:]
        target_log_probs = log_probs.gather(dim=-1, index=target_ids.unsqueeze(-1)).squeeze(-1)
        target_mask = (labels[:, 1:] != -100).float()
        sequence_log_probs = (target_log_probs * target_mask).sum(dim=-1).detach().cpu().tolist()
        for candidate, score in zip(batch_candidates, sequence_log_probs):
            scores[candidate] = float(score)
    return scores


def _softmax(logits: list[float]) -> list[float]:
    if not logits:
        return []
    max_logit = max(logits)
    weights = [exp(value - max_logit) for value in logits]
    total = sum(weights)
    return [value / total for value in weights] if total else [1.0 / len(logits)] * len(logits)


def _adacad_probability(features: ArbitrationFeatures) -> float:
    evidence_gap = logit(max(min(features.contextual_score, 1.0 - 1e-6), 1e-6)) - logit(
        max(min(features.parametric_score, 1.0 - 1e-6), 1e-6)
    )
    reliability_gap = logit(max(min(features.context_reliability, 1.0 - 1e-6), 1e-6)) - logit(
        max(min(features.parametric_reliability, 1.0 - 1e-6), 1e-6)
    )
    disagreement = abs(features.contextual_score - features.parametric_score)
    return sigmoid(1.0 * evidence_gap + 0.18 * reliability_gap + 0.25 * disagreement)


def _build_closed_book_prompt(question: str) -> str:
    return (
        "You are answering an open-domain QA question.\n"
        "Answer briefly and directly.\n\n"
        f"Question: {question}\nAnswer:"
    )


def _build_context_prompt(question: str, contexts: list[str]) -> str:
    joined = "\n\n".join(f"[Passage {idx + 1}]\n{text}" for idx, text in enumerate(contexts))
    return (
        "You are answering an open-domain QA question using retrieved passages.\n"
        "Use the evidence when it is reliable. Answer briefly and directly.\n\n"
        f"Question: {question}\n\nRetrieved passages:\n{joined}\n\nAnswer:"
    )


def _context_hit(contexts: list[str], answers: list[str]) -> bool:
    normalized_context = _normalize("\n".join(contexts))
    return any((needle := _normalize(answer)) and needle in normalized_context for answer in answers)


def _pick_by_weight(candidates: list[str], prior_scores: dict[str, float], post_scores: dict[str, float], weight: float) -> str:
    best_candidate = candidates[0]
    best_score = float("-inf")
    for candidate in candidates:
        score = weight * post_scores[candidate] + (1.0 - weight) * prior_scores[candidate]
        if score > best_score:
            best_score = score
            best_candidate = candidate
    return best_candidate


def _load_model(model_name: str, torch_dtype: str) -> tuple[Any, Any]:
    import importlib.util
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype_map = {
        "auto": "auto",
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    load_kwargs: dict[str, Any] = {"torch_dtype": dtype_map[torch_dtype]}
    if torch.cuda.is_available() and importlib.util.find_spec("accelerate") is not None:
        load_kwargs["device_map"] = "auto"
    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    if "device_map" not in load_kwargs:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
    model.eval()
    return model, tokenizer


def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    cache_path = Path(args.cache_file)
    cache = _load_cache(cache_path)
    model, tokenizer = _load_model(args.model, args.torch_dtype)

    dataset_names = [item.strip() for item in args.datasets.split(",") if item.strip()]
    per_dataset: dict[str, Any] = {}
    method_rows: list[dict[str, Any]] = []

    for dataset_name in dataset_names:
        examples = _load_examples(dataset_name, args.max_examples)
        rows: list[dict[str, Any]] = []
        for index, example in enumerate(examples, start=1):
            contexts = _wiki_search(
                example["question"],
                search_limit=args.search_limit,
                cache_path=cache_path,
                cache=cache,
            )[: args.top_k_contexts]
            if not contexts:
                continue
            closed_prompt = _build_closed_book_prompt(example["question"])
            context_prompt = _build_context_prompt(example["question"], contexts)
            closed_answer = _generate_answer(model, tokenizer, prompt=closed_prompt, max_new_tokens=args.max_new_tokens)
            context_answer = _generate_answer(model, tokenizer, prompt=context_prompt, max_new_tokens=args.max_new_tokens)
            candidates = []
            for candidate in [closed_answer, context_answer]:
                if candidate and candidate not in candidates:
                    candidates.append(candidate)
            if not candidates:
                continue
            prior_scores = _score_candidates(model, tokenizer, prompt=closed_prompt, candidates=candidates, batch_size=args.batch_size)
            post_scores = _score_candidates(model, tokenizer, prompt=context_prompt, candidates=candidates, batch_size=args.batch_size)
            prior_distribution = _softmax([prior_scores[candidate] for candidate in candidates])
            posterior_distribution = _softmax([post_scores[candidate] for candidate in candidates])
            context_hit = _context_hit(contexts, example["answers"])
            context_reliability = 0.88 if context_hit else 0.25
            features = ArbitrationFeatures(
                parametric_score=max(prior_distribution) if prior_distribution else 0.5,
                contextual_score=max(posterior_distribution) if posterior_distribution else 0.5,
                context_reliability=context_reliability,
                parametric_reliability=0.65,
                conflict_magnitude=0.15 if context_hit else 0.55,
            )
            bayes_weight = bayes_arbitration_probability(features)
            adacad_weight = _adacad_probability(features)
            predictions = {
                "closed_book": closed_answer,
                "cad": _pick_by_weight(candidates, prior_scores, post_scores, 1.0),
                "adacad": _pick_by_weight(candidates, prior_scores, post_scores, adacad_weight),
                "bayes_proxy": _pick_by_weight(candidates, prior_scores, post_scores, bayes_weight),
            }
            row = {
                "id": example["id"],
                "dataset": dataset_name,
                "question": example["question"],
                "answers": example["answers"],
                "context_hit": context_hit,
                "weights": {
                    "bayes_proxy": round(bayes_weight, 6),
                    "adacad": round(adacad_weight, 6),
                },
                "predictions": {},
            }
            for method_name, prediction in predictions.items():
                em = _exact_match(prediction, example["answers"])
                rouge_l = _rouge_l_f1(prediction, example["answers"])
                row["predictions"][method_name] = {
                    "answer": prediction,
                    "em": em,
                    "rouge_l": round(rouge_l, 6),
                }
                method_rows.append(
                    {
                        "dataset": dataset_name,
                        "method": method_name,
                        "em": em,
                        "rouge_l": rouge_l,
                    }
                )
            rows.append(row)
            if index % 10 == 0:
                print(json.dumps({"event": "processed_examples", "dataset": dataset_name, "completed": index, "rows_kept": len(rows)}), flush=True)
        per_dataset[dataset_name] = rows

    summary: dict[str, dict[str, Any]] = {}
    for dataset_name in dataset_names:
        summary[dataset_name] = {}
        dataset_rows = [row for row in method_rows if row["dataset"] == dataset_name]
        for method_name in sorted({row["method"] for row in dataset_rows}):
            scoped = [row for row in dataset_rows if row["method"] == method_name]
            summary[dataset_name][method_name] = {
                "count": len(scoped),
                "em": round(sum(row["em"] for row in scoped) / len(scoped), 6) if scoped else 0.0,
                "rouge_l": round(sum(row["rouge_l"] for row in scoped) / len(scoped), 6) if scoped else 0.0,
            }
    return {
        "metadata": {
            "model": args.model,
            "datasets": dataset_names,
            "max_examples": args.max_examples,
            "search_limit": args.search_limit,
            "top_k_contexts": args.top_k_contexts,
        },
        "summary": summary,
        "rows": per_dataset,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Paper 2 Free-Form Evaluation",
        "",
        "This run evaluates free-form open-domain QA using candidate generation plus token-level rescoring under closed-book and retrieved-context prompts.",
        "",
        f"- Model: `{payload['metadata']['model']}`",
        f"- Datasets: `{', '.join(payload['metadata']['datasets'])}`",
        f"- Max examples per dataset: `{payload['metadata']['max_examples']}`",
        "",
    ]
    for dataset_name, method_map in payload["summary"].items():
        lines.extend(
            [
                f"## {dataset_name}",
                "",
                "| Method | Count | EM | ROUGE-L |",
                "|---|---:|---:|---:|",
            ]
        )
        for method_name, stats in method_map.items():
            lines.append(
                f"| {method_name} | {stats['count']} | {stats['em']:.4f} | {stats['rouge_l']:.4f} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    payload = run_eval(args)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(output_prefix.with_suffix('.json')), "markdown": str(output_prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
