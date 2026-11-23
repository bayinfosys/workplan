"""Running git. No other module calls the git binary."""

import subprocess
from pathlib import Path


class Fail(Exception):
    """An operation that cannot go on; the CLI prints it and exits 1."""


def run(*args: str, input: str | None = None, cwd: Path | str | None = None,
        strip: bool = True) -> str:
    """Run git and return its output, or raise Fail with its error.

    strip=False returns stdout unchanged, as a diff needs.
    """
    result = subprocess.run(
        ["git", *args], text=True, input=input, capture_output=True, cwd=cwd,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise Fail(f"git {' '.join(args)} failed" + (f": {detail}" if detail else ""))
    return result.stdout.strip() if strip else result.stdout


def ok(*args: str, cwd: Path | str | None = None) -> bool:
    """True when the git command exits 0."""
    return subprocess.run(["git", *args], capture_output=True, cwd=cwd).returncode == 0


def toplevel() -> Path:
    return Path(run("rev-parse", "--show-toplevel"))


def branch() -> str:
    """The current branch, or HEAD when detached."""
    return run("rev-parse", "--abbrev-ref", "HEAD")


def ref_exists(ref: str) -> bool:
    return ok("rev-parse", "--verify", "-q", ref)


def clean() -> bool:
    return ok("diff", "--quiet") and ok("diff", "--cached", "--quiet")


def is_ancestor(a: str, b: str) -> bool:
    return ok("merge-base", "--is-ancestor", a, b)


def git_path(name: str) -> Path:
    """A path inside the repository's git directory, such as hooks."""
    return Path(run("rev-parse", "--git-path", name))


def interactive(*args: str) -> None:
    """Run git attached to the terminal, as an editor needs; raise Fail
    when it exits non-zero."""
    if subprocess.run(["git", *args]).returncode != 0:
        raise Fail(f"git {' '.join(args)} failed")


def edit(path: Path) -> None:
    """Open path in the editor git uses for commit messages
    (GIT_EDITOR, core.editor, VISUAL, EDITOR), the way git runs it."""
    editor = run("var", "GIT_EDITOR")
    if subprocess.run(["sh", "-c", f'{editor} "$@"', editor, str(path)]).returncode != 0:
        raise Fail(f"the editor ({editor}) exited with an error")
