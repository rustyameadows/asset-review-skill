# Static Review Contract

Read this reference when authoring or validating the optional `review.json` used to generate a static Asset Review site.

The manifest describes presentation only. It does not contain annotations, comments, decisions, approval state, browser state, or submission state.

## Contract rules

- Use schema version `1.0`.
- Use stable unique IDs for reviews, assets, groups, relationships, and comparisons.
- Keep `source_path` values relative to the declared project root.
- Treat generated preview paths as disposable output.
- Put every reviewable asset into the initial generated HTML.
- Regenerate HTML after source changes; do not add a live data API.

## review.json

```json
{
  "schema_version": "1.0",
  "review": {
    "id": "campaign-round-01",
    "title": "Campaign review",
    "objective": "Compare adaptations with the approved master",
    "instructions": "Annotate any asset that needs revision.",
    "round": 1,
    "previous_review_id": null,
    "created_at": "2026-07-10T12:00:00Z"
  },
  "assets": [],
  "groups": [],
  "relationships": [],
  "comparisons": []
}
```

## Asset

Required fields:

- `id`: stable identity within the review
- `label`: human-facing name
- `filename`: source filename
- `source_path`: project-root-relative path
- `media_type`: MIME type
- `preview_kind`: `image`, `video`, `pdf`, or `file`
- `file_size`: source bytes
- `content_fingerprint`: source SHA-256

Useful optional fields:

- `group_id`
- `width`, `height`, `duration`, or `page_count`
- `version`, `role`, and `tags`
- `context` or `agent_context`
- `review_questions`

The generator adds `preview_path`, `thumbnail_path`, or `page_paths` only to reference files copied or rendered inside the static output.

## Group

```json
{
  "id": "social",
  "label": "Social adaptations",
  "asset_ids": ["square-v3", "story-v2"]
}
```

Groups become static `<section>` elements. Assets become direct `<figure>` children inside the group collection.

## Relationship

```json
{
  "id": "story-from-master",
  "type": "adaptation_of",
  "source_asset_id": "master-v1",
  "target_asset_id": "story-v2",
  "description": "Story placement derived from the approved master"
}
```

Relationship types may include `version_of`, `derived_from`, `adaptation_of`, `reference_for`, or `replaces`.

## Comparison

```json
{
  "id": "master-vs-story",
  "label": "Master / Story",
  "left_asset_id": "master-v1",
  "right_asset_id": "story-v2",
  "purpose": "Check hierarchy and product scale"
}
```

Each comparison becomes its own static HTML page containing two directly rendered and independently labeled `<figure>` elements.

## Output contract

```text
<review-id>/
  index.html
  list.html
  review.json
  diagnostics.json
  static/
    styles.css
    enhancements.js
  asset/
    <asset-id>.html
  comparison/
    <comparison-id>.html
  assets/
  thumbnails/
  pages/
```

There is no server process and no mutable state file.

## Optional rounds

Create another round only when preserving the earlier static presentation is valuable:

- increment `review.round`
- assign a new `review.id`
- set `review.previous_review_id`
- choose the assets deliberately
- generate a separate static folder

For ordinary iterative work, rebuilding the same folder and refreshing the page is sufficient.
