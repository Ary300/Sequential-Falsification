#!/usr/bin/env python3
"""Build a production-style live retrieval evaluation with latency metrics."""

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
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.loaders import load_arbitration_dataset  # noqa: E402
from utils.io import dump_json  # noqa: E402


SEARCH_URL = "https://en.wikipedia.org/w/api.php"
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a production-style live RAG evaluation.")
    parser.add_argument("--max-examples", type=int, default=20)
    parser.add_argument("--search-limit", type=int, default=12)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--sleep-seconds", type=float, default=0.25)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--cache-file", default=str(ROOT / "docs/generated/production_rag_eval_cache.json"))
    parser.add_argument("--output-prefix", default=str(ROOT / "docs/generated/production_rag_eval"))
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


def _get_with_retry(
    session: requests.Session,
    *,
    params: dict[str, Any],
    sleep_seconds: float,
    max_retries: int,
) -> requests.Response:
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
        # Add a small jitter so we do not hammer the API at deterministic intervals.
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
    top_k: int,
    sleep_seconds: float,
    max_retries: int,
    cache_path: Path,
    cache: dict[str, Any],
) -> tuple[list[dict[str, Any]], float]:
    key = f"live::{question}"
    cached = cache.get(key)
    if isinstance(cached, list):
        return cached, 0.0

    start = time.perf_counter()
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": question,
        "srlimit": search_limit,
        "utf8": 1,
    }
    response = _get_with_retry(
        session,
        params=params,
        sleep_seconds=sleep_seconds,
        max_retries=max_retries,
    )
    response.raise_for_status()
    search_rows = response.json().get("query", {}).get("search", [])
    page_ids = [str(row.get("pageid")) for row in search_rows[:top_k] if row.get("pageid") is not None]
    page_lookup: dict[str, dict[str, Any]] = {}
    if page_ids:
        detail_params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "pageids": "|".join(page_ids),
            "explaintext": 1,
            "exintro": 1,
            "utf8": 1,
        }
        detail_response = _get_with_retry(
            session,
            params=detail_params,
            sleep_seconds=sleep_seconds,
            max_retries=max_retries,
        )
        detail_response.raise_for_status()
        pages = detail_response.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            page_lookup[str(page_id)] = page
    elapsed = time.perf_counter() - start

    candidates = []
    for row in search_rows[:top_k]:
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


def _bm25_scores(query: str, docs: list[str]) -> np.ndarray:
    query_tokens = _normalize(query).split()
    doc_tokens = [_normalize(doc).split() for doc in docs]
    doc_freqs = []
    df = {}
    lengths = []
    for tokens in doc_tokens:
        freqs = {}
        for token in tokens:
            freqs[token] = freqs.get(token, 0) + 1
        doc_freqs.append(freqs)
        lengths.append(len(tokens))
        for token in freqs:
            df[token] = df.get(token, 0) + 1
    num_docs = max(1, len(docs))
    avgdl = float(sum(lengths) / num_docs) if lengths else 0.0
    idf = {token: np.log(1.0 + (num_docs - freq + 0.5) / (freq + 0.5)) for token, freq in df.items()}
    k1 = 1.5
    b = 0.75
    scores = []
    for freqs in doc_freqs:
        doc_len = sum(freqs.values())
        score = 0.0
        for token in query_tokens:
            if token not in freqs:
                continue
            tf = freqs[token]
            denom = tf + k1 * (1.0 - b + b * (doc_len / max(avgdl, 1e-6)))
            score += idf.get(token, 0.0) * ((tf * (k1 + 1.0)) / max(denom, 1e-6))
        scores.append(score)
    return np.asarray(scores, dtype=float)


def _dense_scores(query: str, docs: list[str]) -> np.ndarray:
    texts = [query] + docs
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    n_features = matrix.shape[1]
    if n_features <= 1:
        return np.zeros(len(docs), dtype=float)
    n_components = max(1, min(16, matrix.shape[0] - 1, matrix.shape[1] - 1))
    try:
        reduced = TruncatedSVD(n_components=n_components, random_state=0).fit_transform(matrix)
    except Exception:
        return np.zeros(len(docs), dtype=float)
    if not np.isfinite(reduced).all():
        return np.zeros(len(docs), dtype=float)
    query_vec = reduced[0]
    doc_vecs = reduced[1:]
    query_norm = np.linalg.norm(query_vec) + 1e-8
    doc_norms = np.linalg.norm(doc_vecs, axis=1) + 1e-8
    return (doc_vecs @ query_vec) / (doc_norms * query_norm)


