from __future__ import annotations

import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from asset_review import (  # noqa: E402
    assemble_review,
    default_manifest,
    image_dimensions,
    inspect_inputs,
    load_json,
    slugify,
    validate_manifest,
)
from serve_review import StaticReviewHandler  # noqa: E402


SVG = """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"640\" height=\"360\" viewBox=\"0 0 640 360\"><rect width=\"640\" height=\"360\" fill=\"#835cff\"/></svg>"""


class AssetReviewTests(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(slugify("Campaign / Round 01"), "campaign-round-01")
        self.assertEqual(slugify("***"), "review")

    def test_svg_inventory_and_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            asset = root / "My Asset.svg"
            asset.write_text(SVG, encoding="utf-8")
            inventory = inspect_inputs(["My Asset.svg"], root)
            self.assertEqual(len(inventory), 1)
            self.assertEqual(image_dimensions(asset), (640, 360))
            self.assertEqual(inventory[0]["source_path"], "My Asset.svg")
            self.assertEqual(inventory[0]["preview_kind"], "image")

    def test_manifest_rejects_bad_relationships_and_duplicate_ids(self) -> None:
        manifest = default_manifest([], "Test", "Test objective", review_id="test-round-01")
        manifest["assets"] = [
            {"id": "same", "source_path": "a.svg", "status": "pending"},
            {"id": "same", "source_path": "b.svg", "status": "pending"},
        ]
        manifest["comparisons"] = [{"id": "bad", "left_asset_id": "same", "right_asset_id": "missing"}]
        errors, _ = validate_manifest(manifest)
        self.assertTrue(any("duplicate asset id" in error for error in errors))
        self.assertTrue(any("missing assets" in error for error in errors))

    def test_assemble_and_validate_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "asset.svg").write_text(SVG, encoding="utf-8")
            assets = inspect_inputs(["asset.svg"], root)
            manifest = default_manifest(assets, "Test", "Review it", review_id="test-round-01")
            output = root / ".codex" / "reviews" / "test-round-01"
            errors, _ = assemble_review(manifest, root, output, ROOT / "assets" / "review-app")
            self.assertEqual(errors, [])
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "list.html").is_file())
            self.assertTrue((output / "assets" / f"{assets[0]['id']}.svg").is_file())
            self.assertTrue((output / "asset" / f"{assets[0]['id']}.html").is_file())
            built_manifest = load_json(output / "review.json")
            self.assertEqual(built_manifest["review"]["id"], "test-round-01")
            self.assertFalse((output / "state.json").exists())
            index = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'<figure class="asset-card" id="asset-{assets[0]["id"]}"', index)
            self.assertIn("<figcaption>", index)
            self.assertNotIn("Submit review", index)
            self.assertNotIn("asset_status", index)
            self.assertNotIn('class="instructions"', index)
            self.assertNotIn('class="asset-tools"', index)
            self.assertNotIn('class="comparison-index"', index)

    def test_static_comparison_page(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "left.svg").write_text(SVG, encoding="utf-8")
            (root / "right.svg").write_text(SVG.replace("#835cff", "#ff835c"), encoding="utf-8")
            assets = inspect_inputs(["left.svg", "right.svg"], root)
            manifest = default_manifest(assets, "Test", "Compare it", review_id="comparison-round-01")
            manifest["comparisons"] = [{
                "id": "left-vs-right",
                "label": "Left / Right",
                "left_asset_id": assets[0]["id"],
                "right_asset_id": assets[1]["id"],
            }]
            output = root / "review"
            errors, _ = assemble_review(manifest, root, output, ROOT / "assets" / "review-app")
            self.assertEqual(errors, [])
            page = output / "comparison" / "left-vs-right.html"
            self.assertTrue(page.is_file())
            html = page.read_text(encoding="utf-8")
            self.assertEqual(html.count('class="comparison-asset"'), 2)
            self.assertNotIn("fetch(", html)

    def test_static_server_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<!doctype html><title>Static</title>", encoding="utf-8")
            handler = lambda *args, **kwargs: StaticReviewHandler(*args, directory=str(root), **kwargs)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            url = f"http://127.0.0.1:{server.server_port}/"
            try:
                with urllib.request.urlopen(url) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.headers["Cache-Control"], "no-store")
                request = urllib.request.Request(url, data=b"{}", method="POST")
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(request)
                self.assertEqual(raised.exception.code, 405)
                raised.exception.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
