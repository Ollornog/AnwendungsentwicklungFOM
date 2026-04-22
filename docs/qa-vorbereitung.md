**Q & A**

**Antwort-Prinzip:** 1–2 Sätze genügen. Wenn Kurik nachbohrt, vertiefen. Niemals vorlesen. Natürlich sprechen, auch wenn die Antwort vorbereitet ist.

**Zuständigkeitsregel:** Die in Klammern genannte Person antwortet primär. Wenn die Person unsicher ist oder die Frage in mehrere Bereiche reicht, springt die nächste angegebene Person ein. Zur Not übergibt man offen: „Das beantwortet Dir am besten Daniel" – das wirkt kompetent, nicht unsicher.

**Goldene Regel:** Wenn jemand etwas nicht weiß, nicht raten. Antwort: „Darauf habe ich jetzt keine saubere Zahl, das steht in `docs/xxx.md` – wir liefern es Ihnen nach, wenn gewünscht." Kurik ist SAP-Consultant, der erkennt Bluffs.

**Verweis-Strategie:** Wir haben gute Doku. Wenn eine Frage in der Tiefe nicht reinpasst, aufs Repo zeigen: „Ausführlich steht das in `docs/architecture.md`" – das zeigt, dass die Antwort existiert, ohne die Q\&A zu sprengen.

**Wenn jemand die Antwort nicht weiß:**

„Darauf habe ich jetzt keine belastbare Zahl/Begründung. Das steht ausführlich in `docs/xxx.md`. Wenn gewünscht, reichen wir die Antwort nach."

**Wenn Kurik die Funktion im Code sehen will:**

„Gerne. Das ist in der Datei `app/xxx.py` – Daniel kann das kurz zeigen." (Laptop bereithalten\!)

**Wenn eine Frage in mehrere Bereiche reicht:**

„Der technische Teil kommt von Daniel, den rechtlichen Rahmen erklärt Okan." (Übergabe transparent machen, wirkt organisiert statt unsicher.)

**Wenn eine kritische Nachfrage kommt:**

„Ja, das ist ein fairer Punkt. Wir haben uns bewusst für \[X\] entschieden, weil \[kurze Begründung aus ADR\]. Eine Alternative wäre \[Y\], das war im Zeitrahmen nicht leistbar."

**Wenn es um einen Punkt geht, der bewusst nicht im Scope ist:**

„Das haben wir bewusst nicht umgesetzt. Begründung steht in `docs/requirements.md` unter FR-xx. Für einen produktiven Einsatz wäre \[X\] zu ergänzen."

# **Q\&A – Schnellüberblick für die Prüfung**

**Format:** Bullet-Antworten, nicht vorlesen. Kernaussagen merken, im Termin frei formulieren.

---

## **Kategorie 1 – Teamarbeit**

**1.1 Wie war die Arbeit im Team verteilt?** *(Okan)*

* Rollen nach Kompetenzprofil – entspricht Folie 4/8  
* Anforderungsanalyse und Architektur gemeinsam, danach aufgeteilt  
* Daniel: Entwicklung | Tamara: Anforderungen | Kayathiri: QS | Okan: Präsentation/Compliance | Sven: Post-Produktion  
* Jede Rolle mit eigenständigen, dokumentierten Artefakten

**1.2 Welches agile Vorgehensmodell?** *(Daniel)*

* Prototyping mit fokussiertem Sprint (Option 1 aus Folie 8\)  
* Kein formales Scrum – Teamgröße und Projektlänge rechtfertigen den Overhead nicht  
* Backlog in Markdown-Dateien im Repo, direkte Kommunikation

**1.3 Warum hat nur eine Person gecodet?** *(Tamara)*

* Ehrliche Antwort auf unterschiedliche Erfahrungsprofile  
* Fünf Parallel-Entwickler hätten mehr Koordination als Wertschöpfung erzeugt  
* Stattdessen vier zusätzliche Artefakte: Anforderungsanalyse, Test-Matrix, Compliance-Review, Video  
* Arbeitsteilige Implementierung im Sinne der Modulbeschreibung

