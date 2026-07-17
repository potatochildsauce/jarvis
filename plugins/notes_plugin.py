from __future__ import annotations
import json
from core.plugin_base import Plugin, Context
from core.config import CONFIG


class NotesPlugin(Plugin):
    name = "notes"
    description = "'note: <text>' saves a note, 'notes' lists them, 'clear notes' wipes them"

    def _load(self) -> list[str]:
        if not CONFIG.notes_path.exists():
            return []
        try:
            return json.loads(CONFIG.notes_path.read_text())
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, notes: list[str]) -> None:
        CONFIG.notes_path.write_text(json.dumps(notes, indent=2))

    def can_handle(self, text: str, ctx: Context) -> bool:
        t = text.lower().strip()
        return t.startswith("note:") or t.startswith("note ") or t in ("notes", "list notes", "clear notes")

    def handle(self, text: str, ctx: Context) -> str:
        t = text.strip()
        low = t.lower()

        if low in ("notes", "list notes"):
            notes = self._load()
            if not notes:
                return "no notes yet."
            return "\n".join(f"{i+1}. {n}" for i, n in enumerate(notes))

        if low == "clear notes":
            self._save([])
            return "cleared."

        if low.startswith("note:"):
            content = t[len("note:"):].strip()
        else:
            content = t[len("note "):].strip()

        if not content:
            return "note about what?"

        notes = self._load()
        notes.append(content)
        self._save(notes)
        return f"saved. ({len(notes)} total)"
