# Architektur

## Überblick
Drei interne Komponenten plus ein externer Dienst:

```
[ Browser / Frontend ]  --REST/JSON-->  [ Backend (FastAPI) ]  --SQL-->  [ PostgreSQL ]
                                                |
                                                +--HTTPS-->  [ LLM-API (Google Gemini) ]
```

Das Frontend wird vom Backend als statische Dateien ausgeliefert (gleiches Origin), die API liegt unter `/api/v1`.

## Komponenten und Grenzen
- **Frontend (HTML + Alpine.js + Pico.css):** Reine Präsentations- und Interaktionsschicht. Kein Datenbankzugriff, keine Preislogik. Spricht nur die REST-API an. Zero-Build: Alpine und Pico kommen via CDN. Details siehe `docs/decisions/0004-frontend-stack.md`.
- **Backend (FastAPI):** Einzige Stelle für Geschäftslogik, Preisstrategie-Auswertung, Authentifizierung und Datenzugriff. Kapselt LLM-Aufrufe und entscheidet, welche Felder das LLM zu sehen bekommt. Liefert zusätzlich `frontend/` via `StaticFiles` aus.
- **Datenbank (PostgreSQL):** Persistiert Produkte, Strategien, Preis-Historie, Benutzer.
- **LLM-Service (extern, Google Gemini):** Wird ausschließlich serverseitig aufgerufen, niemals direkt aus dem Frontend.

## Warum Frontend/Backend getrennt?
- Klare Verantwortlichkeiten und Testbarkeit.
- Sicherheit: API-Keys und DB-Zugriff bleiben serverseitig.
- Austauschbarkeit: Frontend kann später durch ein Framework oder eine andere UI ersetzt werden, weil die Kommunikation ausschließlich über REST läuft.

## Authentifizierung
Session-Cookie (HttpOnly, SameSite=Lax), siehe `docs/decisions/0003-auth-session-cookie.md`. Frontend setzt bei jedem API-Call `credentials: 'include'`.

## Offene Punkte
- Deployment-Form (lokal für Demo, Container, Hosting) – TBD.
- Session-Store (In-Memory für Prototyp, für Produktiv: Redis o. ä.).
