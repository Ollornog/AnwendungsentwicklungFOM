# Contributions

Diese Datei dokumentiert, wer welchen Beitrag zum Projekt geleistet hat. Sie dient als Grundlage für die Rollen-Folie im Präsentationsvideo, als Referenz für die Selbstreflexionen und als transparente Übersicht für Prof. Kurik.

---

## Team

| Person | Rolle |
|--------|-------|
| Daniel Brunthaler | Projektleitung & Entwicklung |
| Tamara Bezrodnow | Anforderungen & Use Cases |
| Kayathiri Raveendran | Qualitätssicherung & Testing |
| Okan Baykal | Präsentation & Compliance-Review |
| Sven Schlickewei | Post-Produktion & Konsolidierung |

---

## Beiträge im Überblick

### Daniel Brunthaler – Projektleitung & Entwicklung

**Code**
- Backend (FastAPI + SQLAlchemy + Alembic)
- Frontend (HTML + Alpine.js + Pico.css + Chart.js)
- Pricing-Engine mit Formel-Evaluator
- Gemini-Anbindung mit Sanity-Check
- Team-Account-Verwaltung, Rate Limiting, DB-Reset
- Deployment-Skript `install.sh` (idempotent, Debian 12)
- HTTPS-per-Klick via certbot-nginx + sudoers-Helper

**Dokumentation**
- `README.md`
- `CLAUDE.md`
- `docs/architecture.md`
- `docs/data-model.md`
- `docs/api-contract.md`
- `docs/pricing-strategies.md`
- `docs/decisions/0001-tech-stack.md` bis `0005-deployment-debian.md`

**Projektleitung**
- Kommunikation mit Prof. Kurik (Anmeldung, Terminbestätigung)
- Koordination der drei Team-Meetings
- Repository-Pflege, Merge-Konflikte, Deployment-Betrieb
- Compliance-Nacharbeit (DPF + PAngV) aus dem Review

**Präsentation**
- Demo-Screen-Recording für das Präsentationsvideo
- Voiceover für Architektur-Block und Demo-Abschnitte zu Formel-Strategie und Simulator

**Quantitativ**
- ~44 Commits, ~90 % Code-Anteil
- 5 ADRs verantwortet

---

### Tamara Bezrodnow – Anforderungen & Use Cases

**Dokumentation**
- `docs/requirements.md` (44 FR + 23 NFR + 22 REG + 12 MOD = 101 Anforderungen mit Status, Story Points, Erhebungszeitpunkt T0–T4)
- `docs/use-cases.md` (6 Hauptflüsse im Format Akteur/Ziel/Vorbedingung/Ablauf/Nachbedingung, gegen Code verifiziert)
- `docs/glossar.md` (zentrale Fachbegriffe)
- `docs/media/use-cases.mmd` + `use-cases.svg` (Use-Case-Diagramm in Mermaid)

**Regulatorik**
- Regulatorischen Block als eigenständigen Anforderungstyp REG-01 bis REG-22 ins Projekt getragen
- Inhaltlicher Input für `/pages/legal.html` und `/pages/compliance.html`
- Grundlage für den späteren Compliance-Review durch Okan

**Präsentation**
- Voiceover für Block „Problem & Idee" und Demo-Abschnitt „Produkt anlegen + Fixpreis"
- Rollen-Slot

---

### Kayathiri Raveendran – Qualitätssicherung & Testing

**Dokumentation**
- `docs/testing.md` (Testkonzept mit Abnahmekriterien)
- `docs/test-matrix.md` (>20 manuelle Testfälle mit Verweis auf pytest)
- `docs/user-tests.md` (drei externe User-Tests mit Think-aloud-Protokoll)
- `docs/bug-log.md` (inkl. BUG-001 mit Root-Cause-Analyse und Verifikation)
- `docs/test-report.md` (Abschluss-Bilanz)

**Testing**
- Co-Testing während des Nacht-Sprints (Meldung von BUG-001)
- Strukturierte manuelle Durchläufe aller sechs Use Cases
- Koordination und Durchführung der drei externen User-Tests
- Re-Test nach BUG-001-Fix, Aufnahme von TC-LLM-01 in die Test-Matrix

**Präsentation**
- Voiceover für Demo-Abschnitt „Preisgraph + Historie"
- Rollen-Slot

---

### Okan Baykal – Präsentation & Compliance-Review

**Dokumentation**
- `docs/video-script.md` (Drehbuch mit Zeitbudget, Sprecher:in, Bildinhalt je Block)
- `docs/compliance-review.md` (Review gegen 12 DSGVO-Artikel, 5 AI-Act-Anforderungen, NIS-2, Preisrecht – inkl. Re-Review nach Nacharbeit)
- `docs/qa-vorbereitung.md` (Fragenkatalog mit Antworten und Zuordnung)

**Compliance-Review**
- 8 priorisierte Befunde abgeleitet, 6 direkt erfüllt, 2 nachgezogen (DPF + PAngV)
- Freigabe nach Re-Review am 22.04.2026

