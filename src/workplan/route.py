"""The next step after a commit.

The targets always come from the commit. The action comes from the
rules, the first of ACTIONS that has targets, or from a model when
route.classifier is "llm", falling back to the rules when the model's
answer is not an action with targets.

define-tasks and produce-patch are also the names of the commands that
carry them out.
"""

import datetime
import re
import shlex
import subprocess
import sys

from workplan import git, llm, plans, templates
from workplan.git import Fail

ACTIONS = ("complete", "review", "produce-patch", "define-tasks", "none")

PLAN_PATH = re.compile(r"^workplans/([^/]+)/WORKPLAN\.md$")
TASK_PATH = re.compile(r"^workplans/([^/]+)/(\d{4})/(?:TASK|BREAKDOWN)\.md$")
TASK_SUBJECT = re.compile(r"^([^/\s]+)/(\d{4}) ")


def branch_containing(rev: str, master: str) -> str:
    """The current branch when it holds the commit, else master when it
    does, else the first branch that does."""
    current = git.branch()
    holding = git.run("branch", "--contains", rev, "--format=%(refname:short)").splitlines()
    for candidate in (current, master):
        if candidate in holding:
            return candidate
    return holding[0] if holding else current


def facts(rev: str, master: str) -> dict:
    """What a commit is: its branch, parents, subject, trailer and paths."""
    parents = git.run("rev-list", "--parents", "-n", "1", rev).split()[1:]
    if len(parents) > 1:
        out = git.run("diff", "--name-only", "-z", parents[0], rev, strip=False)
    else:
        out = git.run("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--root",
                      rev, strip=False)
    return {
        "rev": git.run("rev-parse", "--short", rev),
        "branch": branch_containing(rev, master),
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


def classify(f: dict, cfg: dict) -> str | None:
    """The action a model picks, or None when it gives no action."""
    prompt = templates.render(
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
    except Fail as e:
        print(f"route: classifier failed: {e}", file=sys.stderr)
        return None

    words = re.findall(r"[a-z-]+", answer.lower())
    choice = next((w for w in words if w in ACTIONS), None)
    if choice is None:
        print(f"route: classifier answered {answer!r}", file=sys.stderr)
    return choice


def decide(rev: str, cfg: dict) -> dict:
    master = cfg["master"]
    f = facts(rev, master)
    found = candidates(f, master)
    rule = next((a for a in ACTIONS if a in found), "none")
    action, source, model = rule, "rules", None

    if cfg["route"]["classifier"] == "llm":
        model = classify(f, cfg)
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


def dispatch(decision: dict, cfg: dict) -> str:
    """Record the decision in the route log and run route.dispatch with
    the action and its targets, unless the action is none."""
    log = git.git_path("workplan") / "route.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = " ".join([stamp, decision["rev"], decision["action"], *decision["targets"],
                     f"({decision['source']})"])
    with log.open("a") as fh:
        fh.write(line + "\n")

    command = cfg["route"]["dispatch"]
    if command and decision["action"] != "none":
        subprocess.run([*shlex.split(command), decision["action"], *decision["targets"]])
    return line
