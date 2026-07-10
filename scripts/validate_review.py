#!/usr/bin/env python3
"""Validate a generated static Asset Review manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from asset_review import load_json, validate_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_dir", type=Path)
    parser.add_argument("--project-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    review_dir = args.review_dir.resolve()
    manifest = load_json(review_dir / "review.json")
    errors, warnings = validate_manifest(manifest, args.project_root.resolve() if args.project_root else None)
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"Review is valid: {review_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
