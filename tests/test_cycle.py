"""A workplan from init to merge, and the states along the way."""

import json
import tempfile
import unittest
from pathlib import Path

from support import Repo, agent_env, planned, scripted_agent


class Cycle(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.env = agent_env(scripted_agent(self.dir))

    def tearDown(self):
        self.repo.cleanup()
        self.tmp.cleanup()

    def states(self) -> dict[str, str]:
        data = json.loads(self.repo.wp("status", "--json").stdout)
        return {t["id"].split("/")[1]: t["state"] for t in data["tasks"]}

    def editor(self, line: str) -> str:
        path = self.dir / "editor.sh"
        path.write_text(f'#!/bin/sh\necho "{line}" >> "$1"\n')
        path.chmod(0o755)
        return str(path)

    # init and plan -------------------------------------------------------

    def test_init_commits_once(self):
        self.repo.wp("init")
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), "workplan init")
        self.assertEqual(self.repo.git("status", "--porcelain"), "")
        self.repo.wp("init")
        self.assertEqual(self.repo.git("rev-list", "--count", "HEAD"), "1")
        self.assertEqual(self.repo.read(".gitignore").count("output.patch"), 1)

    def test_plan_unchanged_creates_nothing(self):
        self.repo.wp("init")
        result = self.repo.wp("add-workplan", "greeting", ok=False)
        self.assertIn("unchanged", result.stderr)
        self.assertEqual(self.repo.git("branch", "--show-current"), "master")
        self.assertFalse(any(p.is_dir() for p in (self.repo.path / "workplans").iterdir()))

    def test_plan_with_editor(self):
        self.repo.wp("init")
        self.repo.wp("add-workplan", "greeting", env={"GIT_EDITOR": self.editor("FROM THE EDITOR")})
        wid = self.repo.wid()
        self.assertEqual(self.repo.git("branch", "--show-current"), f"workplan/{wid}/definition")
        plan = self.repo.read(f"workplans/{wid}/WORKPLAN.md")
        self.assertTrue(plan.startswith(f"# Workplan {wid}: greeting\n"))
        self.assertTrue(plan.endswith("FROM THE EDITOR\n"))
        self.assertEqual(self.repo.git("status", "--porcelain"), "")
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), f"{wid} workplan")

    def test_plan_with_goal(self):
        self.repo.wp("init")
        self.repo.wp("add-workplan", "greeting", "-m", "app.txt says goodbye.")
        wid = self.repo.wid()
        self.assertIn("## Goal\n\napp.txt says goodbye.\n",
                      self.repo.read(f"workplans/{wid}/WORKPLAN.md"))

    # gen-task --------------------------------------------------------

    def test_gen_task(self):
        wid = planned(self.repo, tasks=2)
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), f"{wid} define tasks")
        self.assertEqual(self.repo.git("status", "--porcelain"), "")
        files = self.repo.git("show", "--name-only", "--format=", "HEAD").splitlines()
        self.assertEqual(sorted(files), sorted([
            f"workplans/{wid}/WORKPLAN.md",
            f"workplans/{wid}/0000/TASK.md", f"workplans/{wid}/0000/BREAKDOWN.md",
            f"workplans/{wid}/0001/TASK.md", f"workplans/{wid}/0001/BREAKDOWN.md",
        ]))
        plan = self.repo.read(f"workplans/{wid}/WORKPLAN.md")
        self.assertIn("## Tasks\n\n0000  Task number 0\n0001  Task number 1\n\n## Dropped", plan)
        self.assertEqual(self.states(), {"0000": "refinement", "0001": "refinement"})
        self.assertEqual(self.repo.git("worktree", "list").count("\n"), 0)

    def test_gen_task_leaves_existing_tasks(self):
        wid = planned(self.repo, tasks=1)
        task = self.repo.path / "workplans" / wid / "0000" / "TASK.md"
        task.write_text("# Edited by hand\n\nDepends on none.\n")
        agent = scripted_agent(self.dir, tasks=2)
        self.repo.wp("gen-task", env=agent_env(agent))
        self.assertEqual(task.read_text(), "# Edited by hand\n\nDepends on none.\n")
        self.assertEqual(sorted(self.states()), ["0000", "0001"])

    def test_gen_task_with_nothing_new_fails(self):
        planned(self.repo, tasks=1)
        result = self.repo.wp("gen-task", env=self.env, ok=False)
        self.assertIn("no new task", result.stderr)

    def test_gen_task_needs_the_branch(self):
        wid = planned(self.repo, tasks=0)
        self.repo.git("switch", "-q", "master")
        self.repo.git("checkout", "-q", f"workplan/{wid}/definition", "--", "workplans")
        result = self.repo.wp("gen-task", wid, env=self.env, ok=False)
        self.assertIn("switch", result.stderr)

    # add-task ------------------------------------------------------------

    def test_add_task(self):
        wid = planned(self.repo, tasks=1)
        out = self.repo.wp("add-task", "Say", "goodbye", "--depend", "0000",
                           env={"GIT_EDITOR": self.editor("FROM THE EDITOR")}).stdout
        self.assertIn(f"{wid}/0001: listed in", out)
        task = self.repo.read(f"workplans/{wid}/0001/TASK.md")
        self.assertTrue(task.startswith("# Say goodbye\n"))
        self.assertIn("<The change, in a sentence or two.>", task)
        self.assertIn("Depends on 0000.", task)
        self.assertTrue(task.endswith("FROM THE EDITOR\n"))
        self.assertTrue(self.repo.read(f"workplans/{wid}/0001/BREAKDOWN.md").startswith("# Breakdown"))
        self.assertIn("0000  Task number 0\n0001  Say goodbye\n\n## Dropped",
                      self.repo.read(f"workplans/{wid}/WORKPLAN.md"))
        self.assertEqual(self.states(), {"0000": "refinement", "0001": "refinement"})

        self.repo.wp("add-task", "Another", "-m", "Append a second line.")
        task = self.repo.read(f"workplans/{wid}/0002/TASK.md")
        self.assertIn("\nAppend a second line.\n", task)
        self.assertIn("Depends on none.", task)

    def test_add_task_refusals(self):
        wid = planned(self.repo, tasks=1)
        result = self.repo.wp("add-task", "X", "--depend", "0007", "-m", "x", ok=False)
        self.assertIn("no such task", result.stderr)
        self.repo.git("switch", "-q", "master")
        self.repo.git("checkout", "-q", f"workplan/{wid}/definition", "--", "workplans")
        result = self.repo.wp("add-task", "X", "--workplan", wid, "-m", "x", ok=False)
        self.assertIn("editable only on", result.stderr)

    # the patch loop ------------------------------------------------------

    def test_full_cycle(self):
        wid = planned(self.repo)
        out = self.repo.wp("gen-patch", "0000", env=self.env).stdout
        self.assertIn("agent finished", out)
        self.assertEqual(self.states(), {"0000": "development"})
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/COMMIT_MSG"),
                         f"{wid}/0000 Say goodbye\n")
        self.assertEqual(self.repo.read("app.txt"), "hello\n")

        self.repo.wp("apply-patch", "0000")
        self.assertEqual(self.states(), {"0000": "testing"})
        self.repo.wp("reject-patch", "0000")
        self.assertEqual(self.states(), {"0000": "development"})
        self.repo.wp("accept-patch", "0000")
        self.assertEqual(self.states(), {"0000": "complete"})
        self.assertEqual(self.repo.read("app.txt"), "hello\ngoodbye\n")

        self.repo.wp("merge-workplan")
        self.assertEqual(self.states(), {"0000": "merged"})
        self.assertEqual(self.repo.git("branch", "--show-current"), "master")
        self.assertEqual(self.repo.git("log", "-1", "--format=%B").strip(), "\n".join([
            f"{wid} greeting", "",
            "app.txt says goodbye. Nothing else changes.", "",
            f"{wid}/0000 Say goodbye", "",
            f"Workplan: workplans/{wid}/WORKPLAN.md",
        ]))
        self.assertEqual(self.repo.git("tag", "--list"), "")

    def test_accept_carries_task_files_and_workplan(self):
        wid = planned(self.repo)
        self.repo.wp("gen-patch", "0000", env=self.env)
        notes = self.repo.write(f"workplans/{wid}/0000/NOTES.md", "# Notes\n\nQ and A.\n")
        plan = self.repo.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text().replace("## Context", "## Context\n\nMore context."))
        self.repo.wp("accept-patch", "0000")
        files = self.repo.git("show", "--name-only", "--format=", "HEAD").splitlines()
        self.assertEqual(sorted(files), sorted(
            ["app.txt", f"workplans/{wid}/0000/NOTES.md", f"workplans/{wid}/WORKPLAN.md"]))
        self.assertEqual(self.repo.git("status", "--porcelain"), "")
        self.assertTrue(notes.is_file())

    def test_gen_patch_sees_uncommitted_task_edits(self):
        wid = planned(self.repo)
        task = self.repo.path / "workplans" / wid / "0000" / "TASK.md"
        task.write_text(task.read_text() + "\nUNCOMMITTED EDIT\n")
        prompt = self.dir / "prompt.txt"
        agent = scripted_agent(self.dir, edit=f"cp workplans/{wid}/0000/TASK.md seen.txt")
        self.repo.wp("gen-patch", "0000", env={**agent_env(agent), "PROMPT_COPY": str(prompt)})
        self.assertIn(f"workplans/{wid}/0000/TASK.md", prompt.read_text())
        self.assertIn("+UNCOMMITTED EDIT", self.repo.read(f"workplans/{wid}/0000/output.patch"))

    def test_gen_patch_with_no_change_fails(self):
        planned(self.repo)
        agent = scripted_agent(self.dir, edit="true")
        result = self.repo.wp("gen-patch", "0000", env=agent_env(agent), ok=False)
        self.assertIn("no change", result.stderr)
        self.assertEqual(self.repo.git("worktree", "list").count("\n"), 0)

    def test_gen_patch_keeps_edits_under_workplans(self):
        wid = planned(self.repo)
        plan = f"workplans/{wid}/WORKPLAN.md"
        self.repo.write(plan, self.repo.read(plan) + "An uncommitted line.\n")
        agent = scripted_agent(self.dir, edit=(
            "printf 'goodbye\\n' >> app.txt; echo x >> workplans/PRINCIPLES.md"))
        self.repo.wp("gen-patch", "0000", env=agent_env(agent))
        patch = self.repo.read(f"workplans/{wid}/0000/output.patch")
        self.assertIn("app.txt", patch)
        self.assertIn("PRINCIPLES", patch)
        self.assertNotIn("WORKPLAN.md", patch)
        self.assertNotIn("COMMIT_MSG", patch)

    # states --------------------------------------------------------------

    def test_waiting_and_stale(self):
        wid = planned(self.repo, tasks=2)
        self.repo.write(f"workplans/{wid}/0001/output.patch",
                        "--- a/missing.txt\n+++ b/missing.txt\n@@ -1 +1 @@\n-a\n+b\n")
        self.assertEqual(self.states()["0001"], "waiting")
        self.repo.wp("gen-patch", "0000", env=self.env)
        self.repo.wp("accept-patch", "0000")
        self.assertEqual(self.states()["0001"], "stale")

    def test_dropped(self):
        wid = planned(self.repo, tasks=2)
        plan = self.repo.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text().replace("0001  Task number 1\n\n## Dropped\n",
                                                 "## Dropped\n\n0001  Task number 1\n"))
        self.assertEqual(self.states(), {"0000": "refinement", "0001": "dropped"})


if __name__ == "__main__":
    unittest.main()
