# API-Vertrag

> Erste Skizze. Endgültige Definition über OpenAPI (FastAPI generiert `/docs` automatisch).

## Konventionen
- Basis-URL: `/api/v1`
- Format: JSON
- Auth: Session-Cookie (HttpOnly, SameSite=Lax), siehe `docs/decisions/0003-auth-session-cookie.md`
- Frontend sendet bei jedem Call `credentials: 'include'`.

## Geplante Endpoints (Entwurf)
| Methode | Pfad | Zweck |
| --- | --- | --- |
| `POST` | `/auth/login` | Anmeldung, setzt Session-Cookie |
| `POST` | `/auth/logout` | Session invalidieren |
| `GET` | `/products` | Produkte listen |
| `POST` | `/products` | Produkt anlegen |
| `GET` | `/products/{id}` | Produkt-Detail |
| `PUT` | `/products/{id}` | Produkt aktualisieren (inkl. Lagerbestand, UC-04) |
| `DELETE` | `/products/{id}` | Produkt löschen |
| `PUT` | `/products/{id}/strategy` | Preisstrategie konfigurieren |
| `POST` | `/products/{id}/price` | Preis **vorschlagen** (berechnen, noch nicht persistieren) |
| `POST` | `/products/{id}/price/confirm` | Vorschlag bestätigen und in Historie persistieren |
| `GET` | `/products/{id}/history` | Preis-Historie abrufen |

## Preis-Flow (UC-03, Human-in-the-Loop)
Zwei-Schritt-Flow, damit Leitprinzip 3 (Human-in-the-Loop) strukturell abgebildet ist:

1. `POST /products/{id}/price` berechnet einen **Vorschlag**, erzeugt aber **keinen** Historien-Eintrag. Response enthält einen Vorschlags-Token, der mit dem Request validiert wird.
2. `POST /products/{id}/price/confirm` mit dem Token persistiert den Eintrag.

Beispiel-Response `POST /products/{id}/price`:

```json
{
  "suggestion_token": "…",
  "price": 49.90,
  "currency": "EUR",
  "strategy": "llm",
  "is_llm_suggestion": true,
  "reasoning": "Wettbewerbspreis 52,00 € – Positionierung leicht darunter.",
  "inputs": { "…": "…" }
}
```

`is_llm_suggestion: true` ist **nur** gesetzt, wenn der Preis von einem LLM vorgeschlagen wurde. Frontend rendert in diesem Fall ein "KI-Vorschlag"-Badge (Leitprinzip 4).

## Historie
`GET /products/{id}/history` liefert Einträge in der Form:

```json
{
  "items": [
    {
      "id": "…",
      "created_at": "2026-04-19T14:12:00Z",
      "price": 49.90,
      "currency": "EUR",
      "strategy": "llm",
      "is_llm_suggestion": true,
      "inputs": { "…": "…" },
      "reasoning": "…"
    }
  ]
}
```

## Verweis
Live-Doku: später unter `/docs` (Swagger UI von FastAPI).
