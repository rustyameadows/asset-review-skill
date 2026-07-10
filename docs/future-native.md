# Future Native Asset Review

## Purpose

Describe the destination native Asset Review surface inside Codex/ChatGPT and show how it can replace the phase-one browser renderer without replacing the review workflow or data model.

This is a future product plan, not a commitment to begin by modifying the Codex application. Native work should follow evidence from the skill prototype.

## Native product definition

Asset Review becomes a first-class task surface alongside code diffs, document editing, terminal output, and web previews.

An agent invokes the surface with structured assets, relationships, context, and requested decisions. Codex renders the session natively. The user reviews the work and submits structured results. The agent receives those results as tool output and continues the current task.

The experience should feel like a combination of:

- a contact sheet for collections
- a focused media inspector
- a version comparison tool
- a lightweight creative approval system
- an agent checkpoint

It should not become a full digital asset manager or creative editor by default.

## Why native

The skill is capable of proving the workflow, but a native surface can improve:

- invocation and lifecycle integration with the current task
- stable structured feedback without a local state bridge
- performance for large collections and high-resolution media
- keyboard, pointer, and accessibility behavior
- consistent annotation targets
- security boundaries for local files
- media decoding and preview generation
- side-by-side and reveal comparisons
- persistence, restoration, and task history
- coherent visual design with the rest of Codex

Native implementation is justified only if the skill validates that users value the loop and identifies which limitations belong to the generated browser surface.

## Product principles

### The agent frames; the user decides

The invocation should include a review objective and requested decisions. The native surface should make those decisions visible without restricting the user from adding broader feedback.

### Review is part of the task

Opening, submitting, revisiting, and superseding a review should remain associated with the originating Codex task and agent turn.

### Structured state is authoritative

Approval, rejection, selection, and requested changes should return as typed results. Spatial annotations supplement these decisions rather than acting as the only persistence channel.

### Versions are immutable review targets

An approval applies to the specific asset content reviewed. If the content changes, the surface must make the new version and its decision state explicit.

### The contract outlives the renderer

The native surface should consume the same logical entities proven by phase one: review, asset, group, relationship, comparison, prompt, and result.

## Native invocation contract

A future tool might expose an invocation conceptually similar to:

```text
open_asset_review(
  review_id,
  title,
  objective,
  instructions,
  round,
  assets,
  groups,
  relationships,
  comparisons,
  prompts,
  requested_decisions,
  previous_review
)
```

The implementation could use a resource handle or manifest reference for large inputs rather than embedding all metadata in one call. The conceptual requirements remain:

- stable caller-supplied or system-normalized IDs
- explicit local file authorization
- immutable asset versions
- optional preview derivatives
- declared relationships and comparison intent
- review questions and required decisions
- linkage to prior rounds

### Example invocation

```json
{
  "review_id": "spring-campaign-round-02",
  "title": "Spring campaign revisions",
  "objective": "Confirm crop and typography changes before delivery",
  "round": 2,
  "instructions": "Review only the revised portrait and story placements.",
  "assets": [
    {
      "id": "story-v2",
      "uri": "project://exports/story-v2.png",
      "label": "Story v2",
      "media_type": "image/png",
      "content_fingerprint": "...",
      "status": "pending"
    }
  ],
  "groups": [],
  "relationships": [],
  "comparisons": [],
  "prompts": [],
  "requested_decisions": ["approve_for_delivery"],
  "previous_review": "spring-campaign-round-01"
}
```

## Native return contract

The user submission should return a typed result:

```text
asset_review_result:
  review_id
  lifecycle
  status_decisions
  selections
  comparison_preferences
  annotations
  comments
  requested_changes
  general_notes
  unanswered_prompts
  submitted_at
```

### Result semantics

- `status_decisions` records explicit version-scoped approval state.
- `selections` records choose-one or choose-many decisions.
- `comparison_preferences` records which side or direction won and optional rationale.
- `annotations` records geometry, target ID, coordinate space, comment, and optional attachment.
- `requested_changes` records structured local or global revision intent when the UI can classify it confidently.
- `comments` preserves unclassified or conversational feedback without forcing a false status.
- `unanswered_prompts` tells the agent which requested decisions remain unresolved.

The agent remains responsible for summarizing and applying the result. The surface should not mutate source assets directly.

