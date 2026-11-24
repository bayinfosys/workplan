"""The workplan command: the registry's CLI, with paging and errors."""

import os
import shlex
import signal
import subprocess
import sys

from workplan.commands import cli_context, registry
from workplan.git import Fail

PAGED = ("show-patch",)


def page(text: str) -> None:
    if not sys.stdout.isatty():
        sys.stdout.write(text)
        return
    pager = shlex.split(os.environ.get("PAGER", "less -R"))
    try:
        subprocess.run(pager, input=text, text=True)
    except FileNotFoundError:
        sys.stdout.write(text)


def main(argv: list[str] | None = None) -> int:
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
        command, text = registry.run_cli(argv, cli_context)
    except Fail as e:
        print(f"workplan: {e}", file=sys.stderr)
        return 1
    if command.name in PAGED:
        page(text)
    elif text:
        print(text)
    return 0
