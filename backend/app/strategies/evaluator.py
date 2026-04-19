"""Sicherer arithmetischer Evaluator für Formel- und Regel-Strategien.

Erlaubt nur Zahlen, whitelisted Variablen, +, -, *, /, //, %, **, Klammern,
Vergleiche (für Regeln) und boolsche Operatoren (and/or/not). Kein Funktionsaufruf,
kein Attribut-Zugriff, kein Import. Rückgabe: Decimal (Arithmetik) oder bool (Vergleich).
"""

from __future__ import annotations

import ast
import operator
from decimal import Decimal
from typing import Any

_ARITH_OPS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type[ast.unaryop], Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
}

_CMP_OPS: dict[type[ast.cmpop], Any] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class ExpressionError(ValueError):
    pass


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    raise ExpressionError(f"Unerwarteter Wert: {value!r}")


def _eval(node: ast.AST, variables: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _eval(node.body, variables)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return _to_decimal(node.value)
        if isinstance(node.value, bool):
            return node.value
        raise ExpressionError(f"Literal vom Typ {type(node.value).__name__} nicht erlaubt")

    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise ExpressionError(f"Unbekannte Variable: {node.id}")
        return variables[node.id]

    if isinstance(node, ast.BinOp):
        op = _ARITH_OPS.get(type(node.op))
        if op is None:
            raise ExpressionError(f"Operator {type(node.op).__name__} nicht erlaubt")
        left = _eval(node.left, variables)
        right = _eval(node.right, variables)
        if isinstance(left, bool) or isinstance(right, bool):
            raise ExpressionError("Arithmetik auf Bool nicht erlaubt")
        return op(_to_decimal(left), _to_decimal(right))

    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ExpressionError(f"Unäroperator {type(node.op).__name__} nicht erlaubt")
        return op(_eval(node.operand, variables))

    if isinstance(node, ast.BoolOp):
        values = [_eval(v, variables) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
        raise ExpressionError("BoolOp nicht erlaubt")

    if isinstance(node, ast.Compare):
        left = _eval(node.left, variables)
        for op_node, comparator in zip(node.ops, node.comparators, strict=True):
            op = _CMP_OPS.get(type(op_node))
            if op is None:
                raise ExpressionError(f"Vergleich {type(op_node).__name__} nicht erlaubt")
            right = _eval(comparator, variables)
            if not op(left, right):
                return False
            left = right
        return True

    raise ExpressionError(f"Ausdruck {type(node).__name__} nicht erlaubt")


def evaluate(expression: str, variables: dict[str, Any]) -> Any:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"Ungültiger Ausdruck: {exc.msg}") from exc
    return _eval(tree, variables)


def evaluate_decimal(expression: str, variables: dict[str, Any]) -> Decimal:
    result = evaluate(expression, variables)
    if isinstance(result, bool):
        raise ExpressionError("Ausdruck liefert keinen Zahlenwert")
    return _to_decimal(result)
