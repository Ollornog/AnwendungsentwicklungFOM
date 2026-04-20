# Preisstrategien

Jedes Produkt hat genau eine aktive Strategie. In der UI lassen sich **Fix**
und **Formel** editieren; **Regel** und **LLM** kommen aus dem Seed bzw. dem
Backend-Evaluator und sind im gleichen Daten-Schema darstellbar.

## 1. Fixpreis

- **Konfiguration:** `{"amount": "49.99"}` (Decimal-String, ≥ 0).
- **Auswertung:** liefert den konfigurierten Betrag.
- **Historie:** Eintrag dokumentiert den Betrag und den Hinweis *„Fixpreis laut
  Konfiguration"*.

## 2. Formel

- **Konfiguration:** `{"expression": "cost_price * 1.8"}`.
- **Auswertung:** AST-basierter Evaluator (`backend/app/strategies/evaluator.py`).
  Kein `eval()`, keine Attribut-Zugriffe, keine Funktionsaufrufe außerhalb der
  Whitelist.
- **Bool-Arithmetik:** Vergleiche liefern `1`/`0` und dürfen multipliziert
  werden. Logische Verknüpfungen `and`/`or`/`not` sind erlaubt (Python-Stil).

### Erlaubte Variablen

| Name | Bedeutung | Quelle |
| --- | --- | --- |
| `cost_price` | Einkaufspreis | Produkt (statisch) |
| `competitor_price` | Wettbewerbspreis | Produkt (statisch) |
| `monthly_demand` | Basis-Nachfrage pro Monat | Produkt (statisch) |
| `start_stock` | Lagergröße (Obergrenze) | Produkt (statisch) |
| `stock` | **aktueller** Lagerbestand | Runtime (Simulation oder Standard = Startbestand) |
| `hour` | Uhrzeit 0–23 | Runtime |
| `day` | Tag im Monat 1–28 (Demo-Zyklus) | Runtime |
| `weekday` | 1=Montag … 7=Sonntag, abgeleitet aus `day` | Runtime |
| `demand` | Nachfrage-Faktor 0.00–2.00 (1 = neutral, 2 = doppelt) | Runtime |
| `pi` | Kreiszahl π | Konstante |

Fehlen Runtime-Werte im API-Request, kommen sinnvolle Defaults zum Einsatz
(`stock = start_stock`, `hour = 0`, `day = 1`, `demand = 1`).

### Erlaubte Funktionen

`sqrt(x)` · `pow(x, y)` · `abs(x)` · `min(a, b, …)` · `max(a, b, …)` ·
`round(x, n=0)` · `floor(x)` · `ceil(x)` · `mod(x, n)` · `sin(x)` · `cos(x)`.

Trig-Funktionen rechnen in Bogenmaß. Damit sind periodische Muster ohne
„Knick" am Rand-Übergang (Stunde 23 → 0, Wochentag 7 → 1) möglich:

```
cost_price * (1 + 0.15 * sin(hour * 2 * pi / 24 - pi/2))   # weicher Abendpeak
cost_price * (1 + 0.08 * cos((weekday - 1) * 2 * pi / 7))  # homogene Woche
```

### Operatoren

`+` `-` `*` `/` `**` `%` Klammern. Vergleiche `<` `<=` `>` `>=` `==` `!=`.

## 3. Regel

- **Konfiguration:**
  ```json
  {
    "rules": [
      {"when": "stock < 20", "then": "cost_price * 2.5"},
      {"when": "competitor_price > 0", "then": "competitor_price - 1"}
    ],
    "fallback": "cost_price * 2"
  }
  ```
- **Auswertung:** erste passende Regel gewinnt, `fallback` ist Pflicht. Beide
  Ausdrücke laufen durch denselben AST-Evaluator wie die Formel.
- **Historie:** Eintrag nennt die ausgelöste Regel oder `Fallback`.

## 4. LLM-basiert

- **Konfiguration:** `{"prompt_template": "Schlage einen Preis für {name} …"}`.
  Das Template nutzt Produkt-Whitelist-Felder (Name, Kategorie, Preise,
  Kontext).
- **Auswertung:** Backend ruft die Gemini-API auf, validiert die strukturierte
  Antwort, quantisiert auf zwei Nachkommastellen.
- **Fehlerbehandlung:** `LLMUnavailableError` → `503`; `LLMResponseError`
  (ungültiges JSON, negativer Preis, etc.) → `422`.
- **Datenschutz:** nur die whitelist-Felder landen im Prompt – keine
  Kundendaten, siehe `docs/compliance.md`.

### KI-Vorschlag für eine neue Strategie

`POST /products/{id}/strategy/suggest` erzeugt einen Fixpreis- oder Formel-
Vorschlag. Der zugehörige `POST /products/{id}/strategy/prompt-preview`
liefert den identischen Prompt **ohne** LLM-Call – so sieht der User im
Modal, was geschickt wird, bevor die Antwort kommt.

## Gemeinsame Regeln

- Negative Preise werden zurückgewiesen.
- Vor jedem Persist läuft `Decimal.quantize(0.01)`.
- `PriceHistory.is_llm_suggestion = true` nur, wenn der Preis tatsächlich
  vom LLM kam.
- Bei Strategie-Wechsel schreibt das Backend automatisch einen Snapshot in
  die Historie, damit die Timeline der aktiven Strategien rekonstruierbar
  ist.
