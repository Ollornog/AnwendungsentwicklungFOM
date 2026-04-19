from app.models import Product
from app.strategies.base import StrategyError, SuggestionResult
from app.strategies.evaluator import ExpressionError, evaluate_decimal
from app.strategies.runtime import build_variables


def compute(
    product: Product,
    config: dict,
    runtime: dict | None = None,
) -> SuggestionResult:
    expression = config.get("expression")
    if not isinstance(expression, str) or not expression.strip():
        raise StrategyError("Formel-Strategie benötigt 'expression'")
    variables = build_variables(product, runtime)
    try:
        price = evaluate_decimal(expression, variables)
    except ExpressionError as exc:
        raise StrategyError(f"Formel-Auswertung fehlgeschlagen: {exc}") from exc
    if price < 0:
        raise StrategyError("Berechneter Preis darf nicht negativ sein")
    return SuggestionResult(
        price=price,
        reasoning=f"Formel: {expression}",
        inputs={k: str(v) for k, v in variables.items()},
    )
