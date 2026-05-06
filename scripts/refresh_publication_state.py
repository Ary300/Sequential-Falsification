"""Refresh progress-derived results, report artifacts, and publication bundles.

This script is the last-mile refresh path for the paper. It rebuilds any
`results_from_progress.json` files for selected run directories, regenerates
report artifacts, and then produces two publication bundles:

- a publication-ready bundle that excludes partial runs
- a monitoring bundle that includes partial runs
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str]) -> None:
    subprocess.run(args, check=True, cwd=ROOT)


def _has_progress_files(progress_dir: Path) -> bool:
    return any(progress_dir.glob("*_seed*_progress.json"))


def refresh_progress_dir(progress_dir: Path) -> Path | None:
    if not _has_progress_files(progress_dir):
        return None
    results_file = progress_dir / "results_from_progress.json"
    _run(
        [
            sys.executable,
            "src/collect_progress.py",
            "--progress-dir",
            str(progress_dir),
            "--output-file",
            str(results_file),
        ]
    )
    return results_file


def refresh_report(results_file: Path, output_dir: Path) -> None:
    _run(
        [
            sys.executable,
            "src/report.py",
            "--results-file",
            str(results_file),
            "--output-dir",
            str(output_dir),
        ]
    )


def refresh_bundle(results_files: list[Path], output_dir: Path, include_partial: bool) -> None:
    existing_results = [path for path in results_files if path.exists()]
    if not existing_results:
        return
    cmd = [
        sys.executable,
        "scripts/build_publication_bundle.py",
        "--output-dir",
        str(output_dir),
    ]
    if include_partial:
        cmd.append("--include-partial")
    for results_file in existing_results:
        cmd.extend(["--results-file", str(results_file)])
    _run(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh paper-facing publication state from completed and in-progress runs.")
    parser.add_argument(
        "--progress-dir",
        action="append",
        default=[],
        help="Run directory containing *_seed*_progress.json files. May be passed multiple times.",
    )
    parser.add_argument(
        "--results-file",
        action="append",
        default=[],
        help="Completed results file to include in the publication bundles. May be passed multiple times.",
    )
    parser.add_argument("--ready-output-dir", default="figures/publication_bundle_ready")
    parser.add_argument("--current-output-dir", default="figures/publication_bundle_current")
    parser.add_argument("--paper-generated-dir", default="paper/generated")
    args = parser.parse_args()

    progress_dirs = [Path(item) for item in args.progress_dir]
    completed_results = [Path(item) for item in args.results_file]

    progress_results: list[Path] = []
    for progress_dir in progress_dirs:
        refreshed = refresh_progress_dir(progress_dir)
        if refreshed is not None:
            progress_results.append(refreshed)
            refresh_report(refreshed, Path("figures") / progress_dir.name)

    all_results = [path for path in progress_results + completed_results if path.exists()]
    if not all_results:
        raise SystemExit("No progress directories or results files were provided.")

    ready_dir = Path(args.ready_output_dir)
    current_dir = Path(args.current_output_dir)
    refresh_bundle(all_results, ready_dir, include_partial=False)
    refresh_bundle(all_results, current_dir, include_partial=True)

    paper_generated_dir = Path(args.paper_generated_dir)
    paper_generated_dir.mkdir(parents=True, exist_ok=True)
    for source_name, source_dir in [
        ("publication_main_table_ready.tex", ready_dir),
        ("publication_main_table_current.tex", current_dir),
    ]:
        source = source_dir / "publication_main_table.tex"
        if source.exists():
            shutil.copyfile(source, paper_generated_dir / source_name)

    print(f"Refreshed {len(progress_results)} progress directories and {len(completed_results)} completed results files.")
    print(f"Publication-ready bundle: {ready_dir}")
    print(f"Monitoring bundle: {current_dir}")
    print(f"Paper-facing tables copied to: {paper_generated_dir}")


if __name__ == "__main__":
    main()
