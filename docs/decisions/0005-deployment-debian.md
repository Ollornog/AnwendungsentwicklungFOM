# ADR-0005: Deployment auf Debian 12

**Status:** Akzeptiert (2026-04-19)
**Datum:** 2026-04-19

## Kontext

Für die Abschluss-Demo braucht das Projekt ein reproduzierbares
Deployment auf einem einfachen VPS. Gefordert: ein Bootstrap, das
Python-Umgebung, Datenbank, Service und Reverse-Proxy in einem
Aufruf aufsetzt, auf einer frisch installierten Debian-12-Maschine
funktioniert und ohne Fremdquellen auskommt.

## Entscheidung

- **Basis:** Debian 12 (Bookworm), Python 3.11 aus dem Distributions-
  Repo, PostgreSQL aus `apt`.
- **Backend-Prozess:** `uvicorn` auf `127.0.0.1:8000`, verwaltet von
  systemd (`preisopt-backend.service`).
- **Reverse-Proxy:** nginx auf Port 80 (`deploy/nginx-preisopt.conf`).
  `@bad_gateway`-Location invalidiert das Session-Cookie bei 5xx-
  Upstream-Fehlern.
- **Frontend:** FastAPI liefert `frontend/` via `StaticFiles`.
- **Zielverzeichnis:** `/opt/preisopt/` mit System-User `preisopt`.
- **Bootstrap:** `install.sh` im Repo-Root, idempotent. Flags:
  `--skip-seed`, `--no-nginx`, `--upgrade-system`, `--admin-username`.
- **HTTPS:** optional per UI-Klick (Einstellungen → HTTPS), Backend
  ruft via `sudo` genau ein Helper-Skript (`/usr/local/bin/preisopt-
  https-enable`) auf, das `certbot --nginx` ausführt. sudoers-Regel
  unter `/etc/sudoers.d/preisopt`, Pfad fest verdrahtet.

## Konsequenzen

- ➕ Ein Kommando (`./install.sh`) bringt das System hoch, inklusive
  Alembic-Migrationen, Seed-Daten, systemd-Unit, nginx-Site und
  Smoke-Test.
- ➕ Idempotenz: Wiederholter Lauf aktualisiert Code und Migrationen
  und respektiert bestehende Passwörter (`Enter = behalten`).
- ➕ HTTPS kann ohne SSH-Zugriff zur Laufzeit ergänzt werden; sudoers-
  Regel ist auf ein Binary begrenzt.
- ➖ systemd-Hardening-Flags wurden angepasst: `NoNewPrivileges=false`
  und `ProtectSystem=true`, damit sudo + certbot funktionieren.
  `PrivateTmp` und `ProtectHome` bleiben aktiv. Für ein produktives
  Setup wäre eine sauberere Trennung (separater root-Service,
  z. B. über `systemd.path`) wünschenswert.
- ➖ HSTS wird bewusst nicht gesetzt, damit ein Rollback auf HTTP
  ohne Browser-Cache-Streit möglich bleibt.

## Alternativen

- **Docker / Compose:** schöner für Reproduzierbarkeit, aber mehr
  Lernaufwand und Overhead. Für den Demo-Scope nicht nötig.
- **Gunicorn + Uvicorn-Worker:** mehr Prozesse, mehr Komplexität,
  für den Demo-Durchsatz nicht erforderlich.
- **HTTP-only-Deployment:** früher so beschlossen, mittlerweile
  ersetzt durch „HTTPS optional per UI", weil Browser-HTTPS-Upgrade
  (Chrome/Edge) ohne Zertifikat zu `ERR_CONNECTION_REFUSED` auf
  Domains führt.
- **Eigenes Let's-Encrypt-Skript ohne certbot:** verworfen,
  `certbot-nginx` bringt fertig getestete nginx-Integration.
