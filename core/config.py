"""
Config is just environment variables with defaults — no config file format
to design or parse. Set these before running, e.g.:

    export ANTHROPIC_API_KEY=sk-...
    python main.py
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Config:
    assistant_name: str = os.environ.get("JARVIS_NAME", "jarvis")
    anthropic_api_key: str | None = os.environ.get("ANTHROPIC_API_KEY")
    anthropic_model: str = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    notes_path: Path = DATA_DIR / "notes.json"


CONFIG = Config()
