# Preisstrategien

## Überblick

Jedes Produkt hat genau eine aktive Strategie aus exakt **zwei**
möglichen Varianten:

| Kind | Wo editierbar | Gespeichert als |
| --- | --- | --- |
| `fix` | Strategie-Modal → *Fixpreis* | `{"amount": "<Decimal>"}` |
| `formula` | Strategie-Modal → *Formel* | `{"expression": "<Ausdruck>"}` |

Die Konfiguration liegt als JSONB im Feld `pricing_strategies.config`
(siehe [data-model.md](./data-model.md)). Der Check-Constraint
erzwingt `kind IN ('fix','formula')` (Migration 0007).

KI-gestützte Preis- bzw. Formelvorschläge sind **kein eigener
Strategietyp**, sondern ein Hilfswerkzeug innerhalb des Strategie-
Modals: die KI liefert entweder eine Fixpreis-Empfehlung oder eine
Formel, die dann als reguläre `fix`- bzw. `formula`-Strategie
gespeichert wird.

## Fixpreis

- **Config:** `{"amount": "49.99"}` – Decimal-String, ≥ 0.
- **Auswertung:** liefert den konfigurierten Betrag unverändert.
- **Anwendungsfall:** statische Preise ohne Abhängigkeit von
  Uhrzeit, Lager oder Wettbewerb.
- **History-Snapshot:** `reasoning = "Fixpreis laut Konfiguration"`.

## Formel

- **Config:** `{"expression": "cost_price * 1.8 + (hour >= 18) * 2"}`.
- **Auswertung:** AST-basierter Evaluator in
  [`backend/app/strategies/evaluator.py`](../backend/app/strategies/evaluator.py).
  Kein `eval()`, keine Attribut-Zugriffe, keine Funktionsaufrufe
  außerhalb der Whitelist. Vergleiche werten zu 1/0 aus und dürfen
  multipliziert werden.
- **Sanity-Check:** negative Preise werden abgewiesen; alle Ergebnisse
  werden auf `Decimal("0.01")` quantisiert.

### Verfügbare Variablen

| Name | Quelle | Beschreibung |
| --- | --- | --- |
| `cost_price` | Produkt | Einkaufspreis |
| `competitor_price` | Produkt | Wettbewerbspreis (fehlt → 0) |
| `monthly_demand` | Produkt | Basis-Nachfrage pro Monat |
| `start_stock` | Produkt | Lagergröße (Obergrenze) |
| `stock` | Runtime | aktueller Lagerbestand (Simulation oder Default = `start_stock`) |
| `hour` | Runtime | 0–23 |
| `day` | Runtime | 1–28 (Demo-Monatszyklus) |
| `weekday` | abgeleitet | `((day − 1) mod 7) + 1`, 1 = Montag |
| `demand` | Runtime | Nachfrage-Faktor 0.00 – 2.00, Default 1 |
| `pi` | Konstante | Kreiszahl π |

### Operatoren und Funktionen

- Arithmetik: `+ − * / ** % ( )`
- Vergleiche: `< <= > >= == !=`
- Logik: `and`, `or`, `not`
- Funktionen: `sqrt`, `pow`, `abs`, `min`, `max`, `round`, `floor`,
  `ceil`, `mod`, `sin`, `cos`

### Beispiele

```
cost_price * 1.8 + (hour >= 18) * 2
    # 80 % Marge, ab 18 Uhr 2 € Abendaufschlag

round(cost_price * (1 + 0.15 * sin(hour * 2 * pi / 24 - pi/2))
      + (weekday == 7) * 3, 2)
    # weicher Tagesverlauf + Sonntagsaufschlag, auf 2 Nachkommastellen
```

### Fehlerverhalten

- **Syntax- oder Variablenfehler** → `StrategyError` → HTTP 422.
  Die Strategie wird nicht gespeichert; die bisherige bleibt aktiv.
- **Negativer Preis** → 422 mit Meldung „Berechneter Preis darf
  nicht negativ sein".
- **Frontend-Live-Evaluator** zeigt bei einem Fehler `—` in der
  Preisspalte und loggt in die Browser-Konsole; er ist rein
  clientseitige Vorschau.

## KI-Vorschlag (Hilfswerkzeug, kein Strategietyp)

Im Strategie-Modal lässt sich per Checkbox *Per KI vorschlagen* ein
Fixpreis- oder Formel-Vorschlag von Gemini holen:

- `POST /products/{id}/strategy/prompt-preview` – Prompt erzeugen,
  ohne die KI aufzurufen (Transparenz vor dem Klick).
- `POST /products/{id}/strategy/suggest` – Vorschlag inkl. Begründung.
- Der User prüft Prompt + Begründung und speichert per
  `PUT /products/{id}/strategy` – erst dann wird die Strategie aktiv
  und ein History-Snapshot geschrieben.

Die generierte Formel durchläuft vor dem Speichern dieselbe
Validierung wie eine manuell eingetippte Formel.
