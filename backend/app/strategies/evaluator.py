"""Sicherer arithmetischer Evaluator für Formel- und Regel-Strategien.

Erlaubt nur Zahlen, whitelisted Variablen, +, -, *, /, //, %, **, Klammern,
Vergleiche, boolsche Operatoren (and/or/not) und eine kleine Whitelist von
Funktionsaufrufen (sqrt, pow, abs, min, max, round, floor, ceil). Keine
Attribute, keine Imports, keine benutzerdefinierten Funktionen.
Rückgabe: Decimal (Arithmetik) oder bool (Vergleich).
"""

from __future__ import annotations

import ast
import math
import operator
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from typing import Any, Callable

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


# Kleine Funktions-Whitelist. Absicht: einfache Mathematik, die man in
# Preisformeln brauchen kann – sqrt fuer gedaempfte Skalierung, min/max fuer
# Deckelungen, round/floor/ceil fuer Preis-Rundungen. Jede Funktion mappt
# die Argumente ueber _to_decimal, damit bool -> 0/1 konsistent laeuft.
def _fn_sqrt(x: Any) -> Decimal:
    val = _to_decimal(x)
    if val < 0:
        raise ExpressionError("sqrt von negativer Zahl")
    return val.sqrt()


def _fn_pow(x: Any, y: Any) -> Decimal:
    return _to_decimal(x) ** _to_decimal(y)


def _fn_abs(x: Any) -> Decimal:
    return abs(_to_decimal(x))


def _fn_min(*args: Any) -> Decimal:
    if not args:
        raise ExpressionError("min() braucht mindestens ein Argument")
    return min(_to_decimal(a) for a in args)


def _fn_max(*args: Any) -> Decimal:
    if not args:
        raise ExpressionError("max() braucht mindestens ein Argument")
    return max(_to_decimal(a) for a in args)


def _fn_round(x: Any, digits: Any = 0) -> Decimal:
    val = _to_decimal(x)
    n = int(_to_decimal(digits))
    # Decimal.quantize mit passendem Exponenten, bankers-rounding default.
    quant = Decimal(1).scaleb(-n) if n >= 0 else Decimal(1).scaleb(-n)
    return val.quantize(quant)


def _fn_floor(x: Any) -> Decimal:
    return _to_decimal(x).to_integral_value(rounding=ROUND_FLOOR)


def _fn_ceil(x: Any) -> Decimal:
    return _to_decimal(x).to_integral_value(rounding=ROUND_CEILING)


def _fn_mod(x: Any, n: Any) -> Decimal:
    # explizite Funktion zusaetzlich zum '%'-Operator – erleichtert
    # periodische Muster wie `mod(hour, 24)` oder `mod(day-1, 7)`.
    return _to_decimal(x) % _to_decimal(n)


def _fn_sin(x: Any) -> Decimal:
    # Decimal hat keinen sin/cos – ueber float, dann wieder zurueck.
    return Decimal(str(math.sin(float(_to_decimal(x)))))


def _fn_cos(x: Any) -> Decimal:
    return Decimal(str(math.cos(float(_to_decimal(x)))))


_FUNCS: dict[str, Callable[..., Any]] = {
    "sqrt": _fn_sqrt,
    "pow": _fn_pow,
    "abs": _fn_abs,
    "min": _fn_min,
    "max": _fn_max,
    "round": _fn_round,
    "floor": _fn_floor,
    "ceil": _fn_ceil,
    "mod": _fn_mod,
    "sin": _fn_sin,
    "cos": _fn_cos,
}


def _to_decimal(value: Any) -> Decimal:
    # bool zuerst pruefen, weil bool Subklasse von int ist – ohne diesen
    # Zweig wuerde Decimal(str(True)) fehlschlagen. Das ermoeglicht Muster
    # wie `(hour >= 18) * 0.2` fuer bedingte Preise in einer Formel.
    if isinstance(value, bool):
        return Decimal(1) if value else Decimal(0)
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
        # bool wird in _to_decimal auf 1/0 gemappt, damit Formeln wie
        # `(hour >= 18) * 0.2` als zeitabhaengiger Aufschlag funktionieren.
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

    if isinstance(node, ast.Call):
        # Nur whitelisted, namentlich aufgerufene Funktionen.
        if not isinstance(node.func, ast.Name):
            raise ExpressionError("Funktion muss ein einfacher Name sein")
        fn = _FUNCS.get(node.func.id)
        if fn is None:
            raise ExpressionError(f"Funktion nicht erlaubt: {node.func.id}")
        if node.keywords:
            raise ExpressionError("Keyword-Argumente nicht erlaubt")
        args = [_eval(a, variables) for a in node.args]
        return fn(*args)

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
