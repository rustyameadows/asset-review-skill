#!/usr/bin/env python3
"""Inspect project assets and emit normalized inventory JSON."""

from __future__ import annotations

import argparse
from pathlib import Path

from asset_review import SCHEMA_VERSION, atomic_write_json, inspect_inputs, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Files or folders relative to the project root")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    assets = inspect_inputs(args.paths, root)
    atomic_write_json(
        args.output,
        {"schema_version": SCHEMA_VERSION, "project_root": str(root), "generated_at": utc_now(), "assets": assets},
    )
    print(f"Inspected {len(assets)} assets -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
