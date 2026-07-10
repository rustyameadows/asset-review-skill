---
name: asset-review
description: Create and coordinate browser-based visual review sessions for project assets. Use when Codex needs to present folders or selected images, documents, generated media, campaign variants, creative directions, or delivery exports for browsing, comparison, annotation, approval, rejection, or revision before continuing production work.
---

# Asset Review

Create a project-local review session that connects asset production to structured user feedback. Treat the review surface as a working checkpoint in the agent loop, not as a standalone gallery.

## Coordinate the review

1. Infer the review objective from the request and current project context.
2. Inspect the proposed source folders and select only assets relevant to that objective.
3. Identify useful groups, version relationships, comparisons, and decisions.
4. Preserve source files. Write generated review artifacts only beneath `.codex/reviews/` unless the user requests another location.
5. Create a stable manifest before rendering the interface.
6. Open the review in the in-app browser and state the decisions needed from the user.
7. Map returned annotations and decisions to stable asset IDs.
8. Summarize the interpreted actions before modifying source work.
9. Preserve approved assets unless the user explicitly includes them in a later change.
10. Create a new round for revised work and retain prior review history.

## Model the session

Create one directory per review round:

```text
.codex/reviews/<review-id>/
  review.json
  state.json
  index.html
  assets/
  thumbnails/
```

Use `review.json` for the immutable presentation contract: identity, objective, instructions, source assets, groups, relationships, comparisons, metadata, review questions, and requested decisions.

Use `state.json` for mutable review results: status changes, selections, comments, annotations, review summary, timestamps, and links to prior or subsequent rounds.

Assign every asset, group, comparison, and prompt a stable ID. Keep source paths explicit and distinguish original files from copied or rendered review derivatives.

## Build the surface

Provide these modes when relevant:

- Grid view for scanning and selecting a collection.
- List view for filenames, dimensions, formats, and status.
- Focus view for zoom, pan, metadata, context, and review questions.
- Comparison view for previous/current, master/adaptation, or direction A/B.

Make asset identity visible near every reviewable region so browser annotations can be mapped back reliably. Prefer a small number of clear controls over an asset-management dashboard.

Support PNG, JPEG, WebP, SVG, GIF, and rendered PDF pages first. Represent unsupported files with useful metadata and a source path instead of silently omitting them.

## Interpret feedback

Classify each returned note as one of:

- approval
- rejection
- asset-specific revision
- global revision
- comparison preference
- question
- project instruction

Resolve each note to one or more stable asset IDs. If a mapping is ambiguous and would change production work materially, ask the user before editing. Otherwise update state, summarize the action list, perform or delegate the requested work, and generate the next review round.

## Guardrails

- Never overwrite or transform source assets merely to make them previewable.
- Never treat a visual annotation as approval unless its meaning is clear.
- Never silently replace a prior round.
- Avoid copying sensitive or unrelated files into the review directory.
- Keep the review runnable locally; do not publish or upload it without explicit authorization.
- Call out missing, unrenderable, duplicated, or stale assets before requesting a decision.

## Development status

This repository currently defines the interaction contract and implementation plan. Consult the documents in `docs/` when implementing or evaluating the phase-one renderer and the future native surface.
