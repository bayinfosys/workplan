"""Templates for documents, prompts and project files.

A template is looked up in workplans/templates/<kind>/<name> first,
then in the package. Rendering is string.Template substitution only:
$name is replaced, $$ is a literal dollar sign.
"""

from importlib import resources
from string import Template

from workplan import plans
from workplan.git import Fail


def text(kind: str, name: str) -> str:
    local = plans.ROOT / "templates" / kind / name
    if local.is_file():
        return local.read_text()
    packaged = resources.files("workplan") / "templates" / kind / name
    if not packaged.is_file():
        raise Fail(f"no template {kind}/{name}")
    return packaged.read_text()


def render(kind: str, name: str, **values: str) -> str:
    try:
        return Template(text(kind, name)).substitute(values)
    except (KeyError, ValueError) as e:
        raise Fail(f"template {kind}/{name}: {e}") from e
