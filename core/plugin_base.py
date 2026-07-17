"""
Base class every plugin implements. Keep it small on purpose — a plugin only
needs to answer two questions: "can you handle this?" and "handle it."

Routing is a plain "first plugin that says yes, wins" — see core/router.py.
Plugins are checked in registration order, so more specific plugins should
generally be registered before more general fallback ones.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    """Shared state handed to every plugin call. Plugins can stash whatever
    they want onto `memory` (a plain dict) if they need to remember things
    across calls within a session — nothing here is persisted automatically
    except what a plugin explicitly writes to disk itself (see NotesPlugin)."""
    memory: dict[str, Any] = field(default_factory=dict)


class Plugin:
    name: str = "unnamed"
    description: str = ""

    def can_handle(self, text: str, ctx: Context) -> bool:
        """Return True if this plugin wants to handle `text`. Should be cheap
        and side-effect free — routing may call this on several plugins
        before picking one."""
        raise NotImplementedError

    def handle(self, text: str, ctx: Context) -> str:
        """Do the thing, return a string response."""
        raise NotImplementedError

    def startup(self, ctx: Context) -> None:
        """Optional: called once when the plugin is loaded."""
        pass
