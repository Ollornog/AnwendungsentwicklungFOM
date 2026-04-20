# KI-gestützte Preisoptimierung im E-Commerce

Studentisches Semesterprojekt der FOM Hochschule, Modul Anwendungsentwicklung.

## Quick Start auf Debian 12

```bash
# als root eingeloggt (oder mit sudo vorweg):
apt-get update && apt-get install -y git
git clone https://github.com/Ollornog/AnwendungsentwicklungFOM
cd AnwendungsentwicklungFOM
./install.sh
```

Ein Web-Tool, in dem Shop-Betreiberinnen und Shop-Betreiber Produkte pflegen
und pro Produkt eine Preisstrategie wählen (Fixpreis, Formel, Regel,
LLM-Vorschlag). Die Preisberechnung läuft gegen einen Live-Simulator
(Uhrzeit, Wochentag, Lagerbestand, Nachfrage) und jede Berechnung landet
in einer append-only Preis-Historie.

Die Anwendung ist ein **Prototyp mit Mock-Daten** – keine echten
Endkundendaten, keine Shop-Anbindung, keine produktive Preisfestlegung.

## Funktionsweise in 60 Sekunden

1. **Einloggen** als `admin` oder als Teammitglied (vier Demo-Accounts
   werden beim Seed angelegt).
2. **Produkt anlegen** über den Nav-Button. Felder: Name, Kategorie,
   Einkaufspreis, Wettbewerbspreis, Verbrauch pro Monat, Lagergröße,
   Kontext-Freitext (wird an die KI gegeben).
3. **Preis-Strategie setzen** – entweder Fixpreis oder eine Formel mit
   den Variablen `cost_price`, `stock`, `hour`, `day`, `weekday`,
   `demand`, `monthly_demand` u. a. Ein KI-Vorschlag ist per Klick
   verfügbar; der Prompt ist vor dem Klick einsehbar
   (Human-in-the-Loop, Transparenz Art. 50 AI Act).
4. **Simulieren** – Sliders oben steuern Uhrzeit und Tag, pro Zeile
   reguliert ein Slider den aktuellen Lagerbestand und ein zweiter die
   Nachfrage (Faktor 0 – 2). Ein Tick = eine Stunde; mit `▶/⏸`
   gesteuert, `3×` beschleunigt.
