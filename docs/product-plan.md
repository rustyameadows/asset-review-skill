# Asset Review Product Plan

## Document purpose

Define the complete product idea, interaction model, durable review contract, phased delivery strategy, and decision framework for Asset Review in Codex/ChatGPT.

This document is the shared product source of truth. The implementation details for the first skill live in [phase-one-skill.md](phase-one-skill.md). The destination native experience lives in [future-native.md](future-native.md).

## Product summary

Asset Review is an agent-initiated surface for reviewing collections of creative project files.

The agent can create or gather work using image generation, computer use, project scripts, or other tools; organize the resulting files into a meaningful review session; and open that session for the user inside Codex. The user can scan the collection, inspect individual files, compare related versions, provide spatial feedback, and record decisions. Codex receives the review result as actionable project context, updates the work, and creates another review round.

The initial product is a distributable skill that generates a completely static HTML/CSS view. It contains no review state or annotation behavior; Codex/ChatGPT's existing browser annotation system owns feedback. The long-term product may introduce a native Codex surface around a richer structured contract.

### Phase-one boundary

Phase one is presentation only. The agent deliberately selects assets and generates semantic static HTML. The user annotates that HTML through Codex. The agent edits the work, regenerates the files, and refreshes the page. There is no application backend, API, submission flow, approval control, comment system, or mutable state. A tiny read-only loopback server may serve the static folder when the browser cannot open local files directly.

## Product thesis

Creative work needs a review loop different from source-code review or prose editing.

The important unit is not a line or paragraph. It may be a visual region, a crop, a relationship between two variants, a family of exports, or the consistency of a treatment across a collection. Effective review therefore requires four things at once:

1. Collection context: understand the body of work and how assets relate.
2. Visual inspection: examine an asset at an appropriate scale and background.
3. Decision capture: distinguish comments, preferences, approvals, rejections, and requested changes.
4. Agent continuity: turn review results directly into the next production action.

Codex already supplies the beginning and end of this loop: agents produce files and can receive browser annotations. Asset Review supplies the missing review-specific presentation and feedback model.

## Product promise

Ask the agent to prepare work for review. Receive a purpose-built review session without manually arranging files. Give feedback in visual and decision-oriented terms. Let the agent continue the work from that feedback without reconstructing which files or versions were meant.

## Primary user

The primary user is a creative professional working with an agent on visual production:

- graphic, brand, marketing, or production designer
- art or creative director
- photographer or photo editor
- video or motion creative
- product designer reviewing exported artifacts
- producer responsible for adaptation and delivery quality

The first version assumes one user reviewing local project work with one active Codex task. It does not assume a separate asset-management system or stakeholder portal.

## Core jobs to be done

### Prepare work for judgment

When an agent has produced multiple visual outputs, help the user understand what was produced, why the assets are grouped together, and what decisions are currently needed.

### Select a direction

When several concepts or source assets are plausible, help the user compare them and choose a preferred direction with clear rationale.

### Review production consistency

When a master has been adapted into many sizes or channels, help the user detect crop, hierarchy, typography, brand, and export inconsistencies across the set.

### Review revisions

When the agent has responded to earlier feedback, help the user compare previous and current work while preserving the history and status of unaffected assets.

### Approve delivery

When assets are believed to be final, help the user verify content, dimensions, filenames, formats, and approval state before packaging or publishing.

## Interaction model

The overall agent workflow is iterative, while the phase-one page itself remains stateless:

```text
User intent
  -> agent production or discovery
  -> review assembly
  -> review session
  -> Codex browser annotations
  -> agent action summary
  -> revision or delivery
  -> next review round or completion
```

### Agent responsibilities before review

The agent must:

- infer or confirm the objective
- identify the assets relevant to that objective
- exclude irrelevant source material
- group and order assets meaningfully
- identify version and derivation relationships
- preconfigure useful comparisons
- provide context and focused review questions
- warn about missing or unrenderable files
- preserve source work

### User responsibilities during review

The user can:

- scan the collection
- filter or group the work
- inspect metadata and production context
- open a focused asset
- zoom, pan, fit, and change the inspection background
- compare related assets
- annotate regions or cards
- annotate assets, captions, or comparison sides through Codex
- express preferences, approvals, rejections, and requested changes in those annotations
- tell the agent when the annotation pass is complete

### Agent responsibilities after review

The agent must:

