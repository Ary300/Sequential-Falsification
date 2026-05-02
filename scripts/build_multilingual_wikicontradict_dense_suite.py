#!/usr/bin/env python3
"""Run a multilingual WikiContradict retrieval suite with dense reranking."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import sys
import time
from typing import Any

import numpy as np
import requests
import torch
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.loaders import load_arbitration_dataset  # noqa: E402
from utils.io import dump_json  # noqa: E402


GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
TOKEN_RE = re.compile(r"\w+", re.UNICODE)
LANGUAGE_MAP = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ar": "Arabic",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a multilingual dense-reranked WikiContradict suite.")
    parser.add_argument("--languages", default="fr,pt")
    parser.add_argument("--max-examples", type=int, default=10)
    parser.add_argument("--search-limit", type=int, default=12)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--encoder-model", default="intfloat/multilingual-e5-small")
    parser.add_argument(
        "--cache-file",
        default=str(ROOT / "docs/generated/multilingual_wikicontradict_dense_cache.json"),
    )
    parser.add_argument(
        "--output-prefix",
        default=str(ROOT / "docs/generated/multilingual_wikicontradict_dense_suite"),
    )
    return parser.parse_args()


def _normalize(text: str) -> str:
    return " ".join(match.group(0).lower() for match in TOKEN_RE.finditer(text or ""))


def _contains_any(text: str, answers: list[str]) -> bool:
    hay = _normalize(text)
    for answer in answers:
        needle = _normalize(answer)
        if needle and needle in hay:
            return True
    return False


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


def _translate(
    session: requests.Session,
    text: str,
    *,
    target_lang: str,
    cache: dict[str, Any],
    cache_path: Path,
    sleep_seconds: float,
    max_retries: int,
) -> str:
    stripped = str(text or "").strip()
    if not stripped:
        return ""
    key = f"translate::{target_lang}::{stripped}"
    cached = cache.get(key)
    if isinstance(cached, str):
        return cached
    response = None
    for retry in range(max_retries):
        response = session.get(
            GOOGLE_TRANSLATE_URL,
            params={"client": "gtx", "sl": "en", "tl": target_lang, "dt": "t", "q": stripped},
            timeout=30,
        )
        if response.status_code != 429:
            break
        time.sleep(sleep_seconds * (2 ** retry))
    if response is None:
        raise RuntimeError("No response returned from translation API.")
    response.raise_for_status()
    payload = response.json()
    translated = "".join(str(chunk[0]) for chunk in payload[0] if isinstance(chunk, list) and chunk and chunk[0]).strip()
    translated = translated or stripped
    cache[key] = translated
    _save_cache(cache_path, cache)
    time.sleep(sleep_seconds)
    return translated


def _search_target_wikipedia(
    session: requests.Session,
    question_translated: str,
    *,
    target_lang: str,
    search_limit: int,
    cache: dict[str, Any],
    cache_path: Path,
    sleep_seconds: float,
    max_retries: int,
) -> list[dict[str, Any]]:
    key = f"search::{target_lang}::{question_translated}::{search_limit}"
    cached = cache.get(key)
    if isinstance(cached, list):
        return cached

    search_url = f"https://{target_lang}.wikipedia.org/w/api.php"
    response = None
    for retry in range(max_retries):
        response = session.get(
            search_url,
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": question_translated,
                "srlimit": search_limit,
                "utf8": 1,
            },
            timeout=30,
        )
        if response.status_code != 429:
            break
        time.sleep(sleep_seconds * (2 ** retry))
    if response is None:
        raise RuntimeError("No response returned from target-language Wikipedia search.")
    response.raise_for_status()
    search_rows = response.json().get("query", {}).get("search", [])
    page_ids = [str(row.get("pageid")) for row in search_rows if row.get("pageid") is not None]
    page_lookup: dict[str, dict[str, Any]] = {}
    if page_ids:
        detail = None
        for retry in range(max_retries):
            detail = session.get(
                search_url,
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
            if detail.status_code != 429:
                break
            time.sleep(sleep_seconds * (2 ** retry))
        if detail is None:
            raise RuntimeError("No response returned from target-language Wikipedia detail fetch.")
        detail.raise_for_status()
        pages = detail.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            page_lookup[str(page_id)] = page

    rows: list[dict[str, Any]] = []
    for row in search_rows:
        page_id = str(row.get("pageid"))
        detail = page_lookup.get(page_id, {})
        rows.append(
            {
                "title": str(row.get("title", "")),
                "snippet": html.unescape(str(row.get("snippet", ""))),
                "extract": str(detail.get("extract", "")),
            }
        )
    cache[key] = rows
    _save_cache(cache_path, cache)
    time.sleep(sleep_seconds)
    return rows


class E5Encoder:
    def __init__(self, model_name: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 1), dtype=np.float32)
        batch = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        batch = {key: value.to(self.device) for key, value in batch.items()}
        with torch.no_grad():
            outputs = self.model(**batch)
        hidden = outputs.last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1)
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
        pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
        return pooled.detach().cpu().numpy()


def _rerank_candidates(encoder: E5Encoder, query_text: str, candidates: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    if not candidates:
        return []
    doc_texts = [f"passage: {item['title']}\n{item['snippet']}\n{item['extract']}".strip() for item in candidates]
    embeddings = encoder.encode([f"query: {query_text}"] + doc_texts)
    query_vec = embeddings[0]
    doc_vecs = embeddings[1:]
    scores = doc_vecs @ query_vec
    ranked = []
    for item, score in sorted(zip(candidates, scores, strict=False), key=lambda pair: float(pair[1]), reverse=True):
        ranked.append({**item, "dense_score": round(float(score), 6)})
    return ranked[:top_k]


def _run_language(lang: str, label: str, *, args: argparse.Namespace, encoder: E5Encoder, session: requests.Session, cache: dict[str, Any], cache_path: Path) -> dict[str, Any]:
    rows = load_arbitration_dataset("wikicontradict", max_examples=args.max_examples)
    top1_gold = 0
    top1_conflict = 0
    topk_gold = 0
    topk_conflict = 0
    topk_both = 0
    completed_examples = 0
    failed_examples: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []

    for row in rows:
        metadata = row.get("metadata", {}) or {}
        try:
            question_translated = _translate(
                session,
                str(row["question"]),
                target_lang=lang,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            gold_translated = [
                _translate(
                    session,
                    item,
                    target_lang=lang,
                    cache=cache,
                    cache_path=cache_path,
                    sleep_seconds=args.sleep_seconds,
                    max_retries=args.max_retries,
                )
                for item in list(row.get("answers") or [])[:2]
                if isinstance(item, str) and item.strip()
            ]
            conflict_translated = [
                _translate(
                    session,
                    item,
                    target_lang=lang,
                    cache=cache,
                    cache_path=cache_path,
                    sleep_seconds=args.sleep_seconds,
                    max_retries=args.max_retries,
                )
                for item in list(metadata.get("conflict_context_answers") or [])[:2]
                if isinstance(item, str) and item.strip()
            ]
            candidates = _search_target_wikipedia(
                session,
                question_translated,
                target_lang=lang,
                search_limit=args.search_limit,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            ranked = _rerank_candidates(encoder, question_translated, candidates, args.top_k)
        except Exception as exc:  # noqa: BLE001
            failed_examples.append(
                {
                    "id": row["id"],
                    "question_en": row["question"],
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue

        scored = []
        for item in ranked:
            text = f"{item.get('title', '')}\n{item.get('snippet', '')}\n{item.get('extract', '')}"
            scored.append(
                {
                    **item,
                    "gold_hit": _contains_any(text, gold_translated),
                    "conflict_hit": _contains_any(text, conflict_translated),
                }
            )
        completed_examples += 1
        top1_gold += int(bool(scored and scored[0]["gold_hit"]))
        top1_conflict += int(bool(scored and scored[0]["conflict_hit"]))
        any_gold = any(item["gold_hit"] for item in scored)
        any_conflict = any(item["conflict_hit"] for item in scored)
        topk_gold += int(any_gold)
        topk_conflict += int(any_conflict)
        topk_both += int(any_gold and any_conflict)
        examples.append(
            {
                "id": row["id"],
                "question_en": row["question"],
                "question_translated": question_translated,
                "gold_answers_translated": gold_translated,
                "conflict_answers_translated": conflict_translated,
                "retriever": f"translated_query_plus_{lang}_wikipedia_search_plus_dense_rerank",
                "retrieved": scored,
            }
        )

    denom = max(completed_examples, 1)
    return {
        "metadata": {
            "target_lang": lang,
            "target_label": label,
            "completed_examples": completed_examples,
            "failed_examples": len(failed_examples),
            "max_examples": args.max_examples,
            "top_k": args.top_k,
            "search_limit": args.search_limit,
            "encoder_model": args.encoder_model,
        },
        "headline": {
            "target_lang": lang,
            "target_label": label,
            "top1_gold_hit_rate": round(top1_gold / denom, 4),
            "top1_conflict_hit_rate": round(top1_conflict / denom, 4),
            "topk_gold_hit_rate": round(topk_gold / denom, 4),
            "topk_conflict_hit_rate": round(topk_conflict / denom, 4),
            "topk_both_hit_rate": round(topk_both / denom, 4),
        },
        "examples": examples,
        "failed_examples": failed_examples,
    }


def build_suite(args: argparse.Namespace) -> dict[str, Any]:
    cache_path = Path(args.cache_file)
    cache = _load_cache(cache_path)
    session = requests.Session()
    session.headers.update({"User-Agent": "SequentialFalsification/1.0 (multilingual dense suite)"})
    encoder = E5Encoder(args.encoder_model)

    rows = []
    payloads = {}
    for lang in [item.strip().lower() for item in args.languages.split(",") if item.strip()]:
        label = LANGUAGE_MAP.get(lang, lang)
        payload = _run_language(lang, label, args=args, encoder=encoder, session=session, cache=cache, cache_path=cache_path)
        payloads[lang] = payload
        rows.append(
            {
                "language": lang,
                "label": label,
                "completed_examples": payload["metadata"]["completed_examples"],
                "failed_examples": payload["metadata"]["failed_examples"],
                "top1_gold_hit_rate": payload["headline"]["top1_gold_hit_rate"],
                "top1_conflict_hit_rate": payload["headline"]["top1_conflict_hit_rate"],
                "topk_gold_hit_rate": payload["headline"]["topk_gold_hit_rate"],
                "topk_conflict_hit_rate": payload["headline"]["topk_conflict_hit_rate"],
                "topk_both_hit_rate": payload["headline"]["topk_both_hit_rate"],
            }
        )
    completed = [row for row in rows if row["completed_examples"] > 0]
    return {
        "metadata": {
            "languages": [row["language"] for row in rows],
            "max_examples_per_language": args.max_examples,
            "top_k": args.top_k,
            "search_limit": args.search_limit,
            "encoder_model": args.encoder_model,
        },
        "headline": {
            "languages_run": len(rows),
            "languages_with_any_gold_hit": sum(1 for row in rows if row["topk_gold_hit_rate"] > 0),
            "languages_with_any_conflict_hit": sum(1 for row in rows if row["topk_conflict_hit_rate"] > 0),
            "mean_topk_gold_hit_rate": round(sum(row["topk_gold_hit_rate"] for row in completed) / len(completed), 4) if completed else 0.0,
            "mean_topk_conflict_hit_rate": round(sum(row["topk_conflict_hit_rate"] for row in completed) / len(completed), 4) if completed else 0.0,
        },
        "rows": rows,
        "payloads": payloads,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    h = summary["headline"]
    lines = [
        "# Multilingual WikiContradict Dense Retrieval Suite",
        "",
        "This suite keeps live target-language Wikipedia search but replaces the weak lexical ranking with multilingual dense reranking.",
        "",
        "## Headline",
        "",
        f"- Languages run: `{h['languages_run']}`",
        f"- Languages with any top-k gold hit: `{h['languages_with_any_gold_hit']}`",
        f"- Languages with any top-k conflict hit: `{h['languages_with_any_conflict_hit']}`",
        f"- Mean top-k gold-hit rate across completed languages: `{h['mean_topk_gold_hit_rate']}`",
        f"- Mean top-k conflict-hit rate across completed languages: `{h['mean_topk_conflict_hit_rate']}`",
        "",
        "| Language | Completed | Failed | Top-1 Gold | Top-1 Conflict | Top-k Gold | Top-k Conflict | Top-k Both |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["rows"]:
        lines.append(
            f"| {row['label']} | {row['completed_examples']} | {row['failed_examples']} | "
            f"{row['top1_gold_hit_rate']:.4f} | {row['top1_conflict_hit_rate']:.4f} | "
            f"{row['topk_gold_hit_rate']:.4f} | {row['topk_conflict_hit_rate']:.4f} | "
            f"{row['topk_both_hit_rate']:.4f} |"
        )
    lines.append("")
    lines.append("This is still a small transfer probe, but it directly tests whether stronger multilingual reranking rescues the weakest retrieval-only languages.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    payload = build_suite(args)
    prefix = Path(args.output_prefix)
    dump_json(payload, prefix.with_suffix(".json"))
    prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["headline"], indent=2))


if __name__ == "__main__":
    main()
