# ADR-0001: Tech-Stack

**Status:** Akzeptiert (2026-04-19)
**Datum:** 2026-04-19

## Kontext

Für ein Studienprojekt im Modul *Projekt Anwendungsentwicklung* mit
vier Personen über ein Semester brauchen wir einen Tech-Stack, der
(1) die Modul-Pflichtthemen abdeckt (DB-gestützte Anwendung, IT-
Architektur, Software-Modellierung, Datenschutz, Informations-
sicherheit), (2) eine klare Frontend/Backend-Trennung erlaubt und
(3) im Team bereits vorhanden bzw. schnell erlernbar ist.

## Entscheidung

- **Backend:** Python 3.11 + FastAPI (Debian-12-Standard, keine
  Fremdquellen).
- **ORM/Migrationen:** SQLAlchemy 2.x + Alembic.
- **Datenbank:** PostgreSQL (ab 15, Debian-Default).
- **Frontend:** HTML + JavaScript, Details in ADR 0004.
- **LLM-API:** externer Cloud-Endpoint, Details in ADR 0002.

## Konsequenzen

- ➕ Klare Schichtentrennung, saubere Testbarkeit, automatische
  OpenAPI-Doku über FastAPI (`/docs`, `/redoc`).
- ➕ PostgreSQL erfüllt das Modulanforderungs-Pflichtthema
  „datenbankgestützte Anwendung" überzeugend (Constraints,
  Transaktionen, JSONB für Strategie-Configs).
- ➖ Python-Stack auf Debian 12 bedeutet Python 3.11 (statt 3.12/3.13);
  für unseren Funktionsumfang irrelevant.
- ➖ Es gibt kein etabliertes Typescript-Tooling im Frontend – dafür
  zero-build (siehe ADR 0004).

## Alternativen

- **Node.js / Express oder NestJS:** zusätzlicher JavaScript-Stack,
  bei gleichem Funktionsumfang höhere Einarbeitung im Team.
- **Java / Spring Boot:** produktionsreif, aber im Team weniger
  geübt, deutlich umfangreicher als nötig.
- **Laravel (PHP):** zur Debatte gestanden (bekannt aus Praktika);
  verworfen, weil die OpenAPI-Integration und die Pydantic-ähnliche
  Validierung nicht so nahtlos sind wie in FastAPI.
- **SQLite** statt PostgreSQL: einfacher, aber erfüllt das Pflicht-
  thema „datenbankgestützte Anwendung" weniger überzeugend und
  blockiert spätere Mehrbenutzer-Szenarien.
