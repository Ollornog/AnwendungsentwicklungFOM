# Use Cases

Vollständige Liste der Benutzerabläufe aus Sicht der Shop-Betreibenden. Die Anwendung kennt **zwei Preisstrategien** (Fixpreis, Formel); die KI ist ein Werkzeug, das den Nutzer beim Befüllen dieser Strategien sowie bei der Wettbewerbspreis-Schätzung unterstützt – keine eigenständige Strategie.

Ausnahmen sind knapp gehalten; der vollständige Bedienablauf steht in der UI. Eine Übersichtsgrafik mit allen Akteuren und Use Cases liegt unter `docs/media/use-case-diagram.png`.

## Akteure

| Akteur | Rechte |
|--------|--------|
| **Team-Benutzer** (eingeloggt) | Alle Kern-Flows: Produkte, Strategien, Preis, Simulation, Historie |
| **Admin** (`admin`-Account) | Wie Team-Benutzer, zusätzlich Benutzerverwaltung, HTTPS-Aktivierung, Rate-Limit-Konfiguration |

Die Ownership-Logik ist pro Produkt: jeder Nutzer sieht nur seine eigenen Produkte. Der Admin-Account hat kein Querlesen.

---

# Primäre Use Cases (Kern-Demo)

## UC-1: Produkt anlegen

**Akteur:** Team-Benutzer oder Admin.
**Ziel:** Neues Produkt mit Stammdaten und Kontext erfassen.
**Vorbedingung:** Nutzer authentifiziert.

**Ablauf:**
1. Klick auf *Produkt hinzufügen* in der Navigation öffnet das Modal.
2. Eingabe Name, Kategorie, Einkaufspreis, Wettbewerbspreis (optional), Verbrauch pro Monat, Lagergröße, Kontext-Freitext (wird später vom KI-Vorschlag gelesen).
3. `POST /products` → Backend validiert via Pydantic und speichert.
4. Liste aktualisiert sich, das neue Produkt erscheint als oberster Eintrag.

**Nachbedingung:** Datensatz in `products`, keine Strategie zugewiesen.
**Ausnahmen:** Validierungsfehler (422) werden im Modal angezeigt.

---

## UC-2: Produkt bearbeiten

**Akteur:** Team-Benutzer oder Admin (Eigentümer des Produkts).
**Ziel:** Produktdaten ändern, insbesondere Wettbewerbspreis oder Kontext.
**Vorbedingung:** Produkt existiert und gehört dem Nutzer.

**Ablauf:**
1. In der Produktzeile *Bearbeiten* → Modal öffnet sich mit vorbelegten Werten.
2. Nutzer ändert beliebige Felder (Name, Kategorie, EK, Wettbewerbspreis, Lager, Kontext, Verbrauch/Monat).
3. *Speichern* → `PUT /products/{id}`.
4. Liste zeigt die aktualisierten Werte; bereits gesetzte Strategie bleibt erhalten.

**Nachbedingung:** Produkt aktualisiert; Live-Preis rechnet bei nächstem Slider-Event mit den neuen Werten.
**Ausnahmen:** Fremdes Produkt → 404; negative Werte → 422.

---

## UC-3: Produkt löschen

**Akteur:** Team-Benutzer oder Admin (Eigentümer).
**Ziel:** Produkt samt Strategie und Historie entfernen.
**Vorbedingung:** Produkt existiert und gehört dem Nutzer.

**Ablauf:**
1. In der Produktzeile *Löschen* (oder im Bearbeiten-Modal).
2. Bestätigungsdialog.
3. `DELETE /products/{id}` → kaskadiert über FK auch `pricing_strategies`, `price_history` und offene `price_suggestions`.

**Nachbedingung:** Produkt und alle abhängigen Daten entfernt.
**Ausnahmen:** Fremdes Produkt → 404.

---

## UC-4: Preisstrategie manuell festlegen (Fixpreis oder Formel)

**Akteur:** Team-Benutzer oder Admin (Eigentümer).
**Ziel:** Dem Produkt einen Fixpreis oder eine Formel zuweisen.
**Vorbedingung:** Produkt existiert.

**Ablauf:**
1. In der Produktzeile *Preis* → Strategie-Modal öffnet sich.
2. Auswahl *Fixpreis* oder *Formel*.
3. Fixpreis: Betrag eintragen. Formel: Ausdruck eintippen, Token-Buttons fügen Variablen (`cost_price`, `stock`, `hour`, `weekday`, `demand` …), Operatoren, Vergleiche (`>=`, `==`) und Funktionen (`sqrt`, `round`, `sin`, …) ein.
4. *Speichern* → `PUT /products/{id}/strategy`.
5. Backend schreibt automatisch einen Snapshot des Defaultpreises in `price_history` (Audit).

