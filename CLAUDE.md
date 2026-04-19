# CLAUDE.md – Projekt-Kontext für KI-Assistenten

Diese Datei ist die zentrale Wahrheit dieses Projekts. Vor jeder Aufgabe lesen, nach jeder Änderung aktualisieren.

## 1. Projekt
- **Name:** KI-gestützte Preisoptimierung im E-Commerce
- **Modul:** Anwendungsentwicklung
- **Hochschule:** FOM Hochschule
- **Team:** 4 Personen
- **Abschlusspräsentation:** 15./16. Juli 2026

## 2. Zielbild
- **In einem Satz:** Web-Tool, in dem Shop-Betreiber Produkte verwalten und pro Produkt eine von vier Preisstrategien (Fixpreis, Formel, Regel, LLM-basiert) wählen, mit vollständiger Historie jeder Preisberechnung.
- **Nicht im Scope:** echte Shop-Anbindung (Shopify/WooCommerce), Multi-Mandanten-Fähigkeit, Echtzeit-Marktdaten-Integration, mobile Apps, produktive Zahlungsabwicklung.

## 3. Architektur (Kurzfassung)
- **Frontend** (HTML/JS, Browser) – nur UI, kommuniziert ausschließlich über REST mit dem Backend.
- **Backend** (Python + FastAPI) – Geschäftslogik, Preisstrategien, Auth, einziger Zugriff auf DB und LLM.
- **Datenbank** (PostgreSQL) – Produkte, Strategien, Preis-Historie, Benutzer.
- **Externer LLM-Service** (Claude oder OpenAI) – wird ausschließlich vom Backend aufgerufen.
- Details: `docs/architecture.md`.

## 4. Tech-Stack (aktuell entschieden)
- Backend: Python 3.12 + FastAPI
- Datenbank: PostgreSQL 16
- Frontend: HTML/JS (vanilla, später ggf. leichtes Framework)
- LLM-API: Anthropic Claude oder OpenAI (final in ADR 0001)
- Begründung & Stand: `docs/decisions/0001-tech-stack.md`

## 5. Doku-Map
| Datei | Inhalt |
| --- | --- |
| `CLAUDE.md` | Diese Datei: zentrale Projekt-Wahrheit |
| `README.md` | Projektname, Kurzbeschreibung, Setup |
| `docs/architecture.md` | Systemarchitektur, Komponenten, Schnittstellen |
| `docs/data-model.md` | DB-Schema, Entitäten, Beziehungen |
| `docs/api-contract.md` | REST-Endpoints, Request-/Response-Formate |
| `docs/pricing-strategies.md` | Die vier Strategien (Fix, Formel, Regel, LLM) |
| `docs/security.md` | Datenschutz, Secrets, LLM-Datennutzung |
| `docs/decisions/` | ADRs, ein File pro Entscheidung |

## 6. Arbeitsregeln
- **Coding-Conventions:** Backend nach PEP 8 + Type Hints; Frontend mit konsistenter Formatierung (Prettier-Default).
- **Commit-Format:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`).
- **Branch-Strategie:** `main` ist immer lauffähig; Feature-Branches `feature/<kurzname>`, Fixes `fix/<kurzname>`.
- **PR-Regeln:** Mindestens ein Review aus dem Team, CI grün, betroffene Doku aktualisiert.
- **Trennung:** Frontend hat keinen DB-Zugriff und keine Geschäftslogik. Alles über die REST-API.
- **Secrets:** ausschließlich in `.env`, nie im Code; `.env.example` als Vorlage pflegen.
- **LLM:** keine Kundendaten an externe LLMs, nur die für die Preisberechnung notwendigen Produkt-Attribute. Begründung in `docs/security.md`.

## 7. Offene Punkte & nächste Schritte
- [ ] Team-Rollen festlegen (Backend, Frontend, DB, Doku) – verantwortlich: Team – Deadline: 1. Treffen
- [ ] Finale LLM-Wahl (Claude vs. OpenAI) inkl. Kostenrahmen – ADR 0001 ergänzen
- [ ] Erstes Datenmodell für Produkt + Strategie + Historie skizzieren – `docs/data-model.md`
- [ ] API-Grundgerüst (FastAPI-Projekt) initialisieren
- [ ] DSGVO-Anforderungen prüfen und in `docs/security.md` ergänzen

## 8. Änderungshistorie (nur relevante Entscheidungen)
- 2026-04-19 – Initiale Doku-Struktur und ADR 0001 (Tech-Stack) angelegt – Commit `chore: initial documentation scaffolding`
