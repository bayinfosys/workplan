"""workplans/config.toml, with environment overrides.

API keys come from the environment only: the variable named by
llm.api_key_env, else WORKPLAN_API_KEY.
"""

import copy
import os
import shlex
import tomllib

from workplan import plans
from workplan.git import Fail

DEFAULTS = {
    "parent": "master",
    "remote": "origin",
    "llm": {
        "api_base": "http://localhost:8000/v1",
        "api_key_env": "WORKPLAN_API_KEY",
        "params": {},
    },
    "route": {
        "classifier": "rules",
        "model": "",
        "timeout": 120,
        "dispatch": "",
    },
    "agent": {
        "name": "none",
        "model": "",
        "attempts": 3,
        "timeout": 1800,
        "setup": "",
        "command": [],
    },
    "test": {
        "command": "",
    },
}

# environment variable -> (section or None, key, conversion)
OVERRIDES = {
    "WORKPLAN_PARENT": (None, "parent", str),
    "WORKPLAN_REMOTE": (None, "remote", str),
    "WORKPLAN_API_BASE": ("llm", "api_base", str),
    "WORKPLAN_ROUTE_CLASSIFIER": ("route", "classifier", str),
    "WORKPLAN_ROUTE_MODEL": ("route", "model", str),
    "WORKPLAN_ROUTE_DISPATCH": ("route", "dispatch", str),
    "WORKPLAN_AGENT": ("agent", "name", str),
    "WORKPLAN_AGENT_MODEL": ("agent", "model", str),
    "WORKPLAN_AGENT_SETUP": ("agent", "setup", str),
    "WORKPLAN_AGENT_COMMAND": ("agent", "command", shlex.split),
    "WORKPLAN_TEST_COMMAND": ("test", "command", str),
}

PATH = plans.ROOT / "config.toml"


def load() -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    if PATH.is_file():
        try:
            data = tomllib.loads(PATH.read_text())
        except tomllib.TOMLDecodeError as e:
            raise Fail(f"{PATH}: {e}") from e
        for key, value in data.items():
            if isinstance(value, dict) and isinstance(cfg.get(key), dict):
                cfg[key].update(value)
            else:
                cfg[key] = value
    for var, (section, key, convert) in OVERRIDES.items():
        if var in os.environ:
            target = cfg[section] if section else cfg
            target[key] = convert(os.environ[var])
    return cfg


def api_key(cfg: dict) -> str:
    return os.environ.get(cfg["llm"]["api_key_env"]) or os.environ.get("WORKPLAN_API_KEY", "")
