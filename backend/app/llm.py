"""Minimaler Gemini-Client.

Wichtig: Es werden ausschließlich die vom Backend übergebenen Produkt-Whitelist-Felder
gesendet. Keine personenbezogenen Daten, keine Kundendaten (siehe docs/compliance.md).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.config import get_settings


class LLMUnavailableError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


@dataclass
class LLMSuggestion:
    price: Decimal
    reasoning: str


_RESPONSE_SCHEMA_HINT = (
    'Antworte ausschließlich als JSON in der Form '
    '{"price": <Zahl>, "currency": "EUR", "reasoning": "<kurz>"}. '
    "Keine zusätzlichen Felder, kein Freitext um das JSON."
)


def _build_prompt(template: str, whitelist: dict[str, Any]) -> str:
    try:
        body = template.format(**whitelist)
    except KeyError as exc:
        raise LLMResponseError(f"Prompt-Vorlage referenziert unbekannte Variable: {exc}") from exc
    return f"{body}\n\n{_RESPONSE_SCHEMA_HINT}"


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text[:-3]
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(f"Antwort war kein JSON: {exc}") from exc


def suggest_price(prompt_template: str, whitelist: dict[str, Any]) -> LLMSuggestion:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise LLMUnavailableError("GEMINI_API_KEY ist nicht gesetzt")

    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise LLMUnavailableError("google-generativeai ist nicht installiert") from exc

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = _build_prompt(prompt_template, whitelist)
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    text = getattr(response, "text", None)
    if not text:
        raise LLMResponseError("Leere Antwort vom LLM")
    payload = _parse_json(text)

    price_raw = payload.get("price")
    reasoning = payload.get("reasoning", "")
    if price_raw is None:
        raise LLMResponseError("LLM-Antwort ohne 'price'-Feld")
    try:
        price = Decimal(str(price_raw)).quantize(Decimal("0.01"))
    except Exception as exc:
        raise LLMResponseError(f"Ungültiger Preis vom LLM: {price_raw}") from exc
    if price < 0:
        raise LLMResponseError("LLM schlug negativen Preis vor")
    return LLMSuggestion(price=price, reasoning=str(reasoning)[:500])
