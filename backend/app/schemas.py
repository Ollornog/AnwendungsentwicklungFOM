import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    role: str


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    category: str = Field(min_length=1, max_length=64)
    cost_price: Decimal = Field(ge=0)
    stock: int = Field(ge=0)
    competitor_price: Decimal | None = Field(default=None, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    cost_price: Decimal | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    competitor_price: Decimal | None = Field(default=None, ge=0)


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


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    price: Decimal
    currency: str
    strategy: StrategyKind = Field(alias="strategy_kind")
    is_llm_suggestion: bool
    inputs: dict[str, Any]
    reasoning: str | None


class HistoryOut(BaseModel):
    items: list[HistoryItem]
