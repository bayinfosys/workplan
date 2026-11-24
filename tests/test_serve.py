"""workplan serve: the server in a subprocess, driven over HTTP."""

import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from support import Repo, agent_env, planned, scripted_agent


class Serve(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.tmp = tempfile.TemporaryDirectory()
        self.server = None

    def tearDown(self):
        if self.server:
            self.server.terminate()
            self.server.wait(timeout=10)
            self.server.stdout.close()
        self.repo.cleanup()
        self.tmp.cleanup()

    def start(self, env: dict | None = None) -> None:
        self.server = subprocess.Popen(
            [sys.executable, "-m", "workplan", "serve", "--port", "0"],
            cwd=self.repo.path, env=self.repo.env(env), stdout=subprocess.PIPE, text=True)
        url = urlparse(self.server.stdout.readline().split(": ", 1)[1].strip())
        self.base = f"http://127.0.0.1:{url.port}"
        self.token = parse_qs(url.query)["token"][0]

    def call(self, path: str, body: dict | None = None, method: str | None = None,
             token: str | None = None, host: str | None = None) -> tuple[int, dict]:
        headers = {"X-Workplan-Token": self.token if token is None else token}
        if host:
            headers["Host"] = host
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(self.base + path, data=data, headers=headers,
                                         method=method or ("POST" if body is not None else "GET"))
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def ok(self, path: str, body: dict | None = None, method: str | None = None):
        code, reply = self.call(path, body, method)
        self.assertEqual(code, 200, reply)
        return reply["data"]

    def test_page_and_access(self):
        wid = planned(self.repo)
        self.start()
        with urllib.request.urlopen(self.base + "/") as response:
            self.assertIn(b"<title>workplan</title>", response.read())
        self.assertEqual(self.call("/api/workplan", token="wrong")[0], 403)
        self.assertEqual(self.call("/api/workplan", host="evil.example")[0], 403)
        self.assertEqual(self.call(f"/api/task/{wid}/0000/patch/apply", {}, token="")[0], 403)
        self.assertEqual(self.call("/api/nothing")[0], 404)
        self.assertEqual(self.call(f"/api/workplan/{wid}/task", method="DELETE")[0], 405)
        self.assertEqual(self.call("/api/install", {})[0], 404)
        rows = self.ok("/api/workplan")
        self.assertEqual([(r["id"].endswith("greeting"), r["editable"]) for r in rows], [(True, True)])

    def test_documents(self):
        wid = planned(self.repo)
        self.start()
        data = self.ok(f"/api/workplan/{wid}/task")
        self.assertEqual([t["state"] for t in data["tasks"]], ["refinement"])
        task = self.ok(f"/api/task/{wid}/0000")
        self.assertTrue(task["documents"]["TASK.md"].startswith("# Task number 0"))
        self.assertTrue(task["editable"])
        self.ok(f"/api/task/{wid}/0000/NOTES.md", {"text": "# Notes"}, method="PUT")
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/NOTES.md"), "# Notes\n")
        added = self.ok(f"/api/workplan/{wid}/task", {"title": "From the page",
                                                       "depend": ["0000"]})
        self.assertEqual(added["task"], f"{wid}/0001")
        added = self.ok(f"/api/task/{wid}/0001")
        self.assertIn("Depends on 0000.", added["documents"]["TASK.md"])
        code, reply = self.call(f"/api/task/{wid}/0000/app.txt", {"text": "x"}, method="PUT")
        self.assertEqual(code, 400)
        self.assertIn("not a workplan document", reply["error"])
        code, reply = self.call(f"/api/task/{wid}/0000/NOTES.md", {}, method="PUT")
        self.assertEqual(code, 400)
        self.assertIn("needs the text", reply["error"])

    def test_the_flow(self):
        wid = planned(self.repo)
        tid = f"{wid}/0000"
        self.start(agent_env(scripted_agent(Path(self.tmp.name))))
        self.ok(f"/api/task/{tid}/patch/gen", {})
        self.assertIn("+goodbye", self.ok(f"/api/task/{tid}/patch")["text"])
        self.ok(f"/api/task/{tid}/patch/apply", {})
        self.ok(f"/api/task/{tid}/patch/accept", {})
        states = [t["state"] for t in self.ok(f"/api/workplan/{wid}/task")["tasks"]]
        self.assertEqual(states, ["complete"])
        message = self.ok(f"/api/workplan/{wid}/merge", {"show": True})["message"]
        self.assertTrue(message.startswith(f"{wid} greeting"))
        self.ok(f"/api/workplan/{wid}/merge", {"message": "Merged from the page\n"})
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), "Merged from the page")
        code, reply = self.call(f"/api/task/{tid}/patch/accept", {})
        self.assertEqual(code, 400)

    def test_manual_mode(self):
        wid = planned(self.repo)
        tid = f"{wid}/0000"
        self.start()
        prompt = self.ok(f"/api/task/{tid}/patch/gen", {"prompt": True})["prompt"]
        self.assertIn(f"===== workplans/{tid}/TASK.md =====", prompt)
        code, reply = self.call(f"/api/task/{tid}/patch", {"reply": "/etc/passwd"})
        self.assertEqual(code, 400)
        self.assertIn("no unified diff", reply["error"])
        diff = "--- a/app.txt\n+++ b/app.txt\n@@ -1 +1,2 @@\n hello\n+goodbye\n"
        self.ok(f"/api/task/{tid}/patch", {"reply": f"{tid} Say goodbye\n\n```diff\n{diff}```\n"})
        states = [t["state"] for t in self.ok(f"/api/workplan/{wid}/task")["tasks"]]
        self.assertEqual(states, ["development"])

    def test_one_write_at_a_time(self):
        wid = planned(self.repo)
        tid = f"{wid}/0000"
        agent = scripted_agent(Path(self.tmp.name), edit="sleep 2; printf 'goodbye\\n' >> app.txt")
        self.start(agent_env(agent))
        first = threading.Thread(target=self.call, args=(f"/api/task/{tid}/patch/gen", {}))
        first.start()
        time.sleep(0.8)
        code, reply = self.call(f"/api/task/{tid}/patch/apply", {})
        self.assertEqual(code, 409, reply)
        self.assertEqual(self.call(f"/api/workplan/{wid}/task")[0], 200)
        first.join()

    def test_plan_and_read_only_workplans(self):
        wid = planned(self.repo)
        self.repo.git("switch", "-q", "master")
        self.start()
        rows = {r["id"]: r for r in self.ok("/api/workplan")}
        self.assertEqual(rows[wid]["source"], f"workplan/{wid}/definition")
        self.assertFalse(rows[wid]["editable"])
        text = self.ok(f"/api/workplan/{wid}")["text"]
        self.assertTrue(text.startswith(f"# Workplan {wid}"))
        code, _ = self.call(f"/api/workplan/{wid}", {"text": "x"}, method="PUT")
        self.assertEqual(code, 400)

        self.assertEqual(self.call("/api/workplan", {"name": "second"})[0], 400)
        created = self.ok("/api/workplan", {"name": "second", "goal": "A second goal."})
        self.assertEqual(self.repo.git("branch", "--show-current"), created["branch"])
        rows = {r["id"]: r for r in self.ok("/api/workplan")}
        self.assertTrue(rows[created["workplan"]]["editable"])


if __name__ == "__main__":
    unittest.main()
