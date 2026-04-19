"""Seed: legt einen Admin-User und Mock-Produkte an, falls noch keine existieren.

Aufruf (mit aktiver venv):
    python -m seed --username admin --password <pw>
"""
from __future__ import annotations

import argparse
import sys
from decimal import Decimal

from sqlalchemy import select

from app.db import SessionLocal
from app.models import PricingStrategy, Product, User
from app.security import hash_password


MOCK_PRODUCTS = [
    {
        "name": "Sneaker Classic",
        "category": "Schuhe",
        "cost_price": Decimal("29.90"),
        "stock": 42,
        "competitor_price": Decimal("59.00"),
        "strategy": {
            "kind": "formula",
            "config": {"expression": "cost_price * 1.8"},
        },
    },
    {
        "name": "Basic T-Shirt",
        "category": "Bekleidung",
        "cost_price": Decimal("4.50"),
        "stock": 120,
        "competitor_price": Decimal("14.90"),
        "strategy": {
            "kind": "rule",
            "config": {
                "rules": [
                    {"when": "stock < 20", "then": "cost_price * 2.5"},
                    {"when": "competitor_price > 0", "then": "competitor_price - 1"},
                ],
                "fallback": "cost_price * 2",
            },
        },
    },
    {
        "name": "Kaffeebohnen 1kg",
        "category": "Lebensmittel",
        "cost_price": Decimal("9.80"),
        "stock": 30,
        "competitor_price": Decimal("18.50"),
        "strategy": {
            "kind": "llm",
            "config": {
                "prompt_template": (
                    "Schlage einen marktgerechten Verkaufspreis für '{name}' "
                    "(Kategorie {category}) vor. Einkaufspreis {cost_price} EUR, "
                    "Lagerbestand {stock}, Wettbewerber-Preis {competitor_price} EUR. "
                    "Ziel: Marge ca. 40-60%."
                )
            },
        },
    },
]


def seed(username: str, password: str) -> None:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, password_hash=hash_password(password), role="admin")
            db.add(user)
            db.flush()
            print(f"User '{username}' angelegt.")
        else:
            print(f"User '{username}' existiert bereits.")

        existing = db.scalar(select(Product).where(Product.owner_id == user.id))
        if existing is not None:
            print("Produkte existieren bereits, überspringe Mock-Daten.")
            db.commit()
            return

        for data in MOCK_PRODUCTS:
            strategy_spec = data.pop("strategy")
            product = Product(owner_id=user.id, **data)
            product.strategy = PricingStrategy(
                kind=strategy_spec["kind"], config=strategy_spec["config"]
            )
            db.add(product)
        db.commit()
        print(f"{len(MOCK_PRODUCTS)} Mock-Produkte angelegt.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    seed(args.username, args.password)
    return 0


if __name__ == "__main__":
    sys.exit(main())
