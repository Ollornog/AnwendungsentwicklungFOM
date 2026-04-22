"""Audit-Protokoll fuer KI-Anfragen.

Append-only: eine Zeile pro Gemini-Aufruf, unabhaengig davon ob der
Call erfolgreich war oder mit einer Exception endete. Admin-only
einsehbar im Einstellungs-Dialog.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LLMAudit, User


# Schutz gegen versehentliches Befuellen der DB mit riesigen Gemini-
# Antworten (z. B. Fancy-Prompts). 16 KB reichen fuer Audit-Zwecke
# deutlich aus, der User kann im UI alles weitere nachvollziehen.
_MAX_TEXT = 16_000


def _clip(text: str | None) -> str | None:
    if text is None:
        return None
    if len(text) <= _MAX_TEXT:
        return text
    # Unicode-Indikator am Ende, damit klar ist, dass gekuerzt wurde.
    return text[: _MAX_TEXT - 20] + "\n…[gekuerzt]"


def record(
    db: Session,
    *,
    user: User,
    kind: str,
    prompt: str,
    success: bool,
    response_raw: str | None = None,
    error_message: str | None = None,
    duration_ms: int | None = None,
) -> LLMAudit:
    """Legt einen Audit-Eintrag an und committed ihn sofort.

    Bewusst eigener Commit, damit ein Audit-Eintrag auch dann uebrig
    bleibt, wenn der umgebende Request spaeter noch scheitert (z. B.
    nginx-Timeout). Bei Fehler im Insert wird die Exception
    weitergereicht – der Audit-Log ist nicht optional.
    """
    entry = LLMAudit(
        user_id=user.id,
        username=user.username,
        kind=kind,
        prompt=_clip(prompt) or "",
        response_raw=_clip(response_raw),
        success=success,
        error_message=_clip(error_message),
        duration_ms=duration_ms,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_recent(db: Session, *, limit: int = 200) -> list[LLMAudit]:
    """Neueste Eintraege zuerst."""
    stmt = select(LLMAudit).order_by(LLMAudit.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())
