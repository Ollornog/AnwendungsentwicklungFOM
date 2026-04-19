from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.deps import get_current_user
from app.mock_data import MOCK_PRODUCTS
from app.models import User
from app.schemas import AppSettingsOut, AppSettingsUpdate, DatabaseResetResponse
from app.services import app_settings as svc
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
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AppSettingsOut:
    return _build_view(db)


@router.put("", response_model=AppSettingsOut)
def update_settings(
    payload: AppSettingsUpdate,
    user: Annotated[User, Depends(get_current_user)],
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
        db, username=user.username, password="", mock_products=MOCK_PRODUCTS
    )
    return DatabaseResetResponse(
        products_created=result.products_added,
        total_configured=len(MOCK_PRODUCTS),
    )
