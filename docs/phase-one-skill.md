# Phase One: Asset Review Skill

## Objective

Build a distributable Codex skill that turns selected project files into a consistent local review application, opens it in the Codex in-app browser, persists review decisions, and helps the agent translate feedback into the next production action.

Phase one must prove the interaction loop and the review contract. It does not need to prove every media type, comparison technique, or asset-management feature.

## Phase-one outcome

A user can say:

> Prepare the latest campaign assets for review.

Codex can then:

1. identify the relevant files
2. explain the proposed review objective and scope
3. build a validated review manifest
4. generate previews and a local browser application
5. open the application in the in-app browser
6. collect status decisions and browser annotations
7. map feedback to stable asset IDs
8. summarize the requested work
9. update assets through the appropriate tools
10. create a traceable second review round

## Implementation principles

- Keep the skill instructions short; put deterministic work in scripts and boilerplate in assets.
- Generate the same application for every review rather than asking the agent to invent UI code per session.
- Treat the manifest as the source of presentation truth and state as the source of decision truth.
- Keep the web application local and dependency-light.
- Preserve source files and prior rounds.
- Make the first complete loop excellent before adding media breadth.
- Design schemas as candidates for a native tool contract, not as DOM implementation details.

## Proposed repository structure

```text
asset-review/
  SKILL.md
  agents/
    openai.yaml
  assets/
    review-app/
      index.html
      app.js
      styles.css
  references/
    review-contract.md
    feedback-mapping.md
  scripts/
    build_review.py
    inspect_assets.py
    render_previews.py
    validate_review.py
    create_round.py
  tests/
    fixtures/
    test_contract.py
    test_build_review.py
  docs/
    product-plan.md
    phase-one-skill.md
    future-native.md
```

Only add a resource when implementation begins to use it. The checked-in browser template belongs in `assets/`; schema and feedback guidance belong in `references/`; repeatable inspection, rendering, validation, and generation belong in `scripts/`.

## Generated project structure

```text
<project>/.codex/reviews/
  <review-slug>-round-01/
    review.json
    state.json
    index.html
    static/
      app.js
      styles.css
    assets/
      <safe review derivatives>
    thumbnails/
    pages/
      <rendered PDF pages>
    diagnostics.json
```

The generator should copy only files required by the browser sandbox. When direct local references are supported and safe, prefer references. Any copied or rendered item must remain distinguishable from its source path in the manifest.

## Skill workflow

### 1. Establish the review objective

Infer the objective from the current task. Ask a question only if choosing the wrong objective would materially change the assets or requested decisions.

Produce an internal preflight containing:

- objective
- candidate paths
- inclusion and exclusion rationale
- proposed groups
- likely comparisons
- requested decisions

For a large or ambiguous set, show a concise scope summary before generating the review.

### 2. Discover and inspect assets

Walk only the authorized project paths. Gather:

- normalized project-relative path
- media type and extension
- byte size
- dimensions for raster and SVG assets
- page count for PDFs
- duration for supported video
- modified time
- a checksum or content fingerprint

Ignore generated review directories, hidden caches, build intermediates, and unrelated source material by default. Detect duplicates by content fingerprint without collapsing intentional aliases silently.

### 3. Curate the session

Do not equate every discovered file with a review asset. Select and organize according to the objective.

Useful grouping signals include:

- directory hierarchy
- filename families and suffixes
- dimensions and aspect ratios
- sequential versions
- master/adaptation relationships
- user-provided labels
- current approval state

Record inferred relationships with confidence or rationale when the inference is not explicit.

### 4. Build and validate the manifest

Create stable IDs before producing HTML. Prefer deterministic IDs derived from review-relative identity plus a content fingerprint so regenerated builds of the same round remain addressable.

Validation must reject:

- duplicate IDs
- missing source files
- paths outside authorized roots
- comparisons referencing missing assets
- groups referencing missing assets
- invalid status values
- a round that claims to replace itself
- browser paths that escape the generated review directory

Validation should warn about:

- unsupported previews
- duplicate content
- unusually large assets
- probable version families with no declared relationship
- missing dimensions or metadata

### 5. Create previews

Phase-one preview policy:

| Type | Collection preview | Focus preview |
| --- | --- | --- |
| PNG/JPEG/WebP | generated thumbnail | source-safe full image |
| SVG | raster thumbnail | sanitized SVG or raster fallback |
| GIF | representative thumbnail | browser playback |
| PDF | first-page thumbnail | rendered page sequence |
| Unsupported | generic file card | metadata and source path |

