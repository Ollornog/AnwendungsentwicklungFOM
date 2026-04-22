**Compliance Review**

**Reviewte Artefakte:**

- `docs/compliance.md`  
- `frontend/pages/legal.html` (öffentliche Kurzfassung)  
- `frontend/pages/compliance.html` (interne Langfassung hinter Login)  
- Quer-Bezug: `docs/security.md`, `docs/requirements.md` (REG-Anforderungen)

---

## **1\. Methodik**

Das Review prüft die drei Dokumente gegen die in `requirements.md` dokumentierten REG-Anforderungen (DSGVO, EU AI Act, Preisrecht) sowie ergänzend NIS-2 und KI-Kompetenz. Pro Anforderung wird bewertet:

| Symbol | Bedeutung |
| :---- | :---- |
| 🟢 | Vollständig und stimmig adressiert |
| 🟡 | Adressiert, aber präziser formulierbar oder unvollständig |
| 🔴 | Fehlt oder sachlich fehlerhaft |
| ⚪ | Bewusst nicht im Scope (Begründung dokumentiert) |

Der Charakter des Projekts (studentischer Prototyp, keine Echtkundendaten, kein Produktivbetrieb) wird bei der Bewertung berücksichtigt. Maßstab: **Ein Prüfer soll nachvollziehen können, dass das Team die Regulatorik verstanden und die Grenzen des Prototyp-Scopes sauber dokumentiert hat.**

## **2\. Review-Verlauf**

Das Review wurde in zwei Durchläufen durchgeführt:

1. **Erster Durchlauf** – Prüfung der drei Dokumente gegen die acht priorisierten Review-Kriterien. Ergebnis: sechs Kriterien direkt erfüllt, zwei Kriterien mit Nachbesserungsbedarf (REG-12 Drittlandtransfer, REG-19 PAngV).  
2. **Nacharbeit durch Daniel** (22.04.2026) – Die beiden offenen Punkte wurden umgesetzt; die Änderungshistorie in `CLAUDE.md` dokumentiert den Commit mit dem Eintrag „Compliance-Review Restarbeiten: DPF \+ PAngV nachgezogen".  
3. **Re-Review** – Prüfung der Änderungen gegen die Befundliste. Ergebnis: alle acht Kriterien erfüllt, Freigabe erteilt.

## **3\. Zusammenfassung**

| Bereich | 🟢 | 🟡 | 🔴 | ⚪ |
| :---- | :---: | :---: | :---: | :---: |
| DSGVO | 11 | 0 | 0 | 0 |
| EU AI Act | 4 | 0 | 0 | 1 |
| NIS-2 | 1 | 0 | 0 | 0 |
| Preisrecht | 3 | 0 | 0 | 2 |
| Informationssicherheit | 6 | 1 | 0 | 1 |

**Gesamturteil:** **Freigegeben für die Präsentation.**

Die beiden im ersten Durchlauf als 🟡 bewerteten Punkte wurden durch die Nacharbeit am 22.04.2026 auf 🟢 angehoben. Der verbleibende 🟡-Befund zu CSRF ist ein bewusster Trade-off des Prototyps und in der Doku transparent benannt – für die Prüfungsleistung ausreichend.

---

## **4\. Einzelbefunde DSGVO**

### REG-01 – Datenminimierung (Art. 5 Abs. 1 lit. c) 🟢

Keine Endkundendaten im Scope. Produktdaten, Strategie-Inputs und Preishistorie sind zweckbezogen, Login-Daten minimal (Benutzername \+ Passwort-Hash). Dokumentiert in der VVT-Tabelle in `compliance.html`.

### REG-02 – Zweckbindung (Art. 5 Abs. 1 lit. b) 🟢

Zweck „Preisvorschlag für Shop-Betreiber:innen" ist eindeutig in der VVT benannt. Keine Zweitverwertung der Daten.

### REG-03 – Rechtsgrundlage Login-Daten (Art. 6 Abs. 1 lit. b) 🟢

