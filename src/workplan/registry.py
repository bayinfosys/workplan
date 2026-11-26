"""Commands declared once, for the CLI and for HTTP.

A command is a function named `cmd_<verb>_<noun>` (or `cmd_<verb>` for
the few with no noun), registered with `@registry.command(...)`. It
takes a context and keyword-only parameters, and returns data.

    @registry.command(help="commit the patch with the task's files")
    def cmd_accept_patch(ctx, *, task: Annotated[str, Positional("[ID/]NNNN")]):
        ...

On the CLI a command is `noun verb`, as `task add`; a command with no
noun, or whose noun is one of the registry's top nouns, is `verb`
alone, as `init` or `merge`. Each parameter is `Positional` or `Flag`
on the CLI. Over HTTP a parameter comes from the route when the route
names it, else from the query string for GET and DELETE, else from the
JSON body. The verb gives the HTTP method and the route:

    list      GET     the noun's collection
    show      GET     the item
    add, new  POST    the collection
    gen       POST    the collection, then /gen
    edit      PUT     the item
    drop      DELETE  the item
    others    POST    the item, then /<verb>

A noun with no collection uses its item route in place of one. In a
route, {workplan} is one path segment and {task} two, <id>/<nnnn>.
"""

import argparse
import inspect
import json
import re
from dataclasses import dataclass, field
from typing import Annotated, Any, Callable, get_args, get_origin, get_type_hints

from workplan.git import Fail

NOUNS = {
    "workplan": ("/api/workplan", "/api/workplan/{workplan}"),
    "task": ("/api/workplan/{workplan}/task", "/api/task/{task}"),
    "patch": (None, "/api/task/{task}/patch"),
}

SEGMENTS = {"task": r"[^/]+/\d{4}"}
SEGMENT = r"[^/]+"


@dataclass(frozen=True)
class Positional:
    metavar: str = ""
    help: str = ""
    optional: bool = False          # may be left out; the command decides what that means
    many: bool = False              # several words, joined with spaces into a str


@dataclass(frozen=True)
class Flag:
    help: str = ""
    short: str = ""


@dataclass
class Parameter:
    name: str
    kind: type
    spec: Positional | Flag
    default: Any


@dataclass
class Command:
    name: str
    function: Callable
    help: str
    parameters: list[Parameter]
    aliases: tuple[str, ...] = ()
    words: tuple[str, ...] = ()
    render: Callable[[Any], str] | None = None
    cli_only: bool = False
    protocol: bool = False      # a protocol command, given as git commands in PROTOCOL.md
    method: str = ""
    route: str = ""
    pattern: re.Pattern | None = field(default=None, repr=False)


def http_of(verb: str, noun: str | None) -> tuple[str, str]:
    """The method and route a verb and noun give."""
    if noun not in NOUNS:
        name = " ".join(w for w in (noun, verb) if w)
        raise ValueError(f"no route for {name}: give route= or cli_only=True")
    collection, item = NOUNS[noun]
    collection = collection or item
    match verb:
        case "list":
            return "GET", collection
        case "show":
            return "GET", item
        case "add" | "new":
            return "POST", collection
        case "gen":
            return "POST", collection + "/gen"
        case "edit":
            return "PUT", item
        case "drop":
            return "DELETE", item
    return "POST", f"{item}/{verb}"


def compile_route(route: str) -> re.Pattern:
    parts = re.split(r"\{(\w+)\}", route)
    pattern = ""
    for i, part in enumerate(parts):
        pattern += re.escape(part) if i % 2 == 0 else f"(?P<{part}>{SEGMENTS.get(part, SEGMENT)})"
    return re.compile(pattern)


def convert(kind: type, value: Any, name: str) -> Any:
    """A value from the CLI, a URL or JSON, as the parameter's type."""
    if value is None:
        return None
    try:
        if kind is bool:
            return value if isinstance(value, bool) else str(value).lower() in ("1", "true", "yes")
        if kind is int:
            return int(value)
        if get_origin(kind) is list:
            items = value if isinstance(value, list) else str(value).split(",")
            return [str(item).strip() for item in items if str(item).strip()]
        if isinstance(value, list):
            return " ".join(str(item) for item in value)
        return str(value)
    except (TypeError, ValueError) as e:
        raise Fail(f"{name}: {e}") from e


