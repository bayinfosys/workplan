"""workplan serve: a local web page over the operations.

The server binds to 127.0.0.1. Every request must name 127.0.0.1 or
localhost on the server's port as its Host, and every /api request
must carry the token printed at startup in an X-Workplan-Token header;
other requests get 403. Another site open in the browser can therefore
neither read nor write. Writes run one at a time; a write while
another runs gets 409. Reads run alongside. The server keeps nothing
but the token and the lock.

GET  /, /app.js, /app.css       the page
GET  /api/workplans             ops.workplans
GET  /api/status?id=            ops.status
GET  /api/document?id=&name=    ops.document
GET  /api/diff?task=            ops.diff
GET  /api/merge-message?id=     ops.merge_message
POST /api/document              {id, name, text}: ops.save_document
POST /api/run                   {op, ...}: plan {name, goal},
                                define-tasks {id}, produce-patch,
                                apply, accept, reject {task},
                                merge {id, message}

Responses are {"data": ...}, or {"error": "..."} with 400 for a failed
operation.
"""

import hmac
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from urllib.parse import parse_qs, urlparse

from workplan import agent, config, ops
from workplan.git import Fail

FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
}


class NotFound(Exception):
    pass


def read(path: str, query: dict, cfg: dict):
    master = cfg["master"]
    match path:
        case "/api/workplans":
            return ops.workplans()
        case "/api/status":
            return ops.status(query.get("id"), master)
        case "/api/document":
            return ops.document(query["id"], query["name"])
        case "/api/diff":
            return {"text": ops.diff(query["task"])}
        case "/api/merge-message":
            return {"text": ops.merge_message(query.get("id"), master)}
    raise NotFound(path)


def run(body: dict, cfg: dict):
    master = cfg["master"]
    match body.get("op"):
        case "plan":
            if not (body.get("goal") or "").strip():
                raise Fail("a new workplan needs a goal")
            return ops.plan(body["name"], master, goal=body["goal"])
        case "define-tasks":
            return agent.define_tasks(body.get("id"), cfg)
        case "produce-patch":
            return agent.produce_patch(body["task"], cfg)
        case "apply":
            return {"stat": ops.apply(body["task"])}
        case "accept":
            return {"commit": ops.accept(body["task"], master)}
        case "reject":
            return {"result": ops.reject(body["task"])}
        case "merge":
            return ops.merge(body.get("id"), master, message=body.get("message") or "")
    raise Fail(f"unknown operation {body.get('op')!r}")


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int):
        try:
            super().__init__(("127.0.0.1", port), Handler)
        except OSError as e:
            raise Fail(f"port {port}: {e.strerror}") from e
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

    def answer(self, work) -> None:
        try:
            self.reply(200, {"data": work(config.load())})
        except Fail as e:
            self.reply(400, {"error": str(e)})
        except KeyError as e:
            self.reply(400, {"error": f"missing {e}"})
        except NotFound as e:
            self.reply(404, {"error": f"no such path {e}"})
        except Exception as e:
            self.reply(500, {"error": f"{type(e).__name__}: {e}"})

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if not self.host_ok():
            return self.reply(403, {"error": "forbidden"})
        if url.path in FILES:
            name, kind = FILES[url.path]
            page = resources.files("workplan") / "web" / name
            if not page.is_file():
                return self.reply(404, {"error": f"no {name}"})
            return self.send(200, page.read_bytes(), kind)
        if not url.path.startswith("/api/") or not self.token_ok():
            return self.reply(403, {"error": "forbidden"})
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        self.answer(lambda cfg: read(url.path, query, cfg))

    def do_POST(self) -> None:
        url = urlparse(self.path)
        if not self.host_ok() or not self.token_ok():
            return self.reply(403, {"error": "forbidden"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self.reply(400, {"error": "the body is not JSON"})
        if url.path == "/api/document":
            work = lambda cfg: ops.save_document(body["id"], body["name"], body["text"])  # noqa: E731
        elif url.path == "/api/run":
            work = lambda cfg: run(body, cfg)  # noqa: E731
        else:
            return self.reply(404, {"error": f"no such path {url.path}"})
        if not self.server.lock.acquire(blocking=False):
            return self.reply(409, {"error": "another operation is running"})
        try:
            self.answer(work)
        finally:
            self.server.lock.release()