**1.4 Wie habt ihr kommuniziert?** *(Okan)*

* WhatsApp für Schnelles, Videocalls für Abstimmungen  
* GitHub-Repo als Single Source of Truth  
* Kein Jira/Confluence – wäre Overhead für ein 5er-Team

**1.5 Größte Teamherausforderung?** *(Tamara)*

* Mein Späteinstieg nach dem Coding-Sprint  
* Rückwirkend eine strukturierte Anforderungsanalyse zum bereits gebauten Prototyp aufsetzen  
* Team hat das ohne Reibung aufgefangen

---

## **Kategorie 2 – Architektur & Technik**

**2.1 Warum Frontend/Backend-Trennung?** *(Daniel)*

* Saubere Verantwortungstrennung, Fachlogik im Backend gekapselt  
* Frontend austauschbar – Shopify-Plugin oder Mobile-App könnten dieselben Endpoints nutzen

**2.2 Warum FastAPI, PostgreSQL, Alpine.js, Gemini?** *(Daniel)*

* FastAPI: automatische OpenAPI-Doku, Pydantic-Validierung, kein Compile-Zyklus (ADR 0001\)  
* PostgreSQL: bessere JSON-Unterstützung, produktiv-taugliche Migrationen  
* Alpine.js \+ Pico.css: zero-build, CDN-basiert, kein Webpack (ADR 0004\)  
* Gemini: kostenloser API-Tier, Anbieter austauschbar, in einer Datei gekapselt (ADR 0002\)

**2.3 Was passiert bei LLM-Ausfall?** *(Daniel)*

* Fixpreis und Formel funktionieren komplett unabhängig  
* Nur KI-Features (Vorschlag, Wettbewerbspreise) fallen aus  
* Manuelle Eingabe jederzeit möglich – bewusste Architekturentscheidung

**2.4 Wie läuft das Deployment?** *(Daniel)*

* Idempotentes Installationsskript für Debian 12  
* Setzt PostgreSQL, Python-venv, Migrationen, nginx, systemd in einem Durchlauf auf  
* HTTPS per Klick via Let's Encrypt über sudoers-kontrollierten Helper

**2.5 Wie skaliert das produktiv?** *(Daniel)*

* Rate Limiting bereits vorhanden  
* DB-Replikation und Monitoring konzeptionell dokumentiert (`docs/security.md`), nicht produktiv umgesetzt  
* Bewusste Scope-Grenze für den Prototyp

**2.6 Wie läuft die Session-Verwaltung?** *(Daniel)*

* Session-Cookie mit HttpOnly und SameSite=Lax  
* Passwörter mit argon2id gehasht  
* Dokumentiert in ADR 0003

---

## **Kategorie 3 – Produktlogik**

**3.1 Wie funktioniert die Formel-Strategie?** *(Daniel)*

* Selbstgeschriebener Evaluator, Laufzeit-Auswertung gegen Kontextvariablen  
* Variablen: Einkaufspreis, Lagerbestand, Uhrzeit, Wochentag, Nachfrage u. a.  
* Grundrechenarten, Vergleiche, Funktionen wie Wurzel/Min/Max  
* Syntaxfehler vom Backend abgefangen, alte Strategie bleibt

**3.2 Warum nur zwei Strategien, keine LLM-Strategie?** *(Tamara)*

* Eine LLM-Strategie wäre eine Blackbox im Produkt  
* Kollidiert mit Artikel 5 und 50 AI Act – nicht begründbar, nicht prüfbar  
* KI schlägt innerhalb der menschenlesbaren Strategien vor → Entscheidung bleibt nachvollziehbar

**3.3 Was ist Human-in-the-Loop?** *(Okan)*

