"""The next step after a commit.

The targets always come from the commit. The action comes from the
rules, the first of ACTIONS that has targets, or from a model when
route.classifier is "llm", falling back to the rules when the model's
answer is not an action with targets.

define-tasks and produce-patch are also the names of the commands that
carry them out.
"""

import re
import shlex
import subprocess
import sys

from workplan import git, llm, plans
from workplan.git import Fail

ACTIONS = ("complete", "review", "produce-patch", "define-tasks", "none")

PLAN_PATH = re.compile(r"^workplans/([^/]+)/WORKPLAN\.md$")
TASK_PATH = re.compile(r"^workplans/([^/]+)/(\d{4})/(?:TASK|BREAKDOWN)\.md$")
TASK_SUBJECT = re.compile(r"^([^/\s]+)/(\d{4}) ")


def facts(rev: str) -> dict:
    """What a commit is: the current branch, its parents, subject,
    trailer and paths."""
    parents = git.run("rev-list", "--parents", "-n", "1", rev).split()[1:]
    if len(parents) > 1:
        out = git.run("diff", "--name-only", "-z", parents[0], rev, strip=False)
    else:
        out = git.run("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--root",
                      rev, strip=False)
    return {
        "rev": git.run("rev-parse", "--short", rev),
        "branch": git.branch(),
        "parents": len(parents),
        "subject": git.run("log", "-1", "--format=%s", rev),
        "workplan": git.run("log", "-1", "--format=%(trailers:key=Workplan,valueonly)", rev),
        "paths": [p for p in out.split("\0") if p],
    }


def candidates(f: dict, master: str) -> dict[str, list[str]]:
    """Each action the commit could lead to, with its targets."""
    found: dict[str, list[str]] = {}

    if f["branch"] == master:
        if m := PLAN_PATH.match(f["workplan"]):
            found["complete"] = [m[1]]

    m = TASK_SUBJECT.match(f["subject"])
    if m and any(not p.startswith(f"{plans.ROOT}/") for p in f["paths"]):
        found["review"] = [f"{m[1]}/{m[2]}"]

    if tids := sorted({f"{m[1]}/{m[2]}" for p in f["paths"] if (m := TASK_PATH.match(p))}):
        found["produce-patch"] = tids

    if wids := sorted({m[1] for p in f["paths"] if (m := PLAN_PATH.match(p))}):
        found["define-tasks"] = wids

    return found


def decide(rev: str, cfg: dict) -> dict:
    """The action and its targets, from the rules or the model."""
    f = facts(rev)
    found = candidates(f, cfg["master"])
    rule = next((a for a in ACTIONS if a in found), "none")
    action, source, model = rule, "rules", None

    if cfg["route"]["classifier"] == "llm":
        prompt = plans.render(
            "prompts", "route.md",
            branch=f["branch"],
            parents=str(f["parents"]),
            subject=f["subject"],
            workplan=f["workplan"] or "(none)",
            paths="\n".join(f["paths"][:50]) or "(none)",
        )
        try:
            answer = llm.chat(cfg, cfg["route"]["model"], [{"role": "user", "content": prompt}],
                              float(cfg["route"]["timeout"]))
            model = next((w for w in re.findall(r"[a-z-]+", answer.lower()) if w in ACTIONS),
                         None)
            if model is None:
                print(f"route: classifier answered {answer!r}", file=sys.stderr)
        except Fail as e:
            print(f"route: classifier failed: {e}", file=sys.stderr)
        if model == "none" or model in found:
            action, source = model, "llm"

    return {
        "rev": f["rev"],
        "branch": f["branch"],
        "action": action,
        "targets": found.get(action, []),
        "source": source,
        "rule": rule,
        "model": model,
    }


def dispatch(decision: dict, cfg: dict) -> None:
    """Run route.dispatch with the action and its targets, unless the
    action is none."""
    command = cfg["route"]["dispatch"]
    if command and decision["action"] != "none":
        subprocess.run([*shlex.split(command), decision["action"], *decision["targets"]])
