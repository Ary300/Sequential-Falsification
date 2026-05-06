#!/usr/bin/env python3
"""Compare closed-book control runs to existing aligned/conflict theorem-3 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _existing_map(payload: dict[str, Any]) -> dict[str, dict[str, float]]:
    out = {}
    for row in payload['rows']:
        out.setdefault(row['benchmark'], {})[row['split']] = row
    return out


def _control_map(payload: dict[str, Any]) -> dict[str, dict[str, float]]:
    out = {}
    for row in payload['trajectories']:
        out[row['benchmark']] = row
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--existing-final', required=True)
    parser.add_argument('--closed-book-control', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    existing = _existing_map(_load_json(Path(args.existing_final)))
    control = _control_map(_load_json(Path(args.closed_book_control)))

    rows = []
    for bench in sorted(existing):
        row = {'benchmark': bench}
        if 'conflict' in existing[bench]:
            row['conflict'] = existing[bench]['conflict']
        if 'no_conflict' in existing[bench]:
            row['aligned_context'] = existing[bench]['no_conflict']
        if bench in control and 'closed_book' in control[bench]:
            row['closed_book'] = control[bench]['closed_book']
        rows.append(row)

    Path(args.output).write_text(json.dumps({'rows': rows}, indent=2), encoding='utf-8')
    print(json.dumps({'output': args.output, 'benchmarks': [r['benchmark'] for r in rows]}, indent=2))


if __name__ == '__main__':
    main()
