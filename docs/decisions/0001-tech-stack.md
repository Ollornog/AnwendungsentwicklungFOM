# ADR 0001: Tech-Stack

- **Status:** Akzeptiert (vorläufig, LLM-Anbieter offen)
- **Datum:** 2026-04-19
- **Entscheider:** Projektteam (4 Personen)

## Kontext
Wir bauen ein Web-Tool zur KI-gestützten Preisoptimierung als Studienprojekt. Der Stack muss in einem Semester von einem 4er-Team beherrschbar sein, die Modul-Pflichtthemen (DB-gestützte Anwendung, IT-Architektur, Software-Modellierung, Datenschutz, Informationssicherheit) abbilden und eine saubere Frontend/Backend-Trennung ermöglichen.

## Entscheidung
- **Backend:** Python 3.12 mit FastAPI.
- **Datenbank:** PostgreSQL 16.
- **Frontend:** HTML + JavaScript (vanilla); leichtes Framework (z. B. Alpine.js oder Vue) bei Bedarf später.
- **LLM-API:** gängige Cloud-APIs kommen in Frage (Google, OpenAI, Anthropic); die finale Wahl wird in einem Folge-ADR (`0002-llm-provider.md`) anhand Kosten, Datenschutz und Antwortqualität getroffen.
- **ORM/Migrations:** SQLAlchemy + Alembic (vorgeschlagen, in Folge-ADR bestätigen).

## Begründung
- **Python/FastAPI:** Im Team vorhanden, sehr gute Dokumentation, automatische OpenAPI-Generierung deckt das Pflichtthema "Doku" gut ab, schnelle Entwicklung von REST-APIs.
- **PostgreSQL:** Robust, kostenlos, vom Modul gefordert (DB-gestützte Anwendung), starkes Tooling, Standard im professionellen Umfeld.
- **HTML/JS ohne großes Framework:** Lernkurve niedrig, der Fokus liegt auf Backend und Datenmodell, nicht auf Frontend-Architektur.
- **LLM extern:** keine eigene Modell-Infrastruktur; Anbieter-Auswahl wird separat entschieden, weil sie Datenschutz- und Kostenfragen aufwirft.

## Konsequenzen
- Klare Frontend/Backend-Trennung wird durch die Architektur vorgegeben (siehe `docs/architecture.md`).
- LLM-Aufrufe ausschließlich serverseitig, Keys in `.env` (siehe `docs/security.md`).
- Folge-ADRs nötig für: LLM-Provider, Auth-Verfahren, Deployment.

## Alternativen
- **Node.js/Express oder Java/Spring** statt FastAPI: höhere Komplexität bzw. Stack im Team weniger geübt.
- **SQLite** statt PostgreSQL: einfacher, aber erfüllt das Pflichtthema "datenbankgestützte Anwendung" weniger überzeugend.
- **React/Vue von Anfang an:** zusätzlicher Lernaufwand ohne Mehrwert für den geforderten Funktionsumfang.
