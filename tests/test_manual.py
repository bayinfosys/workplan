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
        prompt = self.repo.wp("gen-patch", "0000", "--prompt").stdout
        self.assertIn(f"===== workplans/{wid}/0000/TASK.md =====", prompt)
        self.assertIn("# Task number 0", prompt)
        self.assertIn("===== app.txt =====", prompt)
        prompt = self.repo.wp("gen-task", "--prompt").stdout
        self.assertIn(f"===== workplans/{wid}/WORKPLAN.md =====", prompt)
        self.assertIn("numbered from 0001 upwards", prompt)
        self.assertEqual(self.repo.git("status", "--porcelain"), before)

    def test_add_patch(self):
        wid = planned(self.repo)
        reply = f"Here it is.\n\n{wid}/0000 Say goodbye\n\n```diff\n{DIFF}```\n"
        out = self.repo.wp("add-patch", "0000", input=reply).stdout
        self.assertIn("by a pasted reply", out)
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/COMMIT_MSG"),
                         f"{wid}/0000 Say goodbye\n")
        self.assertIn("+goodbye", self.repo.read(f"workplans/{wid}/0000/output.patch"))
        self.assertEqual(self.state("0000"), "development")
        self.assertEqual(self.repo.read("app.txt"), "hello\n")

        file = Path(self.tmp.name) / "reply.txt"
        file.write_text(reply)
        self.repo.wp("add-patch", "0000", str(file))
        self.repo.wp("accept-patch", "0000")
        self.assertEqual(self.repo.read("app.txt"), "hello\ngoodbye\n")

    def test_add_patch_refusals(self):
        wid = planned(self.repo)
        result = self.repo.wp("add-patch", "0000", input="No diff at all.\n", ok=False)
        self.assertIn("no unified diff", result.stderr)
        wrong = DIFF.replace(" hello", " not the content")
        result = self.repo.wp("add-patch", "0000", input=f"```diff\n{wrong}```\n", ok=False)
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
        out = self.repo.wp("add-task", "--reply", str(file)).stdout
        self.assertEqual(out.strip(), f"added {wid}/0001")
        self.assertTrue(self.repo.read(f"workplans/{wid}/0000/TASK.md").startswith("# Task number 0"))
        self.assertIn("0001  From a chat", self.repo.read(f"workplans/{wid}/WORKPLAN.md"))
        self.assertEqual(self.state("0001"), "refinement")
        self.assertIn(f"?? workplans/{wid}/0001/", self.repo.git("status", "--porcelain"))

        result = self.repo.wp("add-task", "--reply", "-", input="nothing useful\n", ok=False)
        self.assertIn("no new task", result.stderr)


if __name__ == "__main__":
    unittest.main()
