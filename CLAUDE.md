# CLAUDE.md – Projekt-Kontext

Zentrale Wahrheit für KI-Assistenten und jedes Teammitglied. Vor der
Arbeit lesen, nach jeder substanziellen Änderung mitziehen.

## 1. Projektkontext

Web-Tool „KI-gestützte Preisoptimierung im E-Commerce", Studienprojekt
im Modul *Projekt Anwendungsentwicklung*, FOM Hochschule, Wirtschafts-
informatik B.Sc., Lehrender **Johannes Kurik**. Team: **Daniel
Brunthaler** (Projektleitung & Entwicklung), Kayathiri Raveendran, Okan
Baykal, Sven Schlickewei. Abschlusspräsentation **16.07.2026**. Demo:
<https://fom.ollornog.de/>. Repo: <https://github.com/Ollornog/AnwendungsentwicklungFOM>.

Charakter: **Prototyp mit Mock-Daten**, kein Produktivsystem, keine
Endkundendaten, keine Shop-Anbindung, keine echten Preisentscheidungen.

## 2. Tech-Stack auf einen Blick

| Ebene | Technologie | ADR |
| --- | --- | --- |
| Sprache Backend | Python 3.11 | [0001](./docs/decisions/0001-tech-stack.md) |
| Web-Framework | FastAPI + Starlette | [0001](./docs/decisions/0001-tech-stack.md) |
| ORM / Migrationen | SQLAlchemy 2.x + Alembic | [0001](./docs/decisions/0001-tech-stack.md) |
| Datenbank | PostgreSQL (≥ 15) | [0001](./docs/decisions/0001-tech-stack.md) |
| Auth | `SessionMiddleware` + argon2id | [0003](./docs/decisions/0003-auth-session-cookie.md) |
| LLM | Google Gemini API | [0002](./docs/decisions/0002-llm-provider.md) |
| Frontend | HTML + Alpine.js + Pico.css + Chart.js, via CDN | [0004](./docs/decisions/0004-frontend-stack.md) |
| Deployment | Debian 12 + nginx + systemd, `install.sh` | [0005](./docs/decisions/0005-deployment-debian.md) |

## 3. Leitprinzipien

1. **Keine personenbezogenen Endkundendaten** im Scope. Nur Produkt-
   Stammdaten und minimale Login-Konten.
2. **Keine echten Daten.** Demo nutzt Mock-Produkte; die UI weist auf
   den Demo-Charakter hin.
3. **Human-in-the-Loop:** LLM-Vorschläge werden nie automatisch
   übernommen, sondern vom Admin bestätigt.
4. **KI sichtbar markieren** (Art. 50 AI Act): KI-Vorschläge tragen
   in UI und Historie das Badge „KI-Vorschlag"; der Prompt ist vor
   dem Klick einsehbar.
5. **Keine Kundendaten ans LLM.** Prompt enthält ausschließlich die
   Whitelist-Felder aus `app/strategies/llm.py` bzw.
   `app/routers/products.py::_strategy_whitelist`.
6. **Secrets in `.env` oder `app_settings`** – nie im Code, nie im
   Frontend. Der Gemini-Key kann per UI überschrieben werden und wird
   in der Tabelle `app_settings` gehalten.
7. **Audit-Trail in der Preis-Historie** (`price_history`, append-only)
   für jede bestätigte Berechnung und jeden Strategie-Wechsel.
8. **Admin-only** für Gemini-API-Key, HTTPS-Aktivierung, Rate-Limit-
   Konfiguration und Benutzerverwaltung – per `get_current_admin` im
   Backend und `$store.auth.isAdmin()` im Frontend.
9. **Rate Limiting** pro Benutzer pro Tag (Standard 50, Admin 200,
   konfigurierbar). Tabelle `api_rate_usage`.
10. **Frontend/Backend-Trennung niemals aufweichen.** Frontend hat
    keinen DB-Zugriff, keine Geschäftslogik; Kommunikation nur über
    die REST-API.
11. **Doku mitziehen.** Jede Änderung, die Scope, API, Datenmodell oder
    Security berührt, aktualisiert auch die zugehörige Doku im gleichen
    PR.

## 4. Doku-Map

| Datei | Inhalt |
| --- | --- |
| [`README.md`](./README.md) | Projektkurzbeschreibung, Quick-Start, Demo-Zugang |
| [`docs/architecture.md`](./docs/architecture.md) | Komponentendiagramm, Datenfluss, Deployment |
| [`docs/data-model.md`](./docs/data-model.md) | ERD, Tabellen, Migrationen |
| [`docs/api-contract.md`](./docs/api-contract.md) | Endpoint-Übersicht, Kern-Beispiele |
| [`docs/pricing-strategies.md`](./docs/pricing-strategies.md) | Fixpreis + Formel im Detail |
| [`docs/use-cases.md`](./docs/use-cases.md) | Sechs Use Cases |
| [`docs/compliance.md`](./docs/compliance.md) | DSGVO, AI Act, UWG/PAngV – knapp |
| [`docs/security.md`](./docs/security.md) | TOMs-Tabelle Prototyp vs. Produktiv |
| [`docs/requirements.md`](./docs/requirements.md) | Anforderungs-Dokument |
| `docs/decisions/` | ADRs 0001–0006 |

## 5. Abdeckung Modulanforderungen

