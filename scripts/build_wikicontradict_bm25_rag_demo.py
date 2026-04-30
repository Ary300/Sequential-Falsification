#!/usr/bin/env python3
"""Build a small retrieval-backed WikiContradict RAG demo note."""

from __future__ import annotations

import json
import math
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.loaders import load_arbitration_dataset  # noqa: E402
from utils.io import dump_json  # noqa: E402


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text or "")]


def _build_bm25(corpus_tokens: list[list[str]]) -> tuple[list[dict[str, int]], dict[str, float], float]:
    doc_freqs: list[dict[str, int]] = []
    df: dict[str, int] = {}
    lengths: list[int] = []
    for tokens in corpus_tokens:
        freqs: dict[str, int] = {}
        for token in tokens:
            freqs[token] = freqs.get(token, 0) + 1
        doc_freqs.append(freqs)
        lengths.append(len(tokens))
        for token in freqs:
            df[token] = df.get(token, 0) + 1
    num_docs = max(1, len(corpus_tokens))
    avgdl = sum(lengths) / num_docs if lengths else 0.0
    idf = {
        token: math.log(1.0 + (num_docs - freq + 0.5) / (freq + 0.5))
        for token, freq in df.items()
    }
    return doc_freqs, idf, avgdl


def _score_bm25(query_tokens: list[str], doc_freqs: list[dict[str, int]], idf: dict[str, float], avgdl: float) -> list[float]:
    k1 = 1.5
    b = 0.75
    scores: list[float] = []
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
    return scores


def build_payload() -> dict[str, Any]:
    rows = load_arbitration_dataset("wikicontradict", max_examples=256)
    corpus: list[dict[str, Any]] = []
    for row in rows:
        corpus.append({"id": row["id"], "kind": "aligned", "text": row["metadata"]["aligned_context_text"]})
        corpus.append({"id": row["id"], "kind": "conflict", "text": row["metadata"]["conflict_context_text"]})

    corpus_tokens = [_tokenize(doc["text"]) for doc in corpus]
    doc_freqs, idf, avgdl = _build_bm25(corpus_tokens)

    top1_aligned = 0
    top1_conflict = 0
    top5_both = 0
    examples = []

    for row in rows:
        query_tokens = _tokenize(row["question"])
        scores = _score_bm25(query_tokens, doc_freqs, idf, avgdl)
        ranked = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)[:5]
        top_docs = [corpus[idx] | {"score": round(scores[idx], 6)} for idx in ranked]
        top_kinds = [doc["kind"] for doc in top_docs if doc["id"] == row["id"]]
        if top_kinds[:1] == ["aligned"]:
            top1_aligned += 1
        if top_kinds[:1] == ["conflict"]:
            top1_conflict += 1
        if "aligned" in top_kinds and "conflict" in top_kinds:
            top5_both += 1

        if len(examples) < 5:
            examples.append(
                {
                    "id": row["id"],
                    "question": row["question"],
                    "gold_answers": row["answers"],
                    "conflict_answers": row["metadata"]["conflict_context_answers"],
                    "top_docs": top_docs,
                }
            )

    total = max(1, len(rows))
    return {
        "metadata": {
            "benchmark": "wikicontradict",
            "num_examples": len(rows),
            "num_corpus_docs": len(corpus),
            "retriever": "local_bm25_over_natural_wikicontradict_passages",
        },
        "headline": {
            "top1_aligned_rate": round(top1_aligned / total, 6),
            "top1_conflict_rate": round(top1_conflict / total, 6),
            "top5_contains_both_rate": round(top5_both / total, 6),
        },
        "examples": examples,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# WikiContradict Retrieval-Backed RAG Demo",
        "",
        "This is a small retrieval-backed demo over naturally occurring Wikipedia contradiction passages from WikiContradict. It is not a full Wikipedia dump experiment, but it does replace fixed hand-assigned passages with an actual BM25-style retrieval step.",
        "",
        "## Headline",
        "",
        f"- Top-1 aligned retrieval rate: `{payload['headline']['top1_aligned_rate']}`",
        f"- Top-1 conflict retrieval rate: `{payload['headline']['top1_conflict_rate']}`",
        f"- Top-5 contains both aligned and conflicting passages: `{payload['headline']['top5_contains_both_rate']}`",
        "",
        "## Example Retrievals",
        "",
    ]
    for example in payload["examples"]:
        lines.append(f"### {example['id']}")
        lines.append("")
        lines.append(f"- Question: {example['question']}")
        lines.append(f"- Gold answers: `{example['gold_answers']}`")
        lines.append(f"- Conflict answers: `{example['conflict_answers']}`")
        for doc in example["top_docs"]:
            snippet = str(doc["text"]).strip().replace("\n", " ")
            if len(snippet) > 180:
                snippet = snippet[:177] + "..."
            lines.append(f"- `{doc['kind']}` score `{doc['score']}`: {snippet}")
        lines.append("")
    lines.extend(
        [
            "## Read",
            "",
            "- This is best used as a deployment-style discussion figure, not as a replacement for the main benchmark matrix.",
            "- The useful point is that once retrieval is made explicit, the system often surfaces both supportive and stale passages, which is exactly the setting where the arbitration rule matters.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = build_payload()
    out_prefix = ROOT / "docs/generated/wikicontradict_bm25_rag_demo"
    dump_json(payload, out_prefix.with_suffix(".json"))
    out_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["headline"], indent=2))


if __name__ == "__main__":
    main()
