# Architektur

## Überblick

```
┌────────────────────┐   REST/JSON    ┌──────────────────────┐     SQL    ┌──────────┐
│ Browser / Frontend │ ─────────────▶ │  Backend (FastAPI)   │ ─────────▶ │Postgres  │
│ HTML + Alpine.js   │   Session-     │  · Auth, Rate Limit  │            │          │
│ + Pico + Chart.js  │   Cookie       │  · Preis-Strategien  │            └──────────┘
└────────────────────┘                │  · KI-Prompt-Bau     │
                                      │  · HTTPS-Helper      │
                                      └──────────┬───────────┘
                                                 │ HTTPS (Produktdaten only)
                                                 ▼
                                          ┌──────────────┐
                                          │ Gemini API   │
                                          └──────────────┘
```

Das Frontend wird vom Backend als statische Dateien ausgeliefert (gleiches
Origin). Die API liegt unter `/api/v1`.

## Komponenten

### Frontend (`frontend/`)
- Zero-Build: Alpine.js, Pico.css und Chart.js werden von jsdelivr geladen.
- `frontend/js/api.js` kapselt `fetch` mit `credentials: 'include'`,
  einheitlichem Error-Handling und automatischem Login-Redirect bei 401
  (per `silent401`-Opt-in deaktivierbar für öffentliche Seiten wie
  `legal.html`).
- `frontend/js/store.js` hält einen Alpine-Store `auth` mit
  `ensureMe()` / `isAdmin()` für konditionelle UI-Blöcke.
- `frontend/js/formula-eval.js` ist ein Mini-Evaluator mit derselben
  Whitelist (Variablen + Funktionen) wie der Backend-AST-Evaluator.
  Reguläre-Ausdruck-Gate + Forbidden-Token-Check; nur deshalb darf für die
  Live-Preview ein `new Function(…)` verwendet werden.
- Seiten unter `frontend/pages/`: `products.html` (Haupt-Dashboard mit
  Simulation), `history.html`, `settings.html`, `legal.html` (öffentlich),
  `compliance.html` (hinter Login).

### Backend (`backend/app/`)
- **Router** unter `app/routers/`: `auth`, `products`, `pricing`, `users`,
  `settings`, `public`. Jede Route ist entweder über `get_current_user`
  (regulär), `get_current_user_rate_limited` (zählt das Tageskontingent)
  oder `get_current_admin` (admin-only) auth'd.
- **Strategien** unter `app/strategies/`: Registry (`registry.py`) mappt
  `kind` → `compute`-Funktion. `evaluator.py` ist der sichere AST-basierte
  Formel-/Regel-Evaluator. `runtime.py` baut das Variablen-Dict aus
  statischen Produktdaten und optionalem Runtime-Kontext zusammen.
- **LLM** (`app/llm.py`) baut die Prompts, ruft die Gemini-API, parst die
  JSON-Antwort und liefert geprüfte Ergebnisse. Alle Aufrufe sind
  zweckgebunden – nur Produkt-Whitelist-Felder gehen raus, keine
  Kundendaten. Siehe `docs/compliance.md`.
- **Services** (`app/services/`): `app_settings` (Key/Value-Store für
  Gemini-Key, HTTPS-Domain, Rate-Limits), `seeding` (Admin- und Mock-
  Produkte idempotent anlegen + DB-Reset).
- **Datenzugriff:** SQLAlchemy 2.x ORM mit `Mapped[…]`, Alembic-
  Migrationen unter `backend/alembic/versions/`.

### Datenbank
PostgreSQL, siehe `docs/data-model.md` für das Schema.

### LLM
Google Gemini, serverseitig aufgerufen. Key kann in `.env` oder per
Einstellungsseite (Tabelle `app_settings`) liegen; DB-Wert hat Vorrang.

## Deployment

Betrieb auf Debian 12, siehe `docs/decisions/0005-deployment-debian.md`.

- `install.sh` richtet Pakete (Python, Postgres, nginx, sudo, certbot,
  python3-certbot-nginx) ein, legt den System-User `preisopt` an und
  startet den Backend-Service.
- `systemd` managt das Backend: `/etc/systemd/system/preisopt-backend.service`
  (Unit-Template im Repo: `deploy/preisopt-backend.service`).
- `nginx` als Reverse-Proxy auf Port 80 (Template: `deploy/nginx-preisopt.conf`).
  Bei 502/503/504 invalidiert die Location `@bad_gateway` das
  Session-Cookie und liefert eine saubere Fehlerseite.
- `HTTPS` per Klick: Einstellungen → HTTPS aktivieren ruft
  `/usr/local/bin/preisopt-https-enable` über sudo auf (sudoers-Regel:
  `deploy/sudoers.d-preisopt`). Helper setzt den `server_name`, lädt
  nginx neu und lässt `certbot --nginx` Zertifikat + Redirect einspielen.

## Datenfluss: Preisvorschlag

1. Frontend → `POST /products/{id}/strategy/prompt-preview` (optional) liefert
   den Prompt **ohne** LLM-Call – Transparenz vor dem Klick.
2. Frontend → `POST /products/{id}/strategy/suggest`; Backend baut erneut den
   Prompt (inkl. `fancy`- und `online`-Flags), ruft Gemini, validiert die
   Formel und gibt sie als Vorschlag zurück.
3. User speichert → `PUT /products/{id}/strategy`; Backend schreibt die neue
   Strategie und zusätzlich einen Snapshot in `price_history` (Audit).
4. Im Tabellenzeilen-Button *„In Historie"* läuft der Confirm-Flow:
   `POST /price` (→ `price_suggestions` + Token) und
   `POST /price/confirm` (Token verbraucht, Historien-Eintrag).

## Sicherheitsgrenzen

- Kein direkter DB-Zugriff aus dem Frontend.
- LLM-Aufrufe nur aus dem Backend, Whitelist strikt.
- Passwörter: Argon2id.
- Session-Cookie: HttpOnly + SameSite=Lax.
- Rate Limit pro User pro Tag; Admin-only Admin-Endpoints.
- nginx invalidiert Session-Cookie bei 5xx, damit keine hängen bleiben.
- HTTPS-Helper läuft mit genau einem sudoers-Eintrag, keine Shell-Interpolation.
