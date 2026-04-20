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
- **Bootstrap:** `install.sh` im Repo-Root, idempotent, ausgelegt auf eine **frisch installierte Debian-12-Maschine**. Einzige Voraussetzung: Root-Rechte und Internet. Das Skript installiert alle nötigen Pakete (Python-Stack, PostgreSQL, nginx, `rsync`, Build-Tools, TLS-Roots, UTF-8-Locale, TZ-Daten) aus den Debian-Repos, legt den System-User an, richtet DB, venv, Migrationen, Seed und Services ein und schließt mit einem Smoke-Test gegen den Health-Endpoint ab. Keine Fremdquellen, kein `curl | bash`.

## Begründung
- Debian 12 ist Standard in der Hochschulumgebung und bietet stabile Pakete.
- Python 3.11 genügt für unseren Stack (FastAPI, SQLAlchemy 2.x, Pydantic 2.x). 3.12 wäre nur marginal besser, brächte aber Zusatzaufwand (Build aus Quelle oder Drittanbieter-Repo).
- nginx + uvicorn ist das übliche Muster in Produktion und hält SSL-/Header-Handling aus dem App-Code heraus.
- systemd-Unit mit separatem System-User, `PrivateTmp`, `ProtectHome` und `ProtectSystem=true` reduziert die Angriffsfläche. `NoNewPrivileges` bleibt bewusst deaktiviert, weil das Feature „HTTPS per Klick" einen sauber abgegrenzten sudo-Aufruf nutzt – die erlaubte Privilegierung ist über `/etc/sudoers.d/preisopt` auf genau ein Binary begrenzt.
- Alle Secrets in `/opt/preisopt/.env` (Mode 640, Owner `preisopt`), nie im Git.

## Konsequenzen
- `.env` wird vom `install.sh` beim ersten Lauf erzeugt, `SESSION_SECRET` zufällig befüllt.
- Wiederholte Läufe des Skripts aktualisieren Code und Migrationen, ohne Daten zu verwerfen.
- Der Installer nutzt `runuser` (Teil von `util-linux`, immer vorhanden), um interne Schritte unter dem `postgres`- bzw. `preisopt`-User laufen zu lassen. `sudo` selbst installiert das Skript zusätzlich – es wird aber nur vom Backend-Service für das HTTPS-Helper-Skript benötigt, nicht im Installer-Ablauf.
- DNS wird über `systemd-resolved` persistent auf `1.1.1.1` und `8.8.8.8` festgenagelt (Drop-in `/etc/systemd/resolved.conf.d/preisopt-dns.conf`, `/etc/resolv.conf` als Symlink auf den Stub-Resolver). `systemd-resolved` ist enabled, die Einstellung gilt damit auch nach jedem Reboot.
- Bei Bedarf kann das Team später auf Container / Compose umsteigen; bis dahin ist das Shell-Skript gut lesbar und ohne Zusatztooling.
- **HTTPS optional per UI.** Die Installation liefert default nginx auf Port 80; ein angemeldeter Admin kann in den Einstellungen eine Domain eintragen und das Let's-Encrypt-Zertifikat holen lassen (`certbot --nginx` via Helper). HSTS wird absichtlich nicht gesetzt (Demo-Charakter).

## Alternativen
- **Docker-Compose:** Schöner für Reproduzierbarkeit, aber zusätzlicher Lernaufwand und Overhead. Für den Demo-Scope nicht nötig.
- **Python 3.12 via deadsnakes/sury-Repo:** Fremdquelle und längere Installationsdauer, kein fachlicher Mehrwert.
- **Gunicorn + Uvicorn-Worker:** Mehr Prozesse, mehr Komplexität, für ein Demo-Tool unnötig.
