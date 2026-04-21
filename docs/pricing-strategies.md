# Preisstrategien

## Überblick

Jedes Produkt hat genau eine aktive Strategie. Im UI-Scope stehen
**zwei** Strategien zur Wahl: **Fixpreis** und **Formel**. Die Felder
`rule` und `llm` sind im Datenbank-Check-Constraint zwar vorgesehen
und werden im Backend auch ausgewertet (Legacy aus frühen Prototyp-
Experimenten), im aktuellen UI aber **nicht editierbar** – Regeln
lassen sich vollständig als Formeln darstellen (eine Kette von
`(bedingung) * wert`-Termen), und der LLM-Pfad wird stattdessen als
*KI-Vorschlag* in das Formel- oder Fixpreis-Modal eingebunden. Die
bewusste Scope-Entscheidung: zwei einfache Strategien + ein
einheitliches KI-Werkzeug.

Gespeichert wird die Strategie im Produkt-Datensatz als Kombination
aus `kind` und `config` (JSONB) in der Tabelle `pricing_strategies`
(siehe [data-model.md](./data-model.md)).

## Fixpreis

- **Config:** `{"amount": "49.99"}` (Decimal-String, ≥ 0).
- **Auswertung:** liefert den konfigurierten Betrag unverändert.
- **Anwendungsfall:** statische Preise, z. B. redaktionell
  festgelegt. Keine Abhängigkeit von Uhrzeit, Lager oder Wettbewerb.
- **Historien-Eintrag:** `reasoning = "Fixpreis laut Konfiguration"`.

## Formel

- **Config:** `{"expression": "cost_price * 1.8 + (hour >= 18) * 2"}`.
- **Auswertung:** AST-basierter Evaluator in
  [`backend/app/strategies/evaluator.py`](../backend/app/strategies/evaluator.py).
  Kein `eval()`, keine Attribut-Zugriffe, keine Funktionsaufrufe
  außerhalb der Whitelist.
- **Sanity-Check:** negative Preise werden abgewiesen; `Decimal` mit
  Quantisierung auf 0.01. Vergleiche (`<`, `>=`, `==` …) liefern 1/0
  und dürfen multipliziert werden.

### Verfügbare Variablen

| Name | Quelle | Beschreibung |
| --- | --- | --- |
| `cost_price` | Produkt | Einkaufspreis |
| `competitor_price` | Produkt | Wettbewerbspreis (fehlt → 0) |
| `monthly_demand` | Produkt | Basis-Nachfrage pro Monat |
| `start_stock` | Produkt | Lagergröße (Obergrenze) |
| `stock` | Runtime | aktueller Lagerbestand (Sim oder Default = `start_stock`) |
| `hour` | Runtime | 0–23 |
| `day` | Runtime | 1–28 (Demo-Zyklus) |
| `weekday` | abgeleitet | `((day − 1) mod 7) + 1`, 1 = Montag |
| `demand` | Runtime | Nachfrage-Faktor 0.00 – 2.00, Default 1 |
| `pi` | Konstante | Kreiszahl π |

### Operatoren & Funktionen

- Arithmetik: `+ − * / ** % ( )`
- Vergleiche: `< <= > >= == !=`
- Logik: `and`, `or`, `not`
- Funktionen: `sqrt`, `pow`, `abs`, `min`, `max`, `round`, `floor`,
  `ceil`, `mod`, `sin`, `cos`

### Beispielformeln

```
cost_price * 1.8 + (hour >= 18) * 2
    # 80 % Marge, ab 18 Uhr 2 € Abendaufschlag

round(cost_price * (1 + 0.15 * sin(hour * 2 * pi / 24 - pi/2))
      + (weekday == 7) * 3, 2)
    # weicher Tagesverlauf + Sonntagsaufschlag, auf 2 Nachkommastellen
```

### Fehlerverhalten

- **Syntaxfehler:** Evaluator wirft `ExpressionError` →
  `StrategyError` → HTTP `422`. Die Strategie wird **nicht**
  gespeichert; die bisherige Strategie bleibt aktiv.
- **Unbekannte Variable:** analog `422`.
- **Negativer Preis:** `422` mit Meldung „Berechneter Preis darf
  nicht negativ sein".
- Im **Frontend-Evaluator** (Live-Vorschau) führt ein Fehler nur
  dazu, dass die Preisspalte `—` zeigt; das Backend bleibt der
  einzige Ort, an dem Fehler auch persistent wirken.

## Speicherung

`pricing_strategies.kind` unterliegt dem Check-Constraint
`IN ('fix','formula','rule','llm')`; der aktuelle UI-Scope nutzt nur
`fix` und `formula`. Bestehende Seed-Produkte mit `rule`/`llm`
werden im Rahmen von Migration 0005 bzw. aktualisiertem Seed
schrittweise auf Formeln umgestellt.
