"""
Discovers plugins in the `plugins/` package and instantiates them. A module
counts as a plugin if it defines a class that subclasses Plugin and isn't
Plugin itself. Drop a new file in plugins/, subclass Plugin, and it's picked
up automatically next run — no registry to hand-edit.
"""
from __future__ import annotations
import importlib
import inspect
import pkgutil
from typing import Iterable

from core.plugin_base import Plugin, Context


def discover_plugins(package_name: str = "plugins") -> list[Plugin]:
    package = importlib.import_module(package_name)
    found: list[Plugin] = []

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_name = f"{package_name}.{module_name}"
        module = importlib.import_module(full_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Plugin) and obj is not Plugin and obj.__module__ == full_name:
                found.append(obj())

    return found


def startup_all(plugins: Iterable[Plugin], ctx: Context) -> None:
    for p in plugins:
        try:
            p.startup(ctx)
        except Exception as e:  # a broken plugin shouldn't take the whole app down
            print(f"[jarvis] plugin '{p.name}' failed to start: {e}")