Vertragserfüllung als Grundlage in `compliance.html` mit Klarstellung, dass der Prototyp mit Einverständnis der Team-Mitglieder als Testnutzer:innen betrieben wird.

### REG-04 – Rechenschaftspflicht / Audit-Trail (Art. 5 Abs. 2\) 🟢

Append-only Preishistorie mit Zeitstempel, Strategie, Input und KI-Badge. Semantik des KI-Badges in ADR 0004 und BUG-001 dokumentiert.

### REG-05 – Informationspflichten (Art. 13\) 🟢

Beleg: `legal.html` §5-DDG-Impressum und H3 „Verantwortlicher"; Querbezug in `compliance.html` VVT (Zeile 402). Alle Pflichtangaben – Identität und Kontaktdaten des Verantwortlichen, Datenkategorien, Speicherdauer, Betroffenenrechte und Empfänger – sind adressiert.

### REG-06 – Betroffenenrechte (Art. 15–17) 🟢

Prozess für Auskunft und Löschung in `compliance.html` beschrieben; Admin-CRUD über Team-Accounts ermöglicht die tatsächliche Umsetzung.

### REG-07 – Keine automatisierte Einzelfallentscheidung ggü. Endkunden (Art. 22\) 🟢

Kein personalisiertes Pricing, Human-in-the-Loop bei jedem KI-Vorschlag. Nicht-Anwendbarkeit von Art. 22 in `compliance.html` explizit mit Begründung dokumentiert.

### REG-08 – AVV / DPA mit LLM-Anbieter (Art. 28\) 🟢

In `compliance.html` Abschnitt 3 wird klargestellt, dass im Produktivbetrieb die Google-Cloud-DPA abzuschließen wäre; der Prototyp nutzt den kostenfreien Tier ohne Produktivdaten. Nach der Nacharbeit enthält der Abschnitt zusätzlich den Hinweis auf die DPF-Zertifizierung von Google LLC.

### REG-09 – VVT (Art. 30\) 🟢

Beleg: `compliance.html` Zeilen 39–52 enthalten alle zehn Pflichtfelder – Name und Kontaktdaten des Verantwortlichen, Zwecke, Kategorien Betroffener, Kategorien Daten, Empfänger einschließlich Drittland, Löschfristen und TOM-Verweis.

### REG-10 – TOMs (Art. 32\) 🟢

Standardkategorien in `compliance.html` und `security.md` abgedeckt: Zutritts-, Zugangs- und Zugriffskontrolle, Weitergabekontrolle, Eingabekontrolle über die Preishistorie, Verfügbarkeit (systemd-Restart, kein HA – ehrlich dokumentiert), Trennungsgebot.

### REG-11 – DSFA-Schwellwertanalyse (Art. 35\) 🟢

Beleg: `compliance.html` Abschnitt 2 „Kurzprüfung" mit Begründung, warum eine vollständige DSFA nicht erforderlich ist. Die drei Schwellwertkriterien sind einzeln durchgegangen.

### REG-12 – Drittlandtransfer Gemini (Art. 44 ff.) 🟢

**Erster Review:** 🟡 – nur SCC-Grundlage genannt, EU-US Data Privacy Framework fehlte.

**Nacharbeit am 22.04.2026:** Die Rechtsgrundlage wurde auf die rechtliche Realität seit Juli 2023 angehoben. Primäre Grundlage ist jetzt der Angemessenheitsbeschluss EU-US Data Privacy Framework (Art. 45 Abs. 3 DSGVO, Beschluss 2023/1795); Google LLC ist unter dem DPF zertifiziert. Standardvertragsklauseln (Art. 46 Abs. 2 lit. c DSGVO) sind als Fallback-Absicherung ergänzend benannt.

**Beleg nach Nacharbeit:**

- `frontend/pages/legal.html` §4 „Empfänger & Drittlandtransfer" (Zeilen 117–126)  
- `frontend/pages/compliance.html` VVT-Zeile 48–49 sowie Abschnitt 3 „AVV mit dem LLM-Anbieter" (Zeilen 83–98)  
- `docs/compliance.md` DSGVO-Tabelle (SCC/DPF-Synchronisierung)

