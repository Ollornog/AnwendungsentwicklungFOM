import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user_rate_limited as get_current_user
from app.llm import (
    LLMResponseError,
    LLMUnavailableError,
    preview_strategy_prompt,
    suggest_competitor_prices,
    suggest_strategy,
)
from app.models import PricingStrategy, Product, User
from app.services import app_settings as app_settings_svc
from app.schemas import (
    CompetitorPriceItem,
    CompetitorPricesResponse,
    ProductCreate,
    ProductList,
    ProductOut,
    ProductUpdate,
    StrategyOut,
    StrategyPromptPreview,
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


# Wichtig: dieser Endpoint muss VOR den {product_id}-Routen registriert
# sein, sonst interpretiert FastAPI "competitor-prices" als UUID-Parameter
# und gibt 422 zurueck.
@router.post("/competitor-prices/suggest", response_model=CompetitorPricesResponse)
def suggest_competitor_prices_endpoint(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CompetitorPricesResponse:
    """Laesst die KI fuer jedes Produkt einen Wettbewerbspreis schaetzen.

    Fuer die Demo genuegt eine plausible KI-Schaetzung; tatsaechliche Preis-
    recherche ist nicht noetig. Der User uebernimmt die Vorschlaege dann
    selbst pro Produkt (Human-in-the-Loop).
    """
    products = db.scalars(
        select(Product).where(Product.owner_id == user.id).order_by(Product.name)
    ).all()
    if not products:
        return CompetitorPricesResponse(items=[])

    payload = [
        {
            "id": str(p.id),
            "name": p.name,
            "category": p.category,
            "cost_price": str(p.cost_price),
            "current_competitor": (
                str(p.competitor_price) if p.competitor_price is not None else None
            ),
            "context": p.context or "",
        }
        for p in products
    ]
    api_key = app_settings_svc.gemini_api_key(db)
    try:
        llm_items = suggest_competitor_prices(payload, api_key=api_key)
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except LLMResponseError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    # KI-Antwort auf unsere Produkte mappen; Eintraege ohne Match
    # ignorieren, Reihenfolge stabil nach Produktname.
    by_id = {str(p.id): p for p in products}
    matched_items: list[CompetitorPriceItem] = []
    seen: set[str] = set()
    for it in llm_items:
        product = by_id.get(it.product_id)
        if product is None or it.product_id in seen:
            continue
        seen.add(it.product_id)
        matched_items.append(
            CompetitorPriceItem(
                id=product.id,
                name=product.name,
                category=product.category,
                current_competitor_price=product.competitor_price,
                suggested_price=it.price,
                reasoning=it.reasoning,
            )
        )
    return CompetitorPricesResponse(items=matched_items)


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

    # Auto-Snapshot in PriceHistory: dokumentiert zeitlich, wann welche
    # Strategie aktiv wurde und welchen Preis sie bei Default-Runtime
    # (hour=0, day=1, stock=start_stock, demand=1) geliefert haette.
    # Fehler im Snapshot (z. B. ungueltige Formel) blockieren den
    # Strategie-Save nicht – es ist ein Nice-to-have-Audit-Trail.
    try:
        from app.models import PriceHistory
        from app.strategies import compute_price

        result = compute_price(
            product, payload.kind, payload.config, runtime=None
        )
        db.add(
            PriceHistory(
                product_id=product.id,
                user_id=user.id,
                strategy=payload.kind,
                price=result.price,
                currency=result.currency,
                is_llm_suggestion=False,
                inputs=result.inputs,
                reasoning=(result.reasoning or "") + " · Snapshot bei Strategie-Aenderung",
            )
        )
        db.commit()
    except Exception:
        # Snapshot ist optional – Save-Flow nicht sprengen.
        db.rollback()

    return product.strategy


@router.post("/{product_id}/strategy/prompt-preview", response_model=StrategyPromptPreview)
def preview_prompt_endpoint(
    product_id: uuid.UUID,
    payload: StrategySuggestRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StrategyPromptPreview:
    """Gibt nur den Prompt zurueck, ohne das LLM aufzurufen.

    Wird vom Modal genutzt, um die Frage an die KI sichtbar zu machen,
    sobald der User "KI fragen" klickt – noch bevor die eigentliche
    (langsame) Antwort da ist.
    """
    product = _get_owned_product(db, user, product_id)
    whitelist = _strategy_whitelist(product)
    try:
        prompt = preview_strategy_prompt(
            payload.target, payload.online, whitelist, fancy=payload.fancy
        )
    except LLMResponseError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return StrategyPromptPreview(target=payload.target, online=payload.online, prompt=prompt)


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
        result = suggest_strategy(
            payload.target,
            payload.online,
            whitelist,
            api_key=api_key,
            fancy=payload.fancy,
        )
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except LLMResponseError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return StrategySuggestResponse(
        target=result.target,
        amount=result.amount,
        expression=result.expression,
        reasoning=result.reasoning,
        prompt=result.prompt,
    )
