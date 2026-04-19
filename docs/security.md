# Sicherheit & Datenschutz

## Secrets
- Alle Secrets (DB-Credentials, LLM-API-Keys, Session-Secret) liegen in `.env` und werden über Umgebungsvariablen geladen.
- `.env` ist in `.gitignore`. Eine `.env.example` ohne Werte dient als Vorlage.
- Keys werden niemals geloggt.

## LLM-Datennutzung
- An den externen LLM-Service werden ausschließlich produktbezogene Whitelist-Felder gesendet (z. B. Titel, Kategorie, Einkaufspreis, Wettbewerbspreis).
- **Niemals** an das LLM gesendet: Kundendaten, Bestelldaten, personenbezogene Daten von Käufern, interne IDs, Auth-Tokens.
- Begründung: DSGVO-Datenminimierung; Vermeidung der Übertragung personenbezogener Daten an Drittanbieter außerhalb des nötigen Zwecks.
- Die Whitelist ist im Backend hart konfiguriert und wird per Code-Review gepflegt.

## Authentifizierung & Autorisierung
- Verfahren: TBD (Session-Cookie oder JWT). Entscheidung folgt in einem ADR.
- Passwörter werden gehasht gespeichert (z. B. argon2 oder bcrypt).

## Transport
- Im Betrieb HTTPS-only; lokal Entwicklung über HTTP zulässig.

## Logging
- Anwendungsdaten ja, sensible Daten (Passwörter, API-Keys, vollständige LLM-Requests mit Klartext-Geheimnissen) nein.

## Offene Punkte
- Konkrete DSGVO-Bewertung dokumentieren (Verantwortlicher, Zwecke, Speicherfristen).
- Backup- und Lösch-Konzept der Datenbank.
