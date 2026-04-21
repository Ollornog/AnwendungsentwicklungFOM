# Glossar

Fachbegriffe, die in diesem Projekt einheitlich verwendet werden. Alphabetisch sortiert, je ein bis drei Sätze pro Eintrag.

---

**ADR (Architecture Decision Record).** Ein kurzes, nummeriertes Dokument in `docs/decisions/`, das eine Architektur- oder Technologieentscheidung festhält: Status, Kontext, Entscheidung, Konsequenzen. Es dient als Gedächtnis des Projekts – wer später fragt „warum haben wir das so gemacht?", findet hier die Antwort.

**Append-only Preishistorie.** Tabelle `price_history`, in die jeder bestätigte Preis-Snapshot geschrieben wird. Kein `UPDATE`, kein `DELETE` im normalen Flow – die Historie ist der Audit-Trail für Art. 5 Abs. 2 DSGVO.

**Fancy-Formel.** Zusatz-Flag beim KI-Vorschlag (Checkbox *Ausführlich* im UI). Der Prompt wird aggressiver formuliert, damit die KI statt einer banalen `cost_price * 1.8`-Formel eine ausdrucksstarke Formel mit Tageszeit-, Wochentag- und Lager-Effekten liefert. Demo-Feature, kein Produktiv-Modus.

**Fixpreis.** Eine der zwei Preisstrategien: ein fest eingetragener Betrag, unabhängig von Uhrzeit, Lagerstand oder Nachfrage. Config-Beispiel: `{"amount": "49.99"}`.

**Formel.** Die zweite Preisstrategie: ein arithmetischer Ausdruck, der zur Laufzeit mit aktuellen Werten ausgewertet wird. Erlaubte Variablen, Operatoren und Funktionen sind in [`pricing-strategies.md`](./pricing-strategies.md) dokumentiert.

**Formel-Evaluator.** Sicherheits-kritische Komponente in `backend/app/strategies/evaluator.py`. Parst die Formel via Python-`ast`, erlaubt nur Zahlen, whitelisted Variablen und eine kleine Funktions-Whitelist. Kein `eval()`, keine Attribut-Zugriffe, keine Imports.

**Gemini.** Das für diesen Prototyp eingesetzte LLM von Google. Austauschbar – der Aufruf ist in `app/llm.py` gekapselt (siehe ADR 0002).

**Human-in-the-Loop.** Leitprinzip: KI-Vorschläge werden nie automatisch übernommen. Der Admin prüft Prompt und Begründung und klickt aktiv *Speichern*. Erfüllt Art. 22 DSGVO (keine automatisierte Einzelfallentscheidung) und Art. 14 AI Act (menschliche Aufsicht).

**KI-Vorschlag.** Oberbegriff für alle drei KI-Einsatzorte im Tool: Strategievorschlag (Fix oder Formel), Prompt-Preview (Transparenz vor dem Call) und Wettbewerbspreis-Batch-Schätzung. Die KI ist **kein eigenständiger Strategietyp**, sondern ein Assistent beim Befüllen der zwei regulären Strategien.

**Nachfrage-Faktor (`demand`).** Runtime-Variable zwischen 0 und 2, pro Produkt als Slider einstellbar. 0 = keine Nachfrage, 1 = normal, 2 = doppelte Nachfrage. Kann in Formeln verwendet werden und multipliziert im Simulator den Lagerverbrauch.

**Ownership.** Jedes Produkt gehört genau einem Nutzer (`products.owner_id`). Andere Nutzer sehen das Produkt nicht, der Admin-Account hat kein Querlesen. Durchgesetzt im Backend über `_get_owned_product`.

**Pricing-Strategie.** Der Typ der Preisermittlung pro Produkt. Im UI stehen zwei Typen zur Wahl: Fixpreis und Formel (siehe [`pricing-strategies.md`](./pricing-strategies.md)).

