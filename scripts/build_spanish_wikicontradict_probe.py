#!/usr/bin/env python3
"""Build a small Spanish transfer probe for WikiContradict retrieval."""

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


TRANSLATE_URL = "https://api.mymemory.translated.net/get"
SEARCH_URL = "https://es.wikipedia.org/w/api.php"
TOKEN_RE = re.compile(r"[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Spanish Wikipedia retrieval transfer probe.")
    parser.add_argument("--max-examples", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--search-limit", type=int, default=5)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument(
        "--cache-file",
        default=str(ROOT / "docs/generated/spanish_wikicontradict_probe_cache.json"),
    )
    parser.add_argument(
        "--output-prefix",
        default=str(ROOT / "docs/generated/spanish_wikicontradict_probe"),
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
    cache: dict[str, Any],
    sleep_seconds: float,
    max_retries: int,
) -> str:
    key = f"translate::{text}"
    cached = cache.get(key)
    if isinstance(cached, str):
        return cached
    response = None
    for retry in range(max_retries):
        response = session.get(
            TRANSLATE_URL,
            params={"q": text, "langpair": "en|es"},
            timeout=30,
        )
        if response.status_code != 429:
            break
        time.sleep(sleep_seconds * (2 ** retry))
    if response is None:
        raise RuntimeError("No response returned from translation API.")
    response.raise_for_status()
    translated = str(response.json().get("responseData", {}).get("translatedText", "")).strip() or text
    cache[key] = translated
    _save_cache(Path(args.cache_file), cache)  # type: ignore[name-defined]
    time.sleep(sleep_seconds)
    return translated


