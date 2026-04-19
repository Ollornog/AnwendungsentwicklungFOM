import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.llm import LLMResponseError, LLMUnavailableError, suggest_strategy
from app.models import PricingStrategy, Product, User
from app.services import app_settings as app_settings_svc
from app.schemas import (
    ProductCreate,
    ProductList,
    ProductOut,
    ProductUpdate,
    StrategyOut,
    StrategySuggestRequest,
    StrategySuggestResponse,
    StrategyUpsert,
)

router = APIRouter(prefix="/products", tags=["products"])


def _strategy_whitelist(product: Product) -> dict:
    """Nur diese Felder gehen an das LLM. Keine Kundendaten."""
    return {
        "name": product.name,
        "category": product.category,
        "cost_price": str(product.cost_price),
        "competitor_price": (
            str(product.competitor_price) if product.competitor_price is not None else None
        ),
        "stock": product.stock,
        "monthly_demand": product.monthly_demand,
        "context": product.context,
    }


def _get_owned_product(db: Session, user: User, product_id: uuid.UUID) -> Product:
    product = db.get(Product, product_id)
    if product is None or product.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produkt nicht gefunden")
    return product


@router.get("", response_model=ProductList)
def list_products(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProductList:
    products = db.scalars(
        select(Product).where(Product.owner_id == user.id).order_by(Product.created_at.desc())
    ).all()
    return ProductList(items=[ProductOut.model_validate(p) for p in products])


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    product = Product(owner_id=user.id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    return _get_owned_product(db, user, product_id)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    product = _get_owned_product(db, user, product_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    product = _get_owned_product(db, user, product_id)
    db.delete(product)
    db.commit()


@router.put("/{product_id}/strategy", response_model=StrategyOut)
def upsert_strategy(
    product_id: uuid.UUID,
    payload: StrategyUpsert,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PricingStrategy:
    product = _get_owned_product(db, user, product_id)
    if product.strategy is None:
        product.strategy = PricingStrategy(
            product_id=product.id, kind=payload.kind, config=payload.config
        )
    else:
        product.strategy.kind = payload.kind
        product.strategy.config = payload.config
    db.commit()
    db.refresh(product.strategy)
    return product.strategy


@router.post("/{product_id}/strategy/suggest", response_model=StrategySuggestResponse)
def suggest_strategy_endpoint(
    product_id: uuid.UUID,
    payload: StrategySuggestRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StrategySuggestResponse:
    product = _get_owned_product(db, user, product_id)
    whitelist = _strategy_whitelist(product)
    api_key = app_settings_svc.gemini_api_key(db)
    try:
        result = suggest_strategy(payload.target, payload.online, whitelist, api_key=api_key)
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except LLMResponseError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return StrategySuggestResponse(
        target=result.target,
        amount=result.amount,
        expression=result.expression,
        reasoning=result.reasoning,
    )
