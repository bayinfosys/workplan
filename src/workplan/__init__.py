"""workplan: plan and record development work in git."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("workplan")
except PackageNotFoundError:
    __version__ = "0+unknown"
