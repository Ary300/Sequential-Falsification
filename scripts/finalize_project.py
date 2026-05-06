"""One-command endgame refresh for results, figures, publication bundles, and paper tables."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str]) -> None:
    subprocess.run(args, check=True, cwd=ROOT)


def _find_results_files(results_root: Path) -> list[Path]:
    files = set(results_root.glob("**/results.json"))
    files.update(results_root.glob("**/results_from_progress*.json"))
    return sorted(path for path in files if path.is_file())


def _publication_candidate_files(results_files: list[Path]) -> list[Path]:
    publication_prefix_roots = ("paper", "reviewer")
    paper_files = [
        path
        for path in results_files
        if path.parts and any(part.startswith(publication_prefix_roots) for part in path.parts)
    ]
    return paper_files or results_files


def _find_progress_dirs(results_root: Path) -> list[Path]:
    progress_dirs = []
    for path in sorted(results_root.glob("**/*_seed*_progress.json")):
        progress_dirs.append(path.parent)
    deduped: list[Path] = []
    seen: set[Path] = set()
    for directory in progress_dirs:
        if directory not in seen:
            seen.add(directory)
            deduped.append(directory)
    return deduped


def refresh_progress_and_reports(progress_dirs: list[Path]) -> list[Path]:
    refreshed_results: list[Path] = []
    for progress_dir in progress_dirs:
        output_file = progress_dir / "results_from_progress.json"
        _run(
            [
                sys.executable,
                "src/collect_progress.py",
                "--progress-dir",
                str(progress_dir),
                "--output-file",
                str(output_file),
            ]
        )
        refreshed_results.append(output_file)
        _run(
            [
                sys.executable,
                "src/report.py",
                "--results-file",
                str(output_file),
                "--output-dir",
                str(Path("figures") / progress_dir.name),
            ]
        )
    return refreshed_results


def build_publication_bundle(results_files: list[Path], output_dir: Path, include_partial: bool) -> None:
    cmd = [
        sys.executable,
        "scripts/build_publication_bundle.py",
        "--output-dir",
        str(output_dir),
        "--allow-empty",
    ]
    if include_partial:
        cmd.append("--include-partial")
    for results_file in results_files:
        cmd.extend(["--results-file", str(results_file)])
    _run(cmd)


def audit_publication_bundle(output_dir: Path) -> None:
    summary = output_dir / "publication_summary.json"
    if not summary.exists():
        return
    _run(
        [
            sys.executable,
            "scripts/audit_neurips_readiness.py",
            "--publication-summary",
            str(summary),
            "--output-dir",
            str(output_dir),
        ]
    )


def copy_paper_tables(bundle_ready_dir: Path, bundle_current_dir: Path, paper_generated_dir: Path) -> None:
    paper_generated_dir.mkdir(parents=True, exist_ok=True)
    table_map = {
        "publication_main_table_ready.tex": bundle_ready_dir / "publication_main_table.tex",
        "publication_main_table_current.tex": bundle_current_dir / "publication_main_table.tex",
        "publication_completion_table_ready.tex": bundle_ready_dir / "publication_completion_table.tex",
        "publication_completion_table_current.tex": bundle_current_dir / "publication_completion_table.tex",
        "publication_gap_recovery_table_ready.tex": bundle_ready_dir / "publication_gap_recovery_table.tex",
        "publication_gap_recovery_table_current.tex": bundle_current_dir / "publication_gap_recovery_table.tex",
        "publication_status_ready.md": bundle_ready_dir / "publication_status.md",
        "publication_status_current.md": bundle_current_dir / "publication_status.md",
        "publication_method_coverage_ready.md": bundle_ready_dir / "publication_method_coverage.md",
        "publication_method_coverage_current.md": bundle_current_dir / "publication_method_coverage.md",
        "publication_highlights_ready.md": bundle_ready_dir / "publication_highlights.md",
        "publication_highlights_current.md": bundle_current_dir / "publication_highlights.md",
        "neurips_readiness_ready.md": bundle_ready_dir / "neurips_readiness.md",
        "neurips_readiness_current.md": bundle_current_dir / "neurips_readiness.md",
        "neurips_readiness_ready.json": bundle_ready_dir / "neurips_readiness.json",
        "neurips_readiness_current.json": bundle_current_dir / "neurips_readiness.json",
    }
    for target_name, source in table_map.items():
        if source.exists():
            shutil.copyfile(source, paper_generated_dir / target_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize the project state from all local results artifacts.")
    parser.add_argument("--results-root", default="results")
    parser.add_argument("--ready-output-dir", default="figures/publication_bundle_ready")
    parser.add_argument("--current-output-dir", default="figures/publication_bundle_current")
    parser.add_argument("--paper-generated-dir", default="paper/generated")
    parser.add_argument(
        "--skip-progress-refresh",
        action="store_true",
        help="Do not rebuild results_from_progress.json files before generating bundles.",
    )
    args = parser.parse_args()

    results_root = Path(args.results_root)
    progress_dirs = _find_progress_dirs(results_root)
    refreshed_results: list[Path] = []
    if progress_dirs and not args.skip_progress_refresh:
        refreshed_results = refresh_progress_and_reports(progress_dirs)

    results_files = _find_results_files(results_root)
    merged_results = sorted({*results_files, *refreshed_results})
    if not merged_results:
        raise SystemExit(f"No results files found under {results_root}")

    publication_results = _publication_candidate_files(merged_results)
    ready_output_dir = Path(args.ready_output_dir)
    current_output_dir = Path(args.current_output_dir)
    build_publication_bundle(publication_results, ready_output_dir, include_partial=False)
    build_publication_bundle(publication_results, current_output_dir, include_partial=True)
    audit_publication_bundle(ready_output_dir)
    audit_publication_bundle(current_output_dir)
    copy_paper_tables(ready_output_dir, current_output_dir, Path(args.paper_generated_dir))

    print(f"Finalized project state from {len(merged_results)} results files.")
    if publication_results != merged_results:
        print(f"Publication bundle source set: {len(publication_results)} paper-scoped results files.")
    print(f"Publication-ready bundle: {ready_output_dir}")
    print(f"Monitoring bundle: {current_output_dir}")
    print(f"Paper outputs: {args.paper_generated_dir}")


if __name__ == "__main__":
    main()
