#!/usr/bin/env python3
"""Build an open-Wikipedia retrieval probe for WikiContradict questions."""

from __future__ import annotations

import argparse
import json
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

from knowledge_arbitration.loaders import load_arbitration_dataset  # noqa: E402
from utils.io import dump_json  # noqa: E402


SEARCH_URL = "https://en.wikipedia.org/w/api.php"
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an open-Wikipedia retrieval probe.")
    parser.add_argument("--max-examples", type=int, default=253)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--search-limit", type=int, default=8)
    parser.add_argument("--sleep-seconds", type=float, default=0.4)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument(
        "--cache-file",
        default=str(ROOT / "docs/generated/open_wikipedia_rag_probe_cache.json"),
    )
    parser.add_argument(
        "--output-prefix",
        default=str(ROOT / "docs/generated/open_wikipedia_rag_probe"),
    )
    return parser.parse_args()


def _normalize(text: str) -> str:
    return " ".join(match.group(0).lower() for match in TOKEN_RE.finditer(text or ""))


def _answer_list(row: dict[str, Any]) -> list[str]:
    answers = list(row.get("answers") or [])
    metadata = row.get("metadata", {}) or {}
    answers.extend(metadata.get("aligned_context_answers") or [])
    return [item.strip() for item in answers if isinstance(item, str) and item.strip()]


def _conflict_list(row: dict[str, Any]) -> list[str]:
    metadata = row.get("metadata", {}) or {}
    return [
        item.strip()
        for item in (metadata.get("conflict_context_answers") or [])
        if isinstance(item, str) and item.strip()
    ]


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


