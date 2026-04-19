from app.models import Product
from app.strategies.base import StrategyError, SuggestionResult
from app.strategies.evaluator import ExpressionError, evaluate, evaluate_decimal
from app.strategies.runtime import build_variables


def compute(
    product: Product,
    config: dict,
    runtime: dict | None = None,
) -> SuggestionResult:
    rules = config.get("rules")
    fallback = config.get("fallback")
    if not isinstance(rules, list):
        raise StrategyError("Regel-Strategie benötigt 'rules' als Liste")
    if not isinstance(fallback, str) or not fallback.strip():
        raise StrategyError("Regel-Strategie benötigt 'fallback' als Ausdruck")

    variables = build_variables(product, runtime)

    for idx, rule in enumerate(rules):
        if not isinstance(rule, dict) or "when" not in rule or "then" not in rule:
            raise StrategyError(f"Regel {idx} braucht 'when' und 'then'")
        try:
            matched = evaluate(rule["when"], variables)
        except ExpressionError as exc:
            raise StrategyError(f"Regel {idx} fehlerhaft: {exc}") from exc
        if bool(matched):
            try:
                price = evaluate_decimal(rule["then"], variables)
            except ExpressionError as exc:
                raise StrategyError(f"Regel {idx} 'then' fehlerhaft: {exc}") from exc
            if price < 0:
                raise StrategyError("Berechneter Preis darf nicht negativ sein")
            return SuggestionResult(
                price=price,
                reasoning=f"Regel {idx} ausgelöst: wenn {rule['when']} dann {rule['then']}",
                inputs={k: str(v) for k, v in variables.items()},
            )

    try:
        price = evaluate_decimal(fallback, variables)
    except ExpressionError as exc:
        raise StrategyError(f"Fallback fehlerhaft: {exc}") from exc
    if price < 0:
        raise StrategyError("Berechneter Preis darf nicht negativ sein")
    return SuggestionResult(
        price=price,
        reasoning=f"Keine Regel griff, Fallback: {fallback}",
        inputs={k: str(v) for k, v in variables.items()},
    )
