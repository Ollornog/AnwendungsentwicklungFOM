"""Seed-Helper: Admin-User + Mock-Produkte.

Wird sowohl vom CLI-Skript `backend/seed.py` als auch vom DB-Reset-Endpoint
(`app/routers/settings.py`) genutzt. Idempotent pro Produktname.
"""


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
    extra_users_added: int = 0


def ensure_admin_and_mock_products(
    db: Session,
    *,
    username: str,
    password: str,
    mock_products: Iterable[dict],
    mock_users: Iterable[dict] | None = None,
) -> SeedResult:
    """Legt Admin an (falls fehlt), fuellt Mock-Produkte und Demo-User idempotent."""
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

    extra_users_added = ensure_demo_users(db, mock_users or [])

    db.commit()
    return SeedResult(
        user_created=user_created,
        user_missing_password=False,
        products_added=added,
        extra_users_added=extra_users_added,
    )


def ensure_demo_users(db: Session, mock_users: Iterable[dict]) -> int:
    """Sorgt dafuer, dass die Team-Demo-Accounts existieren.

    Idempotent pro Username: bestehende Accounts werden nicht angefasst
    (auch kein Passwort-Reset). Rueckgabe: Anzahl neu angelegter User.
    """
    added = 0
    for spec in mock_users:
        username = spec.get("username")
        if not username:
            continue
        if db.scalar(select(User).where(User.username == username)) is not None:
            continue
        db.add(
            User(
                username=username,
                password_hash=hash_password(spec["password"]),
                role=spec.get("role", "admin"),
            )
        )
        added += 1
    return added


def reset_database(db: Session, user_id) -> None:
    """Loescht fuer den angegebenen User alle Produkte + History.

    Behalten bleiben:
      - der User selbst (inkl. Passwort-Hash) und andere Benutzer
      - `app_settings` (insbesondere der per UI gesetzte Gemini-API-Key)

    Produkte loeschen kaskadiert ueber FK-ON-DELETE die daran haengenden
    Strategien und PriceHistory-Eintraege; offene PriceSuggestions werden
    ebenfalls mitgenommen.
    """
    from app.models import PriceHistory, PriceSuggestion

    # Produkte des Users – pricing_strategies/history/suggestions haengen
    # per FK CASCADE dran und werden mitgenommen.
    db.query(Product).filter(Product.owner_id == user_id).delete(synchronize_session=False)
    # Waisen-Cleanup: PriceSuggestion und History-Zeilen ohne Produkt-
    # Bezug (Edge-Cases) entfernen wir sicherheitshalber auch.
    db.query(PriceSuggestion).delete(synchronize_session=False)
    db.query(PriceHistory).filter(PriceHistory.user_id == user_id).delete(
        synchronize_session=False
    )
    db.commit()
