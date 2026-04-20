# Use Cases

Kurzformat: Akteur, Ziel, Ablauf. Ausnahmen nur, wenn relevant.

## UC-01 Produkt anlegen
- **Akteur:** Shop-Betreiber.
- **Ziel:** Ein Produkt mit Stammdaten und Kontext erfassen.
- **Ablauf:**
  1. Klick auf **Produkt hinzufügen** in der Navigation öffnet das
     Anlegen-/Bearbeiten-Modal.
  2. Felder: Name, Kategorie, Einkaufspreis, Wettbewerbspreis (optional),
     Verbrauch/Monat, Lagergröße, Kontext-Freitext (wird an die KI gegeben).
  3. Backend validiert (Pydantic) und speichert.
  4. Liste aktualisiert sich sofort, Produkt taucht ganz oben auf.

## UC-02 Preisstrategie festlegen
- **Akteur:** Shop-Betreiber.
- **Ziel:** Fixpreis oder Formel für das Produkt setzen.
- **Ablauf:**
  1. In der Produktzeile **Preis** klicken.
  2. Im Modal zwischen *Fixpreis* und *Formel* wählen.
  3. Wert direkt eintragen, oder **KI vorschlagen** aktivieren; optional
     dazu **Online recherchieren** und **Ausführlich**. Per *KI fragen* wird
     der Vorschlag erzeugt (Frage und Begründung sind sichtbar).
  4. *Speichern* persistiert die Strategie und schreibt einen
     Snapshot-Eintrag in die Preis-Historie.

## UC-03 Live-Simulation und Live-Preis
- **Akteur:** Shop-Betreiber.
- **Ziel:** Verstehen, wie der Preis auf Uhrzeit, Tag, Lagerstand und
  Nachfrage reagiert.
- **Ablauf:**
  1. Globale Slider **Stunde** (0–23) und **Tag** (1–28) oben in der Leiste.
  2. Pro Produkt: Slider für **Lager (aktuell)** und **Nachfrage** (0.00–2.00).
  3. **▶/⏸** startet/pausiert den Tick; **3×** läuft dreimal so schnell.
  4. Ein Tick entspricht einer Stunde Simulationszeit; Lager reduziert sich
     um `monthly_demand / (28·24) · demand` pro Tick und füllt bei 0 auf
     die Lagergröße auf.
  5. Spalte **Verkaufspreis** wird bei jeder Slider-Änderung live neu
     berechnet (JS-Evaluator mit dem gleichen Variablen-/Funktions-Satz wie
     das Backend).

## UC-04 Preis-Historie einsehen
- **Akteur:** Shop-Betreiber.
- **Ziel:** Nachvollziehen, wann welche Strategie wie ausgewertet wurde.
- **Ablauf:**
  1. In der Produktzeile **Historie** klicken.
  2. Seite zeigt Zeitstempel, Preis, Strategie, Benutzer, KI-Markierung
     (Badge) und Begründung.
  3. Einträge entstehen entweder beim Strategie-Wechsel (automatischer
     Snapshot) oder über den Confirm-Flow `POST /price/confirm`.

## UC-05 Graph pro Variable
- **Akteur:** Shop-Betreiber.
- **Ziel:** Preisverlauf über eine Achse (Zeit, Lager, Nachfrage, …) prüfen.
- **Ablauf:**
  1. Pro Produktzeile **Graph** öffnet ein Modal mit Chart.js-Line-Chart.
  2. Dropdown wählt die Variable (z. B. *Zeit gesamt (1 Monat)* für 672
     Stunden-Samples). Alle anderen Werte bleiben auf dem aktuellen
     Simulations-/Produkt-Stand.
  3. Funktioniert für Fix und Formel; für *Regel*/*LLM* zeigt das Modal
     einen Hinweis (nicht sinnvoll client-seitig simulierbar).

## UC-06 KI-gestützte Wettbewerbspreise
- **Akteur:** Shop-Betreiber.
- **Ziel:** Für alle Produkte auf einmal plausible Wettbewerbspreise
  generieren und selektiv übernehmen.
- **Ablauf:**
  1. Nav-Link **Wettbewerb (KI)** öffnet das Modal.
  2. Backend schickt die Produkt-Whitelist (Name, Kategorie, Einkaufspreis,
     Kontext, aktueller Wettbewerb) in einem einzigen Gemini-Call.
  3. KI liefert pro Produkt einen geschätzten Preis + Begründung.
  4. Pro Zeile **Übernehmen** oder **Alle übernehmen** – Änderungen sind
     sofort in der Produktliste sichtbar.

## UC-07 Benutzerverwaltung (admin-only)
- **Akteur:** Admin.
- **Ziel:** Team-Accounts pflegen.
- **Ablauf:**
  1. Einstellungen → **Benutzerverwaltung** listet alle Accounts.
  2. Passwort ändern per Zeilen-Button (Prompt-Dialog); Account löschen mit
     Confirm.
  3. Der bootstrap-Admin (`admin`) ist geschützt – beide Aktionen in der UI
     deaktiviert und im Backend mit `403`.

## UC-08 Rate Limit einstellen (admin-only)
- **Akteur:** Admin.
- **Ziel:** Tageskontingent pro Nutzer festlegen.
- **Ablauf:**
  1. Einstellungen → **Rate Limiting**.
  2. Zwei Felder (Standard-Nutzer / Admin), persistiert in `app_settings`.
  3. Zähler laufen um Mitternacht Serverzeit auf 0. Überschreitung →
     HTTP 429.

## UC-09 HTTPS per Klick (admin-only)
- **Akteur:** Admin.
- **Ziel:** TLS-Zertifikat über Let's Encrypt holen und nginx umstellen.
- **Ablauf:**
  1. Einstellungen → **HTTPS (Let's Encrypt)**, Domain eintragen.
  2. Backend ruft über `sudo` ein klar abgegrenztes Helper-Skript auf, das
     den `server_name` der nginx-Site setzt, `certbot --nginx` ausführt und
     den HTTP→HTTPS-Redirect konfiguriert.
  3. Status („aktiv für <domain>") wird in `app_settings` gehalten.

## UC-10 Datenbank zurücksetzen
- **Akteur:** eingeloggter Nutzer (für eigene Daten).
- **Ziel:** Demo-Zustand wiederherstellen.
- **Ablauf:**
  1. Einstellungen → **Datenbank zurücksetzen**, Confirm.
  2. Backend löscht alle Produkte, Strategien, Historie, Suggestions **des
     aufrufenden Users**.
  3. Mock-Produkte werden neu angelegt. Accounts und API-Key bleiben.
