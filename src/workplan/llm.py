"""A client for any OpenAI-compatible chat completions endpoint.
The only module that makes HTTP requests."""

import json
import urllib.error
import urllib.request

from workplan import config
from workplan.git import Fail


def chat(cfg: dict, model: str, messages: list[dict], timeout: float) -> str:
    """Post messages to <api_base>/chat/completions; return the reply text."""
    if not model:
        raise Fail("no model configured")
    base = cfg["llm"]["api_base"].rstrip("/")
    body = {"model": model, "messages": messages, **cfg["llm"].get("params", {})}
    headers = {"Content-Type": "application/json"}
    if key := config.api_key(cfg):
        headers["Authorization"] = f"Bearer {key}"

    request = urllib.request.Request(
        f"{base}/chat/completions", data=json.dumps(body).encode(), headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        raise Fail(f"{base}: HTTP {e.code}: {detail}") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise Fail(f"{base}: {e}") from e

    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as e:
        raise Fail(f"{base}: unexpected response: {str(data)[:300]}") from e
