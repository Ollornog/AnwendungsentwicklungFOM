# KI-gestützte Preisoptimierung im E-Commerce

Web-Tool, in dem Shop-Betreiber Produkte verwalten und pro Produkt eine
Preisstrategie (Fixpreis oder Formel, optional KI-Vorschlag) festlegen.
Eine Live-Simulation (Uhrzeit, Tag, Lagerbestand, Nachfrage) zeigt den
resultierenden Verkaufspreis in Echtzeit; jede bestätigte Berechnung
landet in einer append-only Preis-Historie.

Studienprojekt im Modul *Projekt Anwendungsentwicklung*, FOM Hochschule
(B.Sc. Wirtschaftsinformatik), Lehrender Johannes Kurik, Team Daniel
Brunthaler (Projektleitung), Kayathiri Raveendran, Okan Baykal, Sven
Schlickewei. Abschlusspräsentation 16.07.2026. Details zum Auftrag in
[`docs/requirements.md`](./docs/requirements.md).

## Demo

- URL: <https://fom.ollornog.de/>
- Benutzer: `Demo`
- Passwort: `DemoUser`

## Quickstart (Debian 12)

```bash
apt-get update && apt-get install -y git
git clone https://github.com/Ollornog/AnwendungsentwicklungFOM
cd AnwendungsentwicklungFOM
./install.sh
```

Das Skript richtet Pakete, PostgreSQL, Backend-Service und nginx ein,
installiert den HTTPS-Helper inklusive sudoers-Regel und schließt mit
einem Health-Check. HTTPS lässt sich anschließend per UI-Klick
(*Einstellungen → HTTPS*) über Let's Encrypt aktivieren. Details in
[`docs/decisions/0005-deployment-debian.md`](./docs/decisions/0005-deployment-debian.md).

## Installation (lokale Entwicklung)

```bash
# 1. PostgreSQL bereitstellen
createdb preisopt

# 2. Env vorbereiten
cp .env.example .env   # Werte anpassen (SESSION_SECRET, GEMINI_API_KEY)

# 3. Backend
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m seed --password changeme
uvicorn app.main:app --reload   # http://localhost:8000
```

Swagger-UI unter `http://localhost:8000/docs`.

## Tech-Stack

- **Backend:** Python 3.11 + FastAPI, SQLAlchemy 2, Alembic
- **Datenbank:** PostgreSQL
- **Frontend:** HTML + Alpine.js + Pico.css + Chart.js (via CDN, zero-build)
- **LLM:** Google Gemini API
- **Deployment:** Debian 12 + nginx + systemd + Let's Encrypt

## Projektstruktur

```
.
├── backend/                FastAPI-Server + Alembic-Migrationen
│   ├── app/
│   │   ├── routers/        Endpoints (auth, products, pricing, users, settings, public)
│   │   ├── strategies/     Pricing-Strategien + AST-Evaluator
│   │   ├── services/       app_settings, seeding
│   │   └── main.py
│   ├── alembic/versions/   Migrationen 0001–0007
│   ├── seed.py             CLI-Seed (Admin + Mock-Produkte)
│   └── tests/              pytest
├── frontend/               Statisches Frontend (von FastAPI ausgeliefert)
│   ├── pages/              products, settings, history, legal, compliance
│   └── js/                 api.js, store.js, formula-eval.js, components/
├── deploy/                 nginx-Config, systemd-Unit, HTTPS-Helper, sudoers
├── docs/                   Architektur, Datenmodell, API, Use Cases, ADRs
├── CLAUDE.md               Projekt-Leitfaden für Beitragende
├── install.sh              Bootstrap-Skript für Debian 12
└── README.md               diese Datei
```

## Dokumentation

Einstieg: [`CLAUDE.md`](./CLAUDE.md). Detail-Doku unter [`docs/`](./docs/):
Architektur, Datenmodell, API-Vertrag, Use Cases, Preisstrategien,
Compliance, Sicherheit, Anforderungen und ADRs.

## Disclaimer

Studentischer Prototyp, kein Produktivsystem. Alle Produktdaten sind
Mock-Daten, es werden keine realen Preise gesetzt. Rechtliche Aspekte
(DSGVO, EU AI Act, NIS-2, UWG/PAngV) sind konzeptionell dokumentiert –
die öffentliche Kurzfassung liegt unter `/pages/legal.html`, die
interne Langfassung hinter Login unter `/pages/compliance.html`.
