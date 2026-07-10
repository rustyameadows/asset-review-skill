# Phase One: Static Asset Review Skill

## Objective

Build a distributable Codex skill that helps an agent deliberately select project assets and present them as a plain, static, annotation-friendly HTML site inside the in-app browser.

Codex/ChatGPT owns annotation, feedback capture, and the conversation loop. The generated site owns only visual presentation and navigation.

## Hard architectural boundary

Phase one is not a review application.

It must not contain:

- an application server or daemon
- an API
- mutable review state
- comments or notes
- approval or rejection controls
- submission controls
- annotation listeners or overlays
- annotation persistence
- a client-side framework
- client-side asset rendering

The complete asset collection must exist as ordinary semantic HTML when `index.html` opens. JavaScript may progressively enhance that HTML, but the review must remain usable and annotatable with JavaScript disabled.

## User and agent flow

1. The user asks the agent to prepare specific work for visual review.
2. The agent decides which files are relevant.
3. The agent assigns useful labels, groups, context, and comparisons.
4. The agent runs the generator or writes from the supplied static template.
5. The output contains HTML, CSS, optional enhancement JavaScript, and safe local preview copies.
6. Codex opens `index.html` directly when supported, or serves the folder through a tiny loopback-only static file server.
7. The user annotates the static page with Codex/ChatGPT's built-in annotation system.
8. The agent receives those annotations through the normal task context.
9. The agent edits the source assets.
10. The agent regenerates the same static output and refreshes the browser page.

No information passes from the page back to the agent. The page is only a visual surface.

## Repository structure

```text
asset-review/
  SKILL.md
  agents/
    openai.yaml
  assets/
    review-app/
      styles.css
      enhancements.js
  references/
    review-contract.md
    feedback-mapping.md
  scripts/
    asset_review.py
    inspect_assets.py
    build_review.py
    validate_review.py
    serve_review.py
    create_round.py
    build_demo.py
  examples/
    demo-assets/
  tests/
    test_asset_review.py
  script/
    verify_phase1
```

## Generated output

```text
<project>/.codex/reviews/<review-id>/
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

There is no `state.json` or application backend. A read-only static file server is allowed only as transport when the browser cannot open a local file directly.

## Static HTML requirements

### Overview pages

`index.html` and `list.html` must contain every selected asset directly in their source HTML.

Each item must be a distinct semantic figure:

```html
<figure
  class="asset-card"
  id="asset-social-square"
  data-asset-id="social-square"
  aria-labelledby="asset-title-social-square"
>
  <a class="asset-preview" href="asset/social-square.html">
    <img src="assets/social-square.png" alt="Social square">
  </a>
  <figcaption>
    <h3 id="asset-title-social-square">Social square</h3>
    <p>social-square.png</p>
  </figcaption>