* Jede KI-Preisentscheidung wird explizit bestätigt  
* Prompt vor dem Absenden einsehbar, Vorschlag übernehmbar/änderbar/verwerfbar  
* Keine automatische Übernahme – Unterschied zwischen KI-Assistenz und KI-Entscheidung

**3.4 Wie wird das KI-Badge vergeben?** *(Daniel)*

* Nur wenn gespeicherter Wert unverändert aus der KI-Antwort stammt  
* Sobald der Nutzer editiert, fällt das Badge weg  
* Dokumentiert in ADR 0004, löst BUG-001

**3.5 Wie verhindert ihr unsinnige KI-Preise?** *(Daniel)*

* Sanity-Check auf Output – Preise außerhalb plausibler Bereiche werden aussortiert  
* Human-in-the-Loop als zweite Schicht  
* Audit-Trail als dritte Schicht

---

## **Kategorie 4 – Anforderungen & Scope**

**4.1 Wie habt ihr Anforderungen erhoben?** *(Tamara)*

* Brainstorming am Anfang \+ Weiterentwicklung im Sprint-Dialog  
* Zusammengeführt in `docs/requirements.md` zu 101 Anforderungen  
* Kategorien: funktional, nicht-funktional, regulatorisch, Modulanforderungen

**4.2 Was sind T0–T4?** *(Tamara)*

* Erhebungszeitpunkte: Brainstorming (T0), Architektur (T1), Sprint (T2), Feedback (T3), Eigeninitiative (T4)  
* Nur \~30 % der Features aus T0 – Rest agil entstanden  
* Genau der Prototyping-Ansatz aus Folie 8

**4.3 Warum sind manche Features nicht umgesetzt?** *(Tamara)*

* Bewusste Scope-Entscheidungen mit Begründung in der Anforderungsliste  
* Beispiele: Shopify-Integration, Multi-Tenant, personalisiertes Pricing  
* Personalisiertes Pricing zusätzlich rechtlich heikel (DSGVO Art. 22\)

**4.4 Eure Use Cases?** *(Tamara)*

* Sechs Hauptflüsse: Produkt anlegen, Strategie zuweisen, Preis berechnen, KI-Vorschlag, Simulator, Historie  
* Format: Akteur / Ziel / Vorbedingung / Ablauf / Nachbedingung  
* Use-Case-Diagramm zeigt zusätzlich Admin-Flows und Gemini-Anbindung

**4.5 Wie passt das zu den Modulanforderungen?** *(Tamara)*

* Vier statt der geforderten drei Themengebiete: IT-Architektur, Software-Modellierung, Datenschutz, Informationssicherheit  
* Datenbankgestützte Anwendung, Doku, funktionsfähiger Prototyp – alles erfüllt  
* Abdeckung als Tabelle MOD-01 bis MOD-12 gegen das Skript gemappt

---

## **Kategorie 5 – Compliance (DSGVO, AI Act, PAngV)**

**5.1 DSGVO-Scope?** *(Okan)*

* Keine Endkundendaten, kein personalisiertes Pricing, Human-in-the-Loop  
* Einzige personenbezogene Daten: Team-Accounts (Rechtsgrundlage Vertragserfüllung)  
* VVT, DSFA-Schwellwertanalyse, TOMs in `/pages/compliance.html`

**5.2 Drittlandtransfer zu Google?** *(Okan)*

* Primär: EU-US Data Privacy Framework nach Art. 45 DSGVO – Google LLC zertifiziert  
* Ergänzend: Standardvertragsklauseln als Fallback  
* Dokumentiert in `/pages/legal.html` und VVT

**5.3 Rolle des EU AI Act?** *(Okan)*

* „Begrenztes Risiko" nach Art. 50 wegen Interaktion mit natürlicher Person  
* Transparenzpflicht erfüllt: Prompt-Preview, KI-Kennzeichnung, KI-Badge in Historie  
* Hochrisiko-Auflagen aus Anhang III nicht einschlägig

