#!/usr/bin/env python3
"""Build a compact PopQA popularity-bin table for paper-body use."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/generated/popqa_nqswap_real_benchmark_note.json"
OUT_PREFIX = ROOT / "docs/generated/popqa_body_bins_table"


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    bins = payload["benchmarks"]["popqa"]["popularity_bins"]
    summary = {
        "bins": bins,
        "read": "Bayes stays clearly ahead in the low- and mid-popularity bins and narrows to a small but still positive gain in the high-popularity bucket.",
    }
    md_lines = [
        "# PopQA Body Bin Table",
        "",
        "| Popularity bin | Bayes regret | Heuristic regret | CoCoA regret | Bayes gain vs heuristic |",
        "|---|---:|---:|---:|---:|",
    ]
    tex_lines = [
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        "Popularity bin & Bayes regret & Heuristic regret & CoCoA regret & Bayes gain \\\\",
        "\\midrule",
    ]
    for row in bins:
        md_lines.append(
            f"| {row['bin']} | {row['bayes_proxy_mean_regret']:.4f} | {row['heuristic_adaptive_mean_regret']:.4f} | "
            f"{row['cocoa_mean_regret']:.4f} | {row['bayes_vs_heuristic_gain']:.4f} |"
        )
        tex_lines.append(
            f"{row['bin']} & {row['bayes_proxy_mean_regret']:.4f} & {row['heuristic_adaptive_mean_regret']:.4f} & "
            f"{row['cocoa_mean_regret']:.4f} & {row['bayes_vs_heuristic_gain']:.4f} \\\\"
        )
    md_lines.extend(["", summary["read"], ""])
    tex_lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    OUT_PREFIX.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    OUT_PREFIX.with_suffix(".md").write_text("\n".join(md_lines), encoding="utf-8")
    OUT_PREFIX.with_suffix(".tex").write_text("\n".join(tex_lines), encoding="utf-8")
    print(json.dumps({"json": str(OUT_PREFIX.with_suffix('.json')), "md": str(OUT_PREFIX.with_suffix('.md')), "tex": str(OUT_PREFIX.with_suffix('.tex'))}, indent=2))


if __name__ == "__main__":
    main()