class Registry:
    def __init__(self, prog: str, description: str = "", version: str = "",
                 top: tuple[str, ...] = ()):
        self.prog = prog
        self.description = description
        self.version = version
        self.top = top
        self.commands: list[Command] = []

    # -- declaring ----------------------------------------------------------

    def command(self, help: str = "", aliases: tuple[str, ...] = (),
                render: Callable[[Any], str] | None = None, cli_only: bool = False,
                method: str = "", route: str = "", protocol: bool = False):
        def register(function: Callable) -> Callable:
            words = function.__name__.removeprefix("cmd_").split("_")
            verb, noun = words[0], "_".join(words[1:]) or None
            cli = (verb,) if noun is None or noun in self.top else (noun, verb)
            name = " ".join(cli)

            hints = get_type_hints(function, include_extras=True)
            parameters = []
            for p in inspect.signature(function).parameters.values():
                if p.kind is not p.KEYWORD_ONLY:
                    continue
                hint = hints[p.name]
                if get_origin(hint) is not Annotated:
                    raise TypeError(f"{name}: {p.name} needs Positional or Flag")
                kind, *extras = get_args(hint)
                spec = next(e for e in extras if isinstance(e, (Positional, Flag)))
                default = None if p.default is p.empty else p.default
                parameters.append(Parameter(p.name, kind, spec, default))

            command = Command(name, function, help, parameters, tuple(aliases), cli, render,
                              cli_only, protocol)
            if not cli_only:
                command.method, command.route = (method, route) if route else http_of(verb, noun)
                command.pattern = compile_route(command.route)
            self.commands.append(command)
            return function
        return register

    # -- the CLI ------------------------------------------------------------

    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog=self.prog, description=self.description)
        if self.version:
            parser.add_argument("--version", action="version", version=f"{self.prog} {self.version}")
        top = parser.add_subparsers(dest="command", required=True, metavar="command")
        groups: dict[str, argparse._SubParsersAction] = {}
        for command in self.commands:
            if len(command.words) == 1:
                self.add_parser(top, command.words[0], command)
            else:
                noun, verb = command.words
                if noun not in groups:
                    group = top.add_parser(noun, help=f"{noun} commands",
                                           description=f"{noun} commands")
                    groups[noun] = group.add_subparsers(dest="verb", required=True,
                                                        metavar="verb")
                self.add_parser(groups[noun], verb, command)
            for alias in command.aliases:
                self.add_parser(top, alias, command, f"{command.name}: {command.help}")
        return parser

    @staticmethod
    def add_parser(sub, name: str, command: Command, help: str = "") -> None:
        help = help or command.help
        p = sub.add_parser(name, help=help, description=help)
        p.set_defaults(_command=command)
        p.add_argument("--json", action="store_true", help="print the result as JSON")
        for param in command.parameters:
            spec = param.spec
            if isinstance(spec, Positional):
                optional = spec.optional or param.default is not None
                nargs = ("*" if optional else "+") if spec.many else ("?" if optional else None)
                p.add_argument(param.name, nargs=nargs, default=param.default,
                               metavar=spec.metavar or param.name.upper(), help=spec.help)
                continue
            names = [f"--{param.name.replace('_', '-')}"] + ([spec.short] if spec.short else [])
            if param.kind is bool:
                p.add_argument(*names, dest=param.name, action="store_true", help=spec.help)
            elif get_origin(param.kind) is list:
                p.add_argument(*names, dest=param.name, action="append",
                               default=param.default, help=spec.help)
            else:
                p.add_argument(*names, dest=param.name, type=param.kind,
                               default=param.default, help=spec.help)

    def run_cli(self, argv: list[str] | None,
                context: Callable[[], Any]) -> tuple[Command, str]:
        """Parse argv, run the command, and return it with its output."""
        args = self.parser().parse_args(argv)
        command: Command = args._command
        values = {p.name: getattr(args, p.name) for p in command.parameters}
        result = self.call(command, context(), values)
        if args.json or command.render is None:
            return command, json.dumps(result, indent=2)
        return command, command.render(result)

    # -- HTTP ---------------------------------------------------------------

    def match(self, method: str, path: str) -> tuple[Command, dict[str, str]]:
        """The command for a request, and the values its route holds.
        LookupError when no route matches, PermissionError when a route
        matches with another method."""
        allowed = False
        for command in self.commands:
            if command.pattern and (m := command.pattern.fullmatch(path)):
                if command.method == method:
                    return command, m.groupdict()
                allowed = True
        raise PermissionError(path) if allowed else LookupError(path)

    def values(self, command: Command, path_values: dict, query: dict, body: dict) -> dict:
        """A request's values for a command: path, then query or body."""
        found = {}
        for param in command.parameters:
            if param.name in path_values:
                found[param.name] = path_values[param.name]
            elif command.method in ("GET", "DELETE"):
                if param.name in query:
                    found[param.name] = query[param.name]
            elif param.name in body:
                found[param.name] = body[param.name]
        return found

    # -- running ------------------------------------------------------------

    def call(self, command: Command, ctx: Any, values: dict) -> Any:
        """Run a command with values from either interface."""
        kwargs = {}
        for param in command.parameters:
            value = values.get(param.name)
            if value is None:
                required = (isinstance(param.spec, Positional) and not param.spec.optional
                            and param.default is None)
                if required:
                    raise Fail(f"{command.name}: {param.name} is needed")
                value = param.default
            kwargs[param.name] = convert(param.kind, value, param.name)
            if param.kind is bool and kwargs[param.name] is None:
                kwargs[param.name] = False
        return command.function(ctx, **kwargs)

    def get(self, name: str) -> Command:
        return next(c for c in self.commands if c.name == name or name in c.aliases)
