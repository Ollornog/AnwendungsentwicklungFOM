import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.deps import get_current_user
from app.models import PriceHistory, PriceSuggestion, Product, User
from app.schemas import (
    ConfirmRequest,
    HistoryItem,
    HistoryOut,
    PriceRequest,
    PriceSuggestionOut,
)
from app.services import app_settings as app_settings_svc
from app.strategies import StrategyError, compute_price

router = APIRouter(prefix="/products/{product_id}", tags=["pricing"])


def _get_owned_product(db: Session, user: User, product_id: uuid.UUID) -> Product:
    product = db.get(Product, product_id)
    if product is None or product.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produkt nicht gefunden")
    return product


@router.post("/price", response_model=PriceSuggestionOut)
def request_price(
    product_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    payload: PriceRequest | None = None,
) -> PriceSuggestionOut:
    product = _get_owned_product(db, user, product_id)
    if product.strategy is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Keine Strategie konfiguriert")

    runtime = payload.model_dump(exclude_none=True) if payload is not None else None
    api_key = app_settings_svc.gemini_api_key(db) if product.strategy.kind == "llm" else None
    try:
        result = compute_price(
            product, product.strategy.kind, product.strategy.config, runtime, api_key=api_key
        )
    except StrategyError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    ttl = timedelta(minutes=get_settings().suggestion_ttl_minutes)
    suggestion = PriceSuggestion(
        token=secrets.token_urlsafe(32),
        product_id=product.id,
        strategy=product.strategy.kind,
        price=result.price,
        currency=result.currency,
        is_llm_suggestion=result.is_llm_suggestion,
        inputs=result.inputs,
        reasoning=result.reasoning,
        expires_at=datetime.now(timezone.utc) + ttl,
    )
    db.add(suggestion)
    db.commit()

    return PriceSuggestionOut(
        suggestion_token=suggestion.token,
        price=result.price,
        currency=result.currency,
        strategy=product.strategy.kind,
        is_llm_suggestion=result.is_llm_suggestion,
        reasoning=result.reasoning,
        inputs=result.inputs,
    )


@router.post("/price/confirm", status_code=status.HTTP_201_CREATED)
def confirm_price(
    product_id: uuid.UUID,
    payload: ConfirmRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    product = _get_owned_product(db, user, product_id)
    suggestion = db.get(PriceSuggestion, payload.suggestion_token)
    if suggestion is None or suggestion.product_id != product.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vorschlag unbekannt")
    if suggestion.expires_at < datetime.now(timezone.utc):
        db.delete(suggestion)
        db.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Vorschlag abgelaufen")

    entry = PriceHistory(
        product_id=product.id,
        strategy=suggestion.strategy,
        price=suggestion.price,
        currency=suggestion.currency,
        is_llm_suggestion=suggestion.is_llm_suggestion,
        inputs=suggestion.inputs,
        reasoning=suggestion.reasoning,
    )
    db.add(entry)
    db.delete(suggestion)
    db.commit()
    db.refresh(entry)
    return {"id": str(entry.id)}


@router.get("/history", response_model=HistoryOut)
def get_history(
    product_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> HistoryOut:
    product = _get_owned_product(db, user, product_id)
    rows = db.scalars(
        select(PriceHistory)
        .where(PriceHistory.product_id == product.id)
        .order_by(PriceHistory.created_at.desc())
    ).all()
    return HistoryOut(items=[HistoryItem.model_validate(r) for r in rows])
