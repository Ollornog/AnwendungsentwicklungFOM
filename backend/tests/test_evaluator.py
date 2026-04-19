from decimal import Decimal

import pytest

from app.strategies.evaluator import ExpressionError, evaluate, evaluate_decimal


def test_arithmetic_returns_decimal():
    result = evaluate_decimal("cost_price * 1.5", {"cost_price": Decimal("10")})
    assert result == Decimal("15.0")


def test_arithmetic_operators():
    vars = {"a": Decimal("10"), "b": Decimal("3")}
    assert evaluate_decimal("a + b", vars) == Decimal("13")
    assert evaluate_decimal("a - b", vars) == Decimal("7")
    assert evaluate_decimal("a * b", vars) == Decimal("30")
    assert evaluate_decimal("a / b", vars) == Decimal("10") / Decimal("3")
    assert evaluate_decimal("a % b", vars) == Decimal("1")
    assert evaluate_decimal("a ** 2", vars) == Decimal("100")
    assert evaluate_decimal("-a + 5", vars) == Decimal("-5")


def test_parentheses_and_precedence():
    assert evaluate_decimal("(1 + 2) * 3", {}) == Decimal("9")
    assert evaluate_decimal("1 + 2 * 3", {}) == Decimal("7")


def test_comparisons_return_bool():
    assert evaluate("stock < 10", {"stock": 5}) is True
    assert evaluate("stock < 10", {"stock": 20}) is False
    assert evaluate("5 == 5", {}) is True
    assert evaluate("5 != 5", {}) is False


def test_chained_comparisons():
    assert evaluate("1 < 2 < 3", {}) is True
    assert evaluate("1 < 2 > 5", {}) is False


def test_boolean_ops():
    vars = {"stock": 5, "cost": Decimal("20")}
    assert evaluate("stock > 0 and cost < 100", vars) is True
    assert evaluate("stock > 10 or cost < 100", vars) is True
    assert evaluate("not (stock > 10)", vars) is True


def test_unknown_variable_raises():
    with pytest.raises(ExpressionError):
        evaluate("unknown + 1", {})


def test_syntax_error_raises():
    with pytest.raises(ExpressionError):
        evaluate("1 +", {})


@pytest.mark.parametrize(
    "expression",
    [
        '__import__("os")',
        'open("/etc/passwd")',
        "globals()",
        "lambda: 1",
        "x if True else 0",
        "[1, 2, 3]",
        "{1: 2}",
        "(1).__class__",
        "print(1)",
        '"hello" + "world"',
        "a.b",
    ],
)
def test_blocks_dangerous_constructs(expression):
    with pytest.raises(ExpressionError):
        evaluate(expression, {"x": 1, "a": 1})


def test_bool_arithmetic_coerces_to_int():
    # Absicht: bool -> 1/0 in Arithmetik, damit Formeln wie
    # `(hour >= 18) * 0.2` als bedingter Aufschlag funktionieren.
    assert evaluate_decimal("flag + 1", {"flag": True}) == Decimal("2")
    assert evaluate_decimal("flag * 5", {"flag": False}) == Decimal("0")
    assert evaluate_decimal("(hour >= 18) * 0.2", {"hour": 20}) == Decimal("0.2")
    assert evaluate_decimal("(hour >= 18) * 0.2", {"hour": 10}) == Decimal("0")


def test_comparison_not_valid_as_price():
    with pytest.raises(ExpressionError):
        evaluate_decimal("1 < 2", {})
