"""The workplan commands, declared once for the CLI and for HTTP.

Commands are verb-noun over three nouns, workplan, task and patch; see
registry.py for how a declaration gives a CLI subcommand and an HTTP
route. Each command returns data; its renderer gives the CLI's text.
"""

import os
import sys
from dataclasses import dataclass
from typing import Annotated

from workplan import __version__, agent, config, git, ops, plans, route, serve
from workplan.git import Fail
from workplan.registry import Flag, Positional, Registry

registry = Registry("workplan", "Plan and record development work in git.", __version__)

WORKPLAN = Annotated[str, Positional("ID", "the workplan; the current one when left out",
                                     optional=True)]
TASK = Annotated[str, Positional("[ID/]NNNN", "the task")]
DOCS = ("TASK.md", "BREAKDOWN.md", "NOTES.md")


@dataclass
class Context:
    cfg: dict
    master: str
    interactive: bool


def cli_context() -> Context:
    """The context of a CLI run: the repository's root, its config."""
    os.chdir(git.toplevel())
    cfg = config.load()
    return Context(cfg, cfg["master"], interactive=True)


def http_context() -> Context:
    """The context of an HTTP request: the config as it is now."""
    cfg = config.load()
    return Context(cfg, cfg["master"], interactive=False)


def read_reply(ctx: Context, reply: str | None) -> str:
    """A pasted reply: on the CLI, the file named, or standard input when
    none is; over HTTP, the text itself. A request never names a file."""
    if not ctx.interactive:
        if not reply:
            raise Fail("the reply is empty")
        return reply
    if reply and reply != "-":
        try:
            return open(reply).read()
        except OSError as e:
            raise Fail(f"{reply}: {e.strerror}") from e
    return sys.stdin.read()


# ---------------------------------------------------------------------------
# rendering

def lines(items: list[str]) -> str:
    return "\n".join(items)


def task_table(data: dict) -> str:
    return lines(f"{t['id']:<28} {t['state']:<12} {t['detail'] or t['title']}".rstrip()
                 for t in data["tasks"])


def agent_report(result: dict) -> list[str]:
    return [result["report"], ""] if result.get("report") else []


def render_workplans(rows: list[dict]) -> str:
    return lines(f"{r['id']:<36} {'editable' if r['editable'] else 'read-only':<10} "
                 f"{r['source']}" for r in rows)


def render_workplan(data: dict) -> str:
    where = data["source"] + ("" if data["editable"] else ", read-only")
    head = [data["title"] or data["workplan"], f"{data['branch']} ({where})", ""]
    if data["goal"]:
        head += [data["goal"], ""]
    return lines(head) + "\n" + task_table(data)


def render_task(data: dict) -> str:
    head = f"{data['id']}  {data['state']}  {data['detail']}".rstrip()
    return head + "\n\n" + data["documents"]["TASK.md"].rstrip()


def render_gen_task(result: dict) -> str:
    return lines(agent_report(result) + [f"defined {tid}" for tid in result["tasks"]]
                 + [f"committed {result['commit']}"])


def render_gen_patch(result: dict) -> str:
    out = agent_report(result) + [
        f"{result['patch']}: against {result['base']}, by {result['agent']}",
        f"COMMIT_MSG: {result['commit_msg']}",
    ]
    if result["note"]:
        out.append(f"note: {result['note']}")
    return lines(out)


def render_merge(result: dict) -> str:
    if "message" in result:
        return result["message"].rstrip()
    return lines([result["commit"], "", "next:"] + [f"  {n}" for n in result["next"]])


# ---------------------------------------------------------------------------
# workplan

@registry.command(help="create workplans/ in this repository, and commit it",
                  render=lines, cli_only=True)
def cmd_init(ctx):
    return ops.init()


@registry.command(help="every workplan, in the tree or on a branch", render=render_workplans)
def cmd_list_workplan(ctx):
    return ops.workplans()


@registry.command(help="a workplan: its goal, its tasks and WORKPLAN.md", render=render_workplan)
def cmd_show_workplan(ctx, *, workplan: WORKPLAN = None):
    data = ops.status(workplan, ctx.master)
    data["text"] = ops.document(data["workplan"], "WORKPLAN.md")["text"]
    return data