def _fetch_question_results(
    session: requests.Session,
    question: str,
    *,
    search_limit: int,
    top_k: int,
    sleep_seconds: float,
    max_retries: int,
    cache: dict[str, Any],
) -> list[dict[str, Any]]:
    cached = cache.get(question)
    if isinstance(cached, list):
        return cached

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": question,
        "srlimit": search_limit,
        "utf8": 1,
    }
    response = None
    for retry in range(max_retries):
        response = session.get(SEARCH_URL, params=params, timeout=30)
        if response.status_code != 429:
            break
        time.sleep(sleep_seconds * (2 ** retry))
    if response is None:
        raise RuntimeError("No response returned from Wikipedia search.")
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
        detail_response = None
        for retry in range(max_retries):
            detail_response = session.get(SEARCH_URL, params=detail_params, timeout=30)
            if detail_response.status_code != 429:
                break
            time.sleep(sleep_seconds * (2 ** retry))
        if detail_response is None:
            raise RuntimeError("No response returned from Wikipedia detail fetch.")
        detail_response.raise_for_status()
        pages = detail_response.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            page_lookup[str(page_id)] = page

    results = []
    for row in search_rows[:top_k]:
        page_id = str(row.get("pageid"))
        detail = page_lookup.get(page_id, {})
        results.append(
            {
                "pageid": page_id,
                "title": str(row.get("title", "")),
                "search_snippet": str(row.get("snippet", "")),
                "extract": str(detail.get("extract", "")),
            }
        )
    cache[question] = results
    _save_cache(Path(args.cache_file), cache)  # type: ignore[name-defined]
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    return results


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_arbitration_dataset("wikicontradict", max_examples=args.max_examples)
    cache_path = Path(args.cache_file)
    cache = _load_cache(cache_path)
    session = requests.Session()
    session.headers.update({"User-Agent": "SequentialFalsification/1.0 (research probe)"})

    top1_gold = 0
    top1_conflict = 0
    top5_gold = 0
    top5_conflict = 0
    top5_both = 0
    neither_top5 = 0
    examples = []

    for row in rows:
        gold_answers = _answer_list(row)
        conflict_answers = _conflict_list(row)
        results = _fetch_question_results(
            session,
            row["question"],
            search_limit=args.search_limit,
            top_k=args.top_k,
            sleep_seconds=args.sleep_seconds,
            max_retries=args.max_retries,
            cache=cache,
        )
        scored = []
        for result in results:
            text = f"{result.get('title', '')}\n{result.get('search_snippet', '')}\n{result.get('extract', '')}"
            scored.append(
                {
                    **result,
                    "gold_hit": _contains_any(text, gold_answers),
                    "conflict_hit": _contains_any(text, conflict_answers),
                }
            )

        if scored:
            if scored[0]["gold_hit"]:
                top1_gold += 1
            if scored[0]["conflict_hit"]:
                top1_conflict += 1
        any_gold = any(item["gold_hit"] for item in scored)
        any_conflict = any(item["conflict_hit"] for item in scored)
        if any_gold:
            top5_gold += 1
        if any_conflict:
            top5_conflict += 1
        if any_gold and any_conflict:
            top5_both += 1
        if not any_gold and not any_conflict:
            neither_top5 += 1

        if len(examples) < 5:
            examples.append(
                {
                    "id": row["id"],
                    "question": row["question"],
                    "gold_answers": gold_answers,
                    "conflict_answers": conflict_answers,
                    "results": scored,
                }
            )

    total = max(1, len(rows))
    return {
        "metadata": {
            "benchmark": "wikicontradict",
            "num_examples": len(rows),
            "search_limit": args.search_limit,
            "top_k": args.top_k,
            "retriever": "live_wikipedia_search_plus_extract_probe",
        },
        "headline": {
            "top1_gold_hit_rate": round(top1_gold / total, 6),
            "top1_conflict_hit_rate": round(top1_conflict / total, 6),
            "top5_gold_hit_rate": round(top5_gold / total, 6),
            "top5_conflict_hit_rate": round(top5_conflict / total, 6),
            "top5_both_hit_rate": round(top5_both / total, 6),
            "top5_neither_hit_rate": round(neither_top5 / total, 6),
        },
        "examples": examples,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Open-Wikipedia Retrieval Probe",
        "",
        "This probe replaces the benchmark-contained retrieval corpus with live Wikipedia search and page extracts.",
        "It is still a lightweight open-web probe rather than a full production RAG service, but it is materially closer to deployment than the bounded in-benchmark BM25 demo.",
        "",
        "## Headline",
        "",
        f"- Top-1 gold-answer hit rate: `{payload['headline']['top1_gold_hit_rate']}`",
        f"- Top-1 conflict-answer hit rate: `{payload['headline']['top1_conflict_hit_rate']}`",
        f"- Top-5 gold-answer hit rate: `{payload['headline']['top5_gold_hit_rate']}`",
        f"- Top-5 conflict-answer hit rate: `{payload['headline']['top5_conflict_hit_rate']}`",
        f"- Top-5 both-hit rate: `{payload['headline']['top5_both_hit_rate']}`",
        f"- Top-5 neither-hit rate: `{payload['headline']['top5_neither_hit_rate']}`",
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
        for result in example["results"]:
            snippet = (result.get("extract") or result.get("search_snippet") or "").replace("\n", " ").strip()
            if len(snippet) > 180:
                snippet = snippet[:177] + "..."
            lines.append(
                f"- `{result['title']}` gold=`{result['gold_hit']}` conflict=`{result['conflict_hit']}`: {snippet}"
            )
        lines.append("")
    lines.extend(
        [
            "## Read",
            "",
            "- The useful signal is whether open retrieval surfaces the gold answer, the stale/conflicting answer, or both.",
            "- A high both-hit rate is the deployment regime where arbitration matters most, because retrieval is surfacing genuine conflict rather than a single clean source.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    global args
    args = parse_args()
    payload = build_payload(args)
    out_prefix = Path(args.output_prefix)
    dump_json(payload, out_prefix.with_suffix(".json"))
    out_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["headline"], indent=2))


if __name__ == "__main__":
    main()
