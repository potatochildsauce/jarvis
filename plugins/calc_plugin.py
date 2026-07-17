"""
Deliberately not using eval()/exec() here — even for a toy calculator plugin,
arbitrary code execution from user input is the wrong default. This walks a
parsed AST and only allows numeric literals and a fixed set of operators.
"""
from __future__ import annotations
import ast
import operator
import re
from core.plugin_base import Plugin, Context

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_TRIGGER_RE = re.compile(r"^(calc(ulate)?|what'?s)\s+(.*)$", re.IGNORECASE)
_EXPR_RE = re.compile(r"^[0-9\.\s\+\-\*\/\%\(\)]+$")


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("that's not an expression i'll evaluate")


class CalcPlugin(Plugin):
    name = "calc"
    description = "'calc <expression>' or 'calculate <expression>' — arithmetic only"

    def _extract_expr(self, text: str) -> str | None:
        m = _TRIGGER_RE.match(text.strip())
        if m:
            candidate = m.group(3).strip()
        elif _EXPR_RE.match(text.strip()) and any(op in text for op in "+-*/%"):
            candidate = text.strip()
        else:
            return None
        return candidate if _EXPR_RE.match(candidate) else None

    def can_handle(self, text: str, ctx: Context) -> bool:
        return self._extract_expr(text) is not None

    def handle(self, text: str, ctx: Context) -> str:
        expr = self._extract_expr(text)
        try:
            tree = ast.parse(expr, mode="eval")
            result = _safe_eval(tree)
        except (ZeroDivisionError,) as e:
            return "division by zero, nice try."
        except Exception:
            return "couldn't parse that as arithmetic."
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
