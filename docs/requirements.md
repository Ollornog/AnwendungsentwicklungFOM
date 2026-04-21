# **Anforderungsanalyse**

# **1\. Legende**

## **Umsetzungsstatus**

| Symbol | Bedeutung |
| :---- | :---- |
| ✅ | Umgesetzt – im Prototyp funktional vorhanden |
| 🔶 | Konzeptionell adressiert – in Doku beschrieben, nicht produktiv umgesetzt |
| ⛔ | Bewusst nicht umgesetzt – mit Begründung |
| 📝 | Dokumentation – erfüllt durch Doku-Artefakt, kein Code |

## **Aufwandsschätzung in Story Points**

Story Points sind relativ, nicht in Stunden. Eine Fibonacci-artige Skala:

| SP | Bedeutung (relativ) | Referenz |
| :---- | :---- | :---- |
| 1 | Trivial, „in einem Rutsch" | Config-Flag ergänzen, kleine UI-Anpassung |
| 2 | Klein, überschaubar | Einfaches CRUD-Endpoint |
| 3 | Standardaufgabe | Neue Entität inkl. Migration und UI |
| 5 | Spürbarer Aufwand, mehrere Komponenten | Auth-Flow, Strategie-Implementierung |
| 8 | Groß, eigener Feature-Block | Simulator, Gemini-Integration |
| 13 | Sehr groß, mehrteilig | Deployment-Installer, Gesamt-UI |

## **Erhebungszeitpunkt**

| Kürzel | Zeitpunkt |
| :---- | :---- |
| T0 | Kick-off / Anforderungsanalyse vor Coding-Start |
| T1 | Architekturbesprechung (gemeinsam, Daniel federführend) |
| T2 | Nacht-Sprint (während des Codens entstanden) |
| T3 | Post-Sprint (Feedback von Mit-Testern, nach erstem Prototyp) |
| T4 | Späte Ergänzung / nach dem Sprint, außerhalb des ursprünglichen Scopes |

# 

# **2\. Funktionale Anforderungen (FR)**

## **2.1 Produkt- und Benutzerverwaltung**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-01 | Nutzer kann Produkte anlegen (Name, Kategorie, Einkaufspreis, Wettbewerbspreis, Lager, Verbrauch, Kontext-Freitext) | T0 | 3 | ✅ | Kern-CRUD |
| FR-02 | Nutzer kann Produktdaten bearbeiten | T0 | 2 | ✅ |  |
| FR-03 | Nutzer kann Produkte löschen | T0 | 1 | ✅ |  |
| FR-04 | Produktliste mit aktuellen Preisen und Strategie-Markierung anzeigen | T0 | 3 | ✅ |  |
| FR-05 | Login für Admin-Bereich (Session-Cookie) | T1 | 5 | ✅ | ADR 0003 |
| FR-06 | Mehrere Benutzer mit Team-Accounts | T4 | 5 | ✅ | Nach Sprint ergänzt – Daniel hat aus eigenem Antrieb implementiert |
| FR-07 | Admin kann Team-Accounts in den Einstellungen verwalten (CRUD) | T4 | 3 | ✅ | Außerhalb ursprünglichem Scope |

## **2.2 Pricing-Strategien**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-08 | Strategie „Fixpreis" pro Produkt | T0 | 2 | ✅ |  |
| FR-09 | Strategie „Formel" mit Variablen (cost\_price, competitor\_price, monthly\_demand, start\_stock, stock, hour, day, weekday, demand, pi) | T0 / T2 | 8 | ✅ | Initial geplant; Variablen-Umfang wuchs während des Sprints |
| FR-10 | Formel-Evaluator wertet zur Laufzeit mit aktuellen Werten aus | T1 | 5 | ✅ |  |
| FR-11 | KI-gestützter Vorschlag für Fixpreis oder Formel (mit Begründung, Human-in-the-Loop-Bestätigung) | T0 | 8 | ✅ |  |
| FR-12 | Strategie „Regel" (wenn-dann, z. B. lagerabhängig) | T0 | 5 | ⛔ | Durch „Formel" abgedeckt – Regeln lassen sich als Formelterm ausdrücken. Scope-Entscheidung. |
| FR-13 | Endpoint POST /products/{id}/strategy/suggest für KI-Vorschlag | T2 | 5 | ✅ | Während Sprint als natürlicher nächster Schritt ergänzt |
| FR-14 | Human-in-the-Loop: LLM-Vorschlag muss bestätigt werden | T1 | 2 | ✅ | Compliance-Leitprinzip |
| FR-15 | „Fancy Formel"-Button (anspruchsvolle Formeln statt banaler Ausgaben) | T3 | 3 | ✅ | Team-Feedback: LLM-Output zu langweilig – Extra-Button mit aggressiverem Prompt |
| FR-16 | Prompt an LLM ist vor dem Absenden einsehbar (Transparenz) | T2 | 2 | ✅ | Für Präsentation wichtig |
| FR-17 | Online-Recherche im KI-Vorschlag (optional) | T2 | 5 | ✅ |  |
| FR-17b | KI-Batch-Schätzung für Wettbewerbspreise aller Produkte | T2 | 5 | ✅ | Human-in-the-Loop: Übernahme pro Produkt oder "Alle übernehmen" |