## Native information architecture

### Task-level review card

The originating task shows a compact card with:

- title and objective
- round and lifecycle
- asset count
- decision progress
- unresolved changes
- open or resume action
- result summary after submission

### Collection surface

The default view displays a responsive contact sheet or production list.

Controls include:

- group and filter
- sort
- grid/list toggle
- multi-select
- status filters
- compare selected
- review-summary access

Cards include preview, label, essential metadata, relationship cues, status, and requested-decision indicators.

### Focus surface

The focused asset view includes:

- native high-resolution media rendering
- fit, fill, 1:1, zoom, and pan
- checker, black, white, and custom backgrounds
- metadata and source location
- status, comment, and annotation controls
- agent context and review prompts
- related versions and derivations
- previous/next navigation within the active group

### Comparison surface

Native comparison should grow in levels:

1. side-by-side with synchronized navigation
2. vertical and horizontal reveal
3. opacity blend or flicker
4. difference visualization where media semantics support it
5. master/adaptation overlays with alignment controls

The surface must identify both operands persistently and retain independent or synchronized zoom state intentionally.

### Review summary surface

Before submission, show:

- status counts
- selected directions
- requested changes grouped by local/global scope
- unanswered required prompts
- annotations with asset thumbnails
- general notes
- a clear statement of what will return to the agent

## Annotation model

Native annotations should be typed, spatial, and renderer-independent.

An annotation needs:

- stable annotation ID
- review and asset version IDs
- geometry type: point, rectangle, freehand path, text range, time range, or page region
- normalized coordinates relative to the canonical media space
- viewport transform at creation time
- comment and optional classification
- author and timestamp
- resolved/unresolved state
- optional relationship to a prompt or comparison

For comparisons, annotations must specify whether they target the left asset, right asset, both, or the comparison relationship itself.

## Native state and lifecycle

Suggested lifecycle states:

```text
draft -> open -> submitted -> superseded
                 |             ^
                 -> reopened ---
```

- `draft`: assembled by the agent but not yet presented.
- `open`: visible and accepting review state.
- `submitted`: decisions returned to the agent and frozen as a result version.
- `reopened`: a new editable result revision associated with the same asset set.
- `superseded`: replaced by a later review round.

Reopening should create a new result revision rather than silently altering the result previously consumed by the agent.

## System architecture

### Agent/tool boundary

The agent submits a validated review contract through a dedicated tool. Tool output represents user-submitted results, cancellation, or interruption. The agent should be able to resume other work while a review remains open if the product supports asynchronous task interaction.

### Asset access layer

Use authorized project-scoped resource handles rather than raw unrestricted filesystem paths. The layer should:

- authorize each source
- fingerprint content
- expose metadata
- provide safe preview streams
- invalidate stale versions
- distinguish originals from generated derivatives

### Preview pipeline

Generate thumbnails and decoded previews through native or sandboxed services. Cache by content fingerprint and rendering parameters. Support cancellation, incremental loading, and memory bounds for large assets.

### Review state store

Persist review contracts, result revisions, annotations, and lifecycle transitions as task-linked structured data. The project may optionally export a portable manifest, but native state should not depend on writing into the user's source tree.

### Renderer

Render collection, focus, comparison, and summary modes from the structured contract. UI state such as current zoom or filter need not enter the durable result unless it affects an annotation or decision.

### Result delivery

On submission, validate completeness, freeze the result revision, and deliver it as structured tool output. Record which agent turn consumed it and which later review supersedes it.

## Relationship to project files

Native Asset Review should support three persistence modes:

### Task-only

The review lives within Codex task state. Appropriate for quick selections and transient generation work.

### Project-recorded

Codex exports a portable manifest and result beneath `.codex/reviews/`. Appropriate when approval history should travel with the project.

### Hybrid

Native state is authoritative for interaction, while a project record is written at meaningful lifecycle points. This is likely the most useful default for production work if the user authorizes project writes.

The product must not imply that native approval state is automatically shared with external systems.

## Extension model

The core product should remain format-agnostic, with media-specific capabilities supplied through preview providers.

Potential providers include:

- raster and vector image renderer
- PDF and document page renderer
- video player and frame-strip provider
- presentation slide renderer
- HTML and interactive preview sandbox
- design-tool integration provider

