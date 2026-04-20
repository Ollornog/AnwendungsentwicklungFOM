# CLAUDE.md – Projekt-Kontext für KI-Assistenten

Diese Datei ist die zentrale Wahrheit dieses Projekts. Vor jeder Aufgabe lesen, nach jeder Änderung aktualisieren.

## 1. Projekt
- **Name:** KI-gestützte Preisoptimierung im E-Commerce
- **Modul:** Anwendungsentwicklung
- **Hochschule:** FOM Hochschule
- **Team:** 4 Personen (Daniel Brunthaler, Kayathiri Raveendran, Okan Baykal, Sven Schlickewei)
- **Abschlusspräsentation:** 15./16. Juli 2026
- **Charakter:** studentischer Semester-Prototyp, kein Produktivsystem.

## 2. Zielbild
- **In einem Satz:** Web-Tool, in dem Shop-Betreiber Produkte verwalten und pro Produkt eine von vier Preisstrategien (Fixpreis, Formel, Regel, LLM-basiert) wählen, mit Live-Simulation (Uhrzeit, Tag, Lagerbestand, Nachfrage) und vollständiger Preishistorie.
- **Nicht im Scope:** echte Shop-Anbindung (Shopify/WooCommerce), Multi-Mandanten-Fähigkeit, Echtzeit-Marktdaten-Integration, mobile Apps, produktive Zahlungsabwicklung, personalisiertes Pricing gegenüber Endkunden.

## 3. Architektur (Kurzfassung)
- **Frontend** (HTML + Alpine.js + Pico.css + Chart.js, Browser) – nur UI, kommuniziert ausschließlich über REST mit dem Backend. Live-Formel-Evaluator spiegelt die Backend-Whitelist (Variablen + Funktionen).
- **Backend** (Python + FastAPI) – Geschäftslogik, Preisstrategien, Auth, Rate Limiting, einziger Zugriff auf DB und LLM. AST-basierter Evaluator für Formeln.
- **Datenbank** (PostgreSQL) – Produkte, Strategien, Preis-Historie, Benutzer, Einstellungen, Tages-API-Zähler.
- **Externer LLM-Service** (Google Gemini API) – wird ausschließlich vom Backend aufgerufen, mit enger Whitelist.
- **Reverse-Proxy** (nginx) – Port 80, optional HTTPS per UI-Klick via certbot-nginx; invalidiert bei 5xx-Upstream-Fehlern das Session-Cookie.
- Details: `docs/architecture.md`.

