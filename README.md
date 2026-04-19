# KI-gestützte Preisoptimierung im E-Commerce

Studentisches Semesterprojekt der FOM Hochschule, Modul Anwendungsentwicklung.

## Installation auf Debian 12

```bash
# als root eingeloggt (oder mit sudo vorweg):
apt-get update && apt-get install -y git
git clone https://github.com/Ollornog/AnwendungsentwicklungFOM
cd AnwendungsentwicklungFOM
./install.sh
```

Das Skript ist auf eine **frisch installierte Debian-12-Maschine** ausgelegt. Voraussetzungen: Root-Rechte und eine Internetverbindung — sonst nichts. Alle Abhängigkeiten kommen aus den Debian-Repos, es werden keine Fremdquellen hinzugefügt.

> Nicht als root eingeloggt? Dann `sudo ./install.sh` statt `./install.sh`. `sudo` ist auf minimalen Debian-Netinstalls aber nicht vorhanden — dann vorher `apt-get install -y sudo` oder direkt als root arbeiten.

> Beim Passwort-Prompt: Die Eingabe ist **unsichtbar** (keine Sternchen). Einfach tippen und mit Enter bestätigen. Das Skript fragt anschließend zur Kontrolle noch einmal.

Das Skript ist idempotent und erledigt alles in einem Schritt:

1. Pakete installieren (Python 3.11, PostgreSQL 16, nginx, `rsync`, Build-Tools, TLS-Roots, UTF-8-Locale, TZ-Daten, `systemd-resolved`)
2. DNS persistent auf `1.1.1.1` und `8.8.8.8` setzen (via `systemd-resolved`, bleibt nach Reboot)
3. System-User `preisopt` anlegen, Code nach `/opt/preisopt/` spiegeln
4. PostgreSQL-User und Datenbank `preisopt` einrichten, `pgcrypto` aktivieren
5. `.env` mit zufällig generiertem `SESSION_SECRET` erzeugen
6. Python-venv anlegen, `requirements.txt` installieren
7. Alembic-Migrationen anwenden
8. Seed: Admin-User + Mock-Produkte (Schuhe, T-Shirt, Kaffeebohnen)
9. `systemd`-Service `preisopt-backend` starten
10. `nginx` als Reverse-Proxy auf Port 80 einrichten
11. Smoke-Test gegen den Health-Endpoint

Am Ende:

```
URL:     http://<server-ip>/
Login:   <admin-username> / <dein-passwort>
Service: systemctl status preisopt-backend
Logs:    journalctl -u preisopt-backend -f
.env:    /opt/preisopt/.env
```

### Optionen und Variablen

Flags:

- `--skip-seed` — keine Mock-Produkte anlegen
- `--no-nginx` — ohne Reverse-Proxy (uvicorn direkt auf `127.0.0.1:8000`)
- `--upgrade-system` — vorher `apt-get upgrade -y` ausführen
- `--admin-username <name>` — Admin-User überschreiben (Default: `admin`)

Umgebungsvariablen (sonst wird interaktiv gefragt bzw. zufällig generiert):

- `PREISOPT_ADMIN_PASSWORD` — Passwort des Admin-Users
- `PREISOPT_DB_PASSWORD` — Passwort des PostgreSQL-Users `preisopt`
- `GEMINI_API_KEY` — Key für die LLM-Strategie. Ohne Key bleiben die drei anderen Strategien (Fixpreis, Formel, Regel) voll funktionsfähig; nur die LLM-Strategie meldet dann "LLM nicht verfügbar".

Beispiel mit voreingestellten Secrets:

```bash
sudo GEMINI_API_KEY=xxx PREISOPT_ADMIN_PASSWORD=demo123 ./install.sh
```

### Erneut ausführen

`./install.sh` darf erneut gestartet werden. Code und Abhängigkeiten werden aktualisiert, Daten bleiben erhalten.

> **Disclaimer:** Studentischer Prototyp der FOM Hochschule. Nicht für den Produktivbetrieb. Läuft bewusst nur über HTTP (siehe `docs/security.md`). Rechtliche Anforderungen (DSGVO, EU AI Act, Preisrecht) werden konzeptionell adressiert, nicht produktiv umgesetzt.

## Überblick

- **Backend:** Python 3.11 + FastAPI + SQLAlchemy + Alembic.
- **Datenbank:** PostgreSQL 16.
- **Frontend:** HTML + Alpine.js + Pico.css (zero-build, via CDN), ausgeliefert von FastAPI `StaticFiles`.
- **LLM:** Google Gemini (Key in `.env`).
- **Deployment:** Debian 12 + nginx + systemd, per `install.sh`.
- **Transport:** ausschließlich HTTP (Prototyp, lokales Demonstrationssystem).

Architektur-Details in `CLAUDE.md` und `docs/`.

## Lokale Entwicklung (ohne install.sh)

```bash
# 1. Postgres bereitstellen und Datenbank anlegen
createdb preisopt

# 2. .env vorbereiten
cp .env.example .env   # Werte anpassen

# 3. Backend
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m seed --password changeme        # Mock-Daten
uvicorn app.main:app --reload             # http://localhost:8000
```

## Tests

```bash
cd backend
source .venv/bin/activate
pip install -r requirements-dev.txt

# Unit-Tests (ohne DB): Evaluator, Strategien
pytest -m "not integration"

# API- und DB-Tests: brauchen eine Postgres-Test-DB
createdb preisopt_test
export TEST_DATABASE_URL="postgresql+psycopg://preisopt:preisopt@localhost:5432/preisopt_test"
pytest
```

Details zu den Tests in `backend/tests/README.md`.

## Doku

Einstieg: [`CLAUDE.md`](./CLAUDE.md). Detail-Doku unter [`docs/`](./docs/).
