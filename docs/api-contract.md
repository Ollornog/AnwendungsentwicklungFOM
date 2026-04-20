# API-Vertrag

Live-Doku: FastAPI generiert unter `/docs` eine Swagger-UI (Dev-Mode) mit allen
Endpoints, Schemas und Fehler-Responses. Dieses Dokument gibt den fachlichen
Überblick; Stichwortverzeichnis für die Architektur.

## Konventionen
- **Basis-URL:** `/api/v1`
- **Format:** JSON
- **Auth:** Session-Cookie (HttpOnly, SameSite=Lax, signiert via
  Starlette-`SessionMiddleware`, siehe ADR 0003).
- **Frontend** sendet bei jedem Call `credentials: 'include'`.
- **Rate Limit:** jeder authentifizierte Aufruf (außer Auth-Endpoints und
  Settings) zählt auf das Tageskontingent des Users. Überschreitung → `429`.
- **Admin-Guards:** die Bereiche `/users`, `/settings/https*` und
  `/settings/rate-limit*` sind nur für den Account `admin` zugänglich (`403`
  für alle anderen).

## Auth

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `POST` | `/auth/login` | Zugangsdaten prüfen, Session setzen |
| `POST` | `/auth/logout` | Session invalidieren (`204`) |
| `GET` | `/auth/me` | Aktuellen Benutzer liefern |
| `POST` | `/auth/password` | Eigenes Passwort ändern (altes + neues) |

## Produkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/products` | Eigene Produkte listen |
| `POST` | `/products` | Produkt anlegen |
| `GET` | `/products/{id}` | Einzeldaten |
| `PUT` | `/products/{id}` | Produkt bearbeiten |
| `DELETE` | `/products/{id}` | Produkt löschen |
| `POST` | `/products/competitor-prices/suggest` | KI schätzt Wettbewerbspreise für alle eigenen Produkte in einem Batch-Call |

## Strategie & Preis

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `PUT` | `/products/{id}/strategy` | Strategie setzen/ändern (schreibt zusätzlich einen Snapshot in die Historie) |
| `POST` | `/products/{id}/strategy/prompt-preview` | Prompt berechnen, ohne das LLM aufzurufen – Transparenz vor dem Klick |
| `POST` | `/products/{id}/strategy/suggest` | KI-Vorschlag für Fix/Formel holen (Body: `target`, `online`, `fancy`) |
| `POST` | `/products/{id}/price` | Preis aus aktiver Strategie **vorschlagen**. Body optional mit Runtime-Kontext (`hour`, `day`, `current_stock`, `demand`). |
| `POST` | `/products/{id}/price/confirm` | Vorschlag bestätigen und in Historie schreiben |
| `GET` | `/products/{id}/history` | Preis-Historie des Produkts |

### Preis-Flow (Human-in-the-Loop)

1. `POST /products/{id}/price` berechnet einen **Vorschlag** und erzeugt noch
   keinen Historien-Eintrag. Response enthält einen `suggestion_token` mit
   TTL (`SUGGESTION_TTL_MINUTES`).
2. `POST /products/{id}/price/confirm` mit dem Token persistiert den Eintrag.
3. Zusätzlich schreibt `PUT /products/{id}/strategy` automatisch einen
   Snapshot in die Historie, damit Strategie-Wechsel auditierbar sind.

Beispiel-Response:
```json
{
  "suggestion_token": "…",
  "price": 49.90,
  "currency": "EUR",
  "strategy": "formula",
  "is_llm_suggestion": false,
  "reasoning": "Formel: cost_price * 1.8",
  "inputs": { "cost_price": "29.90", "hour": "12", "day": "15", "…": "…" }
}
```

`is_llm_suggestion = true` nur, wenn der Preis vom LLM kam. Das Frontend rendert
dann das `KI-Vorschlag`-Badge (Transparenzpflicht Art. 50 AI Act).

## Benutzer (admin-only)

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/users` | Alle Accounts listen |
| `POST` | `/users` | Account anlegen |
| `PUT` | `/users/{id}` | Passwort / Rolle ändern |
| `DELETE` | `/users/{id}` | Account löschen |

Der bootstrap-Admin (`username=admin`) ist serverseitig gegen PUT/DELETE
geschützt (`403`).

## Einstellungen

| Methode | Pfad | Zweck | Admin-only |
| --- | --- | --- | --- |
| `GET` | `/settings` | Status des Gemini-Keys (DB vs. `.env`) | nein |
| `PUT` | `/settings` | Gemini-Key setzen/löschen | nein |
| `POST` | `/settings/reset-database` | Alle eigenen Produkte + Historie auf Seed-Stand zurücksetzen | nein |
| `GET` | `/settings/https` | HTTPS-Status (aktiv? Domain?) | ja |
| `POST` | `/settings/https/enable` | Let's-Encrypt-Zertifikat holen (certbot-nginx via Helper) | ja |
| `GET` | `/settings/rate-limit` | Tages-Limits ausgeben | ja |
| `PUT` | `/settings/rate-limit` | Tages-Limits ändern | ja |

## Öffentlich (ohne Login)

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/public/info` | Für die Impressum-/Datenschutz-Seite: hinterlegte Domain + HTTPS-Status |
| `GET` | `/health` | Health-Check (Smoketest des Installers) |

## Historie-Payload

```json
{
  "items": [
    {
      "id": "…",
      "created_at": "2026-04-20T14:12:00Z",
      "price": 49.90,
      "currency": "EUR",
      "strategy": "formula",
      "is_llm_suggestion": false,
      "inputs": { "…": "…" },
      "reasoning": "…",
      "username": "admin"
    }
  ]
}
```
