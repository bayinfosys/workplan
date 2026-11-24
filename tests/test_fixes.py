"""Guards on accept and merge, the routing rules, and the hooks."""

import tempfile
import unittest
from pathlib import Path

from support import Repo, agent_env, planned, scripted_agent


class Guards(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.tmp = tempfile.TemporaryDirectory()
        self.env = agent_env(scripted_agent(Path(self.tmp.name)))

    def tearDown(self):
        self.repo.cleanup()
        self.tmp.cleanup()

    def ready(self, tasks: int = 1) -> str:
        wid = planned(self.repo, tasks=tasks)
        self.repo.wp("gen-patch", "0000", env=self.env)
        self.repo.wp("accept-patch", "0000")
        return wid

    def test_accept_refuses_on_master(self):
        wid = planned(self.repo)
        self.repo.wp("gen-patch", "0000", env=self.env)
        self.repo.git("switch", "-q", "master")
        self.repo.git("checkout", "-q", f"workplan/{wid}/definition", "--", "workplans")
        result = self.repo.wp("accept-patch", f"{wid}/0000", ok=False)
        self.assertIn("HEAD is master", result.stderr)
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), "workplan init")

    def test_merge_refuses_when_branch_lacks_master(self):
        wid = self.ready()
        self.repo.git("switch", "-q", "master")
        self.repo.write("app.txt", "conflict\n")
        self.repo.commit_all("master moved")
        self.repo.git("switch", "-q", f"workplan/{wid}/definition")

        result = self.repo.wp("merge-workplan", ok=False)
        self.assertIn("rebase", result.stderr)
        self.assertEqual(self.repo.git("branch", "--show-current"), f"workplan/{wid}/definition")
        self.assertEqual(self.repo.git("status", "--porcelain"), "")

    def test_merge_restores_when_the_editor_aborts(self):
        wid = self.ready()
        before = self.repo.git("rev-parse", "master")
        result = self.repo.wp("merge-workplan", ok=False, env={"GIT_EDITOR": "sh -c ': > \"$1\"' x"})
        self.assertIn("failed", result.stderr)
        self.assertEqual(self.repo.git("rev-parse", "master"), before)
        self.assertEqual(self.repo.git("branch", "--show-current"), f"workplan/{wid}/definition")
        self.assertEqual(self.repo.git("status", "--porcelain"), "")

    def test_merge_refuses_open_tasks(self):
        wid = self.ready(tasks=2)
        result = self.repo.wp("merge-workplan", ok=False)
        self.assertIn(f"{wid}/0001", result.stderr)

    def test_merge_allows_dropped_tasks(self):
        wid = planned(self.repo, tasks=2)
        plan = self.repo.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text().replace(
            "0001  Task number 1\n\n## Dropped\n", "## Dropped\n\n0001  Task number 1\n"))
        self.repo.wp("gen-patch", "0000", env=self.env)
        self.repo.wp("accept-patch", "0000")
        self.repo.wp("merge-workplan")
        self.assertEqual(self.repo.git("branch", "--show-current"), "master")
        self.assertNotIn(f"{wid}/0001", self.repo.git("log", "-1", "--format=%B"))

    def test_merge_uses_the_project_template(self):
        wid = self.ready()
        self.repo.write("workplans/templates/documents/SQUASH_COMMIT_MSG",
                        "$id: $title\n\n$tasks\n\nWorkplan: $path\n")
        self.repo.commit_all("project template")
        self.repo.wp("merge-workplan")
        self.assertTrue(self.repo.git("log", "-1", "--format=%B").startswith(f"{wid}: greeting\n"))

    def test_save_document(self):
        wid = planned(self.repo)
        save = f"from workplan import ops; ops.save_document('{wid}', %r, 'text')"
        self.repo.py(save % "0000/NOTES.md")
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/NOTES.md"), "text\n")
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), f"{wid} define tasks")
        for name in ("0000/output.patch", "../config.toml", "0009/TASK.md", "app.txt"):
            self.repo.py(save % name, ok=False)
        self.repo.git("add", "-A")
        self.repo.git("commit", "-q", "-m", "notes")
        self.repo.git("switch", "-q", "master")
        self.repo.git("checkout", "-q", f"workplan/{wid}/definition", "--", "workplans")
        result = self.repo.py(save % "0000/TASK.md", ok=False)
        self.assertIn("editable only on", result.stderr)

    def test_merge_with_a_message(self):
        wid = self.ready()
        preview = self.repo.py(
            "from workplan import ops; print(ops.merge_message(None, 'master'), end='')").stdout
        self.assertTrue(preview.startswith(f"{wid} greeting\n"))
        self.repo.py("from workplan import ops; "
                     "ops.merge(None, 'master', message='Short message\\n\\nBody\\n')",
                     )
        self.assertEqual(self.repo.git("log", "-1", "--format=%B").strip(), "Short message\n\nBody")

    def test_install_writes_and_respects_hooks(self):
        hooks = self.repo.path / ".git" / "hooks"
        hooks.mkdir(exist_ok=True)
        (hooks / "post-merge").write_text("#!/bin/sh\necho mine\n")
        out = self.repo.wp("install").stdout
        self.assertIn("wrote", out)
        self.assertIn("skipped", out)
        self.assertIn("workplan route", (hooks / "post-commit").read_text())
        self.assertEqual((hooks / "post-merge").read_text(), "#!/bin/sh\necho mine\n")


class Routing(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.tmp = tempfile.TemporaryDirectory()
        self.env = agent_env(scripted_agent(Path(self.tmp.name)))

    def tearDown(self):
        self.repo.cleanup()
        self.tmp.cleanup()

    def route(self) -> str:
        return self.repo.wp("route").stdout.strip()

    def test_rules(self):
        wid = planned(self.repo)
        self.assertEqual(self.route(), f"gen-patch {wid}/0000")

        self.repo.wp("gen-patch", "0000", env=self.env)
        self.repo.wp("accept-patch", "0000")
        self.assertEqual(self.route(), f"review {wid}/0000")

        plan = self.repo.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text() + "\nmore\n")
        self.repo.commit_all("edit the plan")
        self.assertEqual(self.route(), f"gen-task {wid}")

        self.repo.write("README", "x\n")
        self.repo.commit_all("unrelated")
        self.assertEqual(self.route(), "none")

        self.repo.wp("merge-workplan")
        self.assertEqual(self.route(), f"complete {wid}")

    def test_paths_with_spaces(self):
        wid = planned(self.repo)
        self.repo.write(f"workplans/{wid}/0000/BREAKDOWN.md", "# Breakdown\n\n1. step\n")
        self.repo.write("a file with spaces.txt", "x\n")
        self.repo.commit_all("edit")
        self.assertEqual(self.route(), f"gen-patch {wid}/0000")

    def test_dispatch(self):
        wid = planned(self.repo)
        log = Path(self.tmp.name) / "dispatched"
        self.repo.wp("route", "--dispatch",
                     env={"WORKPLAN_ROUTE_DISPATCH": f"sh -c 'echo \"$@\" > {log}' x"})
        self.assertEqual(log.read_text().strip(), f"gen-patch {wid}/0000")
        self.assertFalse((self.repo.path / ".git" / "workplan" / "route.log").exists())

if __name__ == "__main__":
    unittest.main()
