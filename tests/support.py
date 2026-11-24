"""Temporary repositories, the workplan command, and a fake endpoint."""

import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
DATE = "2026-01-01T12:00:00+00:00"


class Repo:
    """A git repository in a temporary directory."""

    def __init__(self, path: Path | None = None):
        self._tmp = None
        if path is None:
            self._tmp = tempfile.TemporaryDirectory(prefix="workplan-test-")
            path = Path(self._tmp.name)
            self.git("init", "-q", "-b", "master", cwd=path)
        self.path = path
        self.git("config", "user.name", "test")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "commit.gpgsign", "false")

    def env(self, extra: dict | None = None) -> dict:
        env = {k: v for k, v in os.environ.items() if not k.startswith("WORKPLAN_")}
        env.update({
            "PYTHONPATH": str(SRC),
            "GIT_AUTHOR_DATE": DATE,
            "GIT_COMMITTER_DATE": DATE,
            "PAGER": "cat",
            "GIT_EDITOR": "true",
        })
        env.update(extra or {})
        return env

    def git(self, *args: str, cwd: Path | None = None, check: bool = True) -> str:
        result = subprocess.run(["git", *args], cwd=cwd or self.path, capture_output=True,
                                text=True, env=self.env())
        if check and result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)}: {result.stderr}")
        return result.stdout.strip()

    def sh(self, script: str, env: dict | None = None) -> str:
        result = subprocess.run(["sh", "-e", "-c", script], cwd=self.path, capture_output=True,
                                text=True, env=self.env(env))
        if result.returncode != 0:
            raise AssertionError(f"sh: {script}\n{result.stdout}\n{result.stderr}")
        return result.stdout

    def wp(self, *args: str, env: dict | None = None, ok: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run([sys.executable, "-m", "workplan", *args], cwd=self.path,
                                capture_output=True, text=True, env=self.env(env))
        if ok and result.returncode != 0:
            raise AssertionError(f"workplan {' '.join(args)}: {result.stdout}\n{result.stderr}")
        if not ok and result.returncode == 0:
            raise AssertionError(f"workplan {' '.join(args)} succeeded: {result.stdout}")
        return result

    def py(self, code: str, ok: bool = True) -> subprocess.CompletedProcess:
        """Run Python in the repository with the package importable."""
        result = subprocess.run([sys.executable, "-c", code], cwd=self.path, capture_output=True,
                                text=True, env=self.env())
        if ok and result.returncode != 0:
            raise AssertionError(f"python: {code}\n{result.stderr}")
        if not ok and result.returncode == 0:
            raise AssertionError(f"python succeeded: {code}\n{result.stdout}")
        return result

    def write(self, rel: str, text: str) -> Path:
        path = self.path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def read(self, rel: str) -> str:
        return (self.path / rel).read_text()

    def commit_all(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def wid(self) -> str:
        names = [p.name for p in (self.path / "workplans").iterdir()
                 if p.is_dir() and p.name[0].isdigit()]
        assert len(names) == 1, names
        return names[0]

    def cleanup(self) -> None:
        if self._tmp:
            self._tmp.cleanup()


def scripted_agent(directory: Path, edit: str = "printf 'goodbye\\n' >> app.txt",
                   tasks: int = 1) -> Path:
    """A command agent. For define-tasks it writes `tasks` tasks, each
    depending on the one before; for produce-patch it runs `edit` and
    writes the commit message. It saves the prompt to $PROMPT_COPY."""
    path = directory / "agent.sh"
    path.write_text(f"""#!/bin/sh
cat > "${{PROMPT_COPY:-/dev/null}}"
case "$WORKPLAN_ACTION" in
define-tasks)
    i=0
    while [ $i -lt {tasks} ]; do
        n=$(printf '%04d' $i)
        d="workplans/$WORKPLAN_TARGET/$n"
        mkdir -p "$d"
        if [ $i -eq 0 ]; then dep=none; else dep=$(printf '%04d' $((i - 1))); fi
        printf '# Task number %s\\n\\nA change.\\n\\nDepends on %s.\\n' $i $dep > "$d/TASK.md"
        printf '# Breakdown\\n\\n1. A step.\\n' > "$d/BREAKDOWN.md"
        i=$((i + 1))
    done
    echo tasks defined;;
produce-patch)
    {edit}
    echo "$WORKPLAN_TARGET Say goodbye" > "$WORKPLAN_COMMIT_MSG"
    echo agent finished;;
esac
""")
    path.chmod(0o755)
    return path


def agent_env(agent: Path) -> dict:
    return {"WORKPLAN_AGENT": "command", "WORKPLAN_AGENT_COMMAND": str(agent)}


def planned(repo: Repo, tasks: int = 1, agent: Path | None = None) -> str:
    """A repository with app.txt, workplans/ and one workplan whose tasks
    are defined and committed on its branch. Returns the workplan id."""
    repo.write("app.txt", "hello\n")
    repo.commit_all("app")
    repo.wp("init")
    repo.wp("plan", "greeting", "-m", "app.txt says goodbye. Nothing else changes.")
    wid = repo.wid()
    if tasks:
        tmp = Path(tempfile.mkdtemp(prefix="workplan-agent-"))
        repo.wp("define-tasks", env=agent_env(agent or scripted_agent(tmp, tasks=tasks)))
    return wid


class FakeEndpoint:
    """An OpenAI-compatible endpoint that replies from a queue."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.requests: list[dict] = []
        endpoint = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                endpoint.requests.append({"path": self.path, "body": body,
                                          "auth": self.headers.get("Authorization")})
                reply = endpoint.replies.pop(0) if endpoint.replies else "none"
                data = json.dumps({"choices": [{"message": {"content": reply}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}/v1"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