@registry.command(help="a workplan on a new branch; the editor opens on WORKPLAN.md",
                  render=lambda r: f"switched to {r['branch']}\ncreated {r['created']}")
def cmd_add_workplan(ctx, *, name: Annotated[str, Positional("NAME", "lower-case words joined by -")],
                     goal: Annotated[str, Flag("the goal; skips the editor", short="-m")] = None):
    if not goal and not ctx.interactive:
        raise Fail("a new workplan needs a goal")
    return ops.plan(name, ctx.master, goal=goal)


@registry.command(help="edit WORKPLAN.md: the editor, or the text given",
                  render=lambda r: f"saved {r['saved']}")
def cmd_edit_workplan(ctx, *, workplan: WORKPLAN = None,
                      text: Annotated[str, Flag("the new text; skips the editor")] = None):
    wid = plans.workplan_id(workplan)
    if text is None:
        if not ctx.interactive:
            raise Fail("edit-workplan needs the text")
        return ops.edit_document(wid, "WORKPLAN.md")
    return ops.save_document(wid, "WORKPLAN.md", text)


@registry.command(help="squash the workplan into master; the editor opens on the message",
                  render=render_merge)
def cmd_merge_workplan(ctx, *, workplan: WORKPLAN = None,
                       message: Annotated[str, Flag("the message; skips the editor",
                                                    short="-m")] = None,
                       show: Annotated[bool, Flag("print the message; merge nothing")] = False):
    if show:
        return {"message": ops.merge_message(workplan, ctx.master)}
    return ops.merge(workplan, ctx.master, edit=ctx.interactive, message=message)


# ---------------------------------------------------------------------------
# task

@registry.command(help="each task's state", aliases=("status",), render=task_table)
def cmd_list_task(ctx, *, workplan: WORKPLAN = None):
    return ops.status(workplan, ctx.master)


@registry.command(help="a task: its state and its documents", render=render_task)
def cmd_show_task(ctx, *, task: TASK):
    tid = plans.task_id(task)
    wid, nnnn = tid.split("/")
    data = next((t for t in ops.status(wid, ctx.master)["tasks"] if t["id"] == tid), None)
    if data is None:
        raise Fail(f"{tid}: no such task")
    data["documents"] = {name: ops.document(wid, f"{nnnn}/{name}")["text"] for name in DOCS}
    data["editable"] = ops.document(wid, "WORKPLAN.md")["editable"]
    return data


@registry.command(help="the next task, from its templates; the editor opens on TASK.md",
                  render=lambda r: lines(f"added {t}" for t in r["tasks"]) if "tasks" in r
                  else f"{r['task']}: listed in {r['listed']}\n"
                  + lines(f"created {p}" for p in r["created"]))
def cmd_add_task(ctx, *, title: Annotated[str, Positional("TITLE", "the task's title",
                                                         optional=True, many=True)] = None,
                 workplan: Annotated[str, Flag("the workplan; the current one when left out")] = None,
                 depend: Annotated[list[str], Flag("a task it depends on; repeat for more")] = None,
                 change: Annotated[str, Flag("the change; skips the editor", short="-m")] = None,
                 reply: Annotated[str, Flag("a gen-task reply from a chat: a file, or - for "
                                            "standard input; its new tasks are added")] = None):
    wid = plans.workplan_id(workplan)
    if reply is not None:
        return agent.add_tasks(wid, read_reply(ctx, reply))
    result = ops.add_task(wid, title, depend, change)
    if change is None and ctx.interactive:
        git.edit(plans.ROOT / result["task"] / "TASK.md")
    return result


@registry.command(help="the agent writes the tasks; WORKPLAN.md and the tasks are committed",
                  render=lambda r: r["prompt"] if "prompt" in r else render_gen_task(r))
def cmd_gen_task(ctx, *, workplan: WORKPLAN = None,
                 prompt: Annotated[bool, Flag("print the prompt for a chat; change nothing")] = False):
    if prompt:
        return agent.prompt("gen-task", workplan)
    return agent.gen_task(workplan, ctx.cfg)