- map feedback to stable review entities
- distinguish local changes from global instructions
- separate decisions from exploratory comments or questions
- summarize the interpreted action list
- request clarification only for consequential ambiguity
- keep interpretation and action context in the Codex task, not in the page
- preserve previously accepted work unless explicitly superseded
- perform or delegate revisions
- create a new round rather than replacing the old one
- narrow subsequent reviews to changed or affected work when useful

## Review modes

### Collection view

A contact sheet optimized for visual scanning and annotation. Phase one uses direct semantic figure cards, grouping, static navigation, lightweight filtering, and readable identity. The earlier prototype demonstrates the value of a dense grid and clear visual families, but phase one must not introduce review-state controls.

### List view

A compact production view emphasizing filename, dimensions, format, file size, version, and group. This is especially useful for export and delivery review.

### Focus view

A large viewer for one asset with zoom, pan, fit, 1:1 inspection, background switching, metadata, agent context, related versions, and review questions.

### Comparison view

A viewer for two related assets. Phase one needs side-by-side comparison. The prior prototype also demonstrates valuable future modes: vertical and horizontal reveals, difference visualization, synchronized zoom and pan, and background inspection.

### Review summary

A final checkpoint that shows decisions made, unresolved items, comments, and the action payload that will return to the agent.

## Review entities

The product contract must remain independent of any particular renderer.

### Review

- stable review ID
- project identity
- title and objective
- review instructions
- round number and lifecycle state
- source and previous-round references
- requested decisions
- summary counts

### Asset

- stable asset ID
- display label and source path
- media type and preview type
- dimensions, duration, page count, size, and checksum where applicable
- group, version, role, and tags
- source/derivative distinction
- agent context and review questions
- current status

### Group

- stable group ID
- label, purpose, and order
- grouping dimension such as concept, placement, channel, version family, or status
- member asset IDs

### Relationship

- source and target IDs
- relationship type such as version-of, derived-from, adaptation-of, reference-for, or replaces
- optional description

### Comparison

- stable comparison ID
- left and right asset IDs
- comparison purpose
- preferred initial mode
- synchronized-view settings
- decision requested

### Prompt

- stable prompt ID
- target entity IDs
- question text
- response type such as comment, choose-one, choose-many, status, or confirmation

### Review result

- status decisions
- selections and comparison preferences
- text comments
- spatial annotations
- global instructions
- unresolved questions
- result summary
- submission timestamp and actor

## Future native status model

Phase one has no status model. If a native Codex surface later needs structured decisions, use a small explicit state model:

Use a small explicit state model:

- `pending`: no decision yet
- `approved`: usable without requested changes
- `rejected`: direction or execution should not continue
- `changes_requested`: retain the asset identity but revise it
- `superseded`: replaced by a later asset or round

Comments do not implicitly change status. Approval applies to the reviewed version, not to all future files sharing a name or family.

## Review rounds and history

A phase-one review round is an optional immutable static snapshot of what the user was shown. Feedback remains in the Codex task. Most iterative work can rebuild the same folder; create a new round only when preserving the prior presentation is useful.

Each later round records:

- the previous round ID
- assets carried forward unchanged
- assets added, revised, removed, or superseded
- feedback addressed
- changes made by the agent
- unresolved items

This history is intentionally simpler than a full asset-management version graph, but it must be rich enough to explain why a new asset exists and what decision it is awaiting.

## Supported asset strategy

### Phase-one priority

- PNG
- JPEG
- WebP
- SVG
- GIF
- PDF rendered to page previews

### Phase-one optional

- MP4 with browser-native playback
- HTML, Markdown, and text previews
- presentation slide renders

### Later expansion

- richer video review and timecoded annotations
- audio waveforms
- design-file or application-specific previews
- 3D and interactive media

Unsupported assets still appear as file cards with metadata and a source path. Silent omission undermines trust in delivery review.

## Design principles

### Agent-initiated, user-controlled

The agent assembles the static presentation, but the user makes creative decisions through Codex's annotation flow.

### Decisions over dashboarding

The surface should make the current review questions obvious. Avoid turning phase one into a general digital asset manager.

### Stable identity everywhere

Every visual region, card, comparison, question, and annotation target must resolve to a stable contract ID.

### Preserve the work

Previews and thumbnails are disposable derivatives. Source assets and prior rounds are not overwritten.

### Context at the point of judgment

Place rationale, metadata, filenames, and review prompts close to the asset or comparison they describe.

### Progressive depth

Start with a scannable collection. Reveal detailed metadata and precision controls only when the user focuses an asset.

### Renderer independence

Do not embed essential review meaning only in visual position. Use semantic figures, stable URLs, visible labels, and stable IDs so annotations can map back to assets.

