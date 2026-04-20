"""Runtime-Variablen fuer Formel-/Regel-Strategien.

Mischung aus statischen Produktdaten (DB), optionalen Simulations-Werten
vom Client (aktueller Lagerbestand, Uhrzeit, Tag) und der Konstante `pi`,
die fuer glatte periodische Formeln nuetzlich ist.
"""


import math
from decimal import Decimal
from typing import Any

from app.models import Product

_PI = Decimal(str(math.pi))


def build_variables(product: Product, runtime: dict | None) -> dict[str, Any]:
    rt = runtime or {}
    competitor = (
        product.competitor_price if product.competitor_price is not None else Decimal("0")
    )
    current_stock = rt.get("current_stock")
    hour = rt.get("hour")
    day_raw = rt.get("day")
    day = 1 if day_raw is None else int(day_raw)
    demand = rt.get("demand")
    # weekday: 1 = Montag, 7 = Sonntag. Tag 1/8/15/22 ist Montag usw.
    weekday = ((day - 1) % 7) + 1
    return {
        # statisch aus DB
        "cost_price": product.cost_price,
        "competitor_price": competitor,
        "monthly_demand": product.monthly_demand,
        "start_stock": product.stock,
        # runtime (mit sinnvollen Defaults, falls Client nichts mitschickt)
        "stock": product.stock if current_stock is None else current_stock,
        "hour": 0 if hour is None else hour,
        "day": day,
        "weekday": weekday,
        # Nachfrage-Faktor 0..2; 1 = normal. Fuer Formeln verfuegbar,
        # im Frontend zusaetzlich als Multiplikator des Lagerverbrauchs.
        "demand": Decimal("1") if demand is None else Decimal(str(demand)),
        # Konstante fuer periodische Formeln (sin/cos)
        "pi": _PI,
    }


ALLOWED_VARIABLES = (
    "cost_price",
    "competitor_price",
    "monthly_demand",
    "start_stock",
    "stock",
    "hour",
    "day",
    "weekday",
    "demand",
    "pi",
)

ALLOWED_FUNCTIONS = (
    "sqrt",
    "pow",
    "abs",
    "min",
    "max",
    "round",
    "floor",
    "ceil",
    "mod",
    "sin",
    "cos",
)