**Nachbedingung:** `pricing_strategies.kind` = `fix` oder `formula`; History-Snapshot mit `reasoning = "... · Snapshot bei Strategie-Aenderung"`.
**Ausnahmen:** Ungültige Formel → 422 (Formel bleibt editierbar, Snapshot entfällt).

---

## UC-5: Preisstrategie durch KI vorschlagen lassen

**Akteur:** Team-Benutzer oder Admin (Eigentümer).
**Ziel:** Fixpreis oder Formel von der KI vorschlagen lassen und nach Sichtprüfung übernehmen.
**Vorbedingung:** Gemini-API-Key hinterlegt (in `.env` oder Einstellungen).

**Ablauf:**
1. Im Strategie-Modal (UC-4) Checkbox *Per KI vorschlagen* aktivieren. Optional *Online recherchieren* und *Ausführlich* (Fancy-Prompt für komplexere Formeln).
2. Klick *KI fragen*:
   a. `POST /products/{id}/strategy/prompt-preview` → Prompt wird sofort angezeigt (Transparenz Art. 50 AI Act).
   b. `POST /products/{id}/strategy/suggest` → KI liefert Fixpreis- oder Formel-Vorschlag plus kurze Begründung.
3. Nutzer prüft Prompt, Vorschlag und Begründung. Er kann den Vorschlag übernehmen, anpassen oder verwerfen.
4. *Speichern* persistiert die Strategie wie in UC-4 – als `fix` oder `formula`.

**Nachbedingung:** Strategie aktiv (Typ `fix` oder `formula`); Snapshot in History wie in UC-4. Wird der KI-Vorschlag unverändert gespeichert, trägt der Snapshot zusätzlich `is_llm_suggestion = true` und das KI-Badge in der Historie (Art. 50 AI Act). Manuelle Edits am Vorschlag setzen das Flag zurück – es ist dann ein regulärer Fixpreis- oder Formel-Eintrag.
**Ausnahmen:** Kein API-Key → 503; ungültige LLM-Antwort → 422; Rate-Limit überschritten → 429; Klick ohne *Speichern* übernimmt nichts (Human-in-the-Loop).

---

## UC-6: Preis berechnen und auditieren

**Akteur:** Jeder eingeloggte Nutzer (Eigentümer).
**Ziel:** Einen Verkaufspreis gemäß aktueller Strategie und Runtime-Kontext berechnen und in der Historie festhalten.
**Vorbedingung:** Produkt hat eine aktive Strategie.

**Ablauf:**
1. `POST /products/{id}/price` mit Runtime-Werten (Stunde, Tag, Lagerbestand, Nachfrage) → Backend wertet via AST-Evaluator aus, liefert einen `suggestion_token` mit TTL 15 Minuten und den berechneten Preis.
2. `POST /products/{id}/price/confirm` mit dem Token → Eintrag in `price_history` mit Benutzer, Strategie, Eingaben und Preis.

**Nachbedingung:** Neuer Historien-Eintrag. Der Zwei-Schritt-Flow (Price → Confirm) erzwingt, dass nur bewusst bestätigte Preise in den Audit-Trail wandern.
**Ausnahmen:** Abgelaufener Token → 410; ungültige Formel → 422; Produkt ohne Strategie → 400.

---

## UC-7: Simulator nutzen (Live-Neuberechnung)

**Akteur:** Jeder eingeloggte Nutzer.
**Ziel:** Preisverhalten gegen Zeit- und Bestandsänderungen live sehen, ohne Datenbankaufrufe.
**Vorbedingung:** Mindestens ein Produkt mit aktiver Strategie.

**Ablauf:**
1. Globale Slider oben: **Stunde (0–23)** und **Tag (1–28)**. Pro Produktzeile: aktueller Lagerbestand (0–Max) und Nachfrage-Faktor (0.00–2.00).
2. `▶/⏸` startet/pausiert den Tick (1 Tick = 1 Stunde, Interval 2 s); `3×` beschleunigt auf 0.67 s.
3. Bei jedem Slider-Event oder Tick berechnet der JS-Formel-Evaluator den neuen Verkaufspreis und schreibt ihn in die Spalte *Verkaufspreis*.
4. Lagerverbrauch läuft pro Stunde mit `monthly_demand / (28*24) * demand`. Bei Bestand 0 Auto-Refill auf Lagergröße.