**Prompt-Preview.** UI-Feature: bevor die KI gerufen wird, zeigt ein separater Endpoint (`/strategy/prompt-preview`) den exakten Prompt an, den das Backend senden wird. Erfüllt die Transparenzpflicht nach Art. 50 AI Act.

**Rate Limit.** Tageslimit pro Nutzer pro Tag (Default 50 für Standardnutzer, 200 für Admin). Zähler in Tabelle `api_rate_usage`, Reset täglich. Bei Überschreitung liefert die API HTTP 429. Admin-only via Einstellungsseite anpassbar.

**Runtime-Variablen.** Werte, die bei der Formelauswertung aus dem aktuellen Kontext gezogen werden: `stock`, `hour`, `day`, `weekday`, `demand`. Gegensatz zu Produkt-Variablen (`cost_price`, `competitor_price`, `monthly_demand`, `start_stock`), die aus der Datenbank kommen.

**Sanity-Check.** Defensive Prüfung auf LLM-Output: negative Preise werden abgewiesen, Formeln gegen die Zeichen-Whitelist und verbotene Tokens geprüft, bevor sie gespeichert werden. Schutz vor Halluzinationen.

**Seed-Daten.** Beim `install.sh`-Lauf oder nach *Datenbank zurücksetzen* angelegte Demo-Produkte und Team-Accounts. Definiert in `backend/app/mock_data.py`.

**Session-Cookie.** Starlette-`SessionMiddleware` mit signiertem, HttpOnly, SameSite=Lax Cookie. Keine Server-Session-Tabelle, die gesamte Nutzlast liegt im Cookie selbst. TTL 8 Stunden. Siehe ADR 0003.

**Simulator.** UI-seitige Live-Preisvorschau. Slider für globale Uhrzeit/Tag und produktbezogen Lager/Nachfrage. Rechnet die Formel im Browser (`frontend/js/formula-eval.js`) – kein Backend-Call. Keine Persistierung; dient nur dem Durchspielen von Szenarien.

**Simulator-Tick.** Ein Zeitschritt im laufenden Simulator (1 Tick = 1 Stunde). Im Normal-Modus alle 2 Sekunden, im 3×-Modus alle 0,67 Sekunden. Bei jedem Tick läuft die Uhr eine Stunde weiter, der Lagerbestand sinkt um `monthly_demand / (28*24) * demand`, und alle Preise rechnen neu.

**Snapshot (History-Snapshot).** Automatischer Eintrag in `price_history`, der jedes Mal geschrieben wird, wenn eine Strategie geändert wird. Hält den Default-Preis der neuen Strategie fest. Ermöglicht lückenlose Rekonstruktion, welche Strategie wann wie gerechnet hätte.

**Suggestion-Token.** Einmal-verwendbarer Token mit TTL 15 Minuten, den das Backend beim Preis-Request (`POST /price`) ausstellt. Erst beim Confirm-Call wird die Berechnung in die Historie geschrieben. Verhindert, dass jede transiente Auswertung automatisch im Audit-Log landet.

**Team-Account.** Normaler Benutzer-Account neben dem bootstrap-`admin`. Im Seed enthalten (Daniel, Kayathiri, Okan, Sven), vom Admin im Einstellungsbereich anlegbar. Sieht alle eigenen Produkte, aber keine Admin-Einstellungen (HTTPS, Rate Limit, Benutzerverwaltung).

**Wettbewerbspreis (`competitor_price`).** Produktfeld, das den (geschätzten) Preis bei der Konkurrenz hält. Manuell eintragbar oder per KI-Batch (UC-9) schätzen lassen. In Formeln als Variable nutzbar.

**Whitelist (LLM-Whitelist).** Genau definierte Teilmenge der Produktfelder, die an das LLM übermittelt werden darf. Zentral in `app/routers/products.py::_strategy_whitelist` und `app/strategies/llm.py::_whitelist`. Keine IDs, keine Owner-Daten, keine personenbezogenen Daten – Umsetzung des Datenminimierungs-Grundsatzes (Art. 5 Abs. 1 lit. c DSGVO).
