"""The registry, in-process, with a few test commands."""

import contextlib
import io
import sys
import unittest
from typing import Annotated

from support import SRC

sys.path.insert(0, str(SRC))

from workplan.git import Fail  # noqa: E402
from workplan.registry import Flag, Positional, Registry  # noqa: E402


def make() -> Registry:
    registry = Registry("wp", version="9", top=("workplan",))

    @registry.command(help="a workplan")
    def cmd_new_workplan(ctx, *, name: Annotated[str, Positional("NAME")]):
        return {"name": name}

    @registry.command(help="tasks", aliases=("status",), render=lambda r: "\n".join(r["tasks"]))
    def cmd_list_task(ctx, *, workplan: Annotated[str, Positional("ID", optional=True)]):
        return {"workplan": workplan, "tasks": ["a", "b"], "ctx": ctx}

    @registry.command(help="add")
    def cmd_add_task(ctx, *, title: Annotated[str, Positional("TITLE", many=True)],
                     workplan: Annotated[str, Flag("the workplan")] = "",
                     depend: Annotated[list[str], Flag("a task")] = None,
                     text: Annotated[str, Flag("the change", short="-m")] = None):
        return {"title": title, "workplan": workplan, "depend": depend, "text": text}

    @registry.command(help="accept")
    def cmd_accept_patch(ctx, *, task: Annotated[str, Positional("[ID/]NNNN")]):
        return {"task": task}

    @registry.command(help="edit", route="/api/task/{task}/{doc}", method="PUT")
    def cmd_edit_task(ctx, *, task: Annotated[str, Positional()],
                      doc: Annotated[str, Flag()] = "TASK.md",
                      text: Annotated[str, Flag()] = None):
        return {"task": task, "doc": doc, "text": text}

    @registry.command(help="hooks", cli_only=True)
    def cmd_install(ctx, *, force: Annotated[bool, Flag("overwrite")] = False):
        return {"force": force}

    return registry


class CLI(unittest.TestCase):
    def setUp(self):
        self.registry = make()

    def test_names_and_alias(self):
        names = [c.name for c in self.registry.commands]
        self.assertEqual(names, ["new", "task list", "task add", "patch accept", "task edit",
                                 "install"])
        self.assertEqual([c.words for c in self.registry.commands][:3],
                         [("new",), ("task", "list"), ("task", "add")])
        self.assertEqual(self.registry.run_cli(["status"], lambda: "ctx")[1], "a\nb")
        self.assertEqual(self.registry.run_cli(["task", "list", "w1"], lambda: "ctx")[1], "a\nb")
        self.assertIn('"name": "x"', self.registry.run_cli(["new", "x"], lambda: None)[1])
        self.assertEqual(self.registry.get("patch accept").words, ("patch", "accept"))
        self.assertEqual(self.registry.get("status").name, "task list")

    def test_old_names_and_a_noun_alone_fail(self):
        for argv in (["list-task"], ["accept-patch", "0000"], ["new-workplan", "x"], ["task"],
                     ["patch"], ["task", "accept"]):
            with self.assertRaises(SystemExit):
                self.registry.run_cli(argv, lambda: None)

    def test_group_help_lists_its_verbs(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            self.registry.run_cli(["task", "--help"], lambda: None)
        help = out.getvalue()
        for verb in ("list", "add", "edit"):
            self.assertIn(verb, help)
        self.assertNotIn("accept", help)

    def test_values(self):
        _, out = self.registry.run_cli(
            ["task", "add", "Say", "goodbye", "--depend", "0000", "--depend", "0001", "-m", "x"],
            lambda: None)
        self.assertIn('"title": "Say goodbye"', out)
        self.assertIn('"0001"', out)
        self.assertIn('"force": true', self.registry.run_cli(["install", "--force"], lambda: None)[1])
        self.assertIn('"force": false', self.registry.run_cli(["install"], lambda: None)[1])

    def test_json_flag(self):
        _, out = self.registry.run_cli(["status", "--json"], lambda: None)
        self.assertIn('"tasks": [', out)

    def test_missing_positional(self):
        with self.assertRaises(SystemExit):
            self.registry.run_cli(["patch", "accept"], lambda: None)


class HTTP(unittest.TestCase):
    def setUp(self):
        self.registry = make()

    def test_routes(self):
        routes = {c.name: (c.method, c.route) for c in self.registry.commands if not c.cli_only}
        self.assertEqual(routes, {
            "new": ("POST", "/api/workplan"),
            "task list": ("GET", "/api/workplan/{workplan}/task"),
            "task add": ("POST", "/api/workplan/{workplan}/task"),
            "patch accept": ("POST", "/api/task/{task}/patch/accept"),
            "task edit": ("PUT", "/api/task/{task}/{doc}"),
        })

    def test_match_and_call(self):
        command, path = self.registry.match("POST", "/api/task/2026-01-01-x/0003/patch/accept")
        self.assertEqual(command.name, "patch accept")
        self.assertEqual(path, {"task": "2026-01-01-x/0003"})
        self.assertEqual(self.registry.call(command, None, path), {"task": "2026-01-01-x/0003"})

        command, path = self.registry.match("POST", "/api/workplan/w1/task")
        values = self.registry.values(command, path, {}, {"title": "T", "depend": ["0000"]})
        self.assertEqual(self.registry.call(command, None, values),
                         {"title": "T", "workplan": "w1", "depend": ["0000"], "text": None})

        command, path = self.registry.match("PUT", "/api/task/w1/0000/NOTES.md")
        values = self.registry.values(command, path, {}, {"text": "hello"})
        self.assertEqual(self.registry.call(command, None, values),
                         {"task": "w1/0000", "doc": "NOTES.md", "text": "hello"})

        command, path = self.registry.match("GET", "/api/workplan/w1/task")
        self.assertEqual(self.registry.call(command, "c", path)["workplan"], "w1")

    def test_misses(self):
        with self.assertRaises(LookupError):
            self.registry.match("GET", "/api/nothing")
        with self.assertRaises(PermissionError):
            self.registry.match("DELETE", "/api/workplan/w1/task")
        command, _ = self.registry.match("POST", "/api/workplan/w1/task")
        with self.assertRaises(Fail):
            self.registry.call(command, None, {})

    def test_routes_need_a_noun_or_a_route(self):
        registry = Registry("wp")
        with self.assertRaises(ValueError):
            @registry.command()
            def cmd_frobnicate(ctx):
                return None


if __name__ == "__main__":
    unittest.main()
