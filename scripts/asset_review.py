#!/usr/bin/env python3
"""Shared implementation for the Asset Review skill."""

from __future__ import annotations

import hashlib
import html
import json
import mimetypes
import os
import re
import shutil
import struct
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
SUPPORTED_IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}
SUPPORTED_VIDEO_TYPES = {".mp4": "video/mp4", ".webm": "video/webm"}
IGNORED_DIRECTORIES = {".git", ".codex", "node_modules", "dist", "build", "__pycache__"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slugify(value: str, fallback: str = "review") -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:64] or fallback


def sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def safe_relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def discover_files(inputs: Iterable[str], project_root: Path) -> list[Path]:
    root = project_root.resolve()
    discovered: list[Path] = []
    seen: set[Path] = set()

    for raw in inputs:
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        if not path_is_within(candidate, root):
            raise ValueError(f"Input escapes project root: {candidate}")
        if not candidate.exists():
            raise FileNotFoundError(candidate)

        if candidate.is_file():
            candidates = [candidate]
        else:
            candidates = []
            for current_root, directories, filenames in os.walk(candidate):
                directories[:] = [name for name in directories if name not in IGNORED_DIRECTORIES]
                for filename in filenames:
                    candidates.append(Path(current_root) / filename)

        for path in sorted(candidates):
            resolved = path.resolve()
            if resolved in seen or not resolved.is_file():
                continue
            seen.add(resolved)
            discovered.append(resolved)

    return sorted(discovered, key=lambda path: safe_relative_path(path, root).lower())


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        return struct.unpack(">II", header[16:24])
    return None


def _gif_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(10)
    if header[:6] in {b"GIF87a", b"GIF89a"} and len(header) >= 10:
        return struct.unpack("<HH", header[6:10])
    return None


def _jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        if handle.read(2) != b"\xff\xd8":
            return None
        while True:
            marker_start = handle.read(1)
            if not marker_start:
                return None
            if marker_start != b"\xff":
                continue
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if marker in {b"\xd8", b"\xd9"}:
                continue
            length_bytes = handle.read(2)
            if len(length_bytes) != 2:
                return None
            segment_length = struct.unpack(">H", length_bytes)[0]
            if marker and marker[0] in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                payload = handle.read(5)
                if len(payload) != 5:
                    return None
                height, width = struct.unpack(">HH", payload[1:5])
                return width, height
            handle.seek(max(0, segment_length - 2), 1)


def _svg_dimensions(path: Path) -> tuple[int, int] | None:
    text = path.read_text(encoding="utf-8", errors="ignore")[:8192]
    width_match = re.search(r"\bwidth=[\"']([0-9.]+)", text)
    height_match = re.search(r"\bheight=[\"']([0-9.]+)", text)
    if width_match and height_match:
        return int(float(width_match.group(1))), int(float(height_match.group(1)))
    viewbox_match = re.search(r"\bviewBox=[\"'][^\"']*?([0-9.]+)[ ,]+([0-9.]+)[\"']", text)
    if viewbox_match:
        return int(float(viewbox_match.group(1))), int(float(viewbox_match.group(2)))
    return None


def image_dimensions(path: Path) -> tuple[int, int] | None:
    extension = path.suffix.lower()
    parsers = {
        ".png": _png_dimensions,
        ".jpg": _jpeg_dimensions,
        ".jpeg": _jpeg_dimensions,
        ".gif": _gif_dimensions,
        ".svg": _svg_dimensions,
    }
    parser = parsers.get(extension)
    if parser:
        try:
            result = parser(path)
            if result:
                return result
        except (OSError, ValueError, struct.error):
            pass

    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.size
    except (ImportError, OSError):
        return None