**5.4 DSFA nötig?** *(Okan)*

* Nein – in Schwellwertanalyse dokumentiert  
* Keines der drei Art.-35-Kriterien erfüllt (keine automatisierte Bewertung mit Rechtswirkung, keine systematische Überwachung, keine besonderen Kategorien)

**5.5 Wie erfüllt ihr Art. 50 Transparenzpflicht?** *(Okan)*

* Strategiebezeichnung weist auf KI hin  
* Prompt vor dem Absenden einsehbar  
* Preishistorie markiert KI-Einträge mit Badge  
* Nutzer weiß immer: wann KI, was gesendet

**5.6 Ist NIS-2 relevant?** *(Okan)*

* Nein – NIS-2 greift erst bei wesentlichen/wichtigen Einrichtungen ab Mindestgröße  
* Studentischer Prototyp fällt nicht darunter  
* Nicht-Anwendbarkeit dokumentiert, Ausblick für Produktivbetrieb benannt

**5.7 Verhältnis zur PAngV?** *(Okan)*

* Anwendung richtet sich an Shop-Betreiber, nicht an Endverbraucher  
* Preise sind Simulationswerte, keine Preisangabe im Sinne der PAngV  
* Bei Shop-Integration zu ergänzen: Brutto-Darstellung, 30-Tage-Regel

---

## **Kategorie 6 – Qualitätssicherung**

**6.1 Wie habt ihr Qualität gesichert?** *(Kayathiri)*

* Drei Ebenen: pytest-Tests, manuelle Test-Matrix (20+ Fälle), drei externe User-Tests  
* Happy Path und Fehlereingaben je Use Case  
* Testkonzept, Matrix, Report vollständig im Repo

**6.2 Was ist ein Think-aloud-Protokoll?** *(Kayathiri)*

* Usability-Methode: Testperson spricht laut aus, was sie sieht und erwartet  
* Beobachter greift nicht ein, notiert Stolperstellen wörtlich  
* Findet Verständnisprobleme, die reine Funktionstests übersehen

**6.3 Welche Testpersonen?** *(Kayathiri)*

* Drei bewusst unterschiedliche Profile  
* Ohne IT-Hintergrund / IT-affin ohne E-Commerce / mit Shop-Erfahrung  
* Breitere Perspektive als nur IT-Studierende

**6.4 Wichtigste Findings?** *(Kayathiri)*

* Formel-Syntax für Nicht-Programmierer:innen unklar → Token-Buttons und Fancy-Formel-Button  
* BUG-001 (fehlende KI-Markierung in der Historie) aus Co-Testing im Nacht-Sprint, behoben und als Testfall aufgenommen

**6.5 Warum keine GitHub-Issues?** *(Kayathiri)*

* Nur ein einziges Finding erforderte Fix – Ticketing wäre Overhead  
* Bugs in `docs/bug-log.md` mit Repro-Schritten, Root-Cause, Verifikation  
* Doku bleibt an einem Ort

---

## **Kategorie 7 – Präsentation & Post-Produktion**

**7.1 Warum Video statt Live-Demo?** *(Okan)*

* 10-Minuten-Grenze strikt einhaltbar  
* Keine technischen Risiken (Crash, LLM-Ausfall, Netzwerk)  
* Jede Person planbar sichtbar (Folie 10\)  
* Q\&A jetzt live – alle vor Ort

**7.2 Wie wurde das Video produziert?** *(Sven)*

* Einzelaufnahmen separat zu Hause \+ Demo-Screen-Recording  
* Schnitt in DaVinci Resolve, Audio auf \-16 LUFS normalisiert  
* Titelkarten im FOM-Farbcode, bewusst schlichter Schnittstil

**7.3 Herausforderung Post-Produktion?** *(Sven)*

* Audio-Angleichung über fünf Mikrofone, fünf Räume, fünf Lautstärken  
* Nur mit Kompressor, EQ und einheitlicher LUFS-Marke sauber zu lösen  
* Während des Projekts neu erlernt