## 

## **5\. Einzelbefunde EU AI Act**

### REG-13 – Einstufung als begrenztes Risiko (Art. 50\) 🟢

Korrekte Einstufung: Kein Hochrisiko, kein verbotenes System, begrenztes Risiko wegen Interaktion mit natürlicher Person. Einstufung mit Begründung in `compliance.html` verschriftlicht.

### REG-14 – Transparenzpflicht (Art. 50, ab 2\. 8\. 2026\) 🟢

KI-Interaktion als solche gekennzeichnet: Prompt-Preview im Strategie-Modal, KI-Badge in der Historie (ADR 0004), expliziter Transparenzhinweis in `legal.html`.

### REG-15 – Menschliche Aufsicht 🟢

Jede KI-gestützte Preisentscheidung erfordert User-Bestätigung. Keine automatische Übernahme.

### REG-16 – KI-Kompetenz (Art. 4\) 🟢

Beleg: `compliance.html` Abschnitt 6 „KI-Governance" benennt, wie die KI-Kompetenz im Team erworben wurde (FOM-Studium, projektspezifische Auseinandersetzung mit DSGVO und AI Act) und welche Schulungsnotwendigkeiten für einen Produktivbetrieb bestünden.

### REG-17 – Hochrisiko-Auflagen ⚪

Nicht anwendbar, korrekt out-of-scope in `compliance.html`.

## **6\. Einzelbefunde NIS-2 🟢**

Beleg: `compliance.html` Abschnitt 5 enthält die Nicht-Anwendbarkeits-Begründung: kein wesentlicher Dienst, keine Mindestgröße, kein Produktivbetrieb. Typische Maßnahmen für einen Produktivbetrieb (ISMS, Risikomanagement, 24-h-Meldepflicht) sind als Ausblick benannt. Das dokumentiert Bewusstsein, ohne falsche Compliance zu beanspruchen.

## **7\. Einzelbefunde Preisrecht**

### REG-18 – Keine irreführenden Preisangaben (§§ 5, 5a UWG) 🟢

Sanity-Check auf LLM-Output verhindert offensichtlich unsinnige Preise, menschliche Bestätigung erforderlich.

### REG-19 – Gesamtpreise inkl. MwSt. (§ 1 PAngV) 🟢

**Erster Review:** 🔴 – der Demo-Disclaimer enthielt zwar den Hinweis „keine echten Preise", aber PAngV wurde nicht explizit genannt.

**Nacharbeit am 22.04.2026:** Neuer `<article>`\-Block als §8 „Preisangaben (PAngV)" nach dem Abschnitt 7 „Automatisierte Entscheidungsfindung" in `legal.html`. Text stellt klar:

- Simulationswerte auf Mock-Produktdaten, kein Angebot im Sinne § 145 BGB.  
- Keine Preisangabe gegenüber Verbrauchern im Sinne der PAngV.  
- Keine Netto-/Bruttounterscheidung, keine Umsatzsteuer.  
- Anwendung richtet sich nicht an Endverbraucher.

**Beleg nach Nacharbeit:**

- `frontend/pages/legal.html` neuer §8-Absatz

### REG-20 – 30-Tage-Regel bei Preisermäßigungen (§ 11 PAngV) ⚪

Nicht im Scope (keine Rabattangaben im Prototyp); in `compliance.html` benannt, dass § 11 PAngV bei einer Shop-Integration zu beachten wäre.

### REG-21, REG-22 ⚪

Kein personalisiertes Pricing, Einzel-Shop-Kontext – nicht anwendbar, korrekt out-of-scope.

## **8\. Informationssicherheit** **(Querbezug zu `security.md`)**

