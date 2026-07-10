---
name: asset-review
description: Create static visual review pages for project assets. Use when Codex needs to deliberately present selected images, documents, generated media, creative directions, campaign variants, or delivery exports in an annotation-friendly grid, focused view, or comparison view inside the in-app browser.
---

# Asset Review

Create a plain static HTML/CSS presentation for assets the agent has deliberately selected. Treat the page as a visual surface for Codex/ChatGPT's existing browser annotation system.

Do not implement feedback, comments, approval state, annotation handling, persistence, or submission inside the generated site. The site must remain unaware of annotation mode.

## Prepare the review

1. Infer the review objective from the current task.
2. Select only assets relevant to that objective; do not automatically dump an entire project into the view.
3. Identify useful groups, labels, context, and comparisons.
4. Preserve source files.
5. Generate a static site beneath `.codex/reviews/<review-id>/`.
6. Open the generated `index.html` directly when supported; otherwise start the bundled read-only static file server and open its loopback URL.
7. Tell the user what to inspect or compare.
8. Receive feedback only through Codex/ChatGPT's browser annotation flow.
9. Edit the source work, regenerate the static site, and refresh the browser page.

## Generate the static site

Resolve this skill's directory as `SKILL_DIR`. For a straightforward selected set, run:

```bash
python3 "$SKILL_DIR/scripts/build_review.py" \
  --project-root "$PROJECT_ROOT" \
  --paths exports/master.png exports/social exports/email \
  --output "$PROJECT_ROOT/.codex/reviews/campaign-round-01" \
  --title "Campaign review" \
  --objective "Compare the adaptations with the approved master"
```

Use `--manifest draft-review.json` when the agent needs explicit labels, groups, context, or prepared comparisons. Read [references/review-contract.md](references/review-contract.md) before authoring a manifest.

Validate the generated folder:

```bash
python3 "$SKILL_DIR/scripts/validate_review.py" \
  "$PROJECT_ROOT/.codex/reviews/campaign-round-01" \
  --project-root "$PROJECT_ROOT"
```

Open the generated file directly when the browser permits local files:

```text
file://<absolute-project-path>/.codex/reviews/campaign-round-01/index.html
```

When the agent cannot navigate to `file://`, serve the folder with the bundled transport helper:

```bash
python3 "$SKILL_DIR/scripts/serve_review.py" \
  "$PROJECT_ROOT/.codex/reviews/campaign-round-01"
```

Open the printed loopback URL. This helper only serves static files with no-cache headers. It has no application endpoints, accepts no writes, and owns no review or annotation state. Stop it when the review task ends.

## Keep the HTML annotation-friendly

The generator writes all asset content into the initial HTML response. Preserve these rules when customizing the template:

- Render every overview item as a visible, labeled `<figure>`.
- Use ordinary `<img>`, `<video>`, `<figcaption>`, heading, link, list, and definition-list elements.
- Give each asset figure a unique `id`, accessible label, and stable asset ID.
- Keep focused assets and comparison sides as distinct semantic figures.
- Never create the asset collection through JavaScript.
- Never place a canvas, opaque interaction layer, or annotation shim over an asset.
- Never react to annotation mode or attempt to store annotations.
- Ensure the complete review remains usable when JavaScript is disabled.

The bundled `assets/review-app/enhancements.js` only changes inspection backgrounds on focus and comparison pages. It must not fetch review data, generate content, or own durable state.

## Refresh after edits

After changing source assets, rerun the same build command against the same output directory and refresh the open file in the in-app browser. A new review round is optional and should be created only when the agent or user needs a preserved historical presentation.

Use `scripts/create_round.py` to create a separate linked round from a prior manifest. It does not interpret feedback or choose affected assets; pass `--include` when the agent wants a subset.

## Guardrails

- Keep the source selection deliberate and explain exclusions when relevant.
- Never overwrite source assets to make them previewable.
- Never publish or upload the static review without explicit authorization.
- Do not copy sensitive or unrelated files into the review folder.
- Call out missing, unrenderable, duplicated, or stale assets.
- Let Codex/ChatGPT own the entire annotation and feedback lifecycle.

## Bundled resources

- Use `scripts/inspect_assets.py` for inventory-only work.
- Use `scripts/build_review.py` to generate the static site.
- Use `scripts/validate_review.py` to verify the manifest and file references.
- Use `scripts/serve_review.py` only as a read-only transport when the in-app browser cannot open `file://`.
- Use `scripts/create_round.py` only when a separate historical round is useful.
- Use `assets/review-app/styles.css` and `enhancements.js` as the static template resources.
- Read [references/feedback-mapping.md](references/feedback-mapping.md) only when the agent needs help interpreting annotations returned by Codex; the generated page never reads it.
