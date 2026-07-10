#!/usr/bin/env python3
"""Create an optional linked static review round from selected asset IDs."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from asset_review import assemble_review, load_json, utc_now


SCRIPT_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_ROOT.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", required=True, type=Path)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--include", nargs="*", help="Explicit asset IDs; defaults to all prior assets")
    parser.add_argument("--title")
    parser.add_argument("--objective")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    previous_dir = args.previous.resolve()
    previous_manifest = load_json(previous_dir / "review.json")
    manifest = copy.deepcopy(previous_manifest)
    old_review = previous_manifest["review"]
    round_number = int(old_review.get("round", 1)) + 1
    review_id = old_review["id"].rsplit("-round-", 1)[0] + f"-round-{round_number:02d}"
    manifest["review"].update(
        {
            "id": review_id,
            "title": args.title or old_review["title"],
            "objective": args.objective or old_review["objective"],
            "round": round_number,
            "previous_review_id": old_review["id"],
            "created_at": utc_now(),
        }
    )

    included = set(args.include) if args.include is not None else {asset["id"] for asset in manifest.get("assets", [])}

    manifest["assets"] = [asset for asset in manifest.get("assets", []) if asset["id"] in included]
    for asset in manifest["assets"]:
        asset.pop("preview_path", None)
        asset.pop("thumbnail_path", None)
        asset.pop("page_paths", None)
    asset_ids = {asset["id"] for asset in manifest["assets"]}
    manifest["groups"] = [
        {**group, "asset_ids": [asset_id for asset_id in group.get("asset_ids", []) if asset_id in asset_ids]}
        for group in manifest.get("groups", [])
        if asset_ids.intersection(group.get("asset_ids", []))
    ]
    manifest["comparisons"] = [
        comparison
        for comparison in manifest.get("comparisons", [])
        if comparison.get("left_asset_id") in asset_ids and comparison.get("right_asset_id") in asset_ids
    ]

    errors, warnings = assemble_review(
        manifest,
        args.project_root.resolve(),
        args.output.resolve(),
        SKILL_ROOT / "assets" / "review-app",
    )
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"Created {review_id} with {len(manifest['assets'])} assets -> {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
