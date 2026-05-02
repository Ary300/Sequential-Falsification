#!/usr/bin/env python3
"""Build translated local theorem-3 datasets from WikiContradict."""

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


MYMEMORY_TRANSLATE_URL = "https://api.mymemory.translated.net/get"
GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
DEFAULT_LANGUAGES = "es:Spanish,de:German,it:Italian,fr:French,pt:Portuguese"
TOKEN_RE = re.compile(r"[A-Za-z0-9À-ÿ]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build translated theorem-3 WikiContradict datasets.")
    parser.add_argument("--max-examples", type=int, default=10)
    parser.add_argument("--languages", default=DEFAULT_LANGUAGES)
    parser.add_argument("--sleep-seconds", type=float, default=0.5)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--translation-provider", default="google", choices=["google", "mymemory"])
    parser.add_argument(
        "--cache-file",
        default=str(ROOT / "docs/generated/multilingual_theorem3_translation_cache.json"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "data/generated/multilingual_theorem3"),
    )
    parser.add_argument(
        "--summary-prefix",
        default=str(ROOT / "docs/generated/multilingual_theorem3_dataset_suite"),
    )
    return parser.parse_args()


def _parse_languages(spec: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for chunk in spec.split(","):
        item = chunk.strip()
        if not item:
            continue
        if ":" in item:
            code, label = item.split(":", 1)
        else:
            code, label = item, item
        items.append((code.strip().lower(), label.strip() or code.strip().lower()))
    return items


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
    provider: str,
    target_lang: str,
    cache: dict[str, Any],
    cache_path: Path,
    sleep_seconds: float,
    max_retries: int,
) -> str:
    stripped = str(text or "").strip()
    if not stripped:
        return ""
    key = f"translate::{provider}::{target_lang}::{stripped}"
    cached = cache.get(key)
    if isinstance(cached, str):
        return cached
    response = None
    for retry in range(max_retries):
        if provider == "google":
            response = session.get(
                GOOGLE_TRANSLATE_URL,
                params={"client": "gtx", "sl": "en", "tl": target_lang, "dt": "t", "q": stripped},
                timeout=30,
            )
        else:
            response = session.get(
                MYMEMORY_TRANSLATE_URL,
                params={"q": stripped, "langpair": f"en|{target_lang}"},
                timeout=30,
            )
        if response.status_code != 429:
            break
        time.sleep(sleep_seconds * (2 ** retry))
    if response is None:
        raise RuntimeError("No response returned from translation API.")
    response.raise_for_status()
    if provider == "google":
        payload = response.json()
        translated = "".join(str(chunk[0]) for chunk in payload[0] if isinstance(chunk, list) and chunk and chunk[0]).strip()
    else:
        translated = str(response.json().get("responseData", {}).get("translatedText", "")).strip()
    translated = translated or stripped
    cache[key] = translated
    _save_cache(cache_path, cache)
    time.sleep(sleep_seconds)
    return translated


def _translate_list(
    session: requests.Session,
    values: list[str],
    *,
    provider: str,
    target_lang: str,
    cache: dict[str, Any],
    cache_path: Path,
    sleep_seconds: float,
    max_retries: int,
) -> list[str]:
    out: list[str] = []
    for value in values:
        translated = _translate(
            session,
            value,
            provider=provider,
            target_lang=target_lang,
            cache=cache,
            cache_path=cache_path,
            sleep_seconds=sleep_seconds,
            max_retries=max_retries,
        )
        if translated not in out:
            out.append(translated)
    return out


def _normalize(text: str) -> str:
    return " ".join(match.group(0).lower() for match in TOKEN_RE.finditer(text or ""))


