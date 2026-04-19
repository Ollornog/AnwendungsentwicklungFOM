"""Runtime-Variablen fuer Formel-/Regel-Strategien.

Mischung aus statischen Produktdaten (DB) und optionalen Simulations-Werten
vom Client (aktueller Lagerbestand, Uhrzeit, Tag, Verbrauch).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.models import Product


def build_variables(product: Product, runtime: dict | None) -> dict[str, Any]:
    rt = runtime or {}
    competitor = (
        product.competitor_price if product.competitor_price is not None else Decimal("0")
    )
    current_stock = rt.get("current_stock")
    usage = rt.get("usage")
    hour = rt.get("hour")
    day = rt.get("day")
    return {
        # statisch aus DB
        "cost_price": product.cost_price,
        "competitor_price": competitor,
        "monthly_demand": product.monthly_demand,
        "start_stock": product.stock,
        # runtime (mit sinnvollen Defaults, falls Client nichts mitschickt)
        "stock": product.stock if current_stock is None else current_stock,
        "usage": product.daily_usage if usage is None else usage,
        "hour": 0 if hour is None else hour,
        "day": 1 if day is None else day,
    }


ALLOWED_VARIABLES = (
    "cost_price",
    "competitor_price",
    "monthly_demand",
    "start_stock",
    "stock",
    "usage",
    "hour",
    "day",
)
