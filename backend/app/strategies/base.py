from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


class StrategyError(Exception):
    """Fehler bei Konfiguration oder Ausführung einer Preisstrategie."""


@dataclass
class SuggestionResult:
    price: Decimal
    currency: str = "EUR"
    is_llm_suggestion: bool = False
    reasoning: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
