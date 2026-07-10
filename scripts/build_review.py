#!/usr/bin/env python3
"""Build a self-contained Asset Review round from a manifest or project paths."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from asset_review import assemble_review, deduplicate_ids, default_manifest, inspect_inputs, load_json


SCRIPT_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_ROOT.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path, help="Draft review.json")
    source.add_argument("--paths", nargs="+", help="Files or folders relative to project root")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="Asset review")
    parser.add_argument("--objective", default="Review the selected assets and record decisions.")
    parser.add_argument("--instructions")
    parser.add_argument("--review-id")
    parser.add_argument("--round", type=int, default=1)
    parser.add_argument("--previous-review-id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    if args.manifest:
        manifest = load_json(args.manifest)
    else:
        assets = inspect_inputs(args.paths, root)
        deduplicate_ids(assets)
        manifest = default_manifest(
            assets,
            title=args.title,
            objective=args.objective,
            review_id=args.review_id,
            round_number=args.round,
            previous_review_id=args.previous_review_id,
            instructions=args.instructions,
        )

    errors, warnings = assemble_review(manifest, root, args.output.resolve(), SKILL_ROOT / "assets" / "review-app")
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(json.dumps({"review_dir": str(args.output.resolve()), "assets": len(manifest.get("assets", []))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
