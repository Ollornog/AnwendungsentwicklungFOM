import re
import subprocess
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.deps import get_current_admin, get_current_user
from app.mock_data import MOCK_PRODUCTS, MOCK_USERS
from app.models import User
from app.schemas import (
    AppSettingsOut,
    AppSettingsUpdate,
    DatabaseResetResponse,
    HTTPSEnableRequest,
    HTTPSEnableResponse,
    HTTPSStatus,
    LLMAuditList,
    RateLimitConfig,
)
from app.services import app_settings as svc
from app.services import llm_audit
from app.services import seeding

router = APIRouter(prefix="/settings", tags=["settings"])


def _build_view(db: Session) -> AppSettingsOut:
    db_value = svc.get(db, svc.GEMINI_API_KEY)
    env_value = get_settings().gemini_api_key or ""
    if db_value:
        source = "db"
        is_set = True
    elif env_value:
        source = "env"
        is_set = True
    else:
        source = "none"
        is_set = False
    return AppSettingsOut(gemini_api_key_set=is_set, gemini_api_key_source=source)


@router.get("", response_model=AppSettingsOut)
def get_settings_view(
    user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> AppSettingsOut:
    return _build_view(db)


@router.put("", response_model=AppSettingsOut)
def update_settings(
    payload: AppSettingsUpdate,
    user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> AppSettingsOut:
    if payload.gemini_api_key is not None:
        # Leerstring -> Override loeschen, Env wird wieder wirksam.
        if payload.gemini_api_key.strip() == "":
            svc.delete(db, svc.GEMINI_API_KEY)
        else:
            svc.set_value(db, svc.GEMINI_API_KEY, payload.gemini_api_key.strip())
    return _build_view(db)


@router.post(
    "/reset-database",
    response_model=DatabaseResetResponse,
    status_code=status.HTTP_200_OK,
)
def reset_database_endpoint(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DatabaseResetResponse:
    """Setzt die Daten auf den Seed-Stand zurueck.

    Loescht alle Produkte (damit per CASCADE auch Strategien, History und
    Suggestions), leert `app_settings` und legt die Mock-Produkte neu an.
    Der Admin-User bleibt erhalten.
    """
    seeding.reset_database(db, user.id)
    result = seeding.ensure_admin_and_mock_products(
        db,
        username=user.username,
        password="",
        mock_products=MOCK_PRODUCTS,
        mock_users=MOCK_USERS,
    )
    return DatabaseResetResponse(
        products_created=result.products_added,
        total_configured=len(MOCK_PRODUCTS),
    )


# --- HTTPS via Let's Encrypt ---------------------------------------------

_HTTPS_HELPER = "/usr/local/bin/preisopt-https-enable"
# defense in depth: domain muss zusaetzlich zu Pydantic auch hier passen.
_DOMAIN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,}$")


@router.get("/https", response_model=HTTPSStatus)
def get_https_status(
    user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> HTTPSStatus:
    enabled = svc.get(db, svc.HTTPS_ENABLED) == "1"
    domain = svc.get(db, svc.HTTPS_DOMAIN)
    return HTTPSStatus(enabled=enabled, domain=domain)


@router.post("/https/enable", response_model=HTTPSEnableResponse)
def enable_https(
    payload: HTTPSEnableRequest,
    user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> HTTPSEnableResponse:
    """Ruft das Helper-Skript auf, um Let's Encrypt via certbot zu holen.

    Das Helper-Skript laeuft unter root (sudoers.d/preisopt erlaubt
    genau diesen einen Befehl). Der Backend-User `preisopt` hat keine
    weiteren root-Rechte.
    """
    domain = payload.domain.strip().lower()
    if not _DOMAIN_RE.match(domain):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ungueltige Domain")

    try:
        proc = subprocess.run(
            ["sudo", "-n", _HTTPS_HELPER, domain],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Helper-Skript nicht installiert. install.sh erneut ausfuehren.",
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout beim Zertifikatsabruf. DNS und Port 80/443 pruefen.",
        ) from exc

    output = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    # Letzte 2 KB reichen fuer die Anzeige; lange certbot-Logs abschneiden.
    if len(output) > 2000:
        output = output[-2000:]

    if proc.returncode != 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTTPS-Aktivierung fehlgeschlagen (rc={proc.returncode}):\n{output}",
        )

    svc.set_value(db, svc.HTTPS_ENABLED, "1")
    svc.set_value(db, svc.HTTPS_DOMAIN, domain)
    return HTTPSEnableResponse(enabled=True, domain=domain, output=output)


# --- Rate Limiting -------------------------------------------------------


@router.get("/rate-limit", response_model=RateLimitConfig)
def get_rate_limit(
    user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> RateLimitConfig:
    return RateLimitConfig(
        default_per_day=svc.rate_limit_for(db, is_admin=False),
        admin_per_day=svc.rate_limit_for(db, is_admin=True),
    )


@router.put("/rate-limit", response_model=RateLimitConfig)
def update_rate_limit(
    payload: RateLimitConfig,
    user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> RateLimitConfig:
    svc.set_value(db, svc.RATE_LIMIT_DEFAULT, str(payload.default_per_day))
    svc.set_value(db, svc.RATE_LIMIT_ADMIN, str(payload.admin_per_day))
    return RateLimitConfig(
        default_per_day=svc.rate_limit_for(db, is_admin=False),
        admin_per_day=svc.rate_limit_for(db, is_admin=True),
    )


# --- LLM-Audit-Protokoll -------------------------------------------------


@router.get("/llm-audit", response_model=LLMAuditList)
def get_llm_audit(
    user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 200,
) -> LLMAuditList:
    """Audit-Eintraege aller KI-Anfragen, neueste zuerst.

    Admin-only: Team-/Demo-Accounts haben keinen Zugriff. `limit` ist
    zwischen 1 und 500 geklemmt – reicht fuer die Demo; echtes Paging
    braeuchte eine Cursor-Variante.
    """
    limit = max(1, min(500, limit))
    items = llm_audit.list_recent(db, limit=limit)
    return LLMAuditList(items=items)