**Nachbedingung:** Kein Datenbank-Write. Reine UI-Visualisierung.
**Ausnahmen:** keine – Fixpreis und Formel sind beide clientseitig auswertbar.

---

## UC-8: Preisgraph analysieren

**Akteur:** Jeder eingeloggte Nutzer (Eigentümer).
**Ziel:** Verhalten der Preisstrategie über einen Variablenbereich hinweg visualisieren.
**Vorbedingung:** Produkt hat eine aktive Fix- oder Formel-Strategie.

**Ablauf:**
1. In der Produktzeile *Graph* → Modal öffnet sich.
2. Dropdown *Variable*: Uhrzeit (0–23), Tag (1–28), Wochentag (1–7), Lagerbestand (0 – Max), Nachfrage-Faktor (0 – 2), Verbrauch/Monat (0–500), Einkaufspreis (± 50 %), Wettbewerbspreis (± 50 %), **Zeit gesamt** (672 Stunden = 1 Monat).
3. Chart.js plottet den Verkaufspreis über die gewählte Variable; alle anderen Werte bleiben auf dem aktuellen Sim- und Produktstand.
4. Wechsel der Variable rendert den Graph neu.

**Nachbedingung:** keine (read-only).
**Ausnahmen:** Produkt ohne Strategie → Hinweistext im Modal statt Graph.

---

## UC-9: Wettbewerbspreise per KI schätzen (Batch)

**Akteur:** Team-Benutzer oder Admin.
**Ziel:** Für alle eigenen Produkte in einem Schritt plausible Wettbewerbspreise vorschlagen lassen und selektiv übernehmen.
**Vorbedingung:** Gemini-API-Key gesetzt; mindestens ein Produkt.

**Ablauf:**
1. Klick *Wettbewerb (KI)* in der Navigation öffnet das Batch-Modal.
2. `POST /products/competitor-prices/suggest` → Backend schickt für alle Produkte des Nutzers eine kompakte Whitelist (Name, Kategorie, EK, aktueller Wettbewerbspreis, Kontext) an Gemini.
3. KI liefert pro Produkt geschätzten Preis und kurze Begründung.
4. Modal zeigt Liste mit alt/neu/Delta. Nutzer entscheidet pro Zeile *Übernehmen* oder lässt stehen. *Alle übernehmen* als Bulk-Aktion.
5. Pro Übernahme: `PUT /products/{id}` mit dem neuen Wert.

**Nachbedingung:** Übernommene Vorschläge aktualisieren `products.competitor_price`. Kein Schreiben in `price_history` (nur Wettbewerbsdaten, keine Preisberechnung). Neu berechnete Preise der Formel-Strategie sehen den neuen Wettbewerbspreis sofort.
**Ausnahmen:** Kein API-Key → 503; ungültige LLM-Antwort → 422; Rate-Limit → 429; keine Produkte → leeres Modal.

---

## UC-10: Preishistorie einsehen

**Akteur:** Jeder eingeloggte Nutzer (Eigentümer).
**Ziel:** Nachvollziehen, wann welche Strategie wie ausgewertet wurde.
**Vorbedingung:** Produkt hat mindestens einen History-Eintrag.

**Ablauf:**
1. In der Produktzeile *Historie* → Historienseite öffnet sich.
2. `GET /products/{id}/history` liefert alle Einträge absteigend nach Zeitstempel.
3. Anzeige: Zeitpunkt, Preis, Strategie (`fix`/`formula`), Benutzer, KI-Badge falls `is_llm_suggestion`, Begründung/Input.

**Nachbedingung:** keine (read-only).
**Ausnahmen:** Fremde Produkte → 404.

---

# Sekundäre Use Cases (Admin & Betrieb)

Nicht Kern der Präsentations-Demo, aber funktional vorhanden und relevant für die produktive Nutzung.

## UC-11: Benutzer verwalten (Admin-only)

**Akteur:** `admin`-Account.
**Ziel:** Team-Accounts anlegen, Passwörter zurücksetzen oder Accounts löschen.
**Vorbedingung:** Als `admin` eingeloggt.

**Ablauf (Anlegen):**
1. *Einstellungen* → Abschnitt *Benutzerverwaltung*.
2. Neuer Benutzername + Passwort → `POST /users`.

**Ablauf (Passwort ändern):** Klick *Passwort* in der Benutzerliste → Prompt → `PUT /users/{id}`.
**Ablauf (Löschen):** Klick *Löschen* → Bestätigung → `DELETE /users/{id}`.