| Thema | Status | Befund |
| :---- | :---: | :---- |
| Passwörter gehasht (argon2id) | 🟢 | NFR-09 erfüllt |
| Session-Cookie HttpOnly / SameSite=Lax | 🟢 | `security.md` Zeile 17, ADR 0003 |
| Secrets in `.env`, nicht in Code | 🟢 | NFR-11 |
| Rate Limiting | 🟢 | NFR-12 |
| HTTPS produktiv | 🟢 | NFR-13, per Klick via Let's Encrypt |
| CSRF-Schutz | 🟡 | SameSite=Lax mitigiert den Kern-Fall; vollständiger Token-Mechanismus fehlt bewusst. In `security.md` transparent als Trade-off benannt. |
| Backups | 🟢 | `security.md` Zeile 21: manueller `pg_dump` dokumentiert, mit 📝-Markierung „nicht im Prototyp produktiv automatisiert" |
| Monitoring | ⚪ | Bewusst out-of-scope, NFR-21 |

Der verbliebene 🟡-Befund zu CSRF ist für den Prototyp-Scope akzeptabel: Session-Cookie mit `SameSite=Lax` deckt die typischen Cross-Site-Request-Forgery-Vektoren ab, ein vollständiger Double-Submit-Token-Mechanismus wäre über das Prototyp-Ziel hinaus.

## 

## **9\. Konsistenz zwischen öffentlicher und interner Fassung 🟢**

- Verantwortlicher in `legal.html` (§5-DDG-Impressum, H3 „Verantwortlicher") und `compliance.html` (VVT Zeile 402\) identisch benannt.  
- Speicherfristen, Empfängerangaben und Drittlandstransfer-Aussagen stimmen nach der Nacharbeit zu REG-12 in allen drei Dokumenten (`legal.html`, `compliance.html`, `docs/compliance.md`) überein.  
- Prototyp-Disclaimer an prominenter Stelle in beiden Fassungen.  
- Keine inhaltlichen Widersprüche zwischen Kurz- und Langfassung gefunden.

## **10\. Sprache und Lesbarkeit 🟢**

- Fachterminologie konsistent („Nutzer:in" für die Rolle im System, „Betroffene:r" im DSGVO-Kontext).  
- Verweise auf Artikel durchgängig mit Gesetz (Art. 30 DSGVO, Art. 50 AI Act, § 1 PAngV).  
- Keine Jura-Floskeln ohne inhaltlichen Gehalt; Formulierungen erkennbar verstanden, nicht kopiert.

---

## **11\. Review-Ergebnis**

**Freigabe:** ☒ **Freigegeben**  ☐ Freigegeben mit Auflagen  ☐ Nicht freigegeben

**Datum der Freigabe:** 22.04.2026 **Grundlage:** Re-Review nach abgeschlossener Nacharbeit zu REG-12 und REG-19.

**Offene Nachbesserungen nach Präsentation (nice-to-have, nicht präsentationsrelevant):**

1. Vollständigen CSRF-Token-Mechanismus implementieren (aktuell bewusst out-of-scope, `SameSite=Lax` mitigiert den Kern-Fall).  
2. Automatisierte Backups über Cron (aktuell manueller `pg_dump` dokumentiert).

Beide Punkte sind in `security.md` als Trade-offs benannt und beeinträchtigen die Freigabe für die Präsentationsleistung nicht.

---

## 

## **Anhang – Änderungsprotokoll Nacharbeit (22.04.2026)**

Umgesetzt durch Daniel, dokumentiert in `CLAUDE.md` Änderungshistorie.

| Datei | Änderung |
| :---- | :---- |
| `frontend/pages/legal.html` | §4 Drittlandtransfer neu formuliert (DPF primär, SCC als Fallback); neuer §8 „Preisangaben (PAngV)" nach §7 eingefügt |
| `frontend/pages/compliance.html` | VVT-Zeile 48–49 Drittlandtransfer aktualisiert; Abschnitt 3 (Zeilen 83–98) um DPF-Zertifizierungs-Hinweis erweitert |
| `docs/compliance.md` | DSGVO-Tabelle mit DPF-Verweis synchronisiert |
| `CLAUDE.md` | Änderungshistorie-Eintrag 2026-04-22 „Compliance-Review Restarbeiten: DPF \+ PAngV nachgezogen" |

**Kein Backend-Code betroffen, keine zusätzlichen Tests erforderlich.**