## 4. Tech-Stack (aktuell entschieden)
- Backend: Python 3.11 + FastAPI, SQLAlchemy 2.x, Alembic
- Datenbank: PostgreSQL (ab 15; Debian-Default)
- Frontend: HTML5 + Alpine.js 3 + Pico.css 2 + Chart.js 4, via CDN, zero-build (siehe `docs/decisions/0004-frontend-stack.md`)
- Auslieferung Frontend: FastAPI `StaticFiles` (gleiches Origin wie API)
- Auth: Starlette-`SessionMiddleware` (signiertes Cookie, HttpOnly, SameSite=Lax), Passwörter mit argon2id (siehe `docs/decisions/0003-auth-session-cookie.md`)
- LLM-API: Google Gemini (vorläufig für den Prototyp – siehe `docs/decisions/0002-llm-provider.md`)
- Deployment: Debian 12 + nginx + systemd + sudo, Setup via `install.sh` (siehe `docs/decisions/0005-deployment-debian.md`); HTTPS per UI (Let's Encrypt) nachladbar
- Begründung & Stand: `docs/decisions/0001-tech-stack.md`, `0002-llm-provider.md`, `0003-auth-session-cookie.md`, `0004-frontend-stack.md`, `0005-deployment-debian.md`

## 5. Leitprinzipien (verbindlich)
1. **Keine personenbezogenen Endkundendaten im Scope.** Verarbeitet werden nur Produktdaten (Name, Kategorie, Einkaufspreis, Wettbewerbspreis, Lagergröße, Verbrauch/Monat, Kontext-Freitext) und minimale Kontodaten für Login (Username, Argon2-Hash, Rolle). Kein personalisiertes Pricing, keine Endkundenprofile. DSGVO-Scope damit minimal.
2. **Keine echten Daten.** Demo läuft mit Mock-Produkten ("Sneaker", "T-Shirt", …). Das Frontend rendert die Disclaimer sichtbar.
3. **Human-in-the-Loop.** LLM-Preisvorschläge werden vom Shop-Betreiber bestätigt, nicht automatisch übernommen (Art. 22 DSGVO, AI-Act menschliche Aufsicht).
4. **KI sichtbar machen.** LLM-Vorschläge werden in UI und Historie als "KI-Vorschlag" markiert (Art. 50 AI Act). Der an die KI geschickte Prompt ist vor dem Klick einsehbar.
5. **Keine Kundendaten ans LLM.** Der Prompt enthält ausschließlich Produkt-Whitelist-Felder (zentral in `app/strategies/llm.py::_whitelist` und `app/routers/products.py::_strategy_whitelist`).
6. **Secrets in `.env` bzw. `app_settings`.** API-Keys nie im Code; `.env.example` pflegen; `.gitignore` prüfen. Der Gemini-Key kann zusätzlich per UI in der Tabelle `app_settings` gesetzt werden und überschreibt dann den `.env`-Wert.
7. **Audit-Trail über Preishistorie.** Jede Berechnung und jeder Strategie-Wechsel erzeugt einen append-only Eintrag mit Zeitstempel, Benutzer, Strategie und Input.
8. **Admin-only für kritische Bereiche.** HTTPS-Aktivierung, Rate-Limit-Konfiguration und Benutzerverwaltung sind nur für den `admin`-Account erreichbar (Backend: `get_current_admin`, Frontend: `$store.auth.isAdmin()`).
9. **Rate Limiting.** Jeder authentifizierte API-Aufruf (außer Auth- und Settings-Endpoints) zählt auf ein tageweises Kontingent pro Nutzer (Standard 50, Admin 200; beides einstellbar).

## 6. Doku-Map
| Datei | Inhalt |
| --- | --- |
| `CLAUDE.md` | Diese Datei: zentrale Projekt-Wahrheit |
| `README.md` | Projektname, Kurzbeschreibung, Quick-Start, Installation, Disclaimer |
| `docs/architecture.md` | Systemarchitektur, Komponenten, Schnittstellen |
| `docs/data-model.md` | DB-Schema, Entitäten, Beziehungen, Migrationen |
| `docs/api-contract.md` | REST-Endpoints, Admin-/Rate-Limit-Regeln |
| `docs/pricing-strategies.md` | Die vier Strategien + Variablen + Funktionen |
| `docs/use-cases.md` | Use Cases im Kurzformat (UC-01 … UC-10) |
| `docs/compliance.md` | DSGVO, EU AI Act, NIS-2-Check, Datenschutzhinweis |
| `docs/security.md` | Informationssicherheit: Prototyp vs. Produktiv |
| `docs/contributions.md` | Wer hat was beigetragen (am Projektende) – **noch zu befüllen** |
| `docs/demo-script.md` | Ablauf der Abschluss-Demo (am Projektende) – **noch zu befüllen** |
| `docs/decisions/` | ADRs, ein File pro Entscheidung |

## 7. Abdeckung Modulanforderungen
| Anforderung | Abgedeckt durch |
| --- | --- |
| IT-Architektur | `docs/architecture.md` |
| Software-Modellierung | `docs/data-model.md`, `docs/api-contract.md`, `docs/use-cases.md` |
| Datenschutz | `docs/compliance.md`, öffentliche Seite `/pages/legal.html` |
| Informationssicherheit | `docs/security.md`, interne Seite `/pages/compliance.html` |
| Datenbankgestützte Anwendung | Datenmodell + Implementierung (PostgreSQL, Alembic-Migrationen 0001–0006) |

## 8. Arbeitsregeln
- **Coding-Conventions:** Backend nach PEP 8 + Type Hints (kein `from __future__ import annotations` – hatte einen FastAPI-204-Fehler ausgelöst); Frontend mit konsistenter Formatierung.
- **Commit-Format:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`).
- **Branch-Strategie:** `main` ist immer lauffähig; Feature-Branches `feature/<kurzname>`, Fixes `fix/<kurzname>`.
- **PR-Regeln:** Mindestens ein Review aus dem Team, CI grün, betroffene Doku aktualisiert.
- **Trennung:** Frontend hat keinen DB-Zugriff und keine Geschäftslogik. Alles über die REST-API.
- **Secrets:** ausschließlich in `.env` oder `app_settings`; nie im Code; `.env.example` als Vorlage pflegen.
- **LLM:** keine Kundendaten an externe LLMs, nur Produkt-Whitelist-Felder. Begründung in `docs/compliance.md`.
- **Privilegierte Operationen:** Backend-Service-User `preisopt` hat **genau einen** sudoers-Eintrag (HTTPS-Helper, fester Pfad).

## 9. Offene Punkte & nächste Schritte
- [ ] Kostenrahmen Gemini (freier Tier vs. bezahlter Tarif) klären – ADR 0002 ergänzen.
- [ ] `docs/contributions.md` und `docs/demo-script.md` vor der Abschlusspräsentation befüllen.
- [ ] Für Produktiv-Ausblick: DSFA-Langfassung, AVV-Unterschrift mit Google Cloud, Backup-/Restore-Drill dokumentieren.
- [ ] HSTS aktivieren sobald HTTPS dauerhaft läuft (aktuell bewusst aus, siehe `docs/security.md`).

## 10. Änderungshistorie (nur relevante Entscheidungen)
- 2026-04-19 – Initiale Doku-Struktur und ADR 0001 (Tech-Stack) angelegt.
- 2026-04-19 – LLM-Provider festgelegt (Google Gemini, vorläufig), Leitprinzipien, Compliance- und Security-Doku ergänzt.
- 2026-04-19 – Frontend-Stack (Alpine.js + Pico.css, ADR 0004) und Auth (Session-Cookie, ADR 0003) festgelegt, Frontend-Scaffold angelegt.
- 2026-04-19 – Backend (FastAPI + SQLAlchemy + Alembic), Preisstrategien, Gemini-Client und Debian-12-Deployment (ADR 0005) implementiert.
- 2026-04-19 – Simulations-UI für Demo: globale Slider (Uhrzeit/Tag), pro Produkt Lager-/Verbrauchs-Slider mit Live-Preisberechnung. Product-Felder `context`, `monthly_demand`; Formel-Evaluator akzeptiert Runtime-Variablen `hour`, `day`, `stock`; Endpoint `POST /products/{id}/strategy/suggest` (KI-Vorschlag mit optionaler Online-Recherche). Migration 0002.
- 2026-04-20 – `weekday`, sanfte Kurven via `sin`/`cos`/`mod` + Konstante `pi`; Token-Gruppen im Formel-Modal; Graph-Modal pro Produkt mit Chart.js.
- 2026-04-20 – Nachfrage-Faktor `demand` als Live-Slider 0–2 (Default 1, ersetzt den früheren Verbrauch/Tick); Migration 0005 entfernt `daily_usage`.
- 2026-04-20 – Einstellungsseite: Gemini-API-Key per UI (Tabelle `app_settings`, Migration 0003), Passwort ändern, Datenbank-Reset auf Seed-Stand.
- 2026-04-20 – HTTPS per Klick: `POST /api/v1/settings/https/enable` ruft via sudo das Helper-Skript `/usr/local/bin/preisopt-https-enable` auf, das `certbot --nginx` startet. sudoers-Regel `deploy/sudoers.d-preisopt`.
- 2026-04-20 – Rate Limiting pro Benutzer pro Tag (Tabelle `api_rate_usage`, Migration 0006); admin-only-Guards für `/users`, `/settings/https*`, `/settings/rate-limit*`.
- 2026-04-20 – Benutzerverwaltung: `POST/PUT/DELETE /api/v1/users` mit Schutz des bootstrap-Admins; vier Team-Accounts im Seed; Passwort-Änderung per UI.
- 2026-04-20 – `price_history.user_id` (Migration 0004), automatischer Snapshot bei Strategie-Wechsel, Wettbewerbs-KI-Button (Batch-Endpoint), nginx invalidiert Cookie bei 5xx.
- 2026-04-20 – Öffentliche Seite `/pages/legal.html` (Impressum, Datenschutz, Betroffenenrechte, KI-Einstufung), interne Seite `/pages/compliance.html` (VVT, DPIA, TOMs, NIS-2, KI-Kompetenz), Footer mit Legal-Links.