Generate thumbnails with bounded dimensions and preserve aspect ratio. Correct image orientation. Do not alter source color profiles or overwrite source files.

### 6. Assemble the application

Copy the bundled renderer into the review round and inject or load the manifest and state through a documented local mechanism.

The application must work without a remote service or CDN. If browser security prevents direct file loading, start a loopback-only static server with an ephemeral port and clearly associate its process with the review session.

### 7. Launch and frame the review

Open the generated application in the in-app browser. Tell the user:

- what is being reviewed
- what is intentionally excluded
- which decisions are needed
- whether status controls and annotations are persisted
- how to submit or indicate completion

### 8. Receive and interpret feedback

Use two complementary channels:

1. Structured application state for status, selection, and typed comments.
2. Existing browser annotations for spatial or cross-element feedback.

Map both channels to stable asset, group, comparison, or prompt IDs. Classify every item using the shared result taxonomy. Produce a short action summary before modifying work.

### 9. Continue production

Update `state.json`, then perform or delegate the requested work using the relevant project tools. Do not modify approved assets unless the feedback explicitly includes them or a global change necessarily affects them and the user confirms that scope.

### 10. Create the next round

Create a new immutable round linked to the previous one. Include changed, rejected, and globally affected assets by default. Allow the full collection when context or consistency review requires it.

## Phase-one manifest shape

The exact JSON Schema should be implemented in `references/review-contract.md`, but phase one should target this logical shape:

```json
{
  "schema_version": "1.0",
  "review": {
    "id": "campaign-round-01",
    "title": "Campaign adaptations",
    "objective": "Approve composition and hierarchy for delivery",
    "round": 1,
    "previous_review_id": null,
    "instructions": "Review each placement against the approved master."
  },
  "assets": [],
  "groups": [],
  "relationships": [],
  "comparisons": [],
  "prompts": [],
  "requested_decisions": []
}
```

Keep mutable state separate:

```json
{
  "schema_version": "1.0",
  "review_id": "campaign-round-01",
  "lifecycle": "open",
  "asset_status": {},
  "selections": [],
  "comments": [],
  "annotations": [],
  "general_notes": [],
  "submitted_at": null
}
```

## Browser application requirements

### Global frame

- review title and objective
- concise instructions
- round indicator
- progress counts
- collection/focus navigation
- clear review completion or submit action

### Collection mode

- responsive grid
- list toggle
- meaningful grouping
- sort and filter controls
- multi-select
- visible status and essential metadata
- lazy-loaded thumbnails
- readable truncation and full filename access

### Focus mode

- large preview
- fit, 1:1, zoom, and pan
- checker, black, white, and custom inspection backgrounds
- filename, path, dimensions, format, and size
- agent context and review questions
- related versions
- status and comment controls

### Comparison mode

- two assets side by side
- synchronized fit and zoom where practical
- clear left/right identity
- comparison purpose and requested decision
- direct preference or status controls

Vertical/horizontal reveal and pixel difference are stretch features, not initial acceptance requirements.

### Review summary

- approved, rejected, changes-requested, and pending counts
- selected versions
- unresolved required decisions
- comments grouped by target
- explicit submit action

## Feedback mapping strategy

Every reviewable DOM region should expose stable entity information through attributes such as:

```html
<article data-review-entity="asset" data-asset-id="social-square-v3">
```

Focus routes should retain stable IDs in the URL or application state. Visible labels should remain human-readable even if IDs are machine-oriented.

When browser annotations arrive, use target metadata, route, nearby label, and annotation text together. Never depend only on card index, screen coordinates, or a filename that can repeat.

## Local persistence

The browser application needs a reliable path for state to reach `state.json`. Evaluate these options in order:

1. A loopback-only helper server that serves the app and exposes narrow state read/write endpoints.
2. Browser-download/export of a review result file that the agent can ingest.
3. Browser local storage as a convenience cache, never as the only durable source.

The first option provides the strongest demo if the in-app browser can safely use it. Bind only to loopback, validate the review ID, restrict writes to the active review directory, and avoid a general filesystem API.

## CLI and script contracts

Target a small composable interface:

```text
inspect_assets.py <paths...> --project-root <path> --output <inventory.json>
build_review.py --manifest <draft.json> --output <round-dir>
validate_review.py <round-dir>
create_round.py --previous <round-dir> --changes <result.json> --output <round-dir>
```

Prefer Python standard-library dependencies plus narrowly justified imaging or PDF libraries already available in the Codex environment. Report missing optional dependencies with actionable fallbacks.

## Security and privacy requirements

