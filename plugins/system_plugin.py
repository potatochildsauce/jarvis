"""
Read-only system info. Deliberately doesn't do anything that changes system
state (no process control, no file deletion, nothing "OS automation" in the
scarier sense) — a voice assistant plugin that pokes at the OS should be
opt-in and explicit, not a default-on part of a demo project.
"""
from __future__ import annotations
import platform
import shutil
import os
from core.plugin_base import Plugin, Context


class SystemPlugin(Plugin):
    name = "system"
    description = "'system info' — platform, cpu count, disk space"

    def can_handle(self, text: str, ctx: Context) -> bool:
        t = text.lower()
        return "system info" in t or t.strip() == "sysinfo"

    def handle(self, text: str, ctx: Context) -> str:
        cpu_count = os.cpu_count() or 1
        usage = shutil.disk_usage(os.path.expanduser("~"))
        free_gb = usage.free / (1024 ** 3)
        return (
            f"{platform.system()} {platform.release()}, "
            f"{cpu_count} logical cpus, "
            f"python {platform.python_version()}, "
            f"{free_gb:.1f} gb free on home."
        )