def _search_spanish_wikipedia(
    session: requests.Session,
    question_es: str,
    cache: dict[str, Any],
    *,
    search_limit: int,
    top_k: int,
    sleep_seconds: float,
    max_retries: int,
) -> list[dict[str, Any]]:
    key = f"search::{question_es}"
    cached = cache.get(key)
    if isinstance(cached, list):
        return cached

    response = None
    for retry in range(max_retries):
        response = session.get(
            SEARCH_URL,
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": question_es,
                "srlimit": search_limit,
                "utf8": 1,
            },
            timeout=30,
        )
        if response.status_code != 429:
            break
        time.sleep(sleep_seconds * (2 ** retry))
    if response is None:
        raise RuntimeError("No response returned from Spanish Wikipedia search.")
    response.raise_for_status()
    search_rows = response.json().get("query", {}).get("search", [])
    page_ids = [str(row.get("pageid")) for row in search_rows[:top_k] if row.get("pageid") is not None]
    page_lookup: dict[str, dict[str, Any]] = {}
    if page_ids:
        detail = None
        for retry in range(max_retries):
            detail = session.get(
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
            if detail.status_code != 429:
                break
            time.sleep(sleep_seconds * (2 ** retry))
        if detail is None:
            raise RuntimeError("No response returned from Spanish Wikipedia detail fetch.")
        detail.raise_for_status()
        pages = detail.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            page_lookup[str(page_id)] = page
    results = []
    for row in search_rows[:top_k]:
        page_id = str(row.get("pageid"))
        detail = page_lookup.get(page_id, {})
        results.append(
            {
                "title": str(row.get("title", "")),
                "snippet": str(row.get("snippet", "")),
                "extract": str(detail.get("extract", "")),
            }
        )
    cache[key] = results
    _save_cache(Path(args.cache_file), cache)  # type: ignore[name-defined]
    time.sleep(sleep_seconds)
    return results


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    session = requests.Session()
    session.headers.update({"User-Agent": "SequentialFalsification/1.0 (multilingual transfer probe)"})
    cache = _load_cache(Path(args.cache_file))
    rows = load_arbitration_dataset("wikicontradict", max_examples=args.max_examples)

    top1_gold = 0
    top1_conflict = 0
    topk_gold = 0
    topk_conflict = 0
    topk_both = 0
    examples = []

    for row in rows:
        metadata = row.get("metadata", {}) or {}
        question_es = _translate(session, str(row["question"]), cache, args.sleep_seconds, args.max_retries)
        gold_es = [
            _translate(session, item, cache, args.sleep_seconds, args.max_retries)
            for item in list(row.get("answers") or [])[:2]
            if isinstance(item, str) and item.strip()
        ]
        conflict_es = [
            _translate(session, item, cache, args.sleep_seconds, args.max_retries)
            for item in list(metadata.get("conflict_context_answers") or [])[:2]
            if isinstance(item, str) and item.strip()
        ]
        results = _search_spanish_wikipedia(
            session,
            question_es,
            cache,
            search_limit=args.search_limit,
            top_k=args.top_k,
            sleep_seconds=args.sleep_seconds,
            max_retries=args.max_retries,
        )
        scored = []
        for result in results:
            text = f"{result.get('title', '')}\n{result.get('snippet', '')}\n{result.get('extract', '')}"
            scored.append(
                {
                    **result,
                    "gold_hit": _contains_any(text, gold_es),
                    "conflict_hit": _contains_any(text, conflict_es),
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
            topk_gold += 1
        if any_conflict:
            topk_conflict += 1
        if any_gold and any_conflict:
            topk_both += 1

        if len(examples) < 5:
            examples.append(
                {
                    "id": row["id"],
                    "question_en": row["question"],
                    "question_es": question_es,
                    "gold_es": gold_es,
                    "conflict_es": conflict_es,
                    "results": scored,
                }
            )

    total = max(1, len(rows))
    return {
        "metadata": {
            "benchmark": "wikicontradict",
            "language": "es",
            "num_examples": len(rows),
            "retriever": "translated_query_plus_spanish_wikipedia_search",
        },
        "headline": {
            "top1_gold_hit_rate": round(top1_gold / total, 6),
            "top1_conflict_hit_rate": round(top1_conflict / total, 6),
            "topk_gold_hit_rate": round(topk_gold / total, 6),
            "topk_conflict_hit_rate": round(topk_conflict / total, 6),
            "topk_both_hit_rate": round(topk_both / total, 6),
        },
        "examples": examples,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    top_k = 3
    lines = [
        "# Spanish WikiContradict Transfer Probe",
        "",
        "This is a small multilingual transfer probe: English WikiContradict questions and answers are translated to Spanish, then searched against Spanish Wikipedia.",
        "",
        "## Headline",
        "",
        f"- Top-1 gold-answer hit rate: `{payload['headline']['top1_gold_hit_rate']}`",
        f"- Top-1 conflict-answer hit rate: `{payload['headline']['top1_conflict_hit_rate']}`",
        f"- Top-{top_k} gold-answer hit rate: `{payload['headline']['topk_gold_hit_rate']}`",
        f"- Top-{top_k} conflict-answer hit rate: `{payload['headline']['topk_conflict_hit_rate']}`",
        f"- Top-{top_k} both-hit rate: `{payload['headline']['topk_both_hit_rate']}`",
        "",
    ]
    for example in payload["examples"]:
        lines.append(f"### {example['id']}")
        lines.append("")
        lines.append(f"- English question: {example['question_en']}")
        lines.append(f"- Spanish question: {example['question_es']}")
        lines.append(f"- Spanish gold answers: `{example['gold_es']}`")
        lines.append(f"- Spanish conflict answers: `{example['conflict_es']}`")
        for result in example["results"]:
            snippet = (result.get("extract") or result.get("snippet") or "").replace("\n", " ").strip()
            if len(snippet) > 160:
                snippet = snippet[:157] + "..."
            lines.append(
                f"- `{result['title']}` gold=`{result['gold_hit']}` conflict=`{result['conflict_hit']}`: {snippet}"
            )
        lines.append("")
    lines.append("This is a transfer spot-check, not a multilingual theorem-3 replacement.")
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
