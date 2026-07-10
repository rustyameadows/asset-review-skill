#!/usr/bin/env python3
"""Build the bundled Solar Club campaign review demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from asset_review import assemble_review, default_manifest, inspect_inputs


SKILL_ROOT = Path(__file__).resolve().parent.parent


DEMO_DETAILS = {
    "master.svg": {
        "id": "campaign-master",
        "label": "Approved campaign master",
        "group_id": "master",
        "role": "master",
        "context": "Approved master establishing the campaign hierarchy, color, product scale, and call to action.",
        "review_questions": ["Use this as the reference for every adaptation."],
    },
    "social-square.svg": {
        "id": "social-square",
        "label": "Social square",
        "group_id": "adaptations",
        "context": "1:1 social placement derived from the approved master.",
        "review_questions": ["Is the hierarchy preserved?", "Is the product scale appropriate?"],
    },
    "social-portrait.svg": {
        "id": "social-portrait",
        "label": "Social portrait",
        "group_id": "adaptations",
        "context": "4:5 feed placement.",
        "review_questions": ["Does the composition feel balanced in the taller format?"],
    },
    "story.svg": {
        "id": "story",
        "label": "Story",
        "group_id": "adaptations",
        "context": "9:16 story placement with a full-width interaction area.",
        "review_questions": ["Is the lower call to action comfortably inside the safe area?"],
    },
    "email-hero.svg": {
        "id": "email-hero",
        "label": "Email hero",
        "group_id": "adaptations",
        "context": "Wide email placement intended to preserve the master composition at smaller display sizes.",
        "review_questions": ["Will the headline remain readable in an email column?"],
    },
    "display-banner.svg": {
        "id": "display-banner",
        "label": "Display banner",
        "group_id": "adaptations",
        "context": "Compressed display placement with reduced supporting copy.",
        "review_questions": ["Is the message legible at banner scale?"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=SKILL_ROOT / ".codex" / "reviews" / "solar-club-round-01")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    assets = inspect_inputs(["examples/demo-assets"], SKILL_ROOT)
    for asset in assets:
        asset.update(DEMO_DETAILS[asset["filename"]])
    manifest = default_manifest(
        assets,
        title="Solar Club campaign adaptations",
        objective="Approve composition, hierarchy, and readiness across six campaign placements.",
        review_id="solar-club-round-01",
        instructions="Compare each adaptation with the approved master and annotate any asset that needs revision.",
    )
    manifest["groups"] = [
        {"id": "master", "label": "Approved master", "asset_ids": ["campaign-master"]},
        {"id": "adaptations", "label": "Campaign adaptations", "asset_ids": [asset["id"] for asset in assets if asset["id"] != "campaign-master"]},
    ]
    manifest["relationships"] = [
        {
            "id": f"{asset['id']}-from-master",
            "type": "adaptation_of",
            "source_asset_id": "campaign-master",
            "target_asset_id": asset["id"],
        }
        for asset in assets
        if asset["id"] != "campaign-master"
    ]
    manifest["comparisons"] = [
        {
            "id": f"master-vs-{asset['id']}",
            "label": f"Master / {asset['label']}",
            "left_asset_id": "campaign-master",
            "right_asset_id": asset["id"],
            "purpose": "Check hierarchy, color, and product scale against the approved master.",
        }
        for asset in assets
        if asset["id"] != "campaign-master"
    ]
    errors, warnings = assemble_review(manifest, SKILL_ROOT, args.output.resolve(), SKILL_ROOT / "assets" / "review-app")
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"Demo review built: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