def _contains_any(text: str, answers: list[str]) -> bool:
    hay = _normalize(text)
    for answer in answers:
        needle = _normalize(answer)
        if needle and needle in hay:
            return True
    return False


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Multilingual Theorem-3 Dataset Suite",
        "",
        f"- source benchmark: `{summary['source_benchmark']}`",
        f"- examples per language: `{summary['max_examples']}`",
        f"- languages built: `{summary['languages_built']}`",
        "",
        "| Language | Code | Rows | Aligned hit | Conflict hit | Output |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in summary["languages"]:
        lines.append(
            "| "
            f"{item['label']} | {item['code']} | {item['rows']} | "
            f"{item['aligned_answer_in_context_rate']:.3f} | {item['conflict_answer_in_context_rate']:.3f} | "
            f"`{item['output_file']}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    cache_path = Path(args.cache_file)
    cache = _load_cache(cache_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    languages = _parse_languages(args.languages)
    rows = load_arbitration_dataset("wikicontradict", max_examples=args.max_examples)

    session = requests.Session()
    session.headers.update({"User-Agent": "SequentialFalsification/1.0 (multilingual theorem3 dataset builder)"})

    suite_languages: list[dict[str, Any]] = []
    for code, label in languages:
        translated_rows: list[dict[str, Any]] = []
        aligned_hits = 0
        conflict_hits = 0
        for row in rows:
            metadata = dict(row.get("metadata", {}) or {})
            question = _translate(
                session,
                str(row.get("question", "")),
                provider=args.translation_provider,
                target_lang=code,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            answers = _translate_list(
                session,
                [str(item) for item in list(row.get("answers") or []) if str(item).strip()],
                provider=args.translation_provider,
                target_lang=code,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            parametric_answers = _translate_list(
                session,
                [str(item) for item in list(metadata.get("parametric_answers") or []) if str(item).strip()],
                provider=args.translation_provider,
                target_lang=code,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            aligned_answers = _translate_list(
                session,
                [str(item) for item in list(metadata.get("aligned_context_answers") or []) if str(item).strip()],
                provider=args.translation_provider,
                target_lang=code,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            conflict_answers = _translate_list(
                session,
                [str(item) for item in list(metadata.get("conflict_context_answers") or []) if str(item).strip()],
                provider=args.translation_provider,
                target_lang=code,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            aligned_context_text = _translate(
                session,
                str(metadata.get("aligned_context_text", "")),
                provider=args.translation_provider,
                target_lang=code,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            conflict_context_text = _translate(
                session,
                str(metadata.get("conflict_context_text", "")),
                provider=args.translation_provider,
                target_lang=code,
                cache=cache,
                cache_path=cache_path,
                sleep_seconds=args.sleep_seconds,
                max_retries=args.max_retries,
            )
            translated_metadata = {
                **metadata,
                "benchmark": f"wikicontradict_{code}",
                "source_benchmark": "wikicontradict",
                "source_language": "en",
                "target_language": code,
                "target_language_label": label,
                "question_en": row.get("question"),
                "answers_en": list(row.get("answers") or []),
                "parametric_answers_en": list(metadata.get("parametric_answers") or []),
                "aligned_context_answers_en": list(metadata.get("aligned_context_answers") or []),
                "conflict_context_answers_en": list(metadata.get("conflict_context_answers") or []),
                "aligned_context_text_en": metadata.get("aligned_context_text"),
                "conflict_context_text_en": metadata.get("conflict_context_text"),
                "parametric_answers": parametric_answers or answers,
                "aligned_context_answers": aligned_answers or answers,
                "conflict_context_answers": conflict_answers,
                "aligned_context_text": aligned_context_text,
                "conflict_context_text": conflict_context_text,
            }
            translated_contexts = [aligned_context_text, conflict_context_text]
            translated_rows.append(
                {
                    "id": row.get("id"),
                    "question": question,
                    "answers": answers,
                    "contexts": [item for item in translated_contexts if item],
                    "condition": row.get("condition"),
                    "metadata": translated_metadata,
                }
            )
            aligned_hits += int(_contains_any(aligned_context_text, translated_metadata["aligned_context_answers"]))
            conflict_hits += int(_contains_any(conflict_context_text, translated_metadata["conflict_context_answers"]))

        output_path = output_dir / f"wikicontradict_{code}_{args.max_examples}.json"
        dump_json(translated_rows, output_path)
        suite_languages.append(
            {
                "code": code,
                "label": label,
                "rows": len(translated_rows),
                "aligned_answer_in_context_rate": (aligned_hits / len(translated_rows)) if translated_rows else 0.0,
                "conflict_answer_in_context_rate": (conflict_hits / len(translated_rows)) if translated_rows else 0.0,
                "output_file": str(output_path.relative_to(ROOT)),
            }
        )

    summary = {
        "source_benchmark": "wikicontradict",
        "max_examples": args.max_examples,
        "languages_built": len(suite_languages),
        "languages": suite_languages,
    }
    summary_prefix = Path(args.summary_prefix)
    dump_json(summary, summary_prefix.with_suffix(".json"))
    summary_prefix.with_suffix(".md").write_text(_render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
