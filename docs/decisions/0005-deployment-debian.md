# ADR 0005: Deployment auf Debian 12

- **Status:** Akzeptiert (Prototyp)
- **Datum:** 2026-04-19
- **Entscheider:** Projektteam

## Kontext
Für die Abschluss-Demo soll der Prototyp auf einem Debian-12-Server laufen. Gefordert: ein Skript, das Python, PostgreSQL, Webserver, Backend und Frontend in einem Rutsch einrichtet, damit jedes Team-Mitglied eine identische Umgebung hochziehen kann.

## Entscheidung
- **Zielplattform:** Debian 12 (Bookworm), Python 3.11 aus dem Distributions-Repo.
- **Datenbank:** PostgreSQL 16 aus `apt`, lokaler Unix-Socket-Zugriff.
- **Prozess:** Uvicorn lauscht auf `127.0.0.1:8000`, verwaltet durch systemd (`preisopt-backend.service`).
- **Reverse-Proxy:** nginx auf Port 80 (`deploy/nginx-preisopt.conf`). Abschaltbar per `install.sh --no-nginx`.
- **Frontend:** FastAPI liefert `frontend/` via `StaticFiles` aus; kein separater Build.
- **Zielverzeichnis:** `/opt/preisopt/` mit System-User `preisopt`.
- **Bootstrap:** `install.sh` im Repo-Root, idempotent, ruft `apt`, richtet Postgres-User, venv, Migration, Seed und Services ein.

## Begründung
- Debian 12 ist Standard in der Hochschulumgebung und bietet stabile Pakete.
- Python 3.11 genügt für unseren Stack (FastAPI, SQLAlchemy 2.x, Pydantic 2.x). 3.12 wäre nur marginal besser, brächte aber Zusatzaufwand (Build aus Quelle oder Drittanbieter-Repo).
- nginx + uvicorn ist das übliche Muster in Produktion und hält SSL-/Header-Handling aus dem App-Code heraus.
- systemd-Unit mit `NoNewPrivileges`, `ProtectSystem=strict`, `PrivateTmp` und separatem System-User reduziert die Angriffsfläche auch für den Prototyp.
- Alle Secrets in `/opt/preisopt/.env` (Mode 640, Owner `preisopt`), nie im Git.

## Konsequenzen
- `.env` wird vom `install.sh` beim ersten Lauf erzeugt, `SESSION_SECRET` zufällig befüllt.
- Wiederholte Läufe des Skripts aktualisieren Code und Migrationen, ohne Daten zu verwerfen.
- Bei Bedarf kann das Team später auf Container / Compose umsteigen; bis dahin ist das Shell-Skript gut lesbar und ohne Zusatztooling.
- HTTPS ist bewusst nicht Teil des Prototyps (siehe `docs/security.md`). Für Produktion würde nginx via `certbot` + Let's Encrypt erweitert.

## Alternativen
- **Docker-Compose:** Schöner für Reproduzierbarkeit, aber zusätzlicher Lernaufwand und Overhead. Für den Demo-Scope nicht nötig.
- **Python 3.12 via deadsnakes/sury-Repo:** Fremdquelle und längere Installationsdauer, kein fachlicher Mehrwert.
- **Gunicorn + Uvicorn-Worker:** Mehr Prozesse, mehr Komplexität, für ein Demo-Tool unnötig.