</figure>
```

Do not create cards with JavaScript. Do not place a canvas, full-card event-capture layer, or invisible overlay over them.

### Group sections

Render groups as real `<section>` elements with headings and anchored IDs. This lets the browser and annotation system understand the page hierarchy.

### Focus pages

Generate one static page per asset. Use one large `<figure>` containing the media, metadata, context, and review questions. The URL and figure ID must identify the asset without application state.

### Comparison pages

Generate one static page per prepared comparison. Render the left and right assets as two independent `<figure>` elements with visible labels and filenames.

### Navigation

Use ordinary links for:

- grid/list views
- group anchors
- opening an asset
- opening a prepared comparison
- returning to the overview

Navigation must work without JavaScript.

## Optional progressive enhancement

The bundled enhancement script may:

- switch inspection backgrounds
- add keyboard conveniences
- improve nonessential focus or display behavior

It must not:

- fetch the manifest
- generate or replace asset elements
- listen for annotation mode
- create an annotation layer
- store comments, decisions, or review state
- call a local or remote API
- prevent the static links from working

Refreshing the page may reset all enhancement state.

## Asset selection

The skill should not automatically review everything it discovers.

The agent must determine:

- the review objective
- which files answer that objective
- which source files should be excluded
- how assets should be grouped
- which labels are meaningful
- which comparisons will help the user
- what context or questions should accompany an asset

The generator is a presentation helper, not the curator.

## Manifest role

`review.json` is an optional build input and a portable presentation record. It is not runtime application data.

It describes:

- review title, objective, instructions, and round label
- asset source paths and stable IDs
- labels and metadata
- groups
- relationships
- prepared comparisons
- optional context and review questions

The generated HTML embeds this information directly. The browser does not fetch `review.json` at runtime.

## Generator behavior

`build_review.py` should:

1. accept explicit files or folders selected by the agent, or accept a curated manifest
2. inspect supported media metadata
3. assign deterministic IDs when the agent did not provide them
4. copy or render safe local previews
5. write static grid and list pages
6. write static focus and comparison pages
7. copy the shared CSS and optional enhancement script
8. write diagnostics
9. validate links and referenced assets

The generator should remain small enough that an agent can instead write or adjust the HTML directly when a project needs a custom presentation.

## Supported media

Initial support:

- PNG
- JPEG
- WebP
- GIF
- SVG
- PDF rendered to static page images when a renderer is available
- MP4/WebM through native `<video>` controls

Unsupported files appear as static file cards with metadata instead of being omitted.

## Refresh model

The normal iteration loop reuses one output folder:

```text
edit sources -> rebuild static output -> refresh browser
```

A new round folder is optional. Use it only when the earlier presentation should remain available for historical comparison.

The page never polls, hot reloads, or watches files. The agent explicitly rebuilds and refreshes. If a static file server is running, no-cache headers ensure the refresh reads the rebuilt files.

## Security and privacy

- Keep output local to the project.
- Copy only deliberately selected files.
- Resolve symlinks before enforcing project-root boundaries.
- Escape labels, filenames, metadata, and context in generated HTML.
- Use relative URLs inside the static output.
- Load no third-party scripts, fonts, analytics, or remote assets.
- Do not publish or upload a review without explicit authorization.
- Prefer rendered derivatives for active or unsafe formats.

## Accessibility

- use semantic headings, sections, figures, captions, links, and definition lists
- provide useful image alt text
- provide visible keyboard focus
- maintain readable contrast
- keep navigation usable without a pointer
- keep the full site usable without JavaScript
- avoid communicating meaning only through color or layout

## Milestones

### Milestone 1: Static contract and curation workflow

- define the presentation-only manifest
- implement explicit asset selection
- inspect file metadata and assign stable IDs
- validate project-root boundaries and relationships

Exit criterion: the agent can represent a deliberate asset set without feedback or state fields.

### Milestone 2: Server-generated overview

- generate actual figure cards into `index.html`
- generate grouped sections and list view
- copy safe local previews
- ensure no client-side rendering is required

Exit criterion: every overview asset is present and identifiable in initial HTML.

### Milestone 3: Static focus and comparison pages

- generate one focus page per asset
- generate one page per prepared comparison
- add ordinary navigation links
- expose metadata, context, and review questions

Exit criterion: every asset and comparison has a stable URL and semantic figure.

### Milestone 4: Optional UI niceties

- add inspection background switching
- verify no-JavaScript fallback

Exit criterion: enhancement failure cannot hide or remove review content.

### Milestone 5: Codex annotation verification

- open the static `file://` page in the in-app browser
- confirm each grid figure can be targeted
- confirm each focus figure can be targeted
- confirm left and right comparison figures can be targeted independently
- confirm the page does not change when annotation mode activates

Exit criterion: Codex owns annotation completely and the page remains visually unchanged.

## Automated tests

- supported file discovery and metadata
- deterministic asset IDs
- path-boundary enforcement
- manifest validation
- static grid and list generation
- one direct `<figure>` per selected asset
- focus page generation
- comparison page generation
- absence of `state.json`
- absence of submit, approval, note, or API UI
- static link targets exist
- enhancement JavaScript syntax
- usable HTML content before JavaScript runs

## Acceptance criteria

- The agent deliberately selects the asset set.
- A single command can generate the static review folder.
- The agent can open `index.html` directly or through the bundled read-only loopback static server.
- Every overview item is a static labeled figure.
- Every asset has a static focus page.
- Every prepared comparison has a static comparison page.
- The page contains no review state, notes, approvals, or submit flow.
- The page contains no annotation-specific behavior.
- Codex annotation mode can target individual asset figures.
- Rebuilding and refreshing shows the agent's edits.
- The page remains usable when JavaScript is disabled.

## Demo

1. Build the bundled Solar Club example.
2. Open `.codex/reviews/solar-club-round-01/index.html` directly.
3. Annotate two different grid figures through Codex.
4. Open a focused asset and annotate its image or caption.
5. Open a prepared master/adaptation comparison and annotate either side.
6. Have the agent edit a source asset.
7. Rebuild the same static folder.
8. Refresh the browser and verify the new source appears.

The demo succeeds when the generated site behaves like a clean document that Codex can annotate, not like an application attempting to manage the review itself.
