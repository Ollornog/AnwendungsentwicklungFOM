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


@dataclass
class LLMStrategySuggestion:
    """Von der KI vorgeschlagene Strategie (Fixpreis oder Formel)."""

    target: str  # "fix" | "formula"
    amount: Decimal | None
    expression: str | None
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


def _load_genai():
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise LLMUnavailableError("google-generativeai ist nicht installiert") from exc
    return genai


def _generate(
    prompt: str,
    *,
    online: bool,
    as_json: bool,
    api_key: str | None = None,
) -> str:
    settings = get_settings()
    effective_key = api_key if api_key else settings.gemini_api_key
    if not effective_key:
        raise LLMUnavailableError("GEMINI_API_KEY ist nicht gesetzt")
    genai = _load_genai()
    genai.configure(api_key=effective_key)

    # Google-Search-Grounding fuer den Online-Modus.
    # Die Tool-API hat sich zwischen Gemini-Modellen geaendert; wir
    # versuchen es optimistisch, fallen bei Fehlern auf einen reinen
    # Prompt-Hinweis zurueck (siehe suggest_strategy()).
    model_kwargs: dict[str, Any] = {}
    if online:
        model_kwargs["tools"] = [{"google_search_retrieval": {}}]

    try:
        model = genai.GenerativeModel(settings.gemini_model, **model_kwargs)
        gen_config = {"response_mime_type": "application/json"} if as_json else {}
        response = model.generate_content(prompt, generation_config=gen_config)
    except Exception:
        if online:
            # Fallback ohne Tool – Prompt enthaelt bereits den Online-Hinweis.
            model = genai.GenerativeModel(settings.gemini_model)
            gen_config = {"response_mime_type": "application/json"} if as_json else {}
            response = model.generate_content(prompt, generation_config=gen_config)
        else:
            raise

    text = getattr(response, "text", None)
    if not text:
        raise LLMResponseError("Leere Antwort vom LLM")
    return text


def suggest_price(
    prompt_template: str,
    whitelist: dict[str, Any],
    api_key: str | None = None,
) -> LLMSuggestion:
    prompt = _build_prompt(prompt_template, whitelist)
    text = _generate(prompt, online=False, as_json=True, api_key=api_key)
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


_ALLOWED_FORMULA_VARS = (
    "cost_price",
    "competitor_price",
    "monthly_demand",
    "start_stock",
    "stock",
    "usage",
    "hour",
    "day",
)


def _strategy_prompt(target: str, online: bool, whitelist: dict[str, Any]) -> str:
    context = (whitelist.get("context") or "").strip() or "—"
    competitor = whitelist.get("competitor_price")
    competitor_txt = competitor if competitor is not None else "—"
    base = (
        "Du bist ein Preis-Assistent fuer einen kleinen Online-Shop. "
        "Der Shop-Betreiber legt den Preis final fest, dein Vorschlag wird "
        "als Empfehlung gekennzeichnet (Human-in-the-Loop).\n\n"
        f"Produkt: {whitelist.get('name')}\n"
        f"Kategorie: {whitelist.get('category')}\n"
        f"Einkaufspreis: {whitelist.get('cost_price')} EUR\n"
        f"Wettbewerbspreis: {competitor_txt} EUR\n"
        f"Startbestand: {whitelist.get('stock')}\n"
        f"Nachfrage pro Monat: {whitelist.get('monthly_demand')}\n"
        f"Kontext: {context}\n"
    )
    if online:
        base += (
            "\nRecherchiere marktuebliche Online-Preise fuer vergleichbare "
            "Produkte in Deutschland und beziehe die Ergebnisse in deine "
            "Empfehlung ein.\n"
        )
    if target == "fix":
        base += (
            '\nAntworte als JSON: {"price": <Zahl>, "reasoning": "<kurz, max 2 Saetze>"}. '
            "Kein Freitext drum herum."
        )
    else:  # formula
        vars_list = ", ".join(_ALLOWED_FORMULA_VARS)
        base += (
            "\nSchlage eine Preisformel vor. Erlaubte Variablen: "
            f"{vars_list}. "
            "Erlaubte Operatoren: + - * / ** % ( ). Keine Funktionsaufrufe, "
            "keine Vergleiche. Die Formel darf vom Lagerbestand (stock), "
            "der Uhrzeit (hour) und dem Tag im Monat (day) abhaengen.\n"
            'Antworte als JSON: {"expression": "<formel>", "reasoning": '
            '"<kurz, max 2 Saetze>"}. Kein Freitext drum herum.'
        )
    return base


def _validate_expression(expression: str) -> None:
    import re

    allowed = re.compile(r"^[0-9A-Za-z_+\-*/%.()\s<>!=&|]*$")
    if not allowed.match(expression):
        raise LLMResponseError("Formel enthaelt ungueltige Zeichen")
    forbidden = ("__", "import", "lambda", "?", ":", ";")
    low = expression.lower()
    for tok in forbidden:
        if tok in low:
            raise LLMResponseError(f"Formel enthaelt verbotenes Token: {tok}")
    # Zuweisungen verbieten: erlaubte Mehrzeichen-Vergleiche rausstreichen,
    # bleibt dann ein '=' uebrig, ist es eine Zuweisung.
    stripped = re.sub(r"==|!=|<=|>=", "", expression)
    if "=" in stripped:
        raise LLMResponseError("Formel darf keine Zuweisung enthalten")


def suggest_strategy(
    target: str,
    online: bool,
    whitelist: dict[str, Any],
    api_key: str | None = None,
) -> LLMStrategySuggestion:
    if target not in ("fix", "formula"):
        raise LLMResponseError(f"Unbekanntes Ziel: {target}")
    prompt = _strategy_prompt(target, online, whitelist)
    text = _generate(prompt, online=online, as_json=True, api_key=api_key)
    payload = _parse_json(text)
    reasoning = str(payload.get("reasoning", ""))[:500]

    if target == "fix":
        price_raw = payload.get("price")
        if price_raw is None:
            raise LLMResponseError("LLM-Antwort ohne 'price'-Feld")
        try:
            price = Decimal(str(price_raw)).quantize(Decimal("0.01"))
        except Exception as exc:
            raise LLMResponseError(f"Ungueltiger Preis vom LLM: {price_raw}") from exc
        if price < 0:
            raise LLMResponseError("LLM schlug negativen Preis vor")
        return LLMStrategySuggestion(
            target="fix", amount=price, expression=None, reasoning=reasoning
        )

    expression = payload.get("expression")
    if not isinstance(expression, str) or not expression.strip():
        raise LLMResponseError("LLM-Antwort ohne 'expression'-Feld")
    expression = expression.strip()
    _validate_expression(expression)
    return LLMStrategySuggestion(
        target="formula", amount=None, expression=expression, reasoning=reasoning
    )