## Primary demo scenario

Use a campaign adaptation workflow because it demonstrates both creative judgment and production operations.

Inputs:

- creative brief and brand guidance
- approved campaign master
- product imagery and logo
- campaign copy

Outputs:

- social square
- social portrait
- story
- email hero
- display banner
- retail screen

The user should be able to review the collection, compare each adaptation to the master, identify a local crop issue, request a cross-format typography change, approve several assets, reject one execution, and receive a second round containing only affected work.

## Scope boundaries

### Included in the product direction

- local project assets and folders
- agent-curated review sessions
- collection, focus, and comparison modes
- metadata and relationships
- annotations and feedback owned by Codex/ChatGPT
- optional static presentation rounds
- action summaries returned to the agent
- a stable contract shared by web and native renderers

### Explicitly excluded from phase one

- source-asset editing inside the review UI
- public links, authentication, or stakeholder portals
- real-time multi-user collaboration
- production DAM features
- deep Adobe, Figma, or cloud-storage integrations
- full video timeline annotation
- automatic pixel-difference judgments
- native Codex application changes

## Product risks and mitigations

### Feedback cannot be mapped reliably

Mitigate with static semantic figures, stable IDs, visible labels, dedicated focus routes, and independently labeled comparison sides. Do not add a parallel submission system.

### The agent selects the wrong files

Mitigate with relevance heuristics, visible source paths, preflight summaries, missing-file warnings, and an option to revise the set before review.

### Approval state becomes unsafe or ambiguous

Keep approval interpretation in the Codex task. The static phase-one page never claims to persist or enforce approval state.

### Generated review apps diverge

Mitigate with a bundled renderer, schema validation, deterministic build scripts, fixtures, and visual regression tests.

### The review feels like a separate website

Mitigate by having the agent launch it, frame the decisions, receive the result in the same task, and immediately continue production work.

### Large collections become unusable

Mitigate with thumbnail generation, lazy loading, grouping, filters, list view, and explicit review subsets.

### Local files leak or are copied unnecessarily

Mitigate with project-local output, path allowlisting, no external network dependencies, clear derivative handling, and no publishing without authorization.

## Success measures

### Demo success

- A natural-language request produces a review without manual gallery configuration.
- The selected assets and relationships make sense to the user.
- The user can find and inspect every included asset.
- Annotations and decisions resolve to the intended asset IDs.
- Each annotation maps to the intended static asset figure or comparison side.
- The agent produces an accurate action summary.
- Revised work generates a traceable next round.

### Product learning

- time from completed production work to review-ready surface
- percentage of annotations mapped without clarification
- percentage of reviews producing actionable agent work
- frequency of collection, focus, and comparison usage
- approval reversals caused by status ambiguity
- number of unnecessary assets included per session
- user preference for full-set versus changed-only subsequent rounds

## Phased strategy

### Phase 0: Contract and interaction plan

Define entities, lifecycle, review result semantics, skill behavior, and test scenario. This repository bootstrap represents the start of Phase 0.

### Phase 1: Distributable skill

Build a deterministic static-site generator, manifest validator, semantic overview/focus/comparison templates, agent-openable local launch workflow, and agent-side feedback interpretation instructions. Permit only a read-only loopback static file server as transport; add no application backend or page-owned review state.

### Phase 2: Skill hardening

Expand media support, performance, comparison modes, accessibility, fixtures, schema migration, error handling, and real-world forward tests. Gather evidence for native product requirements.

### Phase 3: Native prototype

Implement the renderer-independent contract as a native Codex surface behind an experimental tool call. Compare its review completion and feedback quality with the skill.

### Phase 4: Native product

Ship a supported Asset Review surface with structured invocation and return values, deeper task integration, scalable media handling, and appropriate extension points.

## Decisions to validate before native investment

- Whether folder-based local sessions cover the dominant use cases.
- Whether browser annotations are precise enough for spatial creative feedback.
- Which review controls are essential versus merely familiar from creative tools.
- Whether users think in assets, groups, comparisons, or review questions first.
- What status language users understand consistently.
- How often a later round should show unchanged approved work.
- Which metadata materially affects decisions.
- How the user most clearly signals that an annotation pass is complete within Codex.
- Which limitations are caused by the web renderer versus the underlying contract.

## Product completion definition

Asset Review succeeds when a user can ask an agent to produce work, inspect and decide on that work visually, and have the agent continue correctly from the review without manually transferring filenames, comments, status, or version context.