## **2.3 Simulation und Visualisierung**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-18 | Globaler Simulator für Uhrzeit und Wochentag (Slider) | T2 | 5 | ✅ | Nicht im initialen Scope, entstand als Demo-Idee im Sprint |
| FR-19 | Pro Produkt: Lagerstand-Slider | T2 | 2 | ✅ |  |
| FR-20 | Pro Produkt: Nachfrage-Faktor-Slider (0–2) | T2 | 2 | ✅ |  |
| FR-21 | Simulator-Tick: ein Klick \= eine Stunde, mit Play/Pause und 3×-Beschleunigung | T2 | 3 | ✅ |  |
| FR-22 | Live-Neuberechnung der Preise bei Slider-Änderung | T2 | 5 | ✅ | Dynamik in der Demo |
| FR-23 | Preisgraph pro Produkt über beliebige Variable (Chart.js) | T3 | 8 | ✅ | Team-Vorschlag: „Formeln vereinfacht darstellen". Sehr wertvoll für die Präsentation. |
| FR-24 | Graph-Modus „Zeit gesamt" (kompletter Monat-Verlauf) | T3 | 3 | ✅ |  |

## **2.4 Historie und Audit**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-25 | Append-only Preishistorie (Zeitstempel, Strategie, Input, Begründung) | T1 | 5 | ✅ | Rechenschaftspflicht \+ Demo-Wert |
| FR-26 | Historie pro Produkt einsehen | T1 | 2 | ✅ |  |
| FR-27 | Historie mit Filter (Zeitraum, Strategie) | T0 | 3 | ⛔ | Bewusst nicht umgesetzt – für den Prototyp-Demo-Zweck nicht nötig, Fokus auf Kern-Flow |

