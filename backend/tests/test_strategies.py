from dataclasses import dataclass
from decimal import Decimal

import pytest

from app.strategies import StrategyError, compute_price


@dataclass
class FakeProduct:
    name: str = "Sneaker"
    category: str = "Schuhe"
    cost_price: Decimal = Decimal("10.00")
    stock: int = 5
    competitor_price: Decimal | None = Decimal("25.00")
    monthly_demand: int = 0
    context: str = ""


def test_fix_strategy_returns_configured_amount():
    result = compute_price(FakeProduct(), "fix", {"amount": "49.99"})
    assert result.price == Decimal("49.99")
    assert result.is_llm_suggestion is False
    assert "Fixpreis" in (result.reasoning or "")


def test_fix_strategy_rejects_missing_amount():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "fix", {})


def test_fix_strategy_rejects_negative():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "fix", {"amount": "-1"})


def test_formula_strategy_uses_product_variables():
    product = FakeProduct(cost_price=Decimal("10"), stock=5)
    result = compute_price(product, "formula", {"expression": "cost_price * 2 + stock"})
    assert result.price == Decimal("25")
    assert result.is_llm_suggestion is False


def test_formula_strategy_rejects_invalid_expression():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "formula", {"expression": "1 +"})


def test_formula_strategy_rejects_dangerous_expression():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "formula", {"expression": '__import__("os")'})


def test_unknown_strategy_raises():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "quantum", {})


def test_legacy_strategies_no_longer_accepted():
    # `rule` und `llm` sind aus dem Scope genommen (siehe docs/pricing-strategies.md).
    # Die Registry kennt nur noch fix + formula.
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "rule", {"rules": [], "fallback": "0"})
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "llm", {"prompt_template": "x"})
