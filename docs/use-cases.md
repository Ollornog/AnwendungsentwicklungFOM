# Use Cases

Kurzformat: Akteur, Ziel, Ablauf. Ausnahmen nur, wenn relevant.

## UC-01 Produkt anlegen
- **Akteur:** Shop-Betreiber
- **Ziel:** Neues Produkt im System erfassen.
- **Ablauf:**
  1. Betreiber ruft "Produkt anlegen" in der UI auf.
  2. Gibt Name, Kategorie, Einkaufspreis, Lagerbestand, optional Wettbewerbspreis ein.
  3. Backend validiert via Pydantic und speichert in der DB.
  4. UI zeigt das neue Produkt in der Liste.

## UC-02 Preisstrategie zuweisen
- **Akteur:** Shop-Betreiber
- **Ziel:** Dem Produkt eine der vier Strategien (Fix, Formel, Regel, LLM) zuweisen.
- **Ablauf:**
  1. Betreiber wählt ein Produkt.
  2. Wählt Strategie und trägt deren Konfiguration ein (Betrag / Formel / Regelliste / LLM-Prompt).
  3. Backend speichert die Strategie; ältere Konfigurationen bleiben in der Historie auffindbar.

## UC-03 Preis berechnen
- **Akteur:** Shop-Betreiber
- **Ziel:** Aktuellen Preis laut aktiver Strategie ermitteln und bestätigen.
- **Ablauf:**
  1. Betreiber löst "Preis berechnen" für ein Produkt aus → `POST /products/{id}/price`.
  2. Backend wertet die aktive Strategie aus; bei LLM-Strategie wird Google Gemini mit Whitelist-Feldern aufgerufen. Die Response enthält `is_llm_suggestion` und einen `suggestion_token`. Es entsteht **noch kein** Historien-Eintrag.
  3. UI zeigt den Vorschlag in einem Bestätigungs-Dialog. Bei LLM-Strategie ist ein "KI-Vorschlag"-Badge sichtbar (Leitprinzip 4).
  4. Betreiber bestätigt den Preis (Human-in-the-Loop, Leitprinzip 3) → `POST /products/{id}/price/confirm` mit dem Token.
  5. Backend persistiert erst jetzt einen Eintrag in der Preishistorie.
- **Abbruch:** Wenn der Betreiber ablehnt, wird kein Request gesendet; der Vorschlag läuft serverseitig mit dem Token ab.

## UC-04 Lagerbestand ändern
- **Akteur:** Shop-Betreiber
- **Ziel:** Lagerbestand eines Produkts aktualisieren (z. B. nach Wareneingang).
- **Ablauf:**
  1. Betreiber öffnet das Produkt und ändert den Bestand.
  2. Backend validiert (z. B. nicht-negativ) und speichert.
  3. Strategien, die den Bestand nutzen (Regel, Formel, LLM), liefern bei der nächsten Preisberechnung entsprechend andere Ergebnisse.

## UC-05 Preishistorie einsehen
- **Akteur:** Shop-Betreiber
- **Ziel:** Nachvollziehen, wie und wann Preise für ein Produkt entstanden sind.
- **Ablauf:**
  1. Betreiber wählt ein Produkt und öffnet die Historie.
  2. Backend liefert Liste aller Einträge mit Zeitstempel, Strategie, Input, berechnetem Preis und LLM-Markierung (falls zutreffend).
  3. UI zeigt die Einträge chronologisch (neueste zuerst).
