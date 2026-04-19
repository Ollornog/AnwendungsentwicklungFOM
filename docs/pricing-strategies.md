# Preisstrategien

Pro Produkt ist genau eine Strategie aktiv (Annahme, siehe `docs/data-model.md`).

## 1. Fixpreis
- **Konfiguration:** ein fester Betrag (Currency, Decimal).
- **Auswertung:** Rückgabe des konfigurierten Betrags.
- **Historie:** Eintrag enthält den Betrag und einen Hinweis "Fixpreis".

## 2. Formel
- **Konfiguration:** mathematischer Ausdruck mit definierten Variablen (z. B. `einkaufspreis * (1 + marge)`).
- **Auswertung:** sicherer Ausdrucks-Evaluator (kein `eval()`), nur erlaubte Variablen und Operatoren.
- **Historie:** Eintrag enthält den berechneten Preis und die verwendeten Eingangswerte.

## 3. Regel
- **Konfiguration:** geordnete Liste von Bedingungen `wenn … dann Preis = …`. Erste passende Regel gewinnt; Fallback zwingend.
- **Auswertung:** deterministisch im Backend ausgewertet.
- **Historie:** Eintrag enthält die ausgelöste Regel und den Preis.

## 4. LLM-basiert
- **Konfiguration:** Prompt-Vorlage + Auswahl der zu sendenden Produkt-Attribute (Whitelist).
- **Auswertung:** Backend ruft LLM-API mit der Whitelist-Datenmenge auf, parst eine strukturierte Antwort (JSON) und validiert sie (Plausibilitätsgrenzen).
- **Historie:** Eintrag enthält Prompt-Hash, Modellname, Rohpreis und ggf. die LLM-Begründung.
- **Datenschutz:** keine Kundendaten an das LLM, nur produktbezogene Whitelist-Felder. Siehe `docs/security.md`.

## Gemeinsame Regeln
- Jede Berechnung erzeugt genau einen `PriceHistory`-Eintrag.
- Plausibilitätsprüfung (Min/Max) wird zentral im Backend angewandt, bevor ein Preis persistiert wird.