| Modul-Skript (Kurik) | Artefakt |
| --- | --- |
| IT-Architektur | [`docs/architecture.md`](./docs/architecture.md) |
| Software-Modellierung (ERM + UC) | [`docs/data-model.md`](./docs/data-model.md), [`docs/use-cases.md`](./docs/use-cases.md) |
| REST-API-Design | [`docs/api-contract.md`](./docs/api-contract.md) |
| Datenschutz & Rechtliches | [`docs/compliance.md`](./docs/compliance.md), öffentliche Seite `/pages/legal.html` |
| Informationssicherheit | [`docs/security.md`](./docs/security.md), interne Seite `/pages/compliance.html` |
| Datenbankgestützte Anwendung | PostgreSQL + Alembic-Migrationen `0001–0007` |
| KI-Integration | Gemini-Client in `app/llm.py`, Strategien in `app/strategies/`, ADR [0002](./docs/decisions/0002-llm-provider.md) |

## 6. Änderungshistorie

- 2026-04-19 – Initiale Doku-Struktur und ADR 0001 (Tech-Stack).
- 2026-04-19 – LLM-Provider festgelegt (ADR 0002), Frontend-Stack
  (ADR 0004) und Auth (ADR 0003).
- 2026-04-19 – Backend-Scaffold (FastAPI + SQLAlchemy + Alembic),
  Preisstrategien und Debian-Deployment (ADR 0005, Migration 0001).
- 2026-04-19 – Simulations-UI: globale Slider, live berechneter
  Verkaufspreis; Produkt-Felder `context`, `monthly_demand`;
  Runtime-Variablen `hour`/`day`/`stock`; Endpoint `/strategy/suggest`
  (Migration 0002).
- 2026-04-20 – Glatte periodische Formeln (`sin`/`cos`/`mod`, `pi`,
  `weekday`); Token-Gruppen im Formel-Modal; Graph-Modal (Chart.js).
- 2026-04-20 – Nachfrage-Faktor `demand` als Slider 0–2 (Default 1)
  statt früherem Verbrauch/Tick; Migration 0005 entfernt
  `daily_usage`.
- 2026-04-20 – Einstellungsseite: Gemini-Key-Override (Migration
  0003), Passwort ändern, DB-Reset auf Seed-Stand.
- 2026-04-20 – HTTPS per Klick via `certbot --nginx`, sudoers-Regel
  für genau ein Helper-Skript.
- 2026-04-20 – Rate Limiting pro Tag (Migration 0006); Admin-only-
  Guards für `/users`, `/settings/https*`, `/settings/rate-limit*`.
- 2026-04-20 – Benutzerverwaltung (`/users`-CRUD) mit Schutz des
  Bootstrap-Admins; vier Team-Accounts im Seed.
- 2026-04-20 – `price_history.user_id` (Migration 0004), automatischer
  Snapshot bei Strategie-Wechsel, Wettbewerbs-KI-Batch-Endpoint,
  nginx invalidiert Cookie bei 5xx.
- 2026-04-20 – Öffentliche Seite `/pages/legal.html` (Impressum,
  Datenschutz, Betroffenenrechte, KI-Einstufung), interne Seite
  `/pages/compliance.html` (VVT, DPIA, TOMs, NIS-2, KI-Kompetenz).
- 2026-04-20 – Scope gestrafft: nur noch zwei Strategien (`fix`,
  `formula`). `rule` und `llm` aus Registry, Modellen, Tests und
  Check-Constraint entfernt (Migration 0007). KI-Vorschläge bleiben
  als Hilfswerkzeug im Strategie-Modal, erzeugen aber `fix`- oder
  `formula`-Einträge.
- 2026-04-22 – Gemini-API-Key auf admin-only gezogen (Frontend +
  `get_current_admin` für `GET`/`PUT /settings`). Strategie-Snapshot
  trägt das KI-Badge nun nur, wenn der gespeicherte Wert unverändert
  aus dem KI-Vorschlag stammt (ADR 0006).
- 2026-04-22 – Compliance-Review-Restarbeiten: Drittlandtransfer-
  Formulierung in `legal.html`, `compliance.html` und
  `docs/compliance.md` auf das **EU-US Data Privacy Framework**
  (Art. 45 DSGVO, Beschluss (EU) 2023/1795) als primäre Grundlage
  umgestellt, SCCs nur noch als Fallback. Neuer §8 „Preisangaben
  (PAngV)" in `legal.html`.
- 2026-04-22 – KI-Audit-Protokoll: neue Tabelle `llm_audit`
  (Migration 0008) loggt jede Gemini-Anfrage (Strategie-Vorschlag
  und Wettbewerbspreis-Batch) mit Zeit, User, Prompt, Roh-Antwort
  und Erfolg/Fehler. Admin-only einsehbar über
  `GET /api/v1/settings/llm-audit` und als Modal im
  Einstellungs-Dialog.
- 2026-04-22 – Seed: jeder frisch angelegte Team-/Demo-User erhält
  beim ersten Start (bzw. `install.sh`-Lauf) die kompletten
  Mock-Produkte als persönliches Startset; bestehende Accounts
  bleiben unberührt. Lehrender `Johannes` (PW `Kurik`) neu im Seed.
- 2026-04-22 – `install.sh`: Ein Re-Run überschreibt die
  `sites-available/preisopt` nicht mehr, wenn die Datei bereits
  einen `listen … ssl`-Block enthält. HTTPS-Deployment und
  Let's-Encrypt-Zertifikat bleiben über Updates hinweg erhalten.

## 7. Offene Punkte

- [ ] Kostenrahmen Gemini (Free-Tier-Grenzen) beobachten, ADR 0002
      ggf. nachziehen.
- [ ] `docs/contributions.md` und `docs/demo-script.md` vor der
      Präsentation befüllen.
- [ ] HSTS aktivieren, sobald HTTPS dauerhaft läuft (siehe
      `docs/security.md`).
- [ ] Produktiv-Ausblick dokumentieren: DSFA-Langfassung, AVV mit
      Google Cloud, automatisiertes Backup- und Restore-Drill.
