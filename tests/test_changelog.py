"""wp changelog: the squash commits between two tags, and their tasks' trailers."""

import json
import unittest

from support import Repo


def task(title: str, trailers: str) -> str:
    return f"# {title}\n\nThe change.\n\nEffects:\n\n- it holds\n\n{trailers}"


class Changelog(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.repo.write("app.txt", "hello\n")
        self.repo.commit_all("app")
        self.repo.git("tag", "v1")
        self.merge("2026-01-01-a", "first", {
            "0000": task("Add a greeting", "Depends: none\nChange: feat\nAudience: users\n"
                                           "Breaking: hello is now hi\n"),
            "0001": task("Fix the greeting", "Depends: 0000\nChange: fix\nAudience: developers\n"),
            "0002": task("An older task", "Depends on none.\n"),
            "0003": task("A dropped task", "Depends: none\nChange: feat\n"),
        }, dropped=["0003"])
        self.repo.write("notes.txt", "notes\n")
        self.repo.commit_all("notes without a workplan")
        self.merge("2026-01-02-b", "second", {
            "0000": task("Tidy the code", "Depends: none\nChange: refactor\nAudience: internal\n"),
        })
        self.repo.git("tag", "v2")
        self.merge("2026-01-03-c", "third", {
            "0000": task("A chore", "Depends: none\nChange: chore\n"),
        })

    def tearDown(self):
        self.repo.cleanup()

    def merge(self, wid: str, title: str, tasks: dict, dropped: tuple = ()):
        listed = "\n".join(f"{n}  {task_text.splitlines()[0][2:]}"
                           for n, task_text in tasks.items() if n not in dropped)
        gone = "\n".join(f"{n}  {tasks[n].splitlines()[0][2:]}" for n in dropped)
        self.repo.write(f"workplans/{wid}/WORKPLAN.md",
                        f"# Workplan {wid}: {title}\n\n## Goal\n\nA goal.\n\n## Tasks\n\n"
                        f"{listed}\n\n## Dropped\n\n{gone}\n")
        for n, text in tasks.items():
            self.repo.write(f"workplans/{wid}/{n}/TASK.md", text)
        self.repo.commit_all(f"{wid} {title}\n\nA goal.\n\nWorkplan: workplans/{wid}/WORKPLAN.md")

    def log(self, *args: str) -> dict:
        return json.loads(self.repo.wp("changelog", *args, "--json").stdout)

    def test_between_two_tags(self):
        log = self.log("v1", "v2")
        self.assertEqual(log["heading"], "v2")
        self.assertEqual([w["id"] for w in log["workplans"]], ["2026-01-01-a", "2026-01-02-b"])
        sections = {e["task"]: e["section"] for e in log["entries"]}
        self.assertEqual(sections, {"2026-01-01-a/0000": "Added", "2026-01-01-a/0001": "Fixed",
                                    "2026-01-01-a/0002": "Other", "2026-01-02-b/0000": "Changed"})
        text = self.repo.wp("changelog", "v1", "v2").stdout
        self.assertTrue(text.startswith("## v2 ("))
        self.assertLess(text.index("### Breaking"), text.index("### Added"))
        self.assertIn("- hello is now hi (first, 2026-01-01-a/0000)", text)
        self.assertIn("### Fixed\n\n- Fix the greeting (first, 2026-01-01-a/0001)", text)
        self.assertIn("### Other\n\n- An older task (first, 2026-01-01-a/0002)", text)
        self.assertNotIn("dropped", text)
        self.assertNotIn("A chore", text)

    def test_the_defaults(self):
        log = self.log()
        self.assertEqual((log["heading"], log["from"]), ("Unreleased", "v2"))
        self.assertEqual([e["task"] for e in log["entries"]], ["2026-01-03-c/0000"])
        code = ("import json; from workplan import ops; "
                "print(json.dumps(ops.changelog(None, 'v2')))")
        log = json.loads(self.repo.py(code).stdout)
        self.assertEqual((log["heading"], log["from"]), ("v2", "v1"))

    def test_audience(self):
        tasks = [e["task"] for e in self.log("v1", "v2", "--audience", "developers")["entries"]]
        self.assertEqual(tasks, ["2026-01-01-a/0001", "2026-01-01-a/0002"])

    def test_its_route(self):
        code = ("from workplan.commands import registry; c = registry.get('changelog'); "
                "print(c.method, c.route, [p.name for p in c.parameters])")
        self.assertEqual(self.repo.py(code).stdout.strip(),
                         "GET /api/changelog ['start', 'end', 'audience']")

    def test_nothing_is_written(self):
        before = (self.repo.git("for-each-ref"), self.repo.git("rev-parse", "HEAD"),
                  self.repo.git("status", "--porcelain"))
        self.repo.wp("changelog", "v1")
        self.assertEqual(before, (self.repo.git("for-each-ref"), self.repo.git("rev-parse", "HEAD"),
                                  self.repo.git("status", "--porcelain")))


if __name__ == "__main__":
    unittest.main()
