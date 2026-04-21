# Use Cases

Sechs zentrale Abläufe aus der Sicht des Shop-Betreibers. Ausnahmen
sind kurz gehalten; der vollständige Bedienablauf steht in der UI.

### UC-1: Produkt anlegen

**Akteur:** Admin oder Team-Benutzer (eingeloggt).
**Ziel:** Ein neues Produkt mit Stammdaten und Kontext erfassen.
**Vorbedingung:** Nutzer ist authentifiziert; Session-Cookie gesetzt.
**Ablauf:**
1. Klick auf *Produkt hinzufügen* in der Navigation öffnet das Modal.
2. Eingabe Name, Kategorie, Einkaufspreis, Wettbewerbspreis (optional),
   Verbrauch pro Monat, Lagergröße, Kontext-Freitext.
3. Frontend sendet `POST /products`. Backend validiert per Pydantic
   und speichert den Datensatz.
4. Liste aktualisiert sich über das `product-created`-Event, das neue
   Produkt erscheint als oberster Eintrag.

**Nachbedingung:** Datensatz in `products`, keine Strategie zugewiesen
(`strategy` = null).
**Ausnahmen:** Validierungsfehler (422) werden im Modal angezeigt,
ohne das Formular zurückzusetzen.

### UC-2: Preisstrategie zuweisen

**Akteur:** Admin oder Team-Benutzer.
**Ziel:** Dem Produkt einen Fixpreis oder eine Formel zuweisen.
**Vorbedingung:** Produkt existiert.
**Ablauf:**
1. In der Produktzeile *Preis* → Modal öffnet sich.
2. Auswahl *Fixpreis* oder *Formel*.
3. Wert direkt eintragen. Bei Formel unterstützen Token-Buttons das
   Einfügen von Variablen, Operatoren, Funktionen.
4. *Speichern* → `PUT /products/{id}/strategy`.
5. Backend schreibt zusätzlich automatisch einen Snapshot des
   Defaultpreises in `price_history` (Audit).

**Nachbedingung:** `pricing_strategies` für das Produkt gesetzt;
ein History-Snapshot mit `reasoning = "... · Snapshot bei
Strategie-Aenderung"` existiert.
**Ausnahmen:** Ungültige Formel → 422 mit Fehlerbeschreibung (Formel
bleibt editierbar, Snapshot entfällt).

### UC-3: Preis berechnen (Formel)

**Akteur:** Jeder eingeloggte Nutzer.
**Ziel:** Verkaufspreis gemäß aktueller Strategie mit Runtime-Kontext
sehen und persistieren.
**Vorbedingung:** Produkt hat eine aktive Strategie.
**Ablauf:**
1. Live-Preis wird automatisch in der Produktliste gezeigt, sobald
   Sliders (Stunde, Tag, Lager, Nachfrage) verändert werden. Die
   Auswertung läuft clientseitig im JS-Evaluator.
2. Für einen auditierbaren Snapshot: `POST /products/{id}/price` mit
   aktuellen Runtime-Werten → Backend wertet via AST-Evaluator aus,
   liefert Vorschlag + `suggestion_token` (TTL 15 Minuten).
3. `POST /products/{id}/price/confirm` mit dem Token persistiert den
   Eintrag in `price_history`.

**Nachbedingung:** Neuer Historien-Eintrag mit Benutzer, Strategie,
Eingaben, berechnetem Preis.
**Ausnahmen:** Abgelaufener Token → 410; ungültige Formel → 422.

### UC-4: KI-Preisvorschlag einholen

**Akteur:** Admin oder Team-Benutzer.
**Ziel:** Fixpreis oder Formel von der KI vorschlagen lassen und nach
Sichtprüfung übernehmen.
**Vorbedingung:** Gemini-API-Key in `.env` oder Einstellungen.
**Ablauf:**
1. Im Strategie-Modal Checkbox *Per KI vorschlagen* aktivieren,
   optional *Online recherchieren* und *Ausführlich*.
2. Klick auf *KI fragen*:
   a. `POST /strategy/prompt-preview` → der Prompt wird sofort
      angezeigt (Transparenz Art. 50 AI Act).
   b. `POST /strategy/suggest` → Antwort kommt zurück, Formel- oder
      Preisvorschlag und Begründung erscheinen unter dem Prompt.
3. Nutzer prüft Prompt + Vorschlag + Begründung und entscheidet.
4. Klick auf *Speichern* persistiert die Strategie wie in UC-2.

**Nachbedingung:** Strategie aktiv; Snapshot in History mit
`is_llm_suggestion = true` bei LLM-Strategie.
**Ausnahmen:** Kein API-Key → 503 mit Hinweis; ungültige
LLM-Antwort → 422; Klick ohne *Speichern* nimmt nichts über
(Human-in-the-Loop).

### UC-5: Simulator nutzen (Live-Neuberechnung)

**Akteur:** Jeder eingeloggte Nutzer.
**Ziel:** Preisverhalten gegen Zeit- und Bestandsänderungen sehen,
ohne Datenbankaufrufe.
**Vorbedingung:** Mindestens ein Produkt mit aktiver Strategie.
**Ablauf:**
1. Sliders oben setzen **Stunde (0–23)** und **Tag (1–28)**. Pro
   Produktzeile: aktueller Lagerbestand (0–Max) und
   Nachfrage-Faktor (0.00–2.00).
2. `▶/⏸` startet/pausiert den Tick (1 Tick = 1 Stunde, Interval 2 s);
   `3×` beschleunigt auf 0.67 s.
3. Bei jedem Slider-Event oder Tick berechnet der JS-Formel-Evaluator
   den neuen Verkaufspreis und schreibt ihn in die Spalte
   *Verkaufspreis*.
4. Optional: *Graph* pro Produkt plottet den Preis über die ausgewählte
   Variable (u. a. „Zeit gesamt" 672 Stunden).

**Nachbedingung:** Kein Datenbank-Write. Der Simulator ist rein
UI-seitig.
**Ausnahmen:** keine – `fix` und `formula` sind beide clientseitig
auswertbar.

### UC-6: Preishistorie einsehen

**Akteur:** Jeder eingeloggte Nutzer.
**Ziel:** Nachvollziehen, wann welche Strategie wie ausgewertet wurde.
**Vorbedingung:** Produkt hat mindestens einen History-Eintrag (durch
Strategie-Wechsel oder Confirm-Flow).
**Ablauf:**
1. In der Produktzeile *Historie* → öffnet die Historienseite für
   dieses Produkt.
2. `GET /products/{id}/history` liefert alle Einträge absteigend nach
   Zeitstempel.
3. Anzeige: Zeitpunkt, Preis, Strategie, Benutzer, KI-Badge falls
   `is_llm_suggestion`, Begründung.

**Nachbedingung:** keine (read-only).
**Ausnahmen:** Fremde Produkte → 404 (Ownership-Check im Backend).