- Accept only explicit project roots and selected source paths.
- Resolve symlinks before enforcing path boundaries.
- Never serve on a non-loopback interface by default.
- Do not load third-party scripts, fonts, analytics, or remote assets.
- Escape filenames, labels, comments, and metadata before rendering.
- Sanitize or rasterize untrusted SVG and HTML.
- Limit upload/write endpoints to expected schemas and sizes.
- Do not expose arbitrary filesystem browsing through the helper server.
- Record which files were copied into the review directory.

## Accessibility requirements

- keyboard access for navigation and status controls
- visible focus states
- semantic labels for controls and asset identity
- sufficient contrast in light and dark inspection contexts
- status communicated by text, not color alone
- reduced-motion behavior
- zoom controls that do not trap keyboard or pointer users

## Development milestones

### Milestone 1: Contract and fixtures

- define JSON schemas and lifecycle semantics
- create a small campaign fixture set
- define deterministic ID rules
- validate valid and invalid manifests

Exit criterion: a round can be represented and validated without a UI.

### Milestone 2: Static collection review

- inspect common image types
- generate thumbnails
- render grid, list, filters, groups, and status
- package a self-contained review directory

Exit criterion: a user can scan all fixture assets and record local decisions.

### Milestone 3: Focus and comparison

- implement focus viewer and inspection backgrounds
- add zoom, pan, fit, and metadata
- add side-by-side comparison
- add related versions and review questions

Exit criterion: the campaign master can be meaningfully compared with each adaptation.

### Milestone 4: Persistence and browser loop

- implement the narrow local state bridge or export fallback
- open the application in the in-app browser
- map browser annotations to stable IDs
- create the action summary

Exit criterion: submitted review results return to the agent without manual filename transcription.

### Milestone 5: Review rounds

- update state from interpreted feedback
- create a linked second round
- show changed-only and full-context modes
- preserve prior results

Exit criterion: one end-to-end production revision loop succeeds.

### Milestone 6: Hardening and packaging

- add unsupported-file behavior
- test large and malformed inputs
- verify accessibility basics
- add deterministic tests and visual smoke checks
- validate skill metadata and installation

Exit criterion: the skill installs from GitHub and completes the demo reliably in a clean project.

## Test strategy

### Contract tests

- schema validation
- stable ID generation
- path-boundary enforcement
- relationship integrity
- review lifecycle transitions
- schema-version rejection and migration behavior

### Generator tests

- inventory of each supported format
- duplicate and unsupported inputs
- thumbnail orientation and dimensions
- deterministic application output
- filenames containing spaces, Unicode, and HTML-sensitive characters

### UI tests

- collection loading and grouping
- filters and status changes
- focus navigation
- zoom and background controls
- comparison selection
- reload persistence
- submit summary

### End-to-end tests

- create a campaign review from folders
- approve several assets and reject one
- add a local and a global annotation
- ingest the result
- create the next round
- verify history and unchanged approvals

### Forward tests

Ask fresh Codex agents to use the installed skill on raw fixture projects without giving them the intended curation or expected answer. Evaluate asset selection, grouping, questions, feedback mapping, and next-round behavior.

## Phase-one acceptance criteria

- The skill triggers from common natural-language review requests.
- It builds a review from one or more folders or explicit files.
- It presents supported assets in a stable collection view.
- It supports focused inspection and side-by-side comparison.
- It records explicit status, selections, and comments.
- Browser annotations can be associated with stable entity IDs.
- The agent summarizes feedback correctly before acting.
- A second round retains traceable history and prior decisions.
- The app runs locally without external services or remote dependencies.
- The skill passes structural validation and its scripts pass automated tests.

## Non-goals

- native application implementation
- public or shared review links
- real-time collaboration
- editing source pixels, vectors, layouts, or timelines in the viewer
- broad digital asset management
- arbitrary plugin integrations
- perfect visual diffing
- exhaustive creative-format support

## Phase-one demo script

1. Start with a project containing an approved master and six adaptations.
2. Ask Codex to prepare the latest campaign assets for review.
3. Show the generated collection, groups, metadata, and explicit review objective.
4. Open one adaptation in focus view and inspect it on multiple backgrounds.
5. Compare the master with the adaptation.
6. Approve three assets, reject one, annotate a crop issue, and request a global typography change.
7. Submit the review.
8. Show Codex's structured action summary.
9. Apply or simulate the requested production edits.
10. Open round two containing the rejected and affected assets with round-one history intact.

The demo succeeds when this feels like one continuous agent task rather than a handoff to an unrelated gallery application.
