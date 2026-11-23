"""Two clones sharing one origin: what each sees of the other's work."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from support import Repo, agent_env, planned, scripted_agent


class TwoClones(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.origin = base / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "master", str(self.origin)],
                       check=True)
        self.alice = Repo()
        self.alice.git("remote", "add", "origin", str(self.origin))
        self.agent = scripted_agent(base, tasks=2)
        self.env = agent_env(self.agent)

    def tearDown(self):
        self.alice.cleanup()
        self.tmp.cleanup()

    def clone(self, name: str) -> Repo:
        path = Path(self.tmp.name) / name
        subprocess.run(["git", "clone", "-q", str(self.origin), str(path)], check=True)
        return Repo(path)

    def states(self, repo: Repo, wid: str) -> dict[str, str]:
        data = json.loads(repo.wp("status", wid, "--json").stdout)
        return {t["id"].split("/")[1]: t["state"] for t in data["tasks"]}

    def test_rehearsal(self):
        wid = planned(self.alice, tasks=2, agent=self.agent)
        self.alice.git("push", "-q", "origin", "master", f"workplan/{wid}/definition")

        bob = self.clone("bob")
        bob.git("switch", "-q", f"workplan/{wid}/definition")
        self.assertEqual(self.states(bob, wid), {"0000": "refinement", "0001": "refinement"})

        # Alice generates a patch: a working file, so Bob does not see it.
        self.alice.wp("produce-patch", "0000", env=self.env)
        self.assertEqual(self.states(self.alice, wid)["0000"], "development")

        # Bob claims 0001 on a task branch and pushes it.
        bob.git("switch", "-q", "-c", f"workplan/{wid}/task/0001")
        bob.git("push", "-q", "origin", f"workplan/{wid}/task/0001")
        self.alice.git("fetch", "-q", "origin")
        claimed = self.alice.git("branch", "-r", "--list", f"origin/workplan/{wid}/*")
        self.assertIn(f"origin/workplan/{wid}/task/0001", claimed)

        # Alice accepts 0000 and pushes; Bob sees it complete after pulling.
        self.alice.wp("accept", "0000")
        self.alice.git("push", "-q", "origin", f"workplan/{wid}/definition")
        bob.git("switch", "-q", f"workplan/{wid}/definition")
        bob.git("pull", "-q", "--rebase", "origin", f"workplan/{wid}/definition")
        self.assertEqual(self.states(bob, wid)["0000"], "complete")

        # Bob drops 0001 and pushes; Alice closes the workplan.
        plan = bob.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text().replace(
            "0001  Task number 1\n\n## Dropped\n", "## Dropped\n\n0001  Task number 1\n"))
        bob.commit_all("drop 0001")
        bob.git("push", "-q", "origin", f"workplan/{wid}/definition")

        self.alice.git("pull", "-q", "--rebase", "origin", f"workplan/{wid}/definition")
        self.alice.wp("merge")
        self.alice.git("push", "-q", "origin", "master")

        bob.git("switch", "-q", "master")
        bob.git("pull", "-q", "--rebase", "origin", "master")
        self.assertEqual(self.states(bob, wid), {"0000": "merged", "0001": "dropped"})


if __name__ == "__main__":
    unittest.main()