def video_duration(path: Path) -> float | None:
    executable = shutil.which("ffprobe")
    if not executable:
        return None
    try:
        completed = subprocess.run(
            [
                executable,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return round(float(completed.stdout.strip()), 3)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def media_type_for(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in SUPPORTED_IMAGE_TYPES:
        return SUPPORTED_IMAGE_TYPES[extension]
    if extension in SUPPORTED_VIDEO_TYPES:
        return SUPPORTED_VIDEO_TYPES[extension]
    if extension == ".pdf":
        return "application/pdf"
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def inspect_file(path: Path, project_root: Path) -> dict[str, Any]:
    resolved = path.resolve()
    root = project_root.resolve()
    if not path_is_within(resolved, root):
        raise ValueError(f"Asset escapes project root: {resolved}")

    fingerprint = sha256(resolved)
    relative = safe_relative_path(resolved, root)
    media_type = media_type_for(resolved)
    dimensions = image_dimensions(resolved) if media_type.startswith("image/") else None
    stat = resolved.stat()
    extension = resolved.suffix.lower()
    preview_kind = "image" if media_type.startswith("image/") else "video" if media_type.startswith("video/") else "pdf" if extension == ".pdf" else "file"
    asset_id = f"{slugify(resolved.stem, 'asset')}-{fingerprint[:8]}"
    item: dict[str, Any] = {
        "id": asset_id,
        "label": resolved.stem.replace("_", " ").replace("-", " ").strip().title(),
        "filename": resolved.name,
        "source_path": relative,
        "media_type": media_type,
        "preview_kind": preview_kind,
        "file_size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "content_fingerprint": fingerprint,
        "tags": [],
    }
    if dimensions:
        item["width"], item["height"] = dimensions
        item["aspect_ratio"] = round(dimensions[0] / dimensions[1], 4) if dimensions[1] else None
    if media_type.startswith("video/"):
        duration = video_duration(resolved)
        if duration is not None:
            item["duration"] = duration
    return item


def inspect_inputs(inputs: Iterable[str], project_root: Path) -> list[dict[str, Any]]:
    return [inspect_file(path, project_root) for path in discover_files(inputs, project_root)]


def deduplicate_ids(assets: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    for asset in assets:
        base = asset["id"]
        counts[base] = counts.get(base, 0) + 1
        if counts[base] > 1:
            asset["id"] = f"{base}-{counts[base]}"


def default_manifest(
    assets: list[dict[str, Any]],
    title: str,
    objective: str,
    review_id: str | None = None,
    round_number: int = 1,
    previous_review_id: str | None = None,
    instructions: str | None = None,
) -> dict[str, Any]:
    review_id = review_id or f"{slugify(title)}-round-{round_number:02d}"
    group_ids: dict[str, list[str]] = {}
    for asset in assets:
        group_name = asset.get("group_id") or Path(asset["source_path"]).parent.name or "Assets"
        group_ids.setdefault(group_name, []).append(asset["id"])
        asset["group_id"] = slugify(group_name, "assets")

    groups = [
        {
            "id": slugify(name, "assets"),
            "label": name.replace("_", " ").replace("-", " ").title(),
            "asset_ids": ids,
        }
        for name, ids in group_ids.items()
    ]
    if not groups and assets:
        groups = [{"id": "assets", "label": "Assets", "asset_ids": [asset["id"] for asset in assets]}]
        for asset in assets:
            asset["group_id"] = "assets"

    return {
        "schema_version": SCHEMA_VERSION,
        "review": {
            "id": review_id,
            "title": title,
            "objective": objective,
            "instructions": instructions or "Inspect the selected assets and annotate any requested changes in Codex.",
            "round": round_number,
            "previous_review_id": previous_review_id,
            "created_at": utc_now(),
        },
        "assets": assets,
        "groups": groups,
        "relationships": [],
        "comparisons": [],
    }


def validate_manifest(manifest: dict[str, Any], project_root: Path | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Unsupported schema_version: {manifest.get('schema_version')!r}")
    review = manifest.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
        review = {}
    for field in ("id", "title", "objective", "round"):
        if not review.get(field):
            errors.append(f"review.{field} is required")
    if review.get("previous_review_id") == review.get("id") and review.get("id"):
        errors.append("review cannot reference itself as previous_review_id")

    assets = manifest.get("assets")
    if not isinstance(assets, list):
        errors.append("assets must be an array")
        assets = []
    asset_ids: set[str] = set()
    fingerprints: dict[str, str] = {}
    for index, asset in enumerate(assets):
        prefix = f"assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{prefix} must be an object")
            continue
        asset_id = asset.get("id")
        if not asset_id:
            errors.append(f"{prefix}.id is required")
        elif asset_id in asset_ids:
            errors.append(f"duplicate asset id: {asset_id}")
        else:
            asset_ids.add(asset_id)
        source_path = asset.get("source_path")
        if not source_path:
            errors.append(f"{prefix}.source_path is required")
        elif project_root:
            source = (project_root / source_path).resolve()
            if not path_is_within(source, project_root):
                errors.append(f"{prefix}.source_path escapes project root")
            elif not source.is_file():
                errors.append(f"{prefix}.source_path does not exist: {source_path}")
        fingerprint = asset.get("content_fingerprint")
        if fingerprint:
            if fingerprint in fingerprints:
                warnings.append(f"duplicate content: {asset_id} and {fingerprints[fingerprint]}")
            else:
                fingerprints[fingerprint] = str(asset_id)
        if asset.get("preview_kind") == "file":
            warnings.append(f"unsupported preview: {asset_id}")

    for group in manifest.get("groups", []):
        if not isinstance(group, dict) or not group.get("id"):
            errors.append("every group requires an id")
            continue
        missing = set(group.get("asset_ids", [])) - asset_ids
        if missing:
            errors.append(f"group {group['id']} references missing assets: {sorted(missing)}")

    for comparison in manifest.get("comparisons", []):
        if not isinstance(comparison, dict) or not comparison.get("id"):
            errors.append("every comparison requires an id")
            continue
        referenced = {comparison.get("left_asset_id"), comparison.get("right_asset_id")}
        missing = {item for item in referenced if item and item not in asset_ids}
        if missing:
            errors.append(f"comparison {comparison['id']} references missing assets: {sorted(missing)}")

    return errors, warnings


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def copy_or_render_asset(asset: dict[str, Any], project_root: Path, review_dir: Path) -> list[str]:
    warnings: list[str] = []
    source = (project_root / asset["source_path"]).resolve()
    if not path_is_within(source, project_root):
        raise ValueError(f"Asset escapes project root: {asset['source_path']}")
    extension = source.suffix.lower()
    destination_name = f"{asset['id']}{extension}"
    destination = review_dir / "assets" / destination_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    asset["preview_path"] = f"assets/{destination_name}"

    thumbnail = review_dir / "thumbnails" / f"{asset['id']}.jpg"
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    if asset.get("preview_kind") == "image" and extension != ".svg":
        try:
            from PIL import Image, ImageOps

            with Image.open(source) as image:
                image = ImageOps.exif_transpose(image)
                if getattr(image, "is_animated", False):
                    image.seek(0)
                image = image.convert("RGB")
                image.thumbnail((720, 720))
                image.save(thumbnail, "JPEG", quality=84, optimize=True)
            asset["thumbnail_path"] = f"thumbnails/{asset['id']}.jpg"
        except (ImportError, OSError, ValueError) as error:
            warnings.append(f"thumbnail fallback for {asset['id']}: {error}")

    if asset.get("preview_kind") == "pdf":
        executable = shutil.which("pdftoppm")
        if executable:
            pages_dir = review_dir / "pages" / asset["id"]
            pages_dir.mkdir(parents=True, exist_ok=True)
            prefix = pages_dir / "page"
            try:
                subprocess.run(
                    [executable, "-jpeg", "-r", "110", str(source), str(prefix)],
                    check=True,
                    capture_output=True,
                    timeout=60,
                )
                pages = sorted(pages_dir.glob("page-*.jpg"))
                asset["page_paths"] = [path.relative_to(review_dir).as_posix() for path in pages]
                if pages:
                    asset["thumbnail_path"] = pages[0].relative_to(review_dir).as_posix()
                    asset["page_count"] = len(pages)
            except (OSError, subprocess.SubprocessError) as error:
                warnings.append(f"PDF rendering failed for {asset['id']}: {error}")
        else:
            warnings.append(f"PDF rendering unavailable for {asset['id']}: pdftoppm not found")
    return warnings


def _escape(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _media_html(asset: dict[str, Any], prefix: str = "") -> str:
    source = _escape(prefix + asset.get("preview_path", ""))
    label = _escape(asset.get("label") or asset.get("filename") or asset.get("id"))
    kind = asset.get("preview_kind")
    if kind == "image" and source:
        return f'<img src="{source}" alt="{label}">'
    if kind == "video" and source:
        return f'<video src="{source}" aria-label="{label}" controls preload="metadata"></video>'
    if kind == "pdf" and asset.get("page_paths"):
        page = _escape(prefix + asset["page_paths"][0])
        return f'<img src="{page}" alt="First page of {label}">'
    extension = _escape(Path(asset.get("filename", "file")).suffix.lstrip(".").upper() or "FILE")
    return f'<div class="file-preview" aria-label="No visual preview for {label}">{extension}</div>'


def _asset_details(asset: dict[str, Any]) -> str:
    details = [
        ("Filename", asset.get("filename")),
        ("Source", asset.get("source_path")),
        ("Type", asset.get("media_type")),
        ("Dimensions", f"{asset['width']} × {asset['height']}" if asset.get("width") and asset.get("height") else None),
        ("File size", f"{asset.get('file_size', 0):,} bytes"),
        ("Asset ID", asset.get("id")),
    ]
    return "".join(
        f"<dt>{_escape(term)}</dt><dd>{_escape(value)}</dd>" for term, value in details if value is not None
    )


def _document(title: str, body: str, prefix: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>{_escape(title)} · Asset Review</title>
  <link rel="stylesheet" href="{_escape(prefix)}static/styles.css">
  <script src="{_escape(prefix)}static/enhancements.js" defer></script>
</head>
<body>
{body}
</body>
</html>
"""


def _asset_card(asset: dict[str, Any]) -> str:
    asset_id = _escape(asset["id"])
    label = _escape(asset.get("label") or asset.get("filename"))
    filename = _escape(asset.get("filename"))
    dimensions = (
        f"{asset['width']} × {asset['height']}" if asset.get("width") and asset.get("height") else "Dimensions unavailable"
    )
    return f"""
<figure class="asset-card" id="asset-{asset_id}" data-asset-id="{asset_id}" aria-labelledby="asset-title-{asset_id}">
  <a class="asset-preview" href="asset/{asset_id}.html" aria-label="Open {label}">
    {_media_html(asset)}
  </a>
  <figcaption>
    <h3 id="asset-title-{asset_id}"><a href="asset/{asset_id}.html">{label}</a></h3>
    <p class="filename">{filename}</p>
    <p class="asset-meta"><span>{_escape(dimensions)}</span><span>{asset.get('file_size', 0):,} bytes</span></p>
  </figcaption>
</figure>"""


def _group_sections(manifest: dict[str, Any], view_class: str) -> str:
    assets_by_id = {asset["id"]: asset for asset in manifest.get("assets", [])}
    sections: list[str] = []
    for group in manifest.get("groups", []):
        cards = "".join(_asset_card(assets_by_id[asset_id]) for asset_id in group.get("asset_ids", []) if asset_id in assets_by_id)
        if not cards:
            continue
        sections.append(
            f"""<section class="asset-group" id="group-{_escape(group['id'])}" aria-labelledby="group-title-{_escape(group['id'])}">
  <header class="group-heading"><h2 id="group-title-{_escape(group['id'])}">{_escape(group.get('label', group['id']))}</h2><span>{len(group.get('asset_ids', []))} assets</span></header>
  <div class="asset-collection {view_class}">{cards}</div>
</section>"""
        )
    if not sections and manifest.get("assets"):
        cards = "".join(_asset_card(asset) for asset in manifest["assets"])
        sections.append(f'<section class="asset-group"><div class="asset-collection {view_class}">{cards}</div></section>')
    return "".join(sections)


def _review_header(manifest: dict[str, Any], active_view: str) -> str:
    review = manifest["review"]
    group_links = "".join(
        f'<a href="#group-{_escape(group["id"])}">{_escape(group.get("label", group["id"]))}</a>'
        for group in manifest.get("groups", [])
    )
    grid_current = ' aria-current="page"' if active_view == "grid" else ""
    list_current = ' aria-current="page"' if active_view == "list" else ""
    return f"""<header class="review-header">
  <div class="eyebrow"><span>Asset Review</span><span>Round {_escape(review.get('round', 1))}</span></div>
  <h1>{_escape(review.get('title'))}</h1>
  <p class="objective">{_escape(review.get('objective'))}</p>
  <p class="instructions">{_escape(review.get('instructions'))}</p>
  <nav class="review-nav" aria-label="Review navigation">
    <a href="index.html"{grid_current}>Grid</a>
    <a href="list.html"{list_current}>List</a>
    {group_links}
  </nav>
  <div class="asset-tools">
    <label for="asset-filter">Filter assets</label>
    <input id="asset-filter" type="search" placeholder="Search names, filenames, or metadata" autocomplete="off">
    <span id="filter-status" aria-live="polite"></span>
  </div>
</header>"""


def _comparison_links(manifest: dict[str, Any]) -> str:
    comparisons = manifest.get("comparisons", [])
    if not comparisons:
        return ""
    links = "".join(
        f'<li><a href="comparison/{_escape(item["id"])}.html">{_escape(item.get("label") or item.get("purpose") or item["id"])}</a></li>'
        for item in comparisons
    )
    return f'<aside class="comparison-index" aria-labelledby="comparison-title"><h2 id="comparison-title">Prepared comparisons</h2><ul>{links}</ul></aside>'


def _focus_page(asset: dict[str, Any], manifest: dict[str, Any]) -> str:
    label = _escape(asset.get("label") or asset.get("filename"))
    context = asset.get("context") or asset.get("agent_context")
    context_html = f'<section class="context"><h2>Context</h2><p>{_escape(context)}</p></section>' if context else ""
    questions = asset.get("review_questions", [])
    questions_html = (
        '<section class="questions"><h2>Review questions</h2><ul>'
        + "".join(f"<li>{_escape(question)}</li>" for question in questions)
        + "</ul></section>"
        if questions
        else ""
    )
    body = f"""<main class="focus-page">
  <nav class="back-nav"><a href="../index.html">← Back to grid</a></nav>
  <header class="page-heading"><p>Focused asset</p><h1>{label}</h1></header>
  <nav class="inspection-toolbar" aria-label="Inspection background">
    <span>Background</span>
    <button type="button" data-background="checker" aria-pressed="true">Checker</button>
    <button type="button" data-background="black" aria-pressed="false">Black</button>
    <button type="button" data-background="white" aria-pressed="false">White</button>
  </nav>
  <figure class="focus-asset" id="asset-{_escape(asset['id'])}" data-asset-id="{_escape(asset['id'])}">
    <div class="focus-stage">{_media_html(asset, '../')}</div>
    <figcaption>
      <dl class="metadata">{_asset_details(asset)}</dl>
      {context_html}
      {questions_html}
    </figcaption>
  </figure>
</main>"""
    return _document(label, body, "../")


def _comparison_page(comparison: dict[str, Any], assets_by_id: dict[str, dict[str, Any]]) -> str:
    left = assets_by_id[comparison["left_asset_id"]]
    right = assets_by_id[comparison["right_asset_id"]]
    title = comparison.get("label") or comparison.get("purpose") or comparison["id"]

    def side(asset: dict[str, Any], position: str) -> str:
        label = _escape(asset.get("label") or asset.get("filename"))
        return f"""<figure class="comparison-asset" id="asset-{_escape(asset['id'])}" data-asset-id="{_escape(asset['id'])}">
  <figcaption><span>{position}</span><h2>{label}</h2><p>{_escape(asset.get('filename'))}</p></figcaption>
  <div class="comparison-stage">{_media_html(asset, '../')}</div>
</figure>"""

    purpose = f'<p class="comparison-purpose">{_escape(comparison.get("purpose"))}</p>' if comparison.get("purpose") else ""
    body = f"""<main class="comparison-page">
  <nav class="back-nav"><a href="../index.html">← Back to grid</a></nav>
  <header class="page-heading"><p>Comparison</p><h1>{_escape(title)}</h1>{purpose}</header>
  <nav class="inspection-toolbar" aria-label="Inspection background">
    <span>Background</span>
    <button type="button" data-background="checker" aria-pressed="true">Checker</button>
    <button type="button" data-background="black" aria-pressed="false">Black</button>
    <button type="button" data-background="white" aria-pressed="false">White</button>
  </nav>
  <section class="comparison-grid" aria-label="{_escape(title)}">{side(left, 'Left')}{side(right, 'Right')}</section>
</main>"""
    return _document(str(title), body, "../")


def render_static_site(manifest: dict[str, Any], output_dir: Path) -> None:
    index_body = '<main class="review-page">' + _review_header(manifest, "grid") + _comparison_links(manifest) + _group_sections(manifest, "grid") + "</main>"
    list_body = '<main class="review-page">' + _review_header(manifest, "list") + _comparison_links(manifest) + _group_sections(manifest, "list") + "</main>"
    (output_dir / "index.html").write_text(_document(manifest["review"]["title"], index_body), encoding="utf-8")
    (output_dir / "list.html").write_text(_document(manifest["review"]["title"], list_body), encoding="utf-8")

    for asset in manifest.get("assets", []):
        (output_dir / "asset" / f"{asset['id']}.html").write_text(_focus_page(asset, manifest), encoding="utf-8")

    assets_by_id = {asset["id"]: asset for asset in manifest.get("assets", [])}
    for comparison in manifest.get("comparisons", []):
        (output_dir / "comparison" / f"{comparison['id']}.html").write_text(
            _comparison_page(comparison, assets_by_id), encoding="utf-8"
        )


def assemble_review(
    manifest: dict[str, Any],
    project_root: Path,
    output_dir: Path,
    template_dir: Path,
) -> tuple[list[str], list[str]]:
    errors, warnings = validate_manifest(manifest, project_root)
    if errors:
        return errors, warnings

    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("assets", "thumbnails", "pages", "static", "asset", "comparison"):
        generated_dir = output_dir / name
        if generated_dir.exists():
            shutil.rmtree(generated_dir)
    for name in ("index.html", "list.html", "review.json", "diagnostics.json"):
        generated_file = output_dir / name
        if generated_file.exists():
            generated_file.unlink()
    for name in ("assets", "thumbnails", "pages", "static", "asset", "comparison"):
        (output_dir / name).mkdir(exist_ok=True)

    for asset in manifest["assets"]:
        warnings.extend(copy_or_render_asset(asset, project_root, output_dir))

    shutil.copy2(template_dir / "styles.css", output_dir / "static" / "styles.css")
    shutil.copy2(template_dir / "enhancements.js", output_dir / "static" / "enhancements.js")
    render_static_site(manifest, output_dir)

    atomic_write_json(output_dir / "review.json", manifest)
    atomic_write_json(
        output_dir / "diagnostics.json",
        {
            "schema_version": SCHEMA_VERSION,
            "generated_at": utc_now(),
            "warnings": warnings,
            "copied_assets": [asset.get("preview_path") for asset in manifest["assets"]],
        },
    )
    return [], warnings
