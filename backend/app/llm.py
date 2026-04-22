"""Minimaler Gemini-Client.

Wichtig: Es werden ausschließlich die vom Backend übergebenen Produkt-Whitelist-Felder
gesendet. Keine personenbezogenen Daten, keine Kundendaten (siehe docs/compliance.md).
"""


import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.config import get_settings


class LLMUnavailableError(RuntimeError):
    pass


class LLMRateLimitError(LLMUnavailableError):
    """Provider-Rate-Limit erreicht (z. B. Gemini Free-Tier RPM).

    `retry_after` ist die vom Provider gemeldete Wartezeit in Sekunden,
    None wenn nicht extrahierbar.
    """

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class LLMResponseError(RuntimeError):
    pass


@dataclass
class LLMStrategySuggestion:
    """Von der KI vorgeschlagene Strategie (Fixpreis oder Formel)."""

    target: str  # "fix" | "formula"
    amount: Decimal | None
    expression: str | None
    reasoning: str
    prompt: str  # der tatsaechlich an die KI geschickte Prompt (Transparenz)
    raw_response: str  # Roh-Text der LLM-Antwort (fuer Audit-Log)


@dataclass
class LLMCompetitorItem:
    """KI-geschaetzter Wettbewerbspreis fuer ein Produkt."""

    product_id: str  # UUID als String, kommt 1:1 vom Request zurueck
    price: Decimal
    reasoning: str


@dataclass
class LLMCompetitorBatch:
    """Ergebnis der batched Wettbewerbspreis-Schaetzung.

    Neben den einzelnen Items enthaelt das Batch-Objekt den Prompt
    und die Roh-Antwort – beide werden vom Audit-Service protokolliert.
    """

    items: list[LLMCompetitorItem]
    prompt: str
    raw_response: str


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


def _extract_retry_after(exc: Exception) -> int | None:
    """Liest die Retry-Dauer aus einer Gemini-Quota-Exception.

    Die SDK serialisiert den RetryInfo-Block als Text in die Nachricht
    (`retry_delay { seconds: 41 }`); fuer eine UI-Anzeige reicht das,
    ohne den zusaetzlichen google.rpc-Import.
    """
    import re

    text = str(exc)
    match = re.search(r"retry_delay\s*\{[^}]*seconds:\s*(\d+)", text)
    if match:
        return int(match.group(1))
    match = re.search(r"retry in\s+([\d.]+)s", text, re.IGNORECASE)
    if match:
        return int(float(match.group(1))) + 1
    return None


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
        from google.api_core.exceptions import ResourceExhausted
    except ImportError:  # pragma: no cover
        ResourceExhausted = ()  # type: ignore[assignment]

    def _rate_limited(exc: Exception) -> LLMRateLimitError:
        retry_after = _extract_retry_after(exc)
        suffix = f" Bitte in ca. {retry_after}s erneut versuchen." if retry_after else ""
        return LLMRateLimitError(
            "Gemini-API-Limit erreicht (Free-Tier)." + suffix,
            retry_after=retry_after,
        )

    gen_config = {"response_mime_type": "application/json"} if as_json else {}
    try:
        model = genai.GenerativeModel(settings.gemini_model, **model_kwargs)
        response = model.generate_content(prompt, generation_config=gen_config)
    except ResourceExhausted as exc:
        # Provider-Quota: Fallback waere nur ein zweiter 429, daher direkt raus.
        raise _rate_limited(exc) from exc
    except Exception:
        if not online:
            raise
        # Fallback ohne Tool – Prompt enthaelt bereits den Online-Hinweis.
        try:
            model = genai.GenerativeModel(settings.gemini_model)
            response = model.generate_content(prompt, generation_config=gen_config)
        except ResourceExhausted as exc:
            raise _rate_limited(exc) from exc

    text = getattr(response, "text", None)
    if not text:
        raise LLMResponseError("Leere Antwort vom LLM")
    return text


_ALLOWED_FORMULA_VARS = (
    "cost_price",
    "competitor_price",
    "monthly_demand",
    "start_stock",
    "stock",
    "hour",
    "day",
    "weekday",
    "demand",
    "pi",
)

_ALLOWED_FORMULA_FUNCS = (
    "sqrt",
    "pow",
    "abs",
    "min",
    "max",
    "round",
    "floor",
    "ceil",
    "mod",
    "sin",
    "cos",
)


