from app.models import Product
from app.strategies import fix, formula, llm, rule
from app.strategies.base import StrategyError, SuggestionResult

_REGISTRY = {
    "fix": fix.compute,
    "formula": formula.compute,
    "rule": rule.compute,
    "llm": llm.compute,
}


def compute_price(product: Product, kind: str, config: dict) -> SuggestionResult:
    compute_fn = _REGISTRY.get(kind)
    if compute_fn is None:
        raise StrategyError(f"Unbekannte Strategie: {kind}")
    return compute_fn(product, config)
