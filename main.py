#!/usr/bin/env python3
"""
jarvis — plugin-based command router, text mode.

    python main.py

Voice mode isn't wired up in this environment (no mic/speaker access here to
test against), but the router doesn't care where text comes from — see the
README for how to bolt on speech_recognition + pyttsx3 for a real voice
front end without touching anything in core/ or plugins/.
"""
from __future__ import annotations
import sys

from core.config import CONFIG
from core.plugin_base import Context
from core.plugin_manager import discover_plugins, startup_all
from core.router import Router


def print_help(plugins):
    print("what i can actually do right now:")
    for p in plugins:
        if getattr(p, "is_fallback", False):
            continue
        print(f"  {p.name:<8} {p.description}")
    print("  exit     quit")


def main():
    plugins = discover_plugins("plugins")
    ctx = Context()
    startup_all(plugins, ctx)
    router = Router(plugins)

    print(f"{CONFIG.assistant_name} — {len(plugins)} plugins loaded. 'help' for what's real, 'exit' to quit.")
    if not CONFIG.anthropic_api_key:
        print("(no ANTHROPIC_API_KEY set — unmatched input just won't be understood, that's fine.)")

    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not text:
            continue
        if text.lower() in ("exit", "quit"):
            break
        if text.lower() in ("help", "?"):
            print_help(plugins)
            continue

        print(router.route(text, ctx))


if __name__ == "__main__":
    sys.exit(main() or 0)
