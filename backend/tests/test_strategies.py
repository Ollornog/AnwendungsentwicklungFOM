from dataclasses import dataclass
from decimal import Decimal

import pytest

from app.strategies import StrategyError, compute_price
from app.strategies.base import SuggestionResult


@dataclass
class FakeProduct:
    name: str = "Sneaker"
    category: str = "Schuhe"
    cost_price: Decimal = Decimal("10.00")
    stock: int = 5
    competitor_price: Decimal | None = Decimal("25.00")
    monthly_demand: int = 0
    daily_usage: int = 0
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


def test_rule_strategy_first_match_wins():
    product = FakeProduct(cost_price=Decimal("10"), stock=5)
    config = {
        "rules": [
            {"when": "stock < 10", "then": "cost_price * 1.5"},
            {"when": "stock < 20", "then": "cost_price * 1.2"},
        ],
        "fallback": "cost_price",
    }
    result = compute_price(product, "rule", config)
    assert result.price == Decimal("15.00")
    assert "Regel 0" in (result.reasoning or "")


def test_rule_strategy_fallback_when_no_match():
    product = FakeProduct(cost_price=Decimal("10"), stock=100)
    config = {
        "rules": [{"when": "stock < 10", "then": "cost_price * 2"}],
        "fallback": "cost_price * 1.1",
    }
    result = compute_price(product, "rule", config)
    assert result.price == Decimal("11.00")
    assert "Fallback" in (result.reasoning or "")


def test_rule_strategy_requires_fallback():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "rule", {"rules": [], "fallback": ""})


def test_unknown_strategy_raises():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "quantum", {})


def test_llm_strategy_uses_monkeypatched_client(monkeypatch):
    captured = {}

    def fake_suggest(template, whitelist):
        captured["template"] = template
        captured["whitelist"] = whitelist
        from app.llm import LLMSuggestion

        return LLMSuggestion(price=Decimal("42.00"), reasoning="mocked")

    monkeypatch.setattr("app.strategies.llm.suggest_price", fake_suggest)

    product = FakeProduct()
    result = compute_price(
        product,
        "llm",
        {"prompt_template": "Preis für {name} in {category}"},
    )

    assert isinstance(result, SuggestionResult)
    assert result.price == Decimal("42.00")
    assert result.is_llm_suggestion is True
    assert result.reasoning == "mocked"
    assert captured["whitelist"]["name"] == "Sneaker"
    # Template wird erst vom LLM-Client formatiert, an compute() geht es unverändert.
    assert captured["template"] == "Preis für {name} in {category}"
    for forbidden in ("password", "session", "email"):
        assert forbidden not in captured["whitelist"]


def test_llm_strategy_propagates_unavailable(monkeypatch):
    from app.llm import LLMUnavailableError

    def fake_suggest(template, whitelist):
        raise LLMUnavailableError("kein key")

    monkeypatch.setattr("app.strategies.llm.suggest_price", fake_suggest)

    with pytest.raises(StrategyError) as excinfo:
        compute_price(FakeProduct(), "llm", {"prompt_template": "x"})
    assert "nicht verfügbar" in str(excinfo.value)


def test_llm_strategy_propagates_response_error(monkeypatch):
    from app.llm import LLMResponseError

    def fake_suggest(template, whitelist):
        raise LLMResponseError("kaputtes JSON")

    monkeypatch.setattr("app.strategies.llm.suggest_price", fake_suggest)

    with pytest.raises(StrategyError) as excinfo:
        compute_price(FakeProduct(), "llm", {"prompt_template": "x"})
    assert "ungültig" in str(excinfo.value)


def test_llm_strategy_requires_prompt_template():
    with pytest.raises(StrategyError):
        compute_price(FakeProduct(), "llm", {})