def _strategy_prompt(
    target: str,
    online: bool,
    whitelist: dict[str, Any],
    fancy: bool = False,
) -> str:
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
    # `fancy` spielt nur bei formula eine Rolle – bei einem einzelnen
    # Fixpreis gibt es nichts zu "kombinieren".
    if fancy and target == "formula":
        base += (
            "\nDemo-Kontext: das ist eine Vorfuehr-Umgebung. Ruhig ausfuehrlich "
            "werden und mehrere Effekte kombinieren (Tageszeit, Wochentag, "
            "Lagerstand als prozentuale Fuellung, Monatstag). Zeig, was geht.\n"
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
            "weekday ist 1=Montag, …, 7=Sonntag. `pi` ist die Kreiszahl. "
            "`demand` ist ein Live-Slider von 0 bis 2 auf der Produktseite "
            "(0 = keine Nachfrage, 1 = neutraler Normalfall, 2 = doppelte "
            "Nachfrage; Schritte in 0.01). `monthly_demand` ist die statische "
            "Basis-Nachfrage aus den Produktdaten. `demand` ist bereits der "
            "natuerliche Multiplikator – z. B. `cost_price * demand` verdoppelt "
            "den Preis bei voller Nachfrage und halbiert ihn gegen 0.\n"
            "Hinweis: die Demo-Simulation rechnet mit einem Monat von "
            "genau 28 Tagen (day laeuft zyklisch von 1 bis 28), damit "
            "Wochentage aufgehen. Bitte in periodischen Formeln 28 als "
            "Monatslaenge verwenden, nicht 30 oder 31.\n"
            "Erlaubte Operatoren: + - * / ** % ( ) sowie die Vergleiche "
            "< <= > >= == != (ein Vergleich ergibt 1 oder 0 und kann "
            "multipliziert werden, z. B. `(hour >= 18) * 2` als Abendaufschlag "
            "oder `(weekday == 7) * 3` als Sonntagsaufschlag). "
            "Logische Verknuepfungen: `and`, `or`, `not` (Python-Stil).\n"
            "Erlaubte Funktionen (mit Signatur):\n"
            "  sqrt(x)         – Quadratwurzel\n"
            "  pow(x, y)       – x hoch y (aequivalent zu x ** y)\n"
            "  abs(x)          – Betrag\n"
            "  min(a, b, ...)  – kleinster Wert (mind. 1 Argument)\n"
            "  max(a, b, ...)  – groesster Wert (mind. 1 Argument)\n"
            "  round(x, n)     – auf n Nachkommastellen; n ist optional (Default 0)\n"
            "  floor(x)        – auf ganze Zahl abrunden\n"
            "  ceil(x)         – auf ganze Zahl aufrunden\n"
            "  mod(x, n)       – Rest-Modulo, gleichwertig zu `x % n`; "
            "praktisch fuer periodische Muster\n"
            "  sin(x)          – Sinus (x im Bogenmass)\n"
            "  cos(x)          – Kosinus (x im Bogenmass)\n"
            "Keine weiteren Funktionsaufrufe, keine Zuweisungen.\n"
            "Best Practices:\n"
            " - Lagerstand prozentual ueber `stock / start_stock` modellieren, "
            "nicht mit absoluten Schwellen.\n"
            " - Bevorzuge glatte, stetige Kurven statt Stufenfunktionen. "
            "`sin`/`cos` eignen sich hervorragend fuer homogene periodische "
            "Muster, die an den Rand-Grenzen (hour 0 vs 23, weekday 1 vs 7) "
            "keinen Knick haben. Beispiele:\n"
            "     cost_price * (1 + 0.15 * sin(hour * 2 * pi / 24 - pi/2))   "
            "# weicher Tagesverlauf, Peak abends\n"
            "     cost_price * (1 + 0.08 * cos((weekday - 1) * 2 * pi / 7))   "
            "# homogene Woche, Peak am Wochenanfang\n"
            "     cost_price * 1.8 * pow(stock / start_stock, -0.2)   "
            "# Preis steigt sanft bei sinkendem Lager\n"
            "     competitor_price - 0.5 + 0.8 * pow(1 - stock / start_stock, 2)   "
            "# quadratischer Aufschlag nahe Null\n"
            " - Runden auf zwei Nachkommastellen uebernimmt der Server "
            "automatisch; du brauchst `round(..., 2)` nicht manuell zu setzen.\n"
            'Antworte als JSON: {"expression": "<formel>", "reasoning": '
            '"<kurz, max 2 Saetze>"}. Kein Freitext drum herum.'
        )
    return base


def _is_round2_wrapped(expression: str) -> bool:
    """True, wenn `expression` bereits als `round(<x>, 2)` vorliegt.

    Prueft via Klammer-Depth, dass die initiale `round(` den kompletten
    Ausdruck umschliesst, und dass das aeussere Argument auf `, 2` endet.
    """
    expr = expression.strip()
    if not (expr.startswith("round(") and expr.endswith(")")):
        return False
    depth = 0
    for i, ch in enumerate(expr[5:], start=5):  # Klammer-Run ab "round("
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                # Passt nur, wenn die erste schliessende Klammer auf Tiefe 0
                # die allerletzte ist – also der Ausdruck komplett umfasst ist.
                if i != len(expr) - 1:
                    return False
                import re

                inner = expr[6:i]  # ohne "round(" und das finale ")"
                return bool(re.search(r",\s*2\s*$", inner))
    return False


def _wrap_round2(expression: str) -> str:
    """Stellt sicher, dass die Formel auf zwei Nachkommastellen rundet."""
    expr = expression.strip()
    if _is_round2_wrapped(expr):
        return expr
    return f"round({expr}, 2)"


def _validate_expression(expression: str) -> None:
    import re

    # ',' ist fuer mehrargumentige Funktionen wie min(a, b, c) noetig.
    allowed = re.compile(r"^[0-9A-Za-z_+\-*/%.()\s<>!=&|,]*$")
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