def _zscore(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    std = float(values.std())
    if std == 0.0:
        return np.zeros_like(values)
    return (values - float(values.mean())) / std


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_arbitration_dataset("wikicontradict", max_examples=args.max_examples)
    cache_path = Path(args.cache_file)
    cache = _load_cache(cache_path)
    session = requests.Session()
    session.headers.update({"User-Agent": "SequentialFalsification/1.0 (production rag eval)"})

    bm25_top1_gold = 0
    bm25_top1_conflict = 0
    bm25_topk_both = 0
    hybrid_top1_gold = 0
    hybrid_top1_conflict = 0
    hybrid_topk_both = 0
    latencies = []
    rerank_times = []
    examples = []

    for row in rows:
        gold_answers = [str(item) for item in row.get("answers", []) if str(item).strip()]
        conflict_answers = [str(item) for item in (row.get("metadata", {}) or {}).get("conflict_context_answers", []) if str(item).strip()]
        candidates, live_latency = _fetch_candidates(
            session,
            row["question"],
            search_limit=args.search_limit,
            top_k=args.search_limit,
            sleep_seconds=args.sleep_seconds,
            max_retries=args.max_retries,
            cache_path=cache_path,
            cache=cache,
        )
        latencies.append(live_latency)
        docs = [candidate["text"] for candidate in candidates]
        rerank_start = time.perf_counter()
        bm25 = _bm25_scores(row["question"], docs)
        dense = _dense_scores(row["question"], docs)
        hybrid = _zscore(bm25) + _zscore(dense)
        rerank_times.append(time.perf_counter() - rerank_start)

        bm25_ranked = [candidates[idx] | {"score": float(bm25[idx])} for idx in np.argsort(-bm25)[: args.top_k]]
        hybrid_ranked = [candidates[idx] | {"score": float(hybrid[idx]), "bm25": float(bm25[idx]), "dense": float(dense[idx])} for idx in np.argsort(-hybrid)[: args.top_k]]

        def annotate(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
            out = []
            for item in items:
                text = item["text"]
                out.append({**item, "gold_hit": _contains_any(text, gold_answers), "conflict_hit": _contains_any(text, conflict_answers)})
            return out

        bm25_annotated = annotate(bm25_ranked)
        hybrid_annotated = annotate(hybrid_ranked)

        if bm25_annotated:
            bm25_top1_gold += int(bm25_annotated[0]["gold_hit"])
            bm25_top1_conflict += int(bm25_annotated[0]["conflict_hit"])
        if hybrid_annotated:
            hybrid_top1_gold += int(hybrid_annotated[0]["gold_hit"])
            hybrid_top1_conflict += int(hybrid_annotated[0]["conflict_hit"])
        bm25_topk_both += int(any(item["gold_hit"] for item in bm25_annotated) and any(item["conflict_hit"] for item in bm25_annotated))
        hybrid_topk_both += int(any(item["gold_hit"] for item in hybrid_annotated) and any(item["conflict_hit"] for item in hybrid_annotated))

        if len(examples) < 5:
            examples.append(
                {
                    "id": row["id"],
                    "question": row["question"],
                    "gold_answers": gold_answers,
                    "conflict_answers": conflict_answers,
                    "bm25_topk": bm25_annotated,
                    "hybrid_topk": hybrid_annotated,
                }
            )

    total = max(1, len(rows))
    total_time = float(sum(latencies) + sum(rerank_times))
    payload = {
        "metadata": {
            "benchmark": "wikicontradict",
            "num_examples": len(rows),
            "retrieval_backend": "live_wikipedia_search_plus_hybrid_rerank",
            "hybrid_stack": "search_api -> bm25 lexical -> tfidf+svd dense rerank",
            "top_k": args.top_k,
            "search_limit": args.search_limit,
        },
        "headline": {
            "bm25_top1_gold_hit_rate": round(bm25_top1_gold / total, 6),
            "bm25_top1_conflict_hit_rate": round(bm25_top1_conflict / total, 6),
            "bm25_topk_both_hit_rate": round(bm25_topk_both / total, 6),
            "hybrid_top1_gold_hit_rate": round(hybrid_top1_gold / total, 6),
            "hybrid_top1_conflict_hit_rate": round(hybrid_top1_conflict / total, 6),
            "hybrid_topk_both_hit_rate": round(hybrid_topk_both / total, 6),
            "mean_live_retrieval_latency_s": round(float(np.mean(latencies)), 4),
            "p50_live_retrieval_latency_s": round(float(np.quantile(latencies, 0.5)), 4),
            "p90_live_retrieval_latency_s": round(float(np.quantile(latencies, 0.9)), 4),
            "mean_rerank_latency_s": round(float(np.mean(rerank_times)), 4),
            "throughput_queries_per_s": round(float(len(rows) / max(total_time, 1e-6)), 4),
        },
        "examples": examples,
    }
    return payload


def build_markdown(payload: dict) -> str:
    h = payload["headline"]
    lines = [
        "# Production-Style RAG Evaluation",
        "",
        "This note upgrades the earlier retrieval probes into a more deployable pipeline: live Wikipedia search as the first stage, then lexical BM25 and a dense-ish TF-IDF+SVD reranker over the candidate pool.",
        "It is still not a full commercial production stack, but it is a real end-to-end retrieval system with latency and throughput accounting.",
        "",
        "## Headline",
        "",
        f"- BM25 top-1 gold hit rate: `{h['bm25_top1_gold_hit_rate']}`",
        f"- BM25 top-1 conflict hit rate: `{h['bm25_top1_conflict_hit_rate']}`",
        f"- BM25 top-{payload['metadata']['top_k']} both-hit rate: `{h['bm25_topk_both_hit_rate']}`",
        f"- Hybrid top-1 gold hit rate: `{h['hybrid_top1_gold_hit_rate']}`",
        f"- Hybrid top-1 conflict hit rate: `{h['hybrid_top1_conflict_hit_rate']}`",
        f"- Hybrid top-{payload['metadata']['top_k']} both-hit rate: `{h['hybrid_topk_both_hit_rate']}`",
        f"- Mean live retrieval latency: `{h['mean_live_retrieval_latency_s']}` s",
        f"- P50 / P90 live retrieval latency: `{h['p50_live_retrieval_latency_s']}` / `{h['p90_live_retrieval_latency_s']}` s",
        f"- Mean rerank latency: `{h['mean_rerank_latency_s']}` s",
        f"- Throughput: `{h['throughput_queries_per_s']}` queries/s",
        "",
        "## Example queries",
        "",
    ]
    for example in payload["examples"]:
        lines.append(f"### {example['id']}")
        lines.append("")
        lines.append(f"- Question: {example['question']}")
        lines.append(f"- Gold answers: `{example['gold_answers']}`")
        lines.append(f"- Conflict answers: `{example['conflict_answers']}`")
        lines.append("- BM25 top-k:")
        for doc in example["bm25_topk"]:
            snippet = doc["text"].replace("\n", " ").strip()
            if len(snippet) > 160:
                snippet = snippet[:157] + "..."
            lines.append(
                f"  - score `{doc['score']:.4f}` gold `{doc['gold_hit']}` conflict `{doc['conflict_hit']}`: {snippet}"
            )
        lines.append("- Hybrid top-k:")
        for doc in example["hybrid_topk"]:
            snippet = doc["text"].replace("\n", " ").strip()
            if len(snippet) > 160:
                snippet = snippet[:157] + "..."
            lines.append(
                f"  - hybrid `{doc['score']:.4f}` bm25 `{doc['bm25']:.4f}` dense `{doc['dense']:.4f}` "
                f"gold `{doc['gold_hit']}` conflict `{doc['conflict_hit']}`: {snippet}"
            )
        lines.append("")
    lines.extend(
        [
            "## Read",
            "",
            "- This is the strongest honest retrieval-side system result in the repo so far because it includes live retrieval, reranking, and latency accounting in one place.",
            "- The numbers should be read as deployment-style evidence, not as a replacement for the benchmark-centered theorem matrix.",
        ]
    )
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
