"""Single Vercel serverless entry point. Routes all /api/* requests."""


from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import asyncio
import sys
import os


# Make lib/ importable from serverless context
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from api._handlers.register import handle_register
from api._handlers.list import handle_list
from api._handlers.verify import handle_verify
from api._handlers.search import handle_search
from api._handlers.federation import handle_federation_get, handle_federation_post
from api._handlers.sync import handle_sync
from api._handlers.stats import handle_stats
from api._handlers.health import handle_health




def route(method: str, path: str, query: dict, body_raw: str) -> tuple:
    """Return (status, headers, body_bytes)."""


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
    def do_GET(self):
        self._handle("GET")


    def do_POST(self):
        self._handle("POST")


    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


    def _handle(self, method: str):
        parsed = urlparse(self.path)
        path = parsed.path
        query = {}
        if parsed.query:
            for pair in parsed.query.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    query[k] = v


        length = int(self.headers.get("content-length", 0)) if method == "POST" else 0
        body_raw = self.rfile.read(length).decode("utf-8") if length else ""


        try:
            status, headers, payload = route(method, path, query, body_raw)
        except Exception as e:
            status = 500
            headers = {"Content-Type": "application/json"}
            payload = json.dumps({"error": "internal", "detail": str(e)}).encode("utf-8")


        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        self.wfile.write(payload)