## **2.5 Einstellungen und Betrieb**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-28 | Gemini-API-Key in den Einstellungen setzen | T2 | 2 | ✅ |  |
| FR-29 | Rate Limit pro User pro Tag (Default 50, Admin 200, UI-konfigurierbar)  | T4 | 3 | ✅ | Daniel ergänzt, außerhalb Kern-Scope |
| FR-30 | HTTPS per Klick aktivieren (Let's Encrypt) | T4 | 8 | ✅ | Daniels „Monk" – deutlich über Scope, aber produktiv-nahe |
| FR-31 | Datenbank-Reset auf Seed-Stand | T2 | 2 | ✅ | Für Demo-Vorführung praktisch |

## **2.6 Compliance-UI-Bausteine**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-32 | Öffentliche Datenschutz-Kurzfassung (/pages/legal.html) | T3 | 2 | ✅ | Team-Vorschlag während Sprint |
| FR-33 | Compliance-Langfassung hinter Login (/pages/compliance.html) | T3 | 3 | ✅ | Enthält VVT, DPIA, TOMs |
| FR-34 | DSGVO-Disclaimer auf jeder Seite / im Footer | T3 | 1 | ✅ |  |

## **2.7 Bewusst nicht umgesetzt (Scope-Grenzen)**

| ID | Anforderung | Erhoben | SP | Status | Begründung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-35 | Personalisiertes Pricing gegenüber Endkunden | T0 | 13 | ⛔ | DSGVO Art. 22, Art. 246a EGBGB – sprengt Prototyp-Rahmen |
| FR-36 | Shop-Integration (Shopify, WooCommerce) | T0 | 13 | ⛔ | Saubere API zeigt Integration konzeptionell; reale Integration nicht im Zeitrahmen |
| FR-37 | Multi-Tenant (mehrere Shops pro Instanz) | T0 | 8 | ⛔ | Einzelinstanz-Demo reicht |
| FR-38 | Mobile Responsive Design (optimiert) | T2 | 5 | ⛔ | Pico.css bringt Basis-Responsiveness mit; gezielte Mobile-Optimierung nicht priorisiert |
| FR-39 | Echtzeit-Marktdaten-Anbindung (Preise der Konkurrenz automatisch ziehen) | T0 | 13 | ⛔ | Wettbewerbspreis als manueller Input; Crawling/API-Anbindung außerhalb Scope |
| FR-40 | Zahlungsabwicklung / Shop-Funktionen | T0 | 21 | ⛔ | Nicht Zweck des Tools – wir liefern Preisvorschläge, kein Shop-Backend |
| FR-41 | Admin-Audit-Log (wer hat was wann in Einstellungen geändert) | T4 | 5 | ⛔ | Nice-to-have, nicht demorelevant |
| FR-42 | Export Historie als CSV/Excel | T4 | 3 | ⛔ | Nicht demorelevant, aber technisch trivial nachrüstbar |
| FR-43 | Mehrsprachigkeit (i18n) | T0 | 8 | ⛔ | Demo auf Deutsch ausreichend |
| FR-44 | E-Mail-Benachrichtigungen (z. B. Preisalarm) | T0 | 5 | ⛔ | Kein Teil des Kern-Flows |

# 

# **3\. Nicht-funktionale Anforderungen (NFR)**

## **3.1 Architektur und Code-Qualität**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| NFR-01 | Frontend-Backend-Trennung über REST-API | T1 | – | ✅ | Kern-Architekturentscheidung |
| NFR-02 | Datenbankgestützte Persistenz (PostgreSQL) | T1 | 5 | ✅ | Modulanforderung, ADR 0001 |
| NFR-03 | Alembic-Migrationen für Schema-Änderungen | T1 | 3 | ✅ |  |
| NFR-04 | Type Hints \+ Pydantic-Validierung im Backend | T1 | 2 | ✅ |  |
| NFR-05 | Automatische OpenAPI-Doku durch FastAPI | T1 | – | ✅ | Demo-Asset |
| NFR-06 | LLM-Anbieter austauschbar konfiguriert | T1 | 2 | ✅ | Aktuell Gemini, architektonisch umstellbar |
| NFR-07 | Sanity-Check auf LLM-Output | T1 | 3 | ✅ | Schutz vor Fantasiepreisen |
| NFR-08 | Unit- und Integration-Tests (pytest) | T1 | 5 | ✅ | Backend-Tests vorhanden |

## **3.2 Sicherheit**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| NFR-09 | Passwörter gehasht speichern | T1 | 1 | ✅ |  |
| NFR-10 | Session-Cookie HttpOnly, SameSite=Lax | T1 | 2 | ✅ | ADR 0003 |
| NFR-11 | Secrets ausschließlich in .env | T1 | 1 | ✅ |  |
| NFR-12 | Rate Limiting der API | T4 | 3 | ✅ | Pro Endpoint konfigurierbar |
| NFR-13 | HTTPS / TLS produktiv | T4 | 8 | ✅ | Per Klick via Let's Encrypt |
| NFR-14 | Reverse-Proxy (nginx) vor dem Backend | T4 | 3 | ✅ | Teil des install.sh-Setups |
| NFR-15 | Eingabevalidierung Backend (Pydantic) | T1 | 2 | ✅ |  |
| NFR-16 | CSRF-Schutz | T4 | 3 | 🔶 | SameSite-Cookie mitigiert den Kern-Fall; zusätzlicher CSRF-Token nicht implementiert |

## 

## **3.3 Betrieb und Deployment**

| ID | Anforderung | Erhoben | SP | Status | Bemerkung |
| :---- | :---- | :---- | :---- | :---- | :---- |
| NFR-17 | install.sh für idempotente Debian-12-Installation | T4 | 13 | ✅ | Sehr umfangreich: DNS, systemd, certbot, Seed-Daten |
| NFR-18 | systemd-Service für Backend | T4 | 3 | ✅ |  |
| NFR-19 | Seed-Daten (Admin, Team-Accounts, Mock-Produkte) | T2 | 3 | ✅ |  |
| NFR-20 | Automatische Backups der DB | T0 | 5 | 🔶 | Nicht automatisiert im Prototyp; Ansatz in docs/security.md |
| NFR-21 | Monitoring / Alerting (Sentry, Grafana) | T0 | 8 | ⛔ | Prototyp – Application-Logs reichen |
| NFR-22 | High-Availability-Deployment | T0 | 13 | ⛔ | Nicht relevant für Demo |
| NFR-23 | Skalierung auf Masse-Nutzer | T0 | 13 | ⛔ | Single-User-Demo ausreichend |

# 

# **4\. Regulatorische Anforderungen (REG)**

## **4.1 DSGVO**

| ID | Anforderung | Art. | Erhoben | Status |
| :---- | :---- | :---- | :---- | :---- |
| REG-01 | Datenminimierung (nur Produktdaten, keine Endkundendaten) | Art. 5 Abs. 1 lit. c | T0 | ✅ |
| REG-02 | Zweckbindung | Art. 5 Abs. 1 lit. b | T0 | ✅ |
| REG-03 | Rechtsgrundlage für Login-Daten (Vertragserfüllung) | Art. 6 Abs. 1 lit. b | T1 | 📝 |
| REG-04 | Rechenschaftspflicht über Audit-Trail | Art. 5 Abs. 2 | T1 | ✅ |
| REG-05 | Informationspflichten (Datenschutzhinweis) | Art. 13 | T3 | 🔶 |
| REG-06 | Betroffenenrechte | Art. 15–17 | T3 | 🔶 |
| REG-07 | Keine automatisierte Einzelfallentscheidung gegenüber Endkunden | Art. 22 | T1 | ✅ (Human-in-the-Loop) |
| REG-08 | AVV / DPA mit LLM-Anbieter | Art. 28 | T3 | 🔶 |
| REG-09 | Verzeichnis von Verarbeitungstätigkeiten | Art. 30 | T3 | 🔶 (Langfassung unter /pages/compliance.html) |
| REG-10 | TOMs nach Stand der Technik | Art. 32 | T3 | 🔶 |
| REG-11 | Datenschutz-Folgenabschätzung (DSFA) | Art. 35 | T3 | 🔶 (Kurzprüfung: nicht erforderlich) |
| REG-12 | Drittlandtransfer-Grundlage bei Gemini (USA) | Art. 44 ff. | T3 | 🔶 |

## **4.2 EU AI Act**

| ID | Anforderung | Art. | Erhoben | Status |
| :---- | :---- | :---- | :---- | :---- |
| REG-13 | Einstufung als KI-System „begrenztes Risiko" | Art. 50 | T3 | 📝 |
| REG-14 | Transparenzpflicht – KI-Interaktion kennzeichnen | Art. 50 (ab 2.8.2026) | T1 | ✅ |
| REG-15 | Menschliche Aufsicht | – | T1 | ✅ |
| REG-16 | KI-Kompetenz im Team | Art. 4 | T3 | 📝 |
| REG-17 | Hochrisiko-Auflagen | Anhang III | – | ⛔ (nicht anwendbar) |

## **4.3 Preisrecht**

| ID | Anforderung | Quelle | Erhoben | Status |
| :---- | :---- | :---- | :---- | :---- |
| REG-18 | Keine irreführenden Preisangaben | §§ 5, 5a UWG | T3 | ✅ (Sanity-Check) |
| REG-19 | Gesamtpreise inkl. MwSt. | § 1 PAngV | T3 | 🔶 |
| REG-20 | 30-Tage-Regel bei Preisermäßigungen | § 11 PAngV | T3 | 🔶 |
| REG-21 | Hinweispflicht bei personalisierten Preisen | Art. 246a EGBGB | T0 | ⛔ (kein personalisiertes Pricing) |
| REG-22 | Kartellrecht | GWB | T0 | ⛔ (Einzel-Shop-Kontext) |

# **5\. Modulanforderungen (MOD) aus FOM-Skript**

| ID | Anforderung | Skript-Folie | Status |
| :---- | :---- | :---- | :---- |
| MOD-01 | Projektarbeit im Team | 3, 4 | ✅ |
| MOD-02 | Rollenverteilung nach Kompetenzen | 4, 8 | ✅ |
| MOD-03 | Mind. drei Themengebiete (IT-Architektur, Software-Modellierung, Datenschutz, Informationssicherheit) | 5 | ✅ (sogar vier) |
| MOD-04 | Prototypische datenbankgestützte Anwendung | 5 | ✅ |
| MOD-05 | Dokumentation der Umsetzung | 5 | ✅ |
| MOD-06 | Aspekte Informationssicherheit und Datenschutz berücksichtigt | 5 | ✅ |
| MOD-07 | Funktionsfähiger Prototyp | 6 | ✅ |
| MOD-08 | Selbstreflexionsbericht (10 Seiten / 2 pro Person) | 6, 11 | 📝 |
| MOD-09 | 10-Minuten-Präsentation | 6 | 📝 |
| MOD-10 | Rollen-Folie in der Präsentation | 10 | 📝 |
| MOD-11 | Anmeldung Präsentationstermin bis 30.04. | 16 | ✅ (bestätigt) |
| MOD-12 | Check-ins (30.04., 28.05., 25.06.) | 16 | 📝 |

# 

# **6\. Aufwandsüberblick Umgesetzter Anforderungen ✅**

| Bereich | Story Points (Summe) |
| :---- | :---- |
| Produkt- und Benutzerverwaltung |  |
| Pricing-Strategien |  |
| Simulation und Visualisierung |  |
| Historie und Audit |  |
| Einstellungen und Betrieb |  |
| Compliance-UI-Bausteine |  |
| **Summe funktional** |  |
| Nicht-funktional (Architektur, Sicherheit, Deployment) |  |
| **Gesamt umgesetzt** |  |

## **Bewusst nicht umgesetzt (⛔)**

Zusammen etwa **115 SP** an Features bewusst ausgeklammert – überwiegend Skalierung, Shop-Integration und personalisiertes Pricing. Das ist bewusstes Scope-Management, keine Versäumnis.

## **Verteilung nach Erhebungszeitpunkt**

| Zeitpunkt | Anteil der umgesetzten Features (grob) |
| :---- | :---- |
| T0 (Kick-off) | ca. 30 % |
| T1 (Architektur) | ca. 25 % |
| T2 (während Sprint) | ca. 25 % |
| T3 (nach Sprint, Team-Feedback) | ca. 12 % |
| T4 (Daniels Eigeninitiative post Sprint) | ca. 8 % |

**Interpretation:** Nur rund 30 % der finalen Features waren zur Anforderungsanalyse exakt so spezifiziert. Der Rest entstand iterativ – durch Architektur-Entscheidungen, während der Umsetzung (T2), durch Team-Feedback nach dem ersten Prototyp (T3, z. B. Graphen und Fancy-Formel-Button) und durch Eigeninitiative am Ende (T4, z. B. Team-Accounts, HTTPS, Rate Limiting). Das ist typisch für agile Vorgehensmodelle und spiegelt genau die Empfehlung aus Folie 8 des Skripts wider (Prototyping / SCRUM / Kanban).

# 

# **7\. Argumentation für Q\&A**

Wenn nach der Anforderungserhebung gefragt wird:

*„Wir haben zum Kick-off eine gemeinsame Anforderungsanalyse durchgeführt, dabei aber bewusst offen gelassen, welche Features während der Umsetzung konkretisiert werden – das passt zum Prototyping-Ansatz aus dem Skript. Tatsächlich sind nur rund 30 % der Features wortgleich aus der initialen Analyse übernommen. Die übrigen entstanden in der Architekturbesprechung, während des Sprints und durch Feedback der mit-testenden Teammitglieder. Klassische Beispiele sind der Preisgraph, der Fancy-Formel-Button und die Compliance-UI – alle drei Ideen kamen vom Team während der Umsetzung und haben den Prototyp spürbar besser gemacht."*
