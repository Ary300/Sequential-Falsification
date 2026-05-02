#!/usr/bin/env python3
"""Build a stronger live retrieval evaluation using dense E5 reranking."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
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


SEARCH_URL = "https://en.wikipedia.org/w/api.php"
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a production-style live RAG evaluation with E5 reranking.")
    parser.add_argument("--max-examples", type=int, default=20)
    parser.add_argument("--search-limit", type=int, default=12)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--sleep-seconds", type=float, default=0.25)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--encoder-model", default="intfloat/multilingual-e5-small")
    parser.add_argument("--cache-file", default=str(ROOT / "docs/generated/production_rag_eval_e5_cache.json"))
    parser.add_argument("--output-prefix", default=str(ROOT / "docs/generated/production_rag_eval_e5"))
    return parser.parse_args()


def _normalize(text: str) -> str:
    return " ".join(match.group(0).lower() for match in TOKEN_RE.finditer(text or ""))


def _contains_any(snippet: str, answers: list[str]) -> bool:
    hay = _normalize(snippet)
    if not hay:
        return False
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


def _get_with_retry(session: requests.Session, *, params: dict[str, Any], sleep_seconds: float, max_retries: int) -> requests.Response:
    response = None
    for retry in range(max_retries):
        response = session.get(SEARCH_URL, params=params, timeout=30)
        if response.status_code != 429:
            return response
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                delay = max(float(retry_after), sleep_seconds)
            except ValueError:
                delay = sleep_seconds
        else:
            delay = sleep_seconds * (2 ** retry)
        time.sleep(delay + random.uniform(0.0, max(0.1, sleep_seconds)))
    if response is None:
        raise RuntimeError("No response returned from Wikipedia API.")
    response.raise_for_status()
    return response


def _fetch_candidates(
    session: requests.Session,
    question: str,
    *,
    search_limit: int,
    sleep_seconds: float,
    max_retries: int,
    cache_path: Path,
    cache: dict[str, Any],
) -> tuple[list[dict[str, Any]], float]:
    key = f"live::{question}::{search_limit}"
    cached = cache.get(key)
    if isinstance(cached, list):
        return cached, 0.0

    start = time.perf_counter()
    response = _get_with_retry(
        session,
        params={
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": question,
            "srlimit": search_limit,
            "utf8": 1,
        },
        sleep_seconds=sleep_seconds,
        max_retries=max_retries,
    )
    search_rows = response.json().get("query", {}).get("search", [])
    page_ids = [str(row.get("pageid")) for row in search_rows if row.get("pageid") is not None]
    page_lookup: dict[str, dict[str, Any]] = {}
    if page_ids:
        detail_response = _get_with_retry(
            session,
            params={
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "pageids": "|".join(page_ids),
                "explaintext": 1,
                "exintro": 1,
                "utf8": 1,
            },
            sleep_seconds=sleep_seconds,
            max_retries=max_retries,
        )
        pages = detail_response.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            page_lookup[str(page_id)] = page
    elapsed = time.perf_counter() - start

    candidates = []
    for row in search_rows:
        page_id = str(row.get("pageid"))
        detail = page_lookup.get(page_id, {})
        text = f"{row.get('title', '')}\n{row.get('snippet', '')}\n{detail.get('extract', '')}"
        candidates.append(
            {
                "pageid": page_id,
                "title": str(row.get("title", "")),
                "search_snippet": str(row.get("snippet", "")),
                "extract": str(detail.get("extract", "")),
                "text": text,
            }
        )
    cache[key] = candidates
    _save_cache(cache_path, cache)
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    return candidates, elapsed


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
        batch = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
        batch = {key: value.to(self.device) for key, value in batch.items()}
        with torch.no_grad():
            outputs = self.model(**batch)
        hidden = outputs.last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1)
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
        pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
        return pooled.detach().cpu().numpy()


def _rerank_candidates(encoder: E5Encoder, query: str, candidates: list[dict[str, Any]], top_k: int) -> tuple[list[dict[str, Any]], float]:
    start = time.perf_counter()
    doc_texts = [f"passage: {row['title']}\n{row['search_snippet']}\n{row['extract']}" for row in candidates]
    embeddings = encoder.encode([f"query: {query}"] + doc_texts)
    query_vec = embeddings[0]
    scores = embeddings[1:] @ query_vec
    ranked = [{**row, "dense_score": round(float(score), 6)} for row, score in sorted(zip(candidates, scores, strict=False), key=lambda pair: float(pair[1]), reverse=True)]
    return ranked[:top_k], time.perf_counter() - start


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_arbitration_dataset("wikicontradict", max_examples=args.max_examples)
    cache_path = Path(args.cache_file)
    cache = _load_cache(cache_path)
    session = requests.Session()
    session.headers.update({"User-Agent": "SequentialFalsification/1.0 (production rag eval e5)"})
    encoder = E5Encoder(args.encoder_model)

    top1_gold = 0
    top1_conflict = 0
    topk_both = 0
    latencies = []
    rerank_times = []
    examples = []

    for row in rows:
        metadata = row.get("metadata", {}) or {}
        candidates, retrieval_time = _fetch_candidates(
            session,
            str(row["question"]),
            search_limit=args.search_limit,
            sleep_seconds=args.sleep_seconds,
            max_retries=args.max_retries,
            cache_path=cache_path,
            cache=cache,
        )
        ranked, rerank_time = _rerank_candidates(encoder, str(row["question"]), candidates, args.top_k)
        gold_answers = [str(item) for item in row.get("answers", []) if str(item).strip()]
        conflict_answers = [str(item) for item in metadata.get("conflict_context_answers", []) if str(item).strip()]
        scored = []
        for item in ranked:
            text = f"{item.get('title', '')}\n{item.get('search_snippet', '')}\n{item.get('extract', '')}"
            scored.append(
                {
                    **item,
                    "gold_hit": _contains_any(text, gold_answers),
                    "conflict_hit": _contains_any(text, conflict_answers),
                }
            )
        latencies.append(retrieval_time)
        rerank_times.append(rerank_time)
        any_gold = any(item["gold_hit"] for item in scored)
        any_conflict = any(item["conflict_hit"] for item in scored)
        top1_gold += int(bool(scored and scored[0]["gold_hit"]))
        top1_conflict += int(bool(scored and scored[0]["conflict_hit"]))
        topk_both += int(any_gold and any_conflict)
        examples.append(
            {
                "id": row["id"],
                "question": row["question"],
                "retriever": "live_wikipedia_search_plus_multilingual_e5_rerank",
                "retrieved": scored,
            }
        )

    denom = max(len(rows), 1)
    total_time = float(sum(latencies) + sum(rerank_times))
    return {
        "metadata": {
            "max_examples": args.max_examples,
            "search_limit": args.search_limit,
            "top_k": args.top_k,
            "encoder_model": args.encoder_model,
        },
        "headline": {
            "top1_gold_hit_rate": round(top1_gold / denom, 4),
            "top1_conflict_hit_rate": round(top1_conflict / denom, 4),
            "topk_both_hit_rate": round(topk_both / denom, 4),
            "mean_retrieval_latency_s": round(float(np.mean(latencies)) if latencies else 0.0, 4),
            "mean_rerank_latency_s": round(float(np.mean(rerank_times)) if rerank_times else 0.0, 4),
            "throughput_qps": round(float(len(rows) / total_time) if total_time > 0 else 0.0, 4),
        },
        "examples": examples,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    h = payload["headline"]
    lines = [
        "# Production RAG Eval (E5 Rerank)",
        "",
        "This rerun keeps live Wikipedia search but replaces the weak TF-IDF+SVD reranker with multilingual E5 dense reranking.",
        "",
        f"- top-1 gold hit rate: `{h['top1_gold_hit_rate']}`",
        f"- top-1 conflict hit rate: `{h['top1_conflict_hit_rate']}`",
        f"- top-{payload['metadata']['top_k']} both-hit rate: `{h['topk_both_hit_rate']}`",
        f"- mean retrieval latency: `{h['mean_retrieval_latency_s']}` s",
        f"- mean rerank latency: `{h['mean_rerank_latency_s']}` s",
        f"- throughput: `{h['throughput_qps']}` q/s",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    out_prefix = Path(args.output_prefix)
    dump_json(payload, out_prefix.with_suffix(".json"))
    out_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["headline"], indent=2))


if __name__ == "__main__":
    main()
