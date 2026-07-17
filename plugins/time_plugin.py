from __future__ import annotations
import re
from datetime import datetime
from core.plugin_base import Plugin, Context


class TimePlugin(Plugin):
    name = "time"
    description = "tells the current time or date"

    _DATE_RE = re.compile(r"\bdate\b|\bday is it\b", re.IGNORECASE)
    _TIME_RE = re.compile(r"\btime\b", re.IGNORECASE)

    def can_handle(self, text: str, ctx: Context) -> bool:
        return bool(self._DATE_RE.search(text) or self._TIME_RE.search(text))

    def handle(self, text: str, ctx: Context) -> str:
        now = datetime.now()
        if self._DATE_RE.search(text):
            return now.strftime("it's %A, %B %d, %Y.")
        hour = now.strftime("%I").lstrip("0") or "12"
        return now.strftime(f"it's {hour}:%M %p.")
