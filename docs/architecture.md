# Architektur

## Überblick
Drei interne Komponenten plus ein externer Dienst:

```
[ Browser / Frontend ]  --REST/JSON-->  [ Backend (FastAPI) ]  --SQL-->  [ PostgreSQL ]
                                                |
                                                +--HTTPS-->  [ LLM-API (Claude/OpenAI) ]
```

## Komponenten und Grenzen
- **Frontend (HTML/JS):** Reine Präsentations- und Interaktionsschicht. Kein Datenbankzugriff, keine Preislogik. Spricht nur die REST-API an.
- **Backend (FastAPI):** Einzige Stelle für Geschäftslogik, Preisstrategie-Auswertung, Authentifizierung und Datenzugriff. Kapselt LLM-Aufrufe und entscheidet, welche Felder das LLM zu sehen bekommt.
- **Datenbank (PostgreSQL):** Persistiert Produkte, Strategien, Preis-Historie, Benutzer.
- **LLM-Service (extern):** Wird ausschließlich serverseitig aufgerufen, niemals direkt aus dem Frontend.

## Warum Frontend/Backend getrennt?
- Klare Verantwortlichkeiten und Testbarkeit.
- Sicherheit: API-Keys und DB-Zugriff bleiben serverseitig.
- Austauschbarkeit: Frontend kann später durch ein Framework oder eine andere UI ersetzt werden.

## Offene Punkte
- Authentifizierungs-Verfahren (Session vs. JWT) – TBD.
- Deployment-Form (lokal für Demo, Container, Hosting) – TBD.
