#!/usr/bin/env python3
"""Serve a generated static review folder on loopback with no application API."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_dir", type=Path)
    parser.add_argument("--port", type=int, default=0)
    return parser.parse_args()


class StaticReviewHandler(SimpleHTTPRequestHandler):
    server_version = "AssetReviewStatic/1.0"

    def do_POST(self) -> None:  # noqa: N802
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Static review server is read-only")

    def do_PUT(self) -> None:  # noqa: N802
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Static review server is read-only")

    def do_DELETE(self) -> None:  # noqa: N802
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Static review server is read-only")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


def main() -> int:
    args = parse_args()
    review_dir = args.review_dir.resolve()
    if not (review_dir / "index.html").is_file():
        raise SystemExit(f"Not a generated review folder: {review_dir}")

    handler = lambda *handler_args, **handler_kwargs: StaticReviewHandler(  # noqa: E731
        *handler_args,
        directory=str(review_dir),
        **handler_kwargs,
    )
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    host, port = server.server_address
    print(f"Static Asset Review: http://{host}:{port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
