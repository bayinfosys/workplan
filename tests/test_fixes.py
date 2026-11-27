"""Guards on accept and merge, the routing rules, and the hooks."""

import os
import sys
import tempfile
import time
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
        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.wp("patch", "accept", "0000")
        return wid

    def test_accept_refuses_on_master(self):
        wid = planned(self.repo)
        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.git("switch", "-q", "master")
        self.repo.git("checkout", "-q", f"workplan/{wid}/definition", "--", "workplans")
        result = self.repo.wp("patch", "accept", f"{wid}/0000", ok=False)
        self.assertIn("HEAD is master", result.stderr)
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), "workplan init")

    def test_accept_refuses_an_unlisted_task(self):
        wid = planned(self.repo)
        task = f"workplans/{wid}/0003"
        self.repo.write(f"{task}/TASK.md", "# A task written by hand\n")
        self.repo.write(f"{task}/output.patch", "--- a/app.txt\n+++ b/app.txt\n"
                        "@@ -1 +1,2 @@\n hello\n+goodbye\n")
        self.repo.write(f"{task}/COMMIT_MSG", f"{wid}/0003 By hand\n")
        head = self.repo.git("rev-parse", "HEAD")
        result = self.repo.wp("patch", "accept", "0003", ok=False)
        self.assertIn(f"{wid}/0003 is not listed in WORKPLAN.md", result.stderr)
        self.assertEqual(self.repo.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.repo.read("app.txt"), "hello\n")

        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.wp("task", "drop", "0000")
        result = self.repo.wp("patch", "accept", "0000", ok=False)
        self.assertIn(f"{wid}/0000 is not listed in WORKPLAN.md", result.stderr)

    def test_merge_message_carries_breaking_changes(self):
        wid = self.ready()
        self.assertNotIn("BREAKING-CHANGE", self.repo.wp("merge", "--show").stdout)
        task = f"workplans/{wid}/0000/TASK.md"
        self.repo.write(task, self.repo.read(task) + "\nDepends: none\nBreaking: app.txt grows\n")
        self.repo.commit_all("breaking")
        message = self.repo.wp("merge", "--show").stdout
        self.assertIn("\nBREAKING-CHANGE: app.txt grows\nWorkplan: ", message)
        self.repo.wp("merge")
        self.assertEqual(self.repo.git("log", "-1",
                                       "--format=%(trailers:key=BREAKING-CHANGE,valueonly)"),
                         "app.txt grows")

    def test_merge_runs_the_test_command(self):
        wid = self.ready()
        result = self.repo.wp("merge", env={"WORKPLAN_TEST_COMMAND": "grep -q goodbye app.txt"})
        self.assertIn("running test.command: grep -q goodbye app.txt", result.stderr)
        self.assertIn("test.command passed: grep -q goodbye app.txt", result.stdout)
        self.assertEqual(self.repo.git("branch", "--show-current"), "master")
        self.assertIn(f"{wid} ", self.repo.git("log", "-1", "--format=%s"))

    def test_merge_refused_before_the_tests_says_nothing_of_them(self):
        self.ready(tasks=2)
        result = self.repo.wp("merge", ok=False, env={"WORKPLAN_TEST_COMMAND": "true"})
        self.assertNotIn("running test.command", result.stderr)

    def test_merge_stops_when_the_test_command_fails(self):
        wid = self.ready()
        head = self.repo.git("rev-parse", "master")
        result = self.repo.wp("merge", ok=False,
                              env={"WORKPLAN_TEST_COMMAND": "echo three failed; exit 3"})
        self.assertIn("test.command failed (exit 3)", result.stderr)
        self.assertIn("three failed", result.stderr)
        self.assertEqual(self.repo.git("branch", "--show-current"), f"workplan/{wid}/definition")
        self.assertEqual(self.repo.git("rev-parse", "master"), head)

    def test_merge_runs_the_test_command_on_the_branch_alone(self):
        wid = self.ready()
        self.repo.git("switch", "-q", "master")
        result = self.repo.wp("merge", wid, ok=False, env={"WORKPLAN_TEST_COMMAND": "true"})
        self.assertIn(f"switch to workplan/{wid}/definition to run test.command", result.stderr)
        self.assertNotIn("running test.command", result.stderr)
        out = self.repo.wp("merge", wid, env={"WORKPLAN_TEST_COMMAND": ""}).stdout
        self.assertNotIn("test.command", out)

    def test_merge_refuses_when_branch_lacks_master(self):
        wid = self.ready()
        self.repo.git("switch", "-q", "master")
        self.repo.write("app.txt", "conflict\n")
        self.repo.commit_all("master moved")
        self.repo.git("switch", "-q", f"workplan/{wid}/definition")

        result = self.repo.wp("merge", ok=False)
        self.assertIn("rebase", result.stderr)
        self.assertEqual(self.repo.git("branch", "--show-current"), f"workplan/{wid}/definition")
        self.assertEqual(self.repo.git("status", "--porcelain"), "")

    def test_merge_restores_when_the_editor_aborts(self):
        wid = self.ready()
        before = self.repo.git("rev-parse", "master")
        result = self.repo.wp("merge", ok=False, env={"GIT_EDITOR": "sh -c ': > \"$1\"' x"})
        self.assertIn("failed", result.stderr)
        self.assertEqual(self.repo.git("rev-parse", "master"), before)
        self.assertEqual(self.repo.git("branch", "--show-current"), f"workplan/{wid}/definition")
        self.assertEqual(self.repo.git("status", "--porcelain"), "")

    def test_merge_refuses_open_tasks(self):
        wid = self.ready(tasks=2)
        result = self.repo.wp("merge", ok=False)
        self.assertIn(f"{wid}/0001", result.stderr)

    def test_merge_allows_dropped_tasks(self):
        wid = planned(self.repo, tasks=2)
        plan = self.repo.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text().replace(
            "0001  Task number 1\n\n## Dropped\n", "## Dropped\n\n0001  Task number 1\n"))
        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.wp("patch", "accept", "0000")
        self.repo.wp("merge")
        self.assertEqual(self.repo.git("branch", "--show-current"), "master")
        self.assertEqual(self.repo.git("branch", "--list", f"workplan/{wid}/*"), "")
        self.assertNotIn(f"{wid}/0001", self.repo.git("log", "-1", "--format=%B"))

    def test_plan_draft_stays_out_of_the_git_directory(self):
        self.repo.wp("init")
        self.repo.wp("new", "drafted",
                     env={"GIT_EDITOR": "sh -c 'echo A goal. >> \"$1\"' x"})
        self.assertFalse((self.repo.path / ".git" / "workplan").exists())

    def test_merge_draft_stays_out_of_the_git_directory(self):
        self.ready()
        self.repo.wp("merge")
        self.assertFalse((self.repo.path / ".git" / "workplan").exists())

    def test_merge_uses_the_project_template(self):
        wid = self.ready()
        self.repo.write("workplans/templates/documents/SQUASH_COMMIT_MSG",
                        "$id: $title\n\n$tasks\n\nWorkplan: $path\n")
        self.repo.commit_all("project template")
        self.repo.wp("merge")
        self.assertTrue(self.repo.git("log", "-1", "--format=%B").startswith(f"{wid}: greeting\n"))

    def test_save_document(self):
        wid = planned(self.repo)
        save = f"from workplan import ops; ops.save_document('{wid}', %r, 'text')"
        self.repo.py(save % "0000/NOTES.md")
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/NOTES.md"), "text\n")
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), f"{wid} edit 0000/NOTES.md")
        self.repo.py(save % "0000/NOTES.md")
        self.assertEqual(self.repo.git("log", "-1", "--format=%s"), f"{wid} edit 0000/NOTES.md")
        self.assertEqual(self.repo.git("rev-list", "--count", "--grep=edit 0000", "HEAD"), "1")
        for name in ("0000/output.patch", "../config.toml", "0009/TASK.md", "app.txt"):
            self.repo.py(save % name, ok=False)
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

    def test_init_writes_the_parent_branch(self):
        self.repo.git("branch", "-q", "-m", "main")
        self.repo.wp("init")
        self.assertIn('parent = "main"', self.repo.read("workplans/config.toml"))
        self.repo.wp("new", "greeting", "-m", "A goal.")
        self.assertEqual(self.repo.git("merge-base", "HEAD", "main"),
                         self.repo.git("rev-parse", "main"))
        self.repo.git("switch", "-q", "main")
        result = self.repo.wp("new", "parting", "-m", "A goal.", ok=False,
                              env={"WORKPLAN_PARENT": "trunk"})
        self.assertIn("no branch trunk", result.stderr)

    def test_init_writes_an_executable_dispatch_script(self):
        self.repo.wp("init")
        script = self.repo.path / "workplans" / "dispatch.sh"
        self.assertTrue(os.access(script, os.X_OK))
        self.assertTrue((self.repo.path / "workplans" / "BACKLOG.md").is_file())

    def test_install_writes_and_respects_hooks(self):
        hooks = self.repo.path / ".git" / "hooks"
        hooks.mkdir(exist_ok=True)
        (hooks / "post-merge").write_text("#!/bin/sh\necho mine\n")
        out = self.repo.wp("install").stdout
        self.assertIn("wrote", out)
        self.assertIn("skipped", out)
        self.assertIn("workplan route", (hooks / "post-commit").read_text())
        self.assertEqual((hooks / "post-merge").read_text(), "#!/bin/sh\necho mine\n")

    def test_hook_clears_git_variables(self):
        wid = planned(self.repo)
        self.repo.wp("install")
        bin_dir = Path(self.tmp.name) / "bin"
        bin_dir.mkdir()
        shim = bin_dir / "workplan"
        shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" -m workplan "$@"\n')
        shim.chmod(0o755)
        log = Path(self.tmp.name) / "dispatched"
        self.repo.sh(".git/hooks/post-commit", env={
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "GIT_INDEX_FILE": str(Path(self.tmp.name) / "elsewhere"),
            "WORKPLAN_ROUTE_DISPATCH":
                f"sh -c 'echo \"[$GIT_INDEX_FILE] $*\" > {log}' x",
        })
        for _ in range(100):
            if log.exists() and log.read_text().endswith("\n"):
                break
            time.sleep(0.1)
        self.assertEqual(log.read_text().strip(), f"[] patch-gen {wid}/0000")


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
        self.assertEqual(self.route(), f"patch-gen {wid}/0000")

        self.repo.wp("patch", "gen", "0000", env=self.env)
        self.repo.wp("patch", "accept", "0000")
        self.assertEqual(self.route(), f"review {wid}/0000")

        plan = self.repo.path / "workplans" / wid / "WORKPLAN.md"
        plan.write_text(plan.read_text() + "\nmore\n")
        self.repo.commit_all("edit the plan")
        self.assertEqual(self.route(), f"task-gen {wid}")

        self.repo.write("README", "x\n")
        self.repo.commit_all("unrelated")
        self.assertEqual(self.route(), "none")

        self.repo.wp("merge")
        self.assertEqual(self.route(), f"complete {wid}")

    def test_paths_with_spaces(self):
        wid = planned(self.repo)
        self.repo.write(f"workplans/{wid}/0000/BREAKDOWN.md", "# Breakdown\n\n1. step\n")
        self.repo.write("a file with spaces.txt", "x\n")
        self.repo.commit_all("edit")
        self.assertEqual(self.route(), f"patch-gen {wid}/0000")

    def test_dispatch(self):
        wid = planned(self.repo)
        log = Path(self.tmp.name) / "dispatched"
        self.repo.wp("route", "--dispatch",
                     env={"WORKPLAN_ROUTE_DISPATCH": f"sh -c 'echo \"$@\" > {log}' x"})
        self.assertEqual(log.read_text().strip(), f"patch-gen {wid}/0000")
        self.assertFalse((self.repo.path / ".git" / "workplan" / "route.log").exists())

if __name__ == "__main__":
    unittest.main()
