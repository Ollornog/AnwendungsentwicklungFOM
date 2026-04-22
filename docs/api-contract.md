# API-Vertrag

Vollständige, maschinenlesbare Doku liefert FastAPI unter `/docs`
(Swagger UI) und `/redoc`. Dieses Dokument fasst Grundlagen und die
wichtigsten Endpoints zusammen.

## Grundlagen

- **Base URL:** `/api/v1`
- **Content-Type:** `application/json`
- **Auth:** signiertes Session-Cookie (`SameSite=Lax`, `HttpOnly`).
  Frontend setzt bei jedem Call `credentials: 'include'`.
- **Rate Limit:** jeder authentifizierte Aufruf (außer Auth- und
  Settings-Endpoints) zählt auf das Tageskontingent des Users.
  Standard 50/Tag, Admin 200/Tag; überschritten → `429`.
- **Admin-Guards:** `/users`, `GET`/`PUT /settings` (Gemini-Key),
  `/settings/https*` und `/settings/rate-limit*` sind nur für den
  Account `admin` zugänglich.
- **Fehlerschema:** Pydantic-Errors als `{"detail": "..."}`; bei
  Validierungsfehlern das FastAPI-`422`-Schema.

## Endpoint-Übersicht

### Auth (`/auth`)

| Methode | Pfad | Zweck | Auth |
| --- | --- | --- | --- |
| POST | `/auth/login` | Session setzen | – |
| POST | `/auth/logout` | Session invalidieren | Cookie |
| GET | `/auth/me` | Aktuellen User liefern | Cookie |
| POST | `/auth/password` | Eigenes Passwort ändern | Cookie |

### Produkte (`/products`)

| Methode | Pfad | Zweck |
| --- | --- | --- |
| GET | `/products` | Eigene Produkte listen |
| POST | `/products` | Produkt anlegen |
| GET | `/products/{id}` | Einzeldaten |
| PUT | `/products/{id}` | Produkt bearbeiten |
| DELETE | `/products/{id}` | Produkt löschen |
| POST | `/products/competitor-prices/suggest` | KI schätzt Wettbewerbspreise (Batch) |

### Strategie & Preis (`/products/{id}`)

| Methode | Pfad | Zweck |
| --- | --- | --- |
| PUT | `/products/{id}/strategy` | Strategie setzen (schreibt Snapshot in History) |
| POST | `/products/{id}/strategy/prompt-preview` | Prompt berechnen ohne LLM-Call |
| POST | `/products/{id}/strategy/suggest` | KI-Vorschlag Fixpreis / Formel |
| POST | `/products/{id}/price` | Preis **vorschlagen** (Runtime-Kontext optional) |
| POST | `/products/{id}/price/confirm` | Vorschlag bestätigen → Historie |
| GET | `/products/{id}/history` | Preis-Historie |

### Benutzer (`/users`, admin-only)

| Methode | Pfad | Zweck |
| --- | --- | --- |
| GET | `/users` | Accounts listen |
| POST | `/users` | Account anlegen |
| PUT | `/users/{id}` | Passwort / Rolle ändern |
| DELETE | `/users/{id}` | Account löschen |

### Einstellungen (`/settings`)

| Methode | Pfad | Zweck | Admin-only |
| --- | --- | --- | --- |
| GET | `/settings` | Gemini-Key-Status | ja |
| PUT | `/settings` | Gemini-Key setzen/löschen | ja |
| POST | `/settings/reset-database` | Eigene Daten auf Seed-Stand | – |
| GET | `/settings/https` | HTTPS-Status | ja |
| POST | `/settings/https/enable` | Let's-Encrypt-Zertifikat holen | ja |
| GET | `/settings/rate-limit` | Aktuelle Tageslimits | ja |
| PUT | `/settings/rate-limit` | Tageslimits ändern | ja |
| GET | `/settings/llm-audit` | Audit-Log aller KI-Anfragen, neueste zuerst (Query-Param `limit`, 1–500, Default 200) | ja |

### Öffentlich

| Methode | Pfad | Zweck |
| --- | --- | --- |
| GET | `/public/info` | Domain + HTTPS-Status für Legal-Seite |
| GET | `/health` | Smoketest (Health-Check) |

## Kern-Endpoints im Detail

### `POST /products`

Request:
```json
{
  "name": "Sneaker Classic",
  "category": "Schuhe",
  "cost_price": "29.90",
  "stock": 42,
  "competitor_price": "59.00",
  "context": "Klassischer Lifestyle-Sneaker...",
  "monthly_demand": 80
}
```

Response `201`: der angelegte Datensatz inkl. `id` und `strategy: null`.

### `PUT /products/{id}/strategy`

Request (Formel):
```json
{
  "kind": "formula",
  "config": { "expression": "cost_price * 1.8 + (hour >= 18) * 2" }
}
```

Response: gespeicherte Strategie. Nebenbei entsteht in
`price_history` ein Snapshot mit dem Preis bei Default-Runtime
(hour = 0, day = 1, stock = start_stock, demand = 1).

### `POST /products/{id}/strategy/suggest`

Request:
```json
{ "target": "formula", "online": false, "fancy": false }
```

Response:
```json
{
  "target": "formula",
  "amount": null,
  "expression": "round(cost_price * 1.8 + (hour >= 18) * 2, 2)",
  "reasoning": "Abendaufschlag ab 18 Uhr, sonst Marge 80 %.",
  "prompt": "Du bist ein Preis-Assistent ... [vollständiger Prompt]"
}
```

### `POST /products/{id}/price`

Body optional mit Runtime-Kontext (`hour`, `day`, `current_stock`,
`demand` 0–2). Response enthält den berechneten Preis + einen
`suggestion_token`; der Eintrag in die Historie entsteht erst mit
`/price/confirm`.

```json
{
  "suggestion_token": "…",
  "price": "53.82",
  "currency": "EUR",
  "strategy": "formula",
  "is_llm_suggestion": false,
  "reasoning": "Formel: cost_price * 1.8",
  "inputs": { "cost_price": "29.90", "hour": "12", "day": "15", "demand": "1" }
}
```

### `GET /products/{id}/history`

Liefert eine chronologisch absteigend sortierte Liste aller Einträge:

```json
{
  "items": [
    {
      "id": "…",
      "created_at": "2026-04-20T14:12:00Z",
      "price": "53.82",
      "currency": "EUR",
      "strategy": "formula",
      "is_llm_suggestion": false,
      "inputs": { "…": "…" },
      "reasoning": "Formel: cost_price * 1.8",
      "username": "admin"
    }
  ]
}
```

## Hinweis

Detaillierte Request-/Response-Schemas pro Endpoint siehe
`http://<host>/docs` (Swagger-UI, automatisch aus den Pydantic-
Schemas generiert) bzw. `/redoc`.
