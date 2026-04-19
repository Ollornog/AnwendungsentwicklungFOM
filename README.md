# KI-gestützte Preisoptimierung im E-Commerce

Studentisches Semesterprojekt der FOM Hochschule, Modul Anwendungsentwicklung.

Web-Tool, in dem Shop-Betreiber Produkte verwalten und pro Produkt eine von vier Preisstrategien (Fixpreis, Formel, Regel, LLM-basiert) wählen. Jede Preisberechnung wird historisiert.

> **Disclaimer:** Studentischer Prototyp der FOM Hochschule. Nicht für den Produktivbetrieb. Rechtliche Anforderungen (DSGVO, EU AI Act, Preisrecht) werden konzeptionell adressiert, nicht produktiv umgesetzt.

## Überblick
- **Backend:** Python 3.11 + FastAPI + SQLAlchemy + Alembic.
- **Datenbank:** PostgreSQL 16.
- **Frontend:** HTML + Alpine.js + Pico.css (zero-build, via CDN).
- **LLM:** Google Gemini (Key in `.env`).
- **Deployment:** Debian 12 + nginx + systemd, per `install.sh`.

Architektur-Details in `CLAUDE.md` und `docs/`.

## Setup auf Debian 12

```bash
git clone <repo-url>
cd AnwendungsentwicklungFOM
sudo ./install.sh
```

Das Skript installiert `python3`, `postgresql`, `nginx`, legt den System-User `preisopt` an, richtet DB, venv, Migrationen, Seed-Daten, systemd-Unit und nginx-Site ein.

Optionen:

- `--skip-seed` – keine Mock-Produkte anlegen
- `--no-nginx` – ohne Reverse-Proxy (Uvicorn direkt auf `127.0.0.1:8000`)
- `--admin-username <name>` – Admin-User überschreiben (Default: `admin`)

Umgebungsvariablen (optional, sonst wird interaktiv gefragt / generiert):

- `PREISOPT_ADMIN_PASSWORD` – Passwort für den Admin-User
- `PREISOPT_DB_PASSWORD` – Passwort für den Postgres-User `preisopt`
- `GEMINI_API_KEY` – Key für die LLM-Strategie (sonst leer → LLM-Strategie schlägt fehl, alle anderen Strategien laufen)

Nach dem Lauf:

```
URL:         http://<server-ip>/
Service:     systemctl status preisopt-backend
Logs:        journalctl -u preisopt-backend -f
.env:        /opt/preisopt/.env
```

## Entwicklung (lokal, ohne install.sh)

```bash
# Postgres bereitstellen (z. B. per Docker oder apt)
createdb preisopt
cp .env.example .env   # und Werte anpassen

cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m seed --password changeme        # Mock-Daten
uvicorn app.main:app --reload             # läuft auf http://localhost:8000
```

## Doku
Einstieg: [`CLAUDE.md`](./CLAUDE.md). Detail-Doku unter [`docs/`](./docs/).
