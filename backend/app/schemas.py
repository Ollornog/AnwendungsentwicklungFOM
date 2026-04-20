import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=256)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    role: str


UserRole = Literal["admin", "viewer"]


class UserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    role: str
    created_at: datetime


class UserList(BaseModel):
    items: list[UserListItem]


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=6, max_length=256)
    role: UserRole = "admin"


class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=6, max_length=256)
    role: UserRole | None = None


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    category: str = Field(min_length=1, max_length=64)
    cost_price: Decimal = Field(ge=0)
    stock: int = Field(ge=0)
    competitor_price: Decimal | None = Field(default=None, ge=0)
    context: str = Field(default="", max_length=2000)
    monthly_demand: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    cost_price: Decimal | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    competitor_price: Decimal | None = Field(default=None, ge=0)
    context: str | None = Field(default=None, max_length=2000)
    monthly_demand: int | None = Field(default=None, ge=0)


StrategyKind = Literal["fix", "formula", "rule", "llm"]


class StrategyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kind: StrategyKind
    config: dict[str, Any]


class StrategyUpsert(BaseModel):
    kind: StrategyKind
    config: dict[str, Any]


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    strategy: StrategyOut | None = None


class ProductList(BaseModel):
    items: list[ProductOut]


class PriceRequest(BaseModel):
    """Runtime-Kontext fuer die Preisberechnung (aus Frontend-Simulation).

    Werte sind optional; wenn weggelassen, fallen Formeln auf Produkt-
    Defaults (stock=start_stock, hour=0, day=1, demand=50) zurueck.
    """

    hour: int | None = Field(default=None, ge=0, le=23)
    day: int | None = Field(default=None, ge=1, le=31)
    current_stock: int | None = Field(default=None, ge=0)
    # 0 = keine Nachfrage, 50 = normal, 100 = doppelt. Multipliziert
    # im Frontend den Lagerverbrauch; in Formeln als Variable `demand`.
    demand: int | None = Field(default=None, ge=0, le=100)


class PriceSuggestionOut(BaseModel):
    suggestion_token: str
    price: Decimal
    currency: str
    strategy: StrategyKind
    is_llm_suggestion: bool
    reasoning: str | None = None
    inputs: dict[str, Any]


class ConfirmRequest(BaseModel):
    suggestion_token: str


SuggestTarget = Literal["fix", "formula"]


class StrategySuggestRequest(BaseModel):
    target: SuggestTarget
    online: bool = False
    fancy: bool = False  # Demo-Flag: KI darf ruhig eine ausfuehrlichere Formel liefern.


class StrategySuggestResponse(BaseModel):
    target: SuggestTarget
    amount: Decimal | None = None
    expression: str | None = None
    reasoning: str
    prompt: str  # Transparenz: der tatsaechlich an die KI geschickte Text.


class StrategyPromptPreview(BaseModel):
    target: SuggestTarget
    online: bool
    prompt: str


class CompetitorPriceItem(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    current_competitor_price: Decimal | None
    suggested_price: Decimal
    reasoning: str


class CompetitorPricesResponse(BaseModel):
    items: list[CompetitorPriceItem]


class AppSettingsOut(BaseModel):
    """Read-only Sicht auf Laufzeit-Einstellungen.

    `gemini_api_key_set` zeigt nur, ob ein Key hinterlegt ist – nie den
    Klartext. `gemini_api_key_source` macht transparent, wo der aktuell
    aktive Key herkommt (DB-Override vs. Env aus .env).
    """

    gemini_api_key_set: bool
    gemini_api_key_source: Literal["db", "env", "none"]


class AppSettingsUpdate(BaseModel):
    # None = unveraendert lassen; "" = loeschen (zurueck auf Env-Default).
    gemini_api_key: str | None = None


class DatabaseResetResponse(BaseModel):
    products_created: int
    total_configured: int


class HTTPSStatus(BaseModel):
    enabled: bool
    domain: str | None = None


class HTTPSEnableRequest(BaseModel):
    domain: str = Field(
        min_length=4,
        max_length=253,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,}$",
    )


class HTTPSEnableResponse(BaseModel):
    enabled: bool
    domain: str
    output: str  # gekuerzter Klartext von certbot / Helper fuer Troubleshooting


class RateLimitConfig(BaseModel):
    """Tages-Rate-Limits. Werte min 1, sonst wuerde niemand mehr arbeiten."""

    default_per_day: int = Field(ge=1, le=100000)
    admin_per_day: int = Field(ge=1, le=100000)


class PublicInfo(BaseModel):
    """Oeffentliche Daten fuer die Legal-Seite (ohne Login)."""

    domain: str | None = None
    https_enabled: bool = False


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    price: Decimal
    currency: str
    strategy: StrategyKind
    is_llm_suggestion: bool
    inputs: dict[str, Any]
    reasoning: str | None
    username: str | None = None


class HistoryOut(BaseModel):
    items: list[HistoryItem]
