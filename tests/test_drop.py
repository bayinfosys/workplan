"""task drop and patch drop."""

import json
import tempfile
import unittest
from pathlib import Path

from support import Repo, agent_env, planned, scripted_agent


class Drop(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.tmp = tempfile.TemporaryDirectory()
        self.env = agent_env(scripted_agent(Path(self.tmp.name)))

    def tearDown(self):
        self.repo.cleanup()
        self.tmp.cleanup()

    def states(self) -> dict[str, str]:
        data = json.loads(self.repo.wp("status", "--json").stdout)
        return {t["id"].split("/")[1]: t["state"] for t in data["tasks"]}

    def test_drop_task(self):
        wid = planned(self.repo, tasks=3, agent=scripted_agent(Path(self.tmp.name), tasks=3))
        plan = self.repo.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text().replace(
            "0001  Task number 1", "0001  Task number 1, which\n      runs on"))
        self.repo.commit_all("a long entry")

        out = self.repo.wp("task", "drop", "0001").stdout
        self.assertEqual(out.strip().split(" ", 1)[1], f"{wid} drop 0001")
        text = plan.read_text()
        self.assertIn("## Tasks\n\n0000  Task number 0\n0002  Task number 2\n\n## Dropped\n\n"
                      "0001  Task number 1, which\n      runs on\n", text)
        self.assertEqual(self.states(), {"0000": "refinement", "0001": "dropped",
                                         "0002": "refinement"})
        self.assertEqual(self.repo.git("status", "--porcelain"), "")
        self.assertIn("dropped already", self.repo.wp("task", "drop", "0001", ok=False).stderr)

    def test_drop_task_refuses_a_committed_task(self):
        planned(self.repo)
        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.wp("patch", "accept", "0000")
        self.assertIn("is complete", self.repo.wp("task", "drop", "0000", ok=False).stderr)

    def test_merge_after_drop(self):
        wid = planned(self.repo, tasks=2, agent=scripted_agent(Path(self.tmp.name), tasks=2))
        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.wp("patch", "accept", "0000")
        self.repo.wp("task", "drop", "0001")
        self.repo.wp("merge")
        self.assertEqual(self.repo.git("branch", "--show-current"), "master")
        self.assertNotIn(f"{wid}/0001", self.repo.git("log", "-1", "--format=%B"))

    def test_drop_patch(self):
        wid = planned(self.repo)
        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.wp("patch", "apply", "0000")
        self.assertIn("applied", self.repo.wp("patch", "drop", "0000", ok=False).stderr)
        self.repo.wp("patch", "reject", "0000")
        self.repo.wp("patch", "drop", "0000")
        task = self.repo.path / "workplans" / wid / "0000"
        self.assertFalse((task / "output.patch").exists())
        self.assertFalse((task / "COMMIT_MSG").exists())
        self.assertEqual(self.states(), {"0000": "refinement"})
        self.assertIn("not found", self.repo.wp("patch", "drop", "0000", ok=False).stderr)


if __name__ == "__main__":
    unittest.main()