**Nachbedingung:** Tabelle `users` aktualisiert.
**Ausnahmen:** Nicht-Admin → 403; Benutzername existiert → 409; `admin`-Account ist geschützt und kann weder geändert noch gelöscht werden; eigenen Account löschen → 400.

---

## UC-12: Eigenes Passwort ändern

**Akteur:** Jeder eingeloggte Nutzer.
**Ziel:** Das eigene Passwort sicher wechseln.
**Vorbedingung:** Authentifiziert.

**Ablauf:**
1. *Einstellungen* → Abschnitt *Passwort ändern*.
2. Aktuelles Passwort + neues Passwort (2×) eingeben.
3. `POST /auth/password` → Backend verifiziert das aktuelle Passwort, hasht das neue mit argon2id und speichert.

**Nachbedingung:** Neuer Passwort-Hash in `users.password_hash`.
**Ausnahmen:** Aktuelles Passwort falsch → 401; zu kurz → 422.

---

## UC-13: Gemini-API-Key setzen (Admin-only)

**Akteur:** Jeder eingeloggte Nutzer.
**Ziel:** Den per UI hinterlegten LLM-Key setzen oder entfernen.
**Vorbedingung:** Authentifiziert.

**Ablauf:**
1. *Einstellungen* → Abschnitt *Google Gemini API-Key*.
2. Eingabe des Keys + *Speichern* → `PUT /settings` speichert den Wert in `app_settings` (DB-Wert überschreibt `.env`).
3. Alternativ *Aus DB entfernen* → Override wird gelöscht, `.env`-Wert wird wieder wirksam.

**Nachbedingung:** `app_settings.gemini_api_key` gesetzt oder entfernt.
**Ausnahmen:** keine spezifischen.

---

## UC-14: Rate Limit konfigurieren (Admin-only)

**Akteur:** `admin`-Account.
**Ziel:** Tageslimits für Standardnutzer und Admin anpassen.
**Vorbedingung:** Als `admin` eingeloggt.

**Ablauf:**
1. *Einstellungen* → Abschnitt *Rate Limiting*.
2. Werte anpassen (Default 50 für Standard, 200 für Admin).
3. *Speichern* → `PUT /settings/rate-limit`.

**Nachbedingung:** Neue Limits aktiv ab dem nächsten Request. Bestehende Tageszähler in `api_rate_usage` werden nicht zurückgesetzt.
**Ausnahmen:** Nicht-Admin → 403; Werte außerhalb 1–100000 → 422.

---

## UC-15: HTTPS per Klick aktivieren (Admin-only)

**Akteur:** `admin`-Account.
**Ziel:** Let's-Encrypt-Zertifikat über `certbot --nginx` holen und nginx auf HTTPS umstellen.
**Vorbedingung:** DNS-A-Record zeigt auf den Server; Ports 80/443 aus dem Internet erreichbar.

**Ablauf:**
1. *Einstellungen* → Abschnitt *HTTPS (Let's Encrypt)*.
2. Domain eingeben, *HTTPS aktivieren* klicken, Bestätigungsdialog.
3. `POST /settings/https/enable` → Backend ruft via sudo genau ein Helper-Skript auf, das certbot-nginx ausführt und die nginx-Konfiguration samt HTTP-Redirect setzt.
4. Ausgabe von certbot wird in gekürzter Form im UI angezeigt.

**Nachbedingung:** `app_settings.https_enabled = "1"`, `https_domain` gesetzt; nginx spricht TLS.
**Ausnahmen:** Nicht-Admin → 403; Helper fehlt → 501; DNS/Port-Probleme → Timeout 504; certbot-Fehler → 500 mit Log-Ausschnitt.

---

## UC-16: Datenbank auf Seed zurücksetzen

**Akteur:** Jeder eingeloggte Nutzer (für die eigenen Daten).
**Ziel:** Produkte, Strategien und Preis-Historie des eigenen Accounts auf den Seed-Stand zurücksetzen.
**Vorbedingung:** Authentifiziert.

**Ablauf:**
1. *Einstellungen* → *Datenbank zurücksetzen*.
2. Bestätigungsdialog.
3. `POST /settings/reset-database` → Backend löscht alle eigenen Produkte (kaskadiert Strategien, Historie, Suggestions) und legt die Mock-Produkte neu an.

**Nachbedingung:** Seed-Produkte zurück, Admin-Account und Gemini-Key bleiben erhalten.
**Ausnahmen:** keine spezifischen (idempotent).
