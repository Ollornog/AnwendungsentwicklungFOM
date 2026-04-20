from datetime import date as _date
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ApiRateUsage, User
from app.services import app_settings as _app_settings

# Usernames mit Admin-Sonderrechten. Aktuell nur der bootstrap-Admin.
_ADMIN_USERNAMES = {"admin"}


def _is_admin(user: User) -> bool:
    return user.username in _ADMIN_USERNAMES or user.role == "admin"


def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nicht authentifiziert")
    user = db.get(User, user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sitzung ungültig")
    return user


def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Gate fuer Admin-only-Endpoints (Users-/HTTPS-/Rate-Limit-Verwaltung)."""
    if user.username not in _ADMIN_USERNAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur fuer den Admin-Account verfuegbar",
        )
    return user


def get_current_user_rate_limited(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Liefert den User und bucht einen API-Call auf das Tageskontingent.

    Zaehler pro (user_id, day) werden in `api_rate_usage` gehalten.
    Bei Ueberschreitung 429. Admin hat ein eigenes (hoeheres) Limit.
    Settings-Endpoints nutzen absichtlich `get_current_user` / `get_current_admin`
    direkt, damit ein selbst-ausgesperrter Admin sich nicht ueberdies
    per Einstellungsseite entsperren muesste.
    """
    today = _date.today()
    # Kein FOR UPDATE – fuer eine Semester-Demo genuegt optimistische
    # Parallelitaet. Bei echter Last gehoerte hier ein Row-Lock oder ein
    # atomares UPSERT.
    row = (
        db.query(ApiRateUsage)
        .filter(ApiRateUsage.user_id == user.id, ApiRateUsage.day == today)
        .one_or_none()
    )
    if row is None:
        row = ApiRateUsage(user_id=user.id, day=today, count=0)
        db.add(row)
        db.flush()

    limit = _app_settings.rate_limit_for(db, is_admin=_is_admin(user))
    if row.count >= limit:
        # Wir commit'en nicht, der Counter bleibt auf dem erreichten Stand.
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Tageslimit von {limit} Anfragen erreicht. Morgen gilt wieder das volle Kontingent.",
        )

    row.count += 1
    db.commit()
    return user