**7.4 Konsolidierung der schriftlichen Abgabe?** *(Sven)*

* Fünf Einzelreflexionen redaktionell durchgesehen und vereinheitlicht  
* PDF mit Deckblatt, Inhaltsverzeichnis, Eigenständigkeitserklärung nach FOM-Vorgabe

---

## **Kategorie 8 – Reflexion**

**8.1 Größte technische Hürde?** *(jede:r eigener Bereich)*

* **Daniel:** Claude Code so steuern, dass der Agent nicht abdriftet → `CLAUDE.md` als zentrale Wahrheit  
* **Tamara:** Regulatorische Tiefe bei AI Act, DSGVO, PAngV  
* **Kayathiri:** Richtige Testtiefe zwischen „Prototyp" und „prüfungsfest"  
* **Okan:** Koordination der Einzelaufnahmen  
* **Sven:** Audio-Angleichung über unterschiedliche Aufnahmesituationen

**8.2 Was würdet ihr anders machen?**

* **Daniel:** Automatisierte Tests parallel zum Code, nicht nachziehen  
* **Tamara:** Früher einsteigen, Regulatorik vor dem Sprint klären  
* **Kayathiri:** Testing früher starten, zwei User-Test-Runden statt einer  
* **Okan:** Aufnahme-Guidelines vorab schriftlich festlegen  
* **Sven:** Rohschnitt mit Platzhalter-Audio früh machen

**8.3 Mit dieser Gruppe wieder arbeiten?** *(Okan, alle nicken)*

* Ja  
* Klare Rollenverteilung, direkte Kommunikation, Findings sachlich diskutiert  
* Späteinstieg reibungslos aufgenommen

**8.4 Was nehmt ihr fachlich mit?**

* **Daniel:** KI-Assistenz im Coding produktiv nutzbar, wenn Kontext sauber geführt  
* **Tamara:** Mermaid für diff-bare Diagramme im Repo  
* **Kayathiri:** Think-aloud-Tests als Methode  
* **Okan:** Vertieftes Verständnis von AI Act, DSGVO, PAngV  
* **Sven:** Audio-Post-Produktion mit LUFS-Normalisierung

---

## **Kategorie 9 – Strategisch & Meta**

**9.1 Produktiv einsetzbar?** *(Daniel)*

* Als Prototyp ja, produktiv fehlen drei Schichten  
* Shop-Integration (Shopify), Skalierung (DB-Replikation, Monitoring), Compliance-Rahmen (AVV, DSB, Schulung)  
* Alles als Ausblick dokumentiert, bewusst nicht im Scope

**9.2 Alleinstellungsmerkmal?** *(Tamara)*

* Konsequente Trennung zwischen KI-Vorschlag und menschlicher Entscheidung  
* Blackbox wird sichtbar gemacht: Prompt-Preview, KI-Kennzeichnung, Audit-Trail  
* Compliance-konform und vertrauensbildend

**9.3 Halluzinierende KI-Antworten?** *(Okan)*

* Drei Schutzschichten: Sanity-Check, Human-in-the-Loop, Audit-Trail  
* KI ist nie Entscheidungsinstanz

**9.4 Grenze Werkzeug ↔ Entscheidungssystem?** *(Tamara)*

* Beim aktiven Bestätigungsschritt  
* Ohne Bestätigung wäre es ein Entscheidungssystem mit Art. 22 DSGVO und AI-Act-Hochrisiko-Implikationen  
* Unser Tool bleibt durch jede bewusste Preisübernahme Werkzeug

**9.5 Was würdet ihr als nächstes bauen?** *(Daniel)*

* Shopify-Integration als erster Produktivschritt  
* Rechtlich durch Datenminimierungs-Ansatz vorbereitet  
* Danach echte Wettbewerbsdaten-APIs statt manueller Eingabe