5. **Graph** pro Produkt zeichnet den Preisverlauf über beliebige
   Variablen (Uhrzeit, Tag, Wochentag, Lagerstand, Nachfrage-Faktor
   oder „Zeit gesamt" für einen ganzen Monat am Stück).
6. **Einstellungen (admin)**: Gemini-API-Key setzen, HTTPS per Klick
   aktivieren (Let's Encrypt), Rate Limit konfigurieren,
   Team-Accounts verwalten, Datenbank auf Seed-Stand zurücksetzen.

## Architektur

```
Browser (HTML + Alpine + Pico + Chart.js)
      │ REST/JSON (Session-Cookie)
      ▼
FastAPI-Backend ──► PostgreSQL
      │
      └─► Gemini API  (nur Produkt-Whitelist, keine Kundendaten)
```

- Backend serviert zugleich die statischen Frontend-Dateien (`StaticFiles`).
- nginx vor dem Backend lauscht auf Port 80 und bei aktivem HTTPS auf 443.
- Details: `docs/architecture.md`, `docs/data-model.md`, `docs/api-contract.md`.

## Installation auf Debian 12

```bash
# als root eingeloggt (oder mit sudo vorweg):
apt-get update && apt-get install -y git
git clone https://github.com/Ollornog/AnwendungsentwicklungFOM
cd AnwendungsentwicklungFOM
./install.sh
```

Das Skript ist auf eine **frisch installierte Debian-12-Maschine** ausgelegt.
Voraussetzungen: Root-Rechte und eine Internetverbindung – sonst nichts. Alle
Abhängigkeiten kommen aus den Debian-Repos.

> Nicht als root eingeloggt? `sudo ./install.sh`. Auf minimalen Debian-
> Netinstalls ohne `sudo`-Paket vorher `apt-get install -y sudo` oder
> direkt als root arbeiten.

> Beim Passwort-Prompt: die Eingabe ist **unsichtbar** (keine Sternchen).
> Einfach tippen und mit Enter bestätigen. Bei einem erneuten Lauf kann
> Enter gedrückt werden, um das bestehende Admin-Passwort zu behalten.

Das Skript ist idempotent und erledigt alles in einem Schritt:

1. Pakete: Python 3.11, PostgreSQL, nginx, sudo, certbot, `rsync`,
   Build-Tools, TLS-Roots, UTF-8-Locale, TZ-Daten, `systemd-resolved`.
2. DNS persistent auf `1.1.1.1` und `8.8.8.8` setzen (per
   `systemd-resolved`-Drop-in, überlebt Reboot).
3. System-User `preisopt` anlegen, Code nach `/opt/preisopt/` spiegeln.
4. PostgreSQL-User und Datenbank `preisopt` einrichten, Encoding `UTF8`
   aus `template0`, `pgcrypto` aktivieren.
5. `.env` mit zufälligem `SESSION_SECRET` und `DATABASE_URL` erzeugen.
6. Python-venv anlegen, `requirements.txt` installieren.
7. Alembic-Migrationen anwenden.
8. Seed: Admin-User (falls neu) + vier Team-Accounts + acht Mock-Produkte.
9. systemd-Service `preisopt-backend` starten.
10. nginx als Reverse-Proxy auf Port 80 einrichten.
11. HTTPS-Helper `/usr/local/bin/preisopt-https-enable` + sudoers-Regel
    installieren (für den „HTTPS aktivieren"-Button in der UI).
12. Smoke-Test gegen `/api/v1/health`.

Am Ende:

```
URL:     http://<server-ip>/
Login:   admin / <dein-passwort>      oder    Daniel/Brunthaler, …
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

Umgebungsvariablen (sonst interaktiv bzw. zufällig):

- `PREISOPT_ADMIN_PASSWORD` — Admin-Passwort
- `PREISOPT_DB_PASSWORD` — Passwort des PostgreSQL-Users `preisopt`
- `GEMINI_API_KEY` — Key für LLM-Features. Ohne Key funktionieren Fixpreis
  und Formel weiterhin; nur LLM-Strategie und KI-Vorschläge melden dann
  „LLM nicht verfügbar".

Beispiel mit voreingestellten Secrets:

```bash
sudo GEMINI_API_KEY=xxx PREISOPT_ADMIN_PASSWORD=demo123 ./install.sh
```

### Erneut ausführen

`./install.sh` darf jederzeit erneut gestartet werden. Ein Self-Update
zieht Änderungen aus dem Git-Repo (falls aus einem Clone gestartet) und
führt sich mit dem neuen Code neu aus. Daten bleiben erhalten.

### HTTPS einrichten

Nach dem ersten Start: DNS-A-Record der Domain auf die Server-IP
setzen, Port 80/443 in der Cloud-Firewall öffnen, dann in der UI
**Einstellungen → HTTPS (Let's Encrypt) → Domain eintragen →
aktivieren**. Der Backend-Service ruft den Helper mit genau einer
sudoers-Regel auf, certbot-nginx legt Zertifikat und HTTP→HTTPS-Redirect
an.

## Lokale Entwicklung (ohne install.sh)

```bash
# 1. PostgreSQL bereitstellen und Datenbank anlegen
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

Die interaktive API-Doku liegt dann unter `http://localhost:8000/docs`
(Swagger UI, von FastAPI generiert).

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

Siehe `backend/tests/README.md`.

## Doku

| Datei | Inhalt |
| --- | --- |
| `CLAUDE.md` | Projektleitbild, Leitprinzipien, Change-History |
| `docs/architecture.md` | Komponenten, Datenfluss, Deployment |
| `docs/data-model.md` | DB-Schema und Migrationen |
| `docs/api-contract.md` | REST-Endpoints mit Auth-/Admin-/Rate-Limit-Regeln |
| `docs/pricing-strategies.md` | Variablen, Funktionen, Beispiele |
| `docs/use-cases.md` | Bedien-Flows pro Feature |
| `docs/compliance.md` | DSGVO, EU AI Act, NIS-2, Datenschutzhinweis |
| `docs/security.md` | Informationssicherheit im Prototyp |
| `docs/decisions/` | ADRs (Tech-Stack, LLM-Provider, Auth, Frontend, Deployment) |

## Disclaimer

Studentischer Prototyp der FOM Hochschule. Nicht für den Produktivbetrieb.
Rechtliche Anforderungen (DSGVO, EU AI Act, NIS-2, Preisrecht) werden
konzeptionell dokumentiert, nicht produktiv umgesetzt. Eine Kurzfassung
liegt öffentlich unter `/pages/legal.html`, die interne Langfassung
(VVT, DPIA, TOMs) hinter Login unter `/pages/compliance.html`.
