"""Manual mode: prompts for a chat, and its replies pasted back."""

import json
import tempfile
import unittest
from pathlib import Path

from support import Repo, planned

DIFF = """\
--- a/app.txt
+++ b/app.txt
@@ -1 +1,2 @@
 hello
+goodbye
"""


class Manual(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.repo.cleanup()
        self.tmp.cleanup()

    def state(self, n: str) -> str:
        data = json.loads(self.repo.wp("status", "--json").stdout)
        return next(t["state"] for t in data["tasks"] if t["id"].endswith(n))

    def test_prompts_change_nothing(self):
        wid = planned(self.repo)
        before = self.repo.git("status", "--porcelain")
        prompt = self.repo.wp("patch", "gen", "0000", "--prompt").stdout
        self.assertIn(f"===== workplans/{wid}/0000/TASK.md =====", prompt)
        self.assertIn("# Task number 0", prompt)
        self.assertIn("===== app.txt =====", prompt)
        prompt = self.repo.wp("task", "gen", "--prompt").stdout
        self.assertIn(f"===== workplans/{wid}/WORKPLAN.md =====", prompt)
        self.assertIn("numbered from 0001 upwards", prompt)
        self.assertEqual(self.repo.git("status", "--porcelain"), before)

    def test_show_patch_heads_the_diff(self):
        wid = planned(self.repo, tasks=2)
        self.repo.write(f"workplans/{wid}/0001/output.patch", DIFF)
        out = self.repo.wp("patch", "show", "0001").stdout
        head, stat, diff = out.split("\n\n", 2)
        self.assertEqual(head.splitlines(), [
            f"{wid}/0001  development  Task number 1",
            "commit   (none)",
            "depends  0000 refinement",
        ])
        self.assertEqual(stat.splitlines()[0].split(), ["app.txt", "|", "1", "+"])
        self.assertEqual(diff, DIFF)

        self.repo.write(f"workplans/{wid}/0001/COMMIT_MSG", f"{wid}/0001 Say goodbye\n")
        data = json.loads(self.repo.wp("patch", "show", "0001", "--json").stdout)
        self.assertEqual(data["commit_msg"], f"{wid}/0001 Say goodbye")
        self.assertEqual(data["depends"], [{"id": f"{wid}/0000", "state": "refinement"}])
        self.assertEqual(data["text"], DIFF)

    def test_add_patch_with_fences_in_the_diff(self):
        wid = planned(self.repo)
        self.repo.write("README.md", "# App\n\n```\nrun\n```\n")
        self.repo.commit_all("readme")
        diff = ("--- a/README.md\n+++ b/README.md\n@@ -2,4 +2,5 @@\n \n ```\n run\n"
                "+run again\n ```\n")
        for reply in (f"{wid}/0000 Run again\n\n```diff\n{diff}```\n",
                      f"{wid}/0000 Run again\n\n{diff}"):
            self.repo.wp("patch", "add", "0000", input=reply)
            self.assertEqual(self.repo.read(f"workplans/{wid}/0000/output.patch").count("```"), 2)
            self.assertEqual(self.state("0000"), "development")

    def test_add_patch_under_workplans(self):
        wid = planned(self.repo, tasks=2)
        plan = f"workplans/{wid}/WORKPLAN.md"
        self.repo.write(plan, self.repo.read(plan) + "An uncommitted line.\n")
        notes = f"workplans/{wid}/0001/NOTES.md"
        diff = (f"--- /dev/null\n+++ b/{notes}\n@@ -0,0 +1 @@\n+# Notes\n")
        self.repo.wp("patch", "add", "0000", input=f"{wid}/0000 Notes\n\n```diff\n{diff}```\n")
        patch = self.repo.read(f"workplans/{wid}/0000/output.patch")
        self.assertIn(f"+++ b/{notes}", patch)
        self.assertNotIn("WORKPLAN.md", patch)
        self.assertNotIn("COMMIT_MSG", patch)
        self.repo.wp("patch", "accept", "0000")
        self.assertEqual(self.repo.git("show", "--format=", "--name-only", "HEAD").split(),
                         sorted([plan, notes]))

    def test_add_patch_refuses_a_reply_for_another_task(self):
        wid = planned(self.repo, tasks=2)
        result = self.repo.wp("patch", "add", "0000", ok=False,
                              input=f"{wid}/0001 Say goodbye\n\n```diff\n{DIFF}```\n")
        self.assertIn(f"the reply is for {wid}/0001, not {wid}/0000", result.stderr)
        self.assertFalse((self.repo.path / f"workplans/{wid}/0000/output.patch").exists())
        self.assertFalse((self.repo.path / f"workplans/{wid}/0000/COMMIT_MSG").exists())

    def test_add_patch_reads_the_commit_line_before_the_diff(self):
        wid = planned(self.repo, tasks=2)
        self.repo.write("log.txt", f"{wid}/0000 was planned\n{wid}/0001 is next\n")
        self.repo.commit_all("log")
        diff = ("--- a/log.txt\n+++ b/log.txt\n@@ -1,2 +1,3 @@\n"
                f" {wid}/0000 was planned\n {wid}/0001 is next\n+done\n")
        out = self.repo.wp("patch", "add", "0000", input=f"Here is the patch.\n\n{diff}")
        self.assertIn("written from TASK.md's title", out.stderr + out.stdout)
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/COMMIT_MSG"),
                         f"{wid}/0000 Task number 0\n")

    def test_add_patch(self):
        wid = planned(self.repo)
        reply = f"Here it is.\n\n{wid}/0000 Say goodbye\n\n```diff\n{DIFF}```\n"
        out = self.repo.wp("patch", "add", "0000", input=reply).stdout
        self.assertIn("by a pasted reply", out)
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/COMMIT_MSG"),
                         f"{wid}/0000 Say goodbye\n")
        self.assertIn("+goodbye", self.repo.read(f"workplans/{wid}/0000/output.patch"))
        self.assertEqual(self.state("0000"), "development")
        self.assertEqual(self.repo.read("app.txt"), "hello\n")

        file = Path(self.tmp.name) / "reply.txt"
        file.write_text(reply)
        self.repo.wp("patch", "add", "0000", str(file))
        self.repo.wp("patch", "accept", "0000")
        self.assertEqual(self.repo.read("app.txt"), "hello\ngoodbye\n")

    def test_add_patch_refusals(self):
        wid = planned(self.repo)
        result = self.repo.wp("patch", "add", "0000", input="No diff at all.\n", ok=False)
        self.assertIn("no unified diff", result.stderr)
        wrong = DIFF.replace(" hello", " not the content")
        result = self.repo.wp("patch", "add", "0000", input=f"```diff\n{wrong}```\n", ok=False)
        self.assertIn("did not apply", result.stderr)
        self.assertFalse((self.repo.path / f"workplans/{wid}/0000/output.patch").exists())
        self.assertEqual(self.repo.git("worktree", "list").count("\n"), 0)

    def test_add_task_from_a_reply(self):
        wid = planned(self.repo, tasks=1)
        reply = (f"===== workplans/{wid}/0000/TASK.md =====\n# Not this one\n"
                 f"===== workplans/{wid}/0001/TASK.md =====\n# From a chat\n\nDepends on 0000.\n"
                 f"===== workplans/{wid}/0001/BREAKDOWN.md =====\n# Breakdown\n\n1. A step.\n")
        file = Path(self.tmp.name) / "tasks.txt"
        file.write_text(reply)
        out = self.repo.wp("task", "add", "--reply", str(file)).stdout
        self.assertEqual(out.strip().splitlines()[0], f"added {wid}/0001")
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), f"{wid} define tasks")
        self.assertTrue(self.repo.read(f"workplans/{wid}/0000/TASK.md").startswith("# Task number 0"))
        self.assertIn("0001  From a chat", self.repo.read(f"workplans/{wid}/WORKPLAN.md"))
        self.assertEqual(self.state("0001"), "refinement")
        self.assertEqual(self.repo.git("status", "--porcelain"), "")

        result = self.repo.wp("task", "add", "--reply", "-", input="nothing useful\n", ok=False)
        self.assertIn("no new task", result.stderr)


if __name__ == "__main__":
    unittest.main()