**Präsentation**
- Konzept „vorproduziertes Video + Live-Q&A"
- Drehplan-Koordination der fünf Einzelaufnahmen
- Voiceover für Hook und Demo-Abschnitt „KI-Vorschlag + Transparenz"
- Moderation der Q&A am Präsentationstag
- Rollen-Slot

---

### Sven Schlickewei – Post-Produktion & Konsolidierung

**Video**
- Schnitt des Präsentationsvideos in DaVinci Resolve
- Audio-Normalisierung auf -16 LUFS, Kompressor, EQ
- Titelkarten im FOM-Farbcode, schlichter Schnittstil
- Zeitdisziplin auf exakt 10 Minuten

**Dokumentation**
- `docs/contributions.md` (diese Datei)
- Konsolidierte PDF-Version des Selbstreflexionsberichts (Deckblatt, Inhaltsverzeichnis, Eigenständigkeitserklärung nach FOM-Vorgabe)
- Redaktionelles Lektorat der Doku-Dateien im Repo (einheitliche Terminologie, Schreibweise)

**Präsentation**
- Voiceover für Fazit-Block
- Rollen-Slot

---

## Artefakt-Zuordnung

### Code

| Komponente | Verantwortlich |
|------------|----------------|
| Backend (FastAPI, Pricing-Engine, Auth) | Daniel |
| Frontend (Alpine.js, Pico.css, Chart.js) | Daniel |
| Datenbank-Schema + Migrationen | Daniel |
| Deployment (`install.sh`, nginx, systemd, HTTPS) | Daniel |
| pytest-Testsuite | Daniel |
| Compliance-Seiten (`legal.html`, `compliance.html`) | Daniel (Umsetzung) / Tamara (Inhalt) / Okan (Review) |

### Dokumentation

| Datei | Verantwortlich |
|-------|----------------|
| `README.md`, `CLAUDE.md` | Daniel |
| `docs/architecture.md`, `data-model.md`, `api-contract.md`, `pricing-strategies.md` | Daniel |
| `docs/decisions/*` (ADRs 0001–0005) | Daniel |
| `docs/compliance.md`, `docs/security.md` | Daniel (Grundlage) / Tamara (Regulatorik) |
| `docs/requirements.md`, `use-cases.md`, `glossar.md` | Tamara |
| `docs/media/use-cases.*` | Tamara |
| `docs/testing.md`, `test-matrix.md`, `user-tests.md`, `bug-log.md`, `test-report.md` | Kayathiri |
| `docs/video-script.md`, `compliance-review.md`, `qa-vorbereitung.md` | Okan |
| `docs/contributions.md`, PDF-Konsolidierung | Sven |

### Präsentation

| Block im Video | Sprecher:in |
|----------------|-------------|
| Hook | Okan |
| Problem & Idee | Tamara |
| Architektur-Überblick | Daniel |
| Demo – Produkt anlegen + Fixpreis | Tamara |
| Demo – Formel-Strategie | Daniel |
| Demo – KI-Vorschlag + Transparenz | Okan |
| Demo – Simulator-Dynamik | Daniel |
| Demo – Preisgraph + Historie | Kayathiri |
| Rollenverteilung | alle fünf |
| Fazit | Sven |
| Schnitt, Audio, Titelkarten | Sven |
| Q&A-Vorbereitung | Okan (alle liefern zu ihren Bereichen) |

---

## Übergreifende Beiträge

Folgende Tätigkeiten lagen nicht in Einzelverantwortung, sondern wurden gemeinsam erbracht:

- **Initiales Brainstorming** zu Thema, Scope und grober Anforderungsliste – alle vier Gründungsmitglieder (Daniel, Kayathiri, Okan, Sven)
- **Architekturbesprechung** vor dem Sprint – Daniel federführend, alle vier Gründungsmitglieder beteiligt
- **Co-Testing im Nacht-Sprint** (Live-Feedback, Scope-Erweiterungen wie Preisgraph und Fancy-Formel-Button) – Kayathiri und Okan begleiteten Daniels Entwicklung aktiv
- **Drei Team-Meetings**: Kick-off (19.04.), Zwischenmeeting (21.05.), Abschlussmeeting (21.06.) – alle fünf
- **Eigenständigkeitserklärung** – unterschrieben von allen fünf

---

## Beitragsbilanz

Arbeit im Projekt verteilt sich nicht gleichmäßig auf die fünf Personen – das wäre bei Kompetenzverteilung nach Rollen weder zu erwarten noch sinnvoll. Daniel trägt den größten Code-Anteil, weil er alleiniger Entwickler ist. Die vier anderen produzieren Artefakte, die in ihrer jeweiligen Rolle den Prototyp ergänzen: Anforderungsanalyse, Test-Matrix, Compliance-Review, Präsentationsvideo und Konsolidierung. Der Umfang jeder Rolle ist in der Selbstreflexion der betreffenden Person dokumentiert.

Diese Aufteilung entspricht der Empfehlung aus Folie 4 und 8 des Modul-Skripts: Rollenverteilung nach Kompetenzprofilen, arbeitsteilige Implementierung, gegenseitige Verantwortlichkeit.
