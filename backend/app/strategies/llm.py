from decimal import Decimal

from app.llm import LLMResponseError, LLMUnavailableError, suggest_price
from app.models import Product
from app.strategies.base import StrategyError, SuggestionResult


_WHITELIST_FIELDS = ("name", "category", "cost_price", "stock", "competitor_price")


def _whitelist(product: Product) -> dict:
    return {
        "name": product.name,
        "category": product.category,
        "cost_price": str(product.cost_price),
        "stock": product.stock,
        "competitor_price": str(product.competitor_price) if product.competitor_price is not None else None,
    }


def compute(product: Product, config: dict, api_key: str | None = None) -> SuggestionResult:
    template = config.get("prompt_template")
    if not isinstance(template, str) or not template.strip():
        raise StrategyError("LLM-Strategie benötigt 'prompt_template'")

    whitelist = _whitelist(product)
    try:
        suggestion = suggest_price(template, whitelist, api_key=api_key)
    except LLMUnavailableError as exc:
        raise StrategyError(f"LLM nicht verfügbar: {exc}") from exc
    except LLMResponseError as exc:
        raise StrategyError(f"LLM-Antwort ungültig: {exc}") from exc

    price = Decimal(suggestion.price).quantize(Decimal("0.01"))
    return SuggestionResult(
        price=price,
        is_llm_suggestion=True,
        reasoning=suggestion.reasoning,
        inputs=whitelist,
    )