@registry.command(help="edit a task's document: the editor, or the text given",
                  render=lambda r: f"saved {r['saved']}",
                  method="PUT", route="/api/task/{task}/{doc}")
def cmd_edit_task(ctx, *, task: TASK,
                  doc: Annotated[str, Flag("TASK.md, BREAKDOWN.md or NOTES.md")] = "TASK.md",
                  text: Annotated[str, Flag("the new text; skips the editor")] = None):
    tid = plans.task_id(task)
    wid, nnnn = tid.split("/")
    if text is None:
        if not ctx.interactive:
            raise Fail("edit-task needs the text")
        return ops.edit_document(wid, f"{nnnn}/{doc}")
    return ops.save_document(wid, f"{nnnn}/{doc}", text)


@registry.command(help="move the task to Dropped in WORKPLAN.md, and commit it",
                  render=lambda r: r["commit"])
def cmd_drop_task(ctx, *, task: TASK):
    return ops.drop_task(task, ctx.master)


# ---------------------------------------------------------------------------
# patch

@registry.command(help="the patch: the staged change if applied, else output.patch",
                  render=lambda r: r["text"])
def cmd_show_patch(ctx, *, task: TASK):
    return {"text": ops.diff(task)}


@registry.command(help="a reply from a chat becomes output.patch and COMMIT_MSG",
                  render=render_gen_patch)
def cmd_add_patch(ctx, *, task: TASK,
                  reply: Annotated[str, Positional("FILE", "the reply; standard input when "
                                                   "left out", optional=True)] = None):
    return agent.add_patch(task, read_reply(ctx, reply), ctx.cfg)


@registry.command(help="the agent writes output.patch and COMMIT_MSG",
                  render=lambda r: r["prompt"] if "prompt" in r else render_gen_patch(r))
def cmd_gen_patch(ctx, *, task: TASK,
                  prompt: Annotated[bool, Flag("print the prompt for a chat; change nothing")] = False):
    if prompt:
        return agent.prompt("gen-patch", task)
    return agent.gen_patch(task, ctx.cfg)


@registry.command(help="stage the patch in the tree and the index", render=lambda r: r["stat"])
def cmd_apply_patch(ctx, *, task: TASK):
    return {"stat": ops.apply(task)}


@registry.command(help="commit the patch with COMMIT_MSG and the task's files",
                  render=lambda r: r["commit"])
def cmd_accept_patch(ctx, *, task: TASK):
    return {"commit": ops.accept(task, ctx.master)}


@registry.command(help="delete an unapplied patch and its COMMIT_MSG",
                  render=lambda r: lines(f"removed {p}" for p in r["removed"]))
def cmd_drop_patch(ctx, *, task: TASK):
    return ops.drop_patch(task)


@registry.command(help="take an applied patch back out", render=lambda r: r["result"])
def cmd_reject_patch(ctx, *, task: TASK):
    return {"result": ops.reject(task)}


# ---------------------------------------------------------------------------
# routing, hooks and the server

@registry.command(help="the next step after a commit",
                  render=lambda d: " ".join([d["action"], *d["targets"]]),
                  method="GET", route="/api/route")
def cmd_route(ctx, *, rev: Annotated[str, Positional("REV", "the commit")] = "HEAD",
              dispatch: Annotated[bool, Flag("run route.dispatch with the result")] = False):
    decision = route.decide(rev, ctx.cfg)
    if ctx.interactive:
        print(f"route: {decision['source']} chose {decision['action']}; "
              f"the rules chose {decision['rule']}", file=sys.stderr)
    if dispatch:
        if not ctx.interactive:
            raise Fail("dispatch runs from the CLI")
        route.dispatch(decision, ctx.cfg)
    return decision


@registry.command(help="hooks that run route after each commit", render=lines, cli_only=True)
def cmd_install(ctx):
    return ops.install()


@registry.command(help="the board, in a local web page", cli_only=True)
def cmd_serve(ctx, *, port: Annotated[int, Flag("the port")] = 8765):
    server = serve.Server(port, registry, http_context)
    print(f"workplan serve: {server.url}", flush=True)
    print("Ctrl-C stops it.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return {}
