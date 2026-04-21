# **Test-Matrix**

Testfälle pro Use Case. 26 Einträge, gruppiert nach Bereichen. Status-Werte: ✅, ⛔, **Open**, **Wontfix** (mit Begründung in Bemerkung).

Automatische Testabdeckung ist mit *pytest* in der Bemerkungs-Spalte markiert. Alle übrigen Testfälle sind manuell durch Person B auszuführen, idealerweise in der Live-Demo-Umgebung ([fom.ollornog.de](https://fom.ollornog.de/)) nach einem Seed-Reset.

---

## **A. Produkt-Management (UC-1 bis UC-3)**

| ID | Beschreibung | Erwartet | Status | Bemerkung |
| ----- | ----- | ----- | ----- | ----- |
| TC-01 | Produkt mit gültigen Daten anlegen | Produkt erscheint oben in der Liste, HTTP 201, Strategie \= null | ✅ | pytest `test_create_and_list` deckt API-Seite ab |
| TC-02 | Produkt mit negativem Einkaufspreis anlegen | 422, Modal bleibt offen, Fehlermeldung sichtbar | ✅ | pytest `test_create_rejects_invalid_payload` |
| TC-03 | Produkt ohne Wettbewerbspreis anlegen | 201, `competitor_price` ist NULL, Live-Preis rechnet mit 0 als Fallback | ✅ |  |
| TC-04 | Produkt bearbeiten: Wettbewerbspreis ändern | UI zeigt neuen Wert, Formel-Preis rechnet im nächsten Tick neu | ✅ | pytest `test_update_product_partial` deckt API-Seite ab |
| TC-05 | Fremdes Produkt bearbeiten (User B versucht Produkt von User A) | 404 | ✅ | pytest `test_ownership_isolation` |
| TC-06 | Produkt mit Strategie und Historie löschen | Kaskade über FK, Produkt aus Liste entfernt, Historie weg | ✅ | pytest `test_delete_product` deckt den Löschvorgang ab |

## **B. Preisstrategien – manuell und via KI (UC-4, UC-5)**

| ID | Beschreibung | Erwartet | Status | Bemerkung |
| ----- | ----- | ----- | ----- | ----- |
| TC-07 | Fixpreis setzen | Strategie gespeichert (`kind=fix`), Snapshot in Historie mit Reasoning „Snapshot bei Strategie-Aenderung" | ✅ | pytest `test_strategy_upsert_creates_and_updates` |
| TC-08 | Formel mit gültiger Syntax speichern | Strategie gespeichert (`kind=formula`), Live-Preis rechnet mit der Formel | ✅ |  |
| TC-09 | Formel mit Syntaxfehler speichern | 422 mit Fehlerbeschreibung, alte Strategie bleibt aktiv, kein Snapshot | ✅ | pytest `test_formula_strategy_rejects_invalid_expression` |
| TC-10 | Formel mit verbotenem Token `__import__("os")` speichern | 422, Strategie wird nicht gespeichert | ✅ | pytest `test_blocks_dangerous_constructs` deckt Evaluator direkt ab |
| TC-11 | Strategiewechsel Fix → Formel → Fix | Jeder Wechsel erzeugt einen History-Snapshot, Gesamthistorie zeigt alle drei Preise | ✅ |  |
| TC-12 | KI-Vorschlag ohne hinterlegten API-Key einholen | 503 mit Hinweistext, keine Strategie-Änderung | ✅ |  |
| TC-13 | KI-Vorschlag mit gültigem Key und Option „Ausführlich" | Prompt wird im Modal angezeigt, Vorschlag und Begründung kommen zurück, nichts wird gespeichert, bis der Nutzer *Speichern* klickt | ✅ | Human-in-the-Loop-Kontrolle |

## **C. Preisberechnung, Simulator, Graph (UC-6 bis UC-8)**

| ID | Beschreibung | Erwartet | Status | Bemerkung |
| ----- | ----- | ----- | ----- | ----- |
| TC-14 | Zwei-Schritt-Flow: `/price` ausstellen, dann `/price/confirm` | Eintrag in Historie mit Benutzer, Strategie, Inputs, Preis | ✅ | pytest `test_price_fix_flow_creates_history_only_on_confirm` |
| TC-15 | Confirm mit abgelaufenem `suggestion_token` (TTL \> 15 Minuten) | HTTP 410, kein Eintrag in Historie | ✅ | pytest `test_confirm_expired_token_410` |
| TC-16 | Stunden-Slider bewegen | Verkaufspreis rechnet live nach, keine Backend-Calls in Netzwerk-Tab | ✅ | Live-Prüfung per DevTools |
| TC-17 | Tagwechsel am Monatsende (Tick von Tag 28 zurück auf 1\) | Wochentag springt korrekt, Lagerbestand läuft bei 0 auf Lagergröße zurück (Auto-Refill) | ✅ |  |
| TC-18 | Graph-Modal mit Formel-Strategie öffnen | Chart rendert, Kurve sichtbar für gewählte Variable | ✅ |  |
| TC-19 | Graph-Variable wechseln (z. B. „Zeit gesamt") | Neue Kurve über 672 Stunden wird gerendert ohne Reload | ✅ |  |

## **D. KI-Wettbewerbspreis und Historie (UC-9, UC-10)**

| ID | Beschreibung | Erwartet | Status | Bemerkung |
| ----- | ----- | ----- | ----- | ----- |
| TC-20 | Wettbewerbspreis-Batch öffnen | Modal lädt, KI-Vorschlag mit alt/neu/Delta pro Produkt | ✅ |  |
| TC-21 | Einzelnen Wettbewerbspreis übernehmen | Nur das eine Produkt wird aktualisiert, andere bleiben unverändert | ✅ |  |
| TC-22 | Historie eines fremden Produkts anrufen | 404 | ✅ | pytest `test_ownership_protects_price_endpoints` |
| TC-23 | Historie zeigt KI-Badge korrekt bei `is_llm_suggestion=true` | Badge „KI-Vorschlag" sichtbar für betroffene Einträge | ⛔ |  |

## **E. Sicherheit und Auth (bereichsübergreifend)**

| ID | Beschreibung | Erwartet | Status | Bemerkung |
| ----- | ----- | ----- | ----- | ----- |
| TC-24 | Login mit falschem Passwort | 401, keine Session-Cookie-Setzung | ✅ | pytest `test_login_wrong_password_401` |
| TC-25 | Zugriff auf `/products` ohne Login | 401; Frontend leitet auf `/` (Login-Seite) | ✅ | pytest `test_list_requires_auth` |
| TC-26 | User A legt Produkt an, User B listet → sieht das Produkt nicht | `items` in der Response enthält das fremde Produkt nicht | ✅ | pytest `test_ownership_isolation` |

---

## **Zusammenfassung**

| Bereich | Anzahl Testfälle | pytest-Abdeckung |
| ----- | ----- | ----- |
| A. Produkt-Management | 6 | 4 |
| B. Preisstrategien | 7 | 3 |
| C. Preisberechnung, Simulator, Graph | 6 | 2 |
| D. KI-Wettbewerbspreis und Historie | 4 | 1 |
| E. Sicherheit und Auth | 3 | 3 |
| **Gesamt** | **26** | **13** |

Die Hälfte der Testfälle ist durch automatische Tests im Backend abgesichert. Die andere Hälfte sind UI-/Flow-bezogene Prüfungen, die sich am besten manuell in der Live-Umgebung durchführen lassen.

## **Vorgehen bei Abweichungen**

Weicht das Ergebnis vom *Erwarteten* ab, wird der Testfall auf ⛔ gesetzt und in [`bug-log.md`](https://claude.ai/chat/bug-log.md) ein Bug mit Titel, Reproduktionsschritten, Priorität und Zuordnung angelegt. Nach Fix und Re-Test aktualisiert Person B den Status zurück auf ✅.

Testfälle, die bewusst nicht behoben werden (z. B. Mobile-Layout-Probleme, weil Mobile-Optimierung out-of-scope ist), gehen auf **Wontfix** mit einer Begründung in der Bemerkung.
