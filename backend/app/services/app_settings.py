"""Schmaler Wrapper um die `app_settings`-Tabelle.

Wird vom Settings-Endpoint und vom LLM-Pfad benutzt. Gibt der DB-Wert
Vorrang vor der Env-Konfiguration, sodass z. B. der GEMINI_API_KEY zur
Laufzeit per UI gewechselt werden kann.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AppSetting

GEMINI_API_KEY = "gemini_api_key"
HTTPS_ENABLED = "https_enabled"  # "1" wenn aktiv, sonst nicht gesetzt
HTTPS_DOMAIN = "https_domain"
RATE_LIMIT_DEFAULT = "rate_limit_default"  # Standardnutzer: default 50/Tag
RATE_LIMIT_ADMIN = "rate_limit_admin"  # Admin: default 200/Tag

DEFAULT_RATE_LIMIT_USER = 50
DEFAULT_RATE_LIMIT_ADMIN = 200


def get(db: Session, key: str) -> str | None:
    row = db.get(AppSetting, key)
    if row is None:
        return None
    return row.value


def set_value(db: Session, key: str, value: str) -> None:
    row = db.get(AppSetting, key)
    if row is None:
        db.add(AppSetting(key=key, value=value))
    else:
        row.value = value
    db.commit()


def delete(db: Session, key: str) -> None:
    row = db.get(AppSetting, key)
    if row is not None:
        db.delete(row)
        db.commit()


def gemini_api_key(db: Session) -> str:
    """DB-Wert zuerst, sonst Env (.env). Leerstring wenn keiner gesetzt."""
    db_value = get(db, GEMINI_API_KEY)
    if db_value:
        return db_value
    return get_settings().gemini_api_key or ""


def _int_setting(db: Session, key: str, default: int) -> int:
    raw = get(db, key)
    if raw is None:
        return default
    try:
        val = int(raw)
    except ValueError:
        return default
    return max(1, val)


def rate_limit_for(db: Session, *, is_admin: bool) -> int:
    """Taegliches Request-Limit fuer den gegebenen User-Typ.

    Admins bekommen den `RATE_LIMIT_ADMIN`-Wert (Default 200), alle
    anderen `RATE_LIMIT_DEFAULT` (Default 50). Beide per UI aenderbar.
    """
    if is_admin:
        return _int_setting(db, RATE_LIMIT_ADMIN, DEFAULT_RATE_LIMIT_ADMIN)
    return _int_setting(db, RATE_LIMIT_DEFAULT, DEFAULT_RATE_LIMIT_USER)
