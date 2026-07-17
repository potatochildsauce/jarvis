"""
Last-resort fallback: if nothing else claimed the input and an API key is
configured, ask Claude. Uses urllib from the standard library instead of the
anthropic SDK so this project has zero required third-party dependencies —
install the real SDK yourself if you'd rather use it (see README).

This plugin never appears in `can_handle` matching for the main routing pass;
the router calls it directly as a fallback (see core/router.py, `is_fallback`).
"""
from __future__ import annotations
import json
import urllib.request
import urllib.error
from core.plugin_base import Plugin, Context
from core.config import CONFIG


class LLMPlugin(Plugin):
    name = "llm"
    description = "fallback for anything no other plugin recognizes (needs ANTHROPIC_API_KEY)"
    is_fallback = True

    def can_handle(self, text: str, ctx: Context) -> bool:
        return False  # never claims input directly — see router.py

    def handle(self, text: str, ctx: Context) -> str:
        if not CONFIG.anthropic_api_key:
            return "not sure what to do with that yet. try 'help' for what i can actually do."

        body = json.dumps({
            "model": CONFIG.anthropic_model,
            "max_tokens": 300,
            "messages": [{"role": "user", "content": text}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": CONFIG.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
        except urllib.error.URLError as e:
            return f"couldn't reach the api: {e}"

        parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "\n".join(parts) if parts else "got an empty response back."
