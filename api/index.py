"""Single Vercel serverless entry point. Routes all /api/* requests."""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# Make lib/ importable from serverless context
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api._handlers.federation import handle_federation_get, handle_federation_post
from api._handlers.health import handle_health
from api._handlers.list import handle_list
from api._handlers.register import handle_register
from api._handlers.search import handle_search
from api._handlers.stats import handle_stats
from api._handlers.sync import handle_sync
from api._handlers.verify import handle_verify

MAX_PAYLOAD_SIZE = 1_048_576  # 1MB


def route(method: str, path: str, query: dict[str, str], body_raw: str) -> tuple[int, dict[str, str], bytes]:
    """Return (status, headers, body_bytes)."""
    # --- Payload size check ---
    if len(body_raw.encode("utf-8")) > MAX_PAYLOAD_SIZE:
        return (
            413,
            {"Content-Type": "application/json"},
            json.dumps({"error": "payload_too_large"}).encode("utf-8"),
        )

    # --- Health ---
    if path == "/api/health":
        return handle_health()

    # --- Registry core ---
    if path == "/api/register" and method == "POST":
        return handle_register(body_raw)
    if path == "/api/list" and method == "GET":
        return handle_list(query)
    if path == "/api/verify" and method == "GET":
        return handle_verify(query)
    if path == "/api/search" and method == "GET":
        return handle_search(query)
    if path == "/api/stats" and method == "GET":
        return handle_stats()

    # --- Federation ---
    if path == "/api/federation" and method == "GET":
        return handle_federation_get()
    if path == "/api/federation/register" and method == "POST":
        return handle_federation_post(body_raw)

    # --- Sync from peer ---
    if path == "/api/sync" and method == "GET":
        return handle_sync(query)

    # --- Fallback ---
    return (
        404,
        {"Content-Type": "application/json"},
        json.dumps({"error": "not_found", "path": path, "method": method}).encode("utf-8"),
    )


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._handle("GET")

    def do_POST(self) -> None:
        self._handle("POST")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _handle(self, method: str) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query: dict[str, str] = {}
        if parsed.query:
            for pair in parsed.query.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    query[k] = v

        length = int(self.headers.get("content-length", 0)) if method == "POST" else 0
        if length > MAX_PAYLOAD_SIZE:
            self.send_response(413)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "payload_too_large"}).encode("utf-8"))
            return

        body_raw = self.rfile.read(length).decode("utf-8") if length > 0 else ""

        try:
            status, headers, payload = route(method, path, query, body_raw)
        except Exception:  # noqa: BLE001
            status = 500
            headers = {"Content-Type": "application/json"}
            payload = json.dumps({"error": "internal_error"}).encode("utf-8")

        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
        self.wfile.write(payload_bytes)


if __name__ == "__main__":
    from http.server import HTTPServer

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer((host, port), handler)
    print(f"Starting server on {host}:{port}")
    server.serve_forever()
