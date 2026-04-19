# CLAUDE.md – Projekt-Kontext für KI-Assistenten

Diese Datei ist die zentrale Wahrheit dieses Projekts. Vor jeder Aufgabe lesen, nach jeder Änderung aktualisieren.

## 1. Projekt
- **Name:** KI-gestützte Preisoptimierung im E-Commerce
- **Modul:** Anwendungsentwicklung
- **Hochschule:** FOM Hochschule
- **Team:** 4 Personen
- **Abschlusspräsentation:** 15./16. Juli 2026
- **Charakter:** studentischer Semester-Prototyp, kein Produktivsystem.

## 2. Zielbild
- **In einem Satz:** Web-Tool, in dem Shop-Betreiber Produkte verwalten und pro Produkt eine von vier Preisstrategien (Fixpreis, Formel, Regel, LLM-basiert) wählen, mit vollständiger Historie jeder Preisberechnung.
- **Nicht im Scope:** echte Shop-Anbindung (Shopify/WooCommerce), Multi-Mandanten-Fähigkeit, Echtzeit-Marktdaten-Integration, mobile Apps, produktive Zahlungsabwicklung, personalisiertes Pricing gegenüber Endkunden.

## 3. Architektur (Kurzfassung)
- **Frontend** (HTML/JS, Browser) – nur UI, kommuniziert ausschließlich über REST mit dem Backend.
- **Backend** (Python + FastAPI) – Geschäftslogik, Preisstrategien, Auth, einziger Zugriff auf DB und LLM.
- **Datenbank** (PostgreSQL) – Produkte, Strategien, Preis-Historie, Benutzer.
- **Externer LLM-Service** (Google Gemini API) – wird ausschließlich vom Backend aufgerufen.
- Details: `docs/architecture.md`.

## 4. Tech-Stack (aktuell entschieden)
- Backend: Python 3.12 + FastAPI
- Datenbank: PostgreSQL 16
- Frontend: HTML5 + Alpine.js 3 + Pico.css 2, via CDN, zero-build (siehe `docs/decisions/0004-frontend-stack.md`)
- Auslieferung Frontend: FastAPI `StaticFiles` (gleiches Origin wie API)
- Auth: Session-Cookie, HttpOnly, SameSite=Lax (siehe `docs/decisions/0003-auth-session-cookie.md`)
- LLM-API: Google Gemini (vorläufig für den Prototyp – siehe `docs/decisions/0002-llm-provider.md`)
- Begründung & Stand: `docs/decisions/0001-tech-stack.md`, `docs/decisions/0002-llm-provider.md`, `docs/decisions/0003-auth-session-cookie.md`, `docs/decisions/0004-frontend-stack.md`

## 5. Leitprinzipien (verbindlich)
1. **Keine personenbezogenen Daten im Scope.** Verarbeitet werden nur Produktdaten (Name, Kosten, Lager, Wettbewerbspreis). Kein personalisiertes Pricing, keine Endkundenprofile. DSGVO-Scope damit minimal.
2. **Keine echten Daten.** Demo läuft mit Mock-Produkten ("Schuhe", "T-Shirt" etc.).
3. **Human-in-the-Loop.** LLM-Preisvorschläge werden vom Shop-Betreiber bestätigt, nicht automatisch übernommen (Art. 22 DSGVO, AI-Act menschliche Aufsicht).
4. **KI sichtbar machen.** LLM-Vorschläge werden in UI und Historie als "KI-Vorschlag" markiert (sinngemäß Art. 50 AI-Act).
5. **Keine Kundendaten ans LLM.** Der Prompt enthält ausschließlich Produktdaten.
6. **Secrets in `.env`.** API-Keys nie im Code; `.env.example` pflegen; `.gitignore` prüfen.
7. **Audit-Trail über Preishistorie.** Jede Berechnung wird mit Zeitstempel, Strategie und Input gespeichert (append-only).

## 6. Doku-Map
| Datei | Inhalt |
| --- | --- |
| `CLAUDE.md` | Diese Datei: zentrale Projekt-Wahrheit |
| `README.md` | Projektname, Kurzbeschreibung, Setup, Disclaimer |
| `docs/architecture.md` | Systemarchitektur, Komponenten, Schnittstellen |
| `docs/data-model.md` | DB-Schema, Entitäten, Beziehungen |
| `docs/api-contract.md` | REST-Endpoints, Request-/Response-Formate |
| `docs/pricing-strategies.md` | Die vier Strategien (Fix, Formel, Regel, LLM) |
| `docs/use-cases.md` | Use Cases im Kurzformat |
| `docs/compliance.md` | DSGVO, EU AI Act, Preisrecht |
| `docs/security.md` | Informationssicherheit: Prototyp vs. Produktiv |
| `docs/contributions.md` | Wer hat was beigetragen (am Projektende) |
| `docs/demo-script.md` | Ablauf der Abschluss-Demo (am Projektende) |
| `docs/decisions/` | ADRs, ein File pro Entscheidung |

## 7. Abdeckung Modulanforderungen
| Anforderung | Abgedeckt durch |
| --- | --- |
| IT-Architektur | `docs/architecture.md` |
| Software-Modellierung | `docs/data-model.md`, `docs/api-contract.md`, `docs/use-cases.md` |
| Datenschutz | `docs/compliance.md` |
| Informationssicherheit | `docs/security.md` |
| Datenbankgestützte Anwendung | Datenmodell + Implementierung (PostgreSQL) |

## 8. Arbeitsregeln
- **Coding-Conventions:** Backend nach PEP 8 + Type Hints; Frontend mit konsistenter Formatierung (Prettier-Default).
- **Commit-Format:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`).
- **Branch-Strategie:** `main` ist immer lauffähig; Feature-Branches `feature/<kurzname>`, Fixes `fix/<kurzname>`.
- **PR-Regeln:** Mindestens ein Review aus dem Team, CI grün, betroffene Doku aktualisiert.
- **Trennung:** Frontend hat keinen DB-Zugriff und keine Geschäftslogik. Alles über die REST-API.
- **Secrets:** ausschließlich in `.env`, nie im Code; `.env.example` als Vorlage pflegen.
- **LLM:** keine Kundendaten an externe LLMs, nur für die Preisberechnung notwendige Produkt-Attribute. Begründung in `docs/compliance.md`.

## 9. Offene Punkte & nächste Schritte
- [ ] Team-Rollen festlegen (Backend, Frontend, DB, Doku) – verantwortlich: Team – Deadline: 1. Treffen
- [ ] Kostenrahmen Gemini (freier Tier vs. bezahlter Tarif) klären – ADR 0002 ergänzen
- [ ] Erstes Datenmodell für Produkt + Strategie + Historie skizzieren – `docs/data-model.md`
- [ ] API-Grundgerüst (FastAPI-Projekt) initialisieren, Frontend via `StaticFiles` einbinden
- [ ] `docs/contributions.md` und `docs/demo-script.md` vor der Abschlusspräsentation befüllen

## 10. Änderungshistorie (nur relevante Entscheidungen)
- 2026-04-19 – Initiale Doku-Struktur und ADR 0001 (Tech-Stack) angelegt – Commit `chore: initial documentation scaffolding`
- 2026-04-19 – LLM-Provider festgelegt (Google Gemini, vorläufig), Leitprinzipien, Compliance- und Security-Doku ergänzt – Commit `docs: compliance and security scaffolding`
- 2026-04-19 – Frontend-Stack (Alpine.js + Pico.css, ADR 0004) und Auth (Session-Cookie, ADR 0003) festgelegt, Frontend-Scaffold angelegt – Commit `feat: frontend scaffolding with alpine and pico`