def preview_strategy_prompt(
    target: str,
    online: bool,
    whitelist: dict[str, Any],
    fancy: bool = False,
) -> str:
    """Baut den gleichen Prompt wie `suggest_strategy`, ohne LLM-Call."""
    if target not in ("fix", "formula"):
        raise LLMResponseError(f"Unbekanntes Ziel: {target}")
    return _strategy_prompt(target, online, whitelist, fancy=fancy)


def suggest_strategy(
    target: str,
    online: bool,
    whitelist: dict[str, Any],
    api_key: str | None = None,
    fancy: bool = False,
) -> LLMStrategySuggestion:
    if target not in ("fix", "formula"):
        raise LLMResponseError(f"Unbekanntes Ziel: {target}")
    prompt = _strategy_prompt(target, online, whitelist, fancy=fancy)
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
            target="fix",
            amount=price,
            expression=None,
            reasoning=reasoning,
            prompt=prompt,
            raw_response=text,
        )

    expression = payload.get("expression")
    if not isinstance(expression, str) or not expression.strip():
        raise LLMResponseError("LLM-Antwort ohne 'expression'-Feld")
    expression = expression.strip()
    _validate_expression(expression)
    # Runden erzwingen: das LLM ist nicht zuverlaessig genug, den round(.., 2)-
    # Wrap immer selbst zu setzen. Wenn schon korrekt gewrappt, nicht doppeln.
    expression = _wrap_round2(expression)
    return LLMStrategySuggestion(
        target="formula",
        amount=None,
        expression=expression,
        reasoning=reasoning,
        prompt=prompt,
        raw_response=text,
    )


def _competitor_prompt(products: list[dict[str, Any]]) -> str:
    """Prompt fuer die batched Wettbewerbspreis-Schaetzung.

    products: Liste mit {id, name, category, cost_price, current_competitor,
    context}. Der Prompt bittet die KI, fuer jedes Produkt einen realistischen
    durchschnittlichen Online-Wettbewerbspreis in EUR zu schaetzen.
    """
    lines = []
    for p in products:
        current = p.get("current_competitor")
        current_txt = f"{current} EUR" if current is not None else "unbekannt"
        context = (p.get("context") or "").strip()
        ctx_txt = (" · " + context[:180]) if context else ""
        lines.append(
            f"- id={p['id']} name=\"{p['name']}\" kategorie=\"{p['category']}\" "
            f"einkauf={p.get('cost_price', '?')} EUR aktueller_wettbewerb={current_txt}"
            f"{ctx_txt}"
        )
    product_block = "\n".join(lines)
    return (
        "Du bist ein Preis-Assistent. Fuer jedes der folgenden Produkte "
        "schaetze einen realistischen durchschnittlichen Online-Wettbewerbspreis "
        "in EUR (Deutschland). Fuer eine Demo reicht eine plausible Schaetzung – "
        "erfinde einen Wert, der zur Produktkategorie passt.\n\n"
        f"Produkte:\n{product_block}\n\n"
        "Antworte ausschliesslich als JSON-Array mit einem Objekt pro Produkt:\n"
        '[{"id": "<uuid>", "price": <zahl>, "reasoning": "<kurz>"} , ...]\n'
        "Kein Freitext drum herum, keine zusaetzlichen Felder."
    )


def preview_competitor_prompt(products: list[dict[str, Any]]) -> str:
    """Baut den gleichen Prompt wie `suggest_competitor_prices`, ohne LLM-Call."""
    return _competitor_prompt(products)


def suggest_competitor_prices(
    products: list[dict[str, Any]],
    api_key: str | None = None,
) -> LLMCompetitorBatch:
    """Batch-KI-Call: Wettbewerbspreis-Schaetzung fuer mehrere Produkte."""
    if not products:
        return LLMCompetitorBatch(items=[], prompt="", raw_response="")
    prompt = _competitor_prompt(products)
    text = _generate(prompt, online=False, as_json=True, api_key=api_key)
    import json as _json

    # Antwort kann entweder direkt ein Array sein oder ein Objekt mit Array darin.
    data: Any
    try:
        data = _json.loads(text.strip().lstrip("`").rstrip("`"))
    except _json.JSONDecodeError:
        data = _parse_json(text)  # laesst Markdown-Fences fallen
    if isinstance(data, dict):
        # manche Modelle wrappen: {"results": [...]}
        for key in ("results", "items", "data"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise LLMResponseError("LLM-Antwort ist kein Array")

    items: list[LLMCompetitorItem] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        pid = str(entry.get("id") or "").strip()
        price_raw = entry.get("price")
        if not pid or price_raw is None:
            continue
        try:
            price = Decimal(str(price_raw)).quantize(Decimal("0.01"))
        except Exception:
            continue
        if price < 0:
            continue
        reasoning = str(entry.get("reasoning", ""))[:400]
        items.append(LLMCompetitorItem(product_id=pid, price=price, reasoning=reasoning))
    return LLMCompetitorBatch(items=items, prompt=prompt, raw_response=text)
