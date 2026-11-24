"""workplan serve: a local web page over the commands.

The server binds to 127.0.0.1. Every request must name 127.0.0.1 or
localhost on the server's port as its Host, and every /api request
must carry the token printed at startup in an X-Workplan-Token header;
other requests get 403. Another site open in the browser can therefore
neither read nor write.

Every /api request is matched to a command through the registry (see
registry.py for the routes a command's verb and noun give). A GET runs
alongside other requests; any other method takes the write lock, and
gets 409 while another holds it. The server keeps nothing but the
token and the lock.

Replies are {"data": ...}, or {"error": "..."} with 400 for a failed
command, 404 for no such route, and 405 for a route with another
method.
"""

import hmac
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from typing import Any, Callable
from urllib.parse import parse_qs, unquote, urlparse

from workplan.git import Fail
from workplan.registry import Registry

FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/api.js": ("api.js", "text/javascript; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
}


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int, registry: Registry, context: Callable[[], Any]):
        try:
            super().__init__(("127.0.0.1", port), Handler)
        except OSError as e:
            raise Fail(f"port {port}: {e.strerror}") from e
        self.registry = registry
        self.context = context
        self.token = secrets.token_urlsafe(16)
        self.lock = threading.Lock()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}/?token={self.token}"


class Handler(BaseHTTPRequestHandler):
    server: Server

    def log_message(self, format: str, *args) -> None:
        pass

    def send(self, code: int, body: bytes, kind: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def reply(self, code: int, data: dict) -> None:
        self.send(code, json.dumps(data).encode(), "application/json")

    def host_ok(self) -> bool:
        port = self.server.server_port
        return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def token_ok(self) -> bool:
        return hmac.compare_digest(self.headers.get("X-Workplan-Token", ""), self.server.token)

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path in FILES and self.host_ok():
            name, kind = FILES[url.path]
            page = resources.files("workplan") / "web" / name
            if not page.is_file():
                return self.reply(404, {"error": f"no {name}"})
            return self.send(200, page.read_bytes(), kind)
        self.api("GET")

    def do_POST(self) -> None:
        self.api("POST")

    def do_PUT(self) -> None:
        self.api("PUT")

    def do_DELETE(self) -> None:
        self.api("DELETE")

    def api(self, method: str) -> None:
        url = urlparse(self.path)
        if not self.host_ok() or not url.path.startswith("/api/") or not self.token_ok():
            return self.reply(403, {"error": "forbidden"})
        registry = self.server.registry
        try:
            command, path_values = registry.match(method, unquote(url.path))
        except LookupError:
            return self.reply(404, {"error": f"no such route {url.path}"})
        except PermissionError:
            return self.reply(405, {"error": f"{method} is not a method of {url.path}"})

        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        body = {}
        if method in ("POST", "PUT"):
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)))
                                  or b"{}")
            except ValueError:
                return self.reply(400, {"error": "the body is not JSON"})
            if not isinstance(body, dict):
                return self.reply(400, {"error": "the body is not a JSON object"})
        values = registry.values(command, path_values, query, body)

        if method == "GET":
            return self.answer(command, values)
        if not self.server.lock.acquire(blocking=False):
            return self.reply(409, {"error": "another operation is running"})
        try:
            self.answer(command, values)
        finally:
            self.server.lock.release()

    def answer(self, command, values: dict) -> None:
        try:
            data = self.server.registry.call(command, self.server.context(), values)
            self.reply(200, {"data": data})
        except Fail as e:
            self.reply(400, {"error": str(e)})
        except Exception as e:
            self.reply(500, {"error": f"{type(e).__name__}: {e}"})
