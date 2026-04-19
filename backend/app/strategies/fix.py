from decimal import Decimal

from app.models import Product
from app.strategies.base import StrategyError, SuggestionResult


def compute(product: Product, config: dict) -> SuggestionResult:
    amount = config.get("amount")
    if amount is None:
        raise StrategyError("Fixpreis-Strategie benötigt 'amount'")
    try:
        price = Decimal(str(amount))
    except Exception as exc:
        raise StrategyError(f"Ungültiger Betrag: {amount}") from exc
    if price < 0:
        raise StrategyError("Fixpreis darf nicht negativ sein")
    return SuggestionResult(
        price=price,
        reasoning="Fixpreis laut Konfiguration",
        inputs={"amount": str(price)},
    )