Providers should return canonical preview surfaces, metadata, supported annotation geometries, and comparison capabilities. They should not redefine status or review lifecycle semantics.

## Native safety and trust

- Require project-scoped authorization for local assets.
- Warn when content changed after a review was opened.
- Scope approvals to a fingerprinted version.
- Keep source editing outside the review surface unless introduced as a separate explicit capability.
- Sanitize active formats and isolate interactive previews.
- Avoid uploading local content merely to render it.
- Make external sharing a separate, explicit product with its own permissions.
- Preserve an audit trail of submitted decisions and superseding rounds.

## Performance targets

Targets should be finalized from prototype measurements, but the native experience should aim for:

- first useful collection content quickly through progressive thumbnails
- smooth scrolling for hundreds of assets
- bounded memory for high-resolution collections
- responsive zoom and pan for a focused image
- background preview generation that can be cancelled
- instant restoration of prior filters, selection, and focus state
- content-fingerprint caching across review rounds

## Accessibility targets

- complete collection and status workflows by keyboard
- predictable focus when entering and leaving focus/comparison modes
- screen-reader identity and metadata for each asset
- text equivalents for status and relationship cues
- adjustable grid density and interface scaling
- reduced-motion modes for comparison effects
- non-color indication for difference and status
- accessible annotation lists even when spatial annotations cannot be perceived visually

## Native phased roadmap

### Native milestone 0: Evidence review

Analyze skill usage, feedback-mapping failures, common asset counts, media types, comparison usage, and user-requested controls. Freeze a native contract proposal only after this evidence.

### Native milestone 1: Read-only prototype

Implement tool invocation, task card, collection view, focus view, safe local asset handles, and cancellation. Return no structured decisions yet.

Exit criterion: native rendering is materially more reliable or integrated than the browser app.

### Native milestone 2: Decisions and results

Add status, selections, comments, prompts, review summary, submission, and typed tool output.

Exit criterion: the agent can consume a complete native review without browser-state translation.

### Native milestone 3: Spatial annotation and comparison

Add normalized annotations, side-by-side comparison, synchronized inspection, reveal modes, and annotation lists.

Exit criterion: the native surface supports the highest-value feedback patterns observed in the skill.

### Native milestone 4: Rounds and project records

Add previous-round relationships, result revisions, changed-only review, project export, and stale-content handling.

Exit criterion: multi-round production work is traceable and safe.

### Native milestone 5: Media and scale

Add provider extensibility, richer documents and video, large-collection performance, caching, and recovery.

Exit criterion: the surface supports real production projects beyond the original image campaign demo.

## Migration from the skill

The skill should transition in stages:

1. Detect whether the native Asset Review tool is available.
2. Build the same logical review contract regardless of renderer.
3. Invoke the native surface when available.
4. Fall back to the generated browser application when unavailable or when a format requires it.
5. Normalize browser and native results into one feedback taxonomy.
6. Eventually reduce the skill to coordination guidance and compatibility helpers.

Projects with `.codex/reviews/` history should be importable into the native surface. Schema versions and content fingerprints are therefore essential in phase one.

## Native success criteria

- Users understand that an agent can initiate Asset Review.
- Opening and submitting a review feels native to the current task.
- Structured results eliminate most feedback-mapping ambiguity.
- Version-scoped approvals remain trustworthy across revisions.
- Collection and comparison workflows outperform general browser preview.
- The surface handles real production-scale collections responsively.
- The agent can proceed from review results without asking users to restate file context.
- The shared contract allows browser fallback and project history import.

## Questions the skill must answer first

- Which review mode is the most common entry point?
- Are explicit prompts helpful or intrusive?
- Do users require a formal submit step?
- How often do annotations span multiple assets?
- Which comparison modes change decisions materially?
- What should happen to approved assets after a global revision request?
- How much history should be visible during the current round?
- Which metadata belongs on cards versus in the inspector?
- What collection size exposes the limits of the browser approach?
- Which asset providers are necessary for an initial native release?

## Native product boundary

Native Asset Review should own presentation, inspection, decisions, annotations, and structured return to the agent. It should not automatically own source editing, external collaboration, publishing, or digital asset management. Those capabilities may integrate with Asset Review, but keeping the review boundary clear is what allows the interaction model to remain dependable.
