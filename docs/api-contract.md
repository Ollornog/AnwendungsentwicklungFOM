# API-Vertrag

> Erste Skizze. Endgültige Definition über OpenAPI (FastAPI generiert `/docs` automatisch).

## Konventionen
- Basis-URL: `/api/v1`
- Format: JSON
- Auth: TBD (Session oder JWT, siehe `docs/security.md`)

## Geplante Endpoints (Entwurf)
| Methode | Pfad | Zweck |
| --- | --- | --- |
| `POST` | `/auth/login` | Anmeldung |
| `GET` | `/products` | Produkte listen |
| `POST` | `/products` | Produkt anlegen |
| `GET` | `/products/{id}` | Produkt-Detail |
| `PUT` | `/products/{id}` | Produkt aktualisieren |
| `DELETE` | `/products/{id}` | Produkt löschen |
| `PUT` | `/products/{id}/strategy` | Preisstrategie konfigurieren |
| `POST` | `/products/{id}/price` | Preis berechnen (laut aktiver Strategie) |
| `GET` | `/products/{id}/history` | Preis-Historie abrufen |

## Verweis
Live-Doku: später unter `/docs` (Swagger UI von FastAPI).
