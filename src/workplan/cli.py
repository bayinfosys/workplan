"""The workplan command. Formats what the operations return."""

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys

from workplan import __version__, agent, config, git, ops, route
from workplan.git import Fail


def page(text: str) -> None:
    if not sys.stdout.isatty():
        sys.stdout.write(text)
        return
    pager = shlex.split(os.environ.get("PAGER", "less -R"))
    try:
        subprocess.run(pager, input=text, text=True)
    except FileNotFoundError:
        sys.stdout.write(text)


def print_status(data: dict) -> None:
    for task in data["tasks"]:
        detail = task["detail"] or task["title"]
        print(f"{task['id']:<28} {task['state']:<12} {detail}".rstrip())


def print_agent(result: dict) -> None:
    if result["report"]:
        print(result["report"])
        print()


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="workplan",
                                description="Plan and record development work in git.")
    p.add_argument("--version", action="version", version=f"workplan {__version__}")
    sub = p.add_subparsers(dest="command", required=True, metavar="command")

    sub.add_parser("init", help="create and commit workplans/")

    pl = sub.add_parser("plan", help="a workplan on a new branch")
    pl.add_argument("name")
    pl.add_argument("-m", "--goal", help="the goal; skips the editor")

    sub.add_parser("define-tasks", help="the agent writes the tasks; commits the plan") \
        .add_argument("id", nargs="?")

    for name, text in (
        ("produce-patch", "the agent writes output.patch and COMMIT_MSG"),
        ("apply", "stage the patch in the tree and the index"),
        ("diff", "the staged change if applied, else the patch"),
        ("accept", "commit the patch with the task's files"),
        ("reject", "take an applied, uncommitted patch back out"),
    ):
        sub.add_parser(name, help=text).add_argument("task", metavar="[ID/]NNNN")

    sub.add_parser("merge", help="squash the workplan into master") \
        .add_argument("id", nargs="?")

    st = sub.add_parser("status", help="where a workplan or a task stands")
    st.add_argument("id", nargs="?")
    st.add_argument("--json", action="store_true")

    rt = sub.add_parser("route", help="the next step after a commit")
    rt.add_argument("rev", nargs="?", default="HEAD")
    rt.add_argument("--dispatch", action="store_true",
                    help="record the decision and run route.dispatch")

    sub.add_parser("install", help="hooks that run route after each commit")
    return p


def run(args: argparse.Namespace) -> None:
    os.chdir(git.toplevel())
    cfg = config.load()
    master = cfg["master"]

    match args.command:
        case "init":
            for line in ops.init():
                print(line)
        case "plan":
            result = ops.plan(args.name, master, goal=args.goal)
            print(f"switched to {result['branch']}\ncreated {result['created']}")
        case "define-tasks":
            result = agent.define_tasks(args.id, cfg)
            print_agent(result)
            for tid in result["tasks"]:
                print(f"defined {tid}")
            print(f"committed {result['commit']}")
        case "produce-patch":
            result = agent.produce_patch(args.task, cfg)
            print_agent(result)
            print(f"{result['patch']}: against {result['base']}, by {result['agent']}")
            print(f"COMMIT_MSG: {result['commit_msg']}")
            if result["note"]:
                print(f"note: {result['note']}")
        case "apply":
            print(ops.apply(args.task))
        case "diff":
            page(ops.diff(args.task))
        case "accept":
            print(ops.accept(args.task, master))
        case "reject":
            print(ops.reject(args.task))
        case "merge":
            result = ops.merge(args.id, master)
            print(result["commit"])
            print("\nnext:")
            for line in result["next"]:
                print(f"  {line}")
        case "status":
            data = ops.status(args.id, master)
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                print_status(data)
        case "route":
            decision = route.decide(args.rev, cfg)
            print(f"route: {decision['source']} chose {decision['action']}; "
                  f"the rules chose {decision['rule']}", file=sys.stderr)
            if args.dispatch:
                route.dispatch(decision, cfg)
            print(" ".join([decision["action"], *decision["targets"]]))
        case "install":
            for line in ops.install():
                print(line)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
        run(args)
    except Fail as e:
        print(f"workplan: {e}", file=sys.stderr)
        return 1
    return 0
