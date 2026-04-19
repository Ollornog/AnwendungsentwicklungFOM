from decimal import Decimal

from app.models import Product
from app.strategies import fix, formula, llm, rule
from app.strategies.base import StrategyError, SuggestionResult

_REGISTRY = {
    "fix": fix.compute,
    "formula": formula.compute,
    "rule": rule.compute,
    "llm": llm.compute,
}

_PRICE_QUANTUM = Decimal("0.01")


def compute_price(product: Product, kind: str, config: dict) -> SuggestionResult:
    compute_fn = _REGISTRY.get(kind)
    if compute_fn is None:
        raise StrategyError(f"Unbekannte Strategie: {kind}")
    result = compute_fn(product, config)
    result.price = Decimal(result.price).quantize(_PRICE_QUANTUM)
    return result
