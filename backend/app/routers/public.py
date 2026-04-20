"""Unauthentifizierte, oeffentliche Endpoints.

Gibt die Datenschutz-/Impressums-Seite genug Info, um die Deployment-
Domain anzuzeigen – ohne dass der Besucher eingeloggt sein muss.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import PublicInfo
from app.services import app_settings as svc

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/info", response_model=PublicInfo)
def public_info(db: Annotated[Session, Depends(get_db)]) -> PublicInfo:
    domain = svc.get(db, svc.HTTPS_DOMAIN)
    enabled = svc.get(db, svc.HTTPS_ENABLED) == "1"
    return PublicInfo(domain=domain, https_enabled=enabled)
