"""
The router itself is deliberately dumb: ask each plugin in turn "can you
handle this?", use the first one that says yes. All the actual intelligence
lives in the plugins. This keeps routing debuggable — if the wrong plugin
answers something, the bug is in one file, not spread across a shared NLU
layer.

If no plugin claims the input and an LLM plugin is available (see
plugins/llm_plugin.py), that one gets a last shot before the generic
fallback response.
"""
from __future__ import annotations
from core.plugin_base import Plugin, Context


class Router:
    def __init__(self, plugins: list[Plugin]):
        self.plugins = plugins
        self.llm_fallback = next((p for p in plugins if getattr(p, "is_fallback", False)), None)

    def route(self, text: str, ctx: Context) -> str:
        text = text.strip()
        if not text:
            return ""

        for plugin in self.plugins:
            if plugin is self.llm_fallback:
                continue  # fallback only runs if nothing else claimed it
            try:
                if plugin.can_handle(text, ctx):
                    return plugin.handle(text, ctx)
            except Exception as e:
                return f"[{plugin.name}] hit an error: {e}"

        if self.llm_fallback is not None:
            try:
                return self.llm_fallback.handle(text, ctx)
            except Exception as e:
                return f"[{self.llm_fallback.name}] hit an error: {e}"

        return "not sure what to do with that yet. try 'help' for what i can actually do."
