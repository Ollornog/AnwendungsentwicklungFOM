"""Seed-Helper: Admin-User + Mock-Produkte.

Wird sowohl vom CLI-Skript `backend/seed.py` als auch vom DB-Reset-Endpoint
(`app/routers/settings.py`) genutzt. Idempotent pro Produktname.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PricingStrategy, Product, User
from app.security import hash_password


@dataclass
class SeedResult:
    user_created: bool
    user_missing_password: bool
    products_added: int


def ensure_admin_and_mock_products(
    db: Session,
    *,
    username: str,
    password: str,
    mock_products: Iterable[dict],
) -> SeedResult:
    """Legt Admin an (falls fehlt) und fuellt Mock-Produkte idempotent."""
    user = db.scalar(select(User).where(User.username == username))
    user_created = False
    if user is None:
        if not password:
            return SeedResult(
                user_created=False, user_missing_password=True, products_added=0
            )
        user = User(username=username, password_hash=hash_password(password), role="admin")
        db.add(user)
        db.flush()
        user_created = True

    existing_names = set(
        db.scalars(select(Product.name).where(Product.owner_id == user.id)).all()
    )
    added = 0
    for data in mock_products:
        if data["name"] in existing_names:
            continue
        strategy_spec = data["strategy"]
        fields = {k: v for k, v in data.items() if k != "strategy"}
        product = Product(owner_id=user.id, **fields)
        product.strategy = PricingStrategy(
            kind=strategy_spec["kind"], config=strategy_spec["config"]
        )
        db.add(product)
        added += 1
    db.commit()
    return SeedResult(
        user_created=user_created, user_missing_password=False, products_added=added
    )


def reset_database(db: Session, user_id) -> None:
    """Loescht fuer den angegebenen User alle Produkte + History + Settings.

    Behalten bleiben: der User selbst und andere Benutzer. Die `app_settings`
    sind global und werden mit geleert, damit ein API-Key-Override ebenfalls
    weg ist (der User hat das explizit ausgeloest).
    """
    from app.models import AppSetting, PriceHistory, PriceSuggestion, PricingStrategy

    # Nur die Produkte des Users – pricing_strategies/history haengen via FK
    # an den Produkten und werden durch ON DELETE CASCADE mitgenommen.
    db.query(Product).filter(Product.owner_id == user_id).delete(synchronize_session=False)
    # app_settings sind global (kein owner) – komplett leeren.
    db.query(AppSetting).delete(synchronize_session=False)
    # History und Suggestions, die aus irgendwelchen Gruenden nicht mitkaskadiert sind
    # (z. B. wenn user_id gesetzt war aber Produkt nicht geloescht wurde), bereinigen.
    db.query(PriceSuggestion).delete(synchronize_session=False)
    # PriceHistory des Users (falls user_id gesetzt und Produkt bereits weg ist).
    db.query(PriceHistory).filter(PriceHistory.user_id == user_id).delete(
        synchronize_session=False
    )
    db.commit()
