**Test Report**

Die automatisierten pytest-Tests im Backend liegen in Daniels Verantwortung und sind nicht Gegenstand dieses Reports. Dieser Bericht fasst die Qualitätssicherung aus Sicht der QS-Rolle zusammen.

## **Zusammenfassung**

| Kennzahl | Wert |
| :---- | :---- |
| Testfälle in Test-Matrix | 26 |
| davon bestanden (✅) | 26 |
| davon fehlgeschlagen (⛔) | 0 |
| Externe User-Tests durchgeführt | 3 |
| Bugs aus QS-Phase gemeldet | 0 |
| Bekannte offene Bugs | 0 |
| Usability-Findings mit Umsetzung | 3 |
| Wontfix mit Begründung | 1 |

**Gesamturteil:**  
Der Prototyp erfüllt alle Abnahmekriterien aus `docs/testing.md`.  
Es gibt **keine offenen Bugs**.  
Die Usability-Findings aus den externen User-Tests wurden soweit umgesetzt, wie es im Prototyp-Scope sinnvoll war.

---

## 

## **Test-Matrix – Ergebnisse**

Die Test-Matrix umfasst 26 manuelle Testfälle, verteilt über die zehn primären Use Cases und gruppiert in fünf Themenbereiche. Für jeden Use Case wurde mindestens ein Happy-Path-Fall und ein Fehlerfall geprüft.

### Abdeckung nach Themenbereich

| Themenbereich (Test-Matrix) | Use Cases | Testfälle | Bestanden | Fehlgeschlagen |
| :---- | :---- | ----: | ----: | ----: |
| A. Produkt-Management | UC-1 bis UC-3 | 6 | 6 | 0 |
| B. Preisstrategien (manuell + KI) | UC-4, UC-5 | 7 | 7 | 0 |
| C. Preisberechnung, Simulator, Graph | UC-6 bis UC-8 | 6 | 6 | 0 |
| D. KI-Wettbewerbspreis und Historie | UC-9, UC-10 | 4 | 4 | 0 |
| E. Sicherheit und Auth | übergreifend | 3 | 3 | 0 |
| **Summe** |  | **26** | **26** | **0** |

### 

### Abnahmekriterien aus `docs/testing.md`

| Kriterium | Status |
| :---- | :---: |
| Jeder Use Case mindestens einmal im Happy Path getestet | ✅ |
| Jeder Use Case mit mindestens einem Fehlerfall getestet | ✅ |
| Alle compliance-relevanten Punkte (KI-Badge, Audit-Trail, Validierung) in eigenen Testfällen | ✅ |
| Kein Bug mit Priorität „kritisch" oder „hoch" offen | ✅ |
| Externe User-Tests mit mindestens zwei Personen außerhalb des Teams durchgeführt | ✅ (drei durchgeführt) |

Alle fünf Abnahmekriterien sind erfüllt.

---

## **Externe User-Tests – Ergebnisse**

Drei Personen mit bewusst unterschiedlichen Profilen haben den Prototyp ohne Einführung bedient. Methodik: Think-aloud-Protokoll, keine Zwischenhilfe, 20–30 Minuten pro Test.

### Testabdeckung pro Testperson

Jede:r hat die sechs vorgegebenen Aufgaben durchlaufen (Anmelden, Produkt anlegen, Fixpreis zuweisen, Formel einrichten, KI-Vorschlag einholen, Historie öffnen). Alle drei Testpersonen haben alle sechs Aufgaben abgeschlossen, teils mit Nachfragen und Umwegen, aber ohne Eingriff durch die Beobachterin.

### Konsolidierte Findings

| \# | Finding | UT-01 | UT-02 | UT-03 | Kategorie | Priorität | Entscheidung |
| :---- | :---- | :---: | :---: | :---: | :---- | :---- | :---- |
| F1 | Formelvariablen (`demand`, `stock`, `cost_price`) nicht selbsterklärend | ✓ | ✓ |  | Usability | Hoch | Fix – Token-Buttons im Formel-Editor (Variablen per Klick) plus Hinweiszeile |
| F2 | Zweck des Kontext-Felds unklar | ✓ |  |  | Verständlichkeit | Mittel | Fix – beschreibender Platzhalter mit Beispielinhalten; KI-Bezug über die Prompt-Vorschau einsehbar |
| F3 | Beispiel-/Vorlage-Formeln fehlen |  | ✓ |  | Feature-Wunsch | Mittel | Fix – Beispiel-Formel als Platzhalter plus Fancy-Formel-Button („Ausführlich") |
| F4 | KI-Vorschlag wird ungeprüft übernommen / Prompt für Laien zu technisch | ✓ | ✓ |  | Verständlichkeit | Niedrig | By Design – Prompt-Vorschau, Begründung und KI-Badge; Human-in-the-Loop |
| F5 | Historie wird bei vielen Produkten unübersichtlich |  |  | ✓ | Usability | Niedrig | Wontfix – Historienfilter außerhalb des Prototyp-Scopes |

### 

### Positive Rückmeldungen (wiederkehrend)

- Übersichtliche Navigation, klare Trennung zwischen Produkten und Strategien  
- Preisgraph wurde – auch über die Aufgaben hinaus – als „der beste Einstieg" in die Formel-Logik bezeichnet  
- Prompt-Vorschau vor dem KI-Aufruf schuf Vertrauen – zwei Testpersonen kommentierten positiv, dass der Prompt vorher sichtbar ist  
- Historie/Audit-Trail wurde als nützlich für die Nachvollziehbarkeit wahrgenommen

### 

### Antworten auf die Kernfragen (Tendenzen)

- **Vertrauen in KI-Vorschlag:** mittel (UT-01, UT-03) bis hoch (UT-02, wegen der sichtbaren Prompt-Vorschau). UT-03 verglich den Vorschlag mit eigener Erfahrung – das bestätigt das Human-in-the-Loop-Design.  
- **Einsatz in echtem Shop:** alle drei würden das Tool einsetzen, mit Einschränkungen – UT-01 nach kurzer Schulung, UT-03 vor allem für kleinere Shops.

---

## **5\. Bug-Bilanz**

| Status | Anzahl |
| :---- | ----: |
| Bugs aus Co-Testing im Nacht-Sprint (vor QS-Phase) | 1 (BUG-001, behoben) |
| Bugs aus manueller Test-Matrix | 0 |
| Bugs aus externen User-Tests | 0 |
| Offene Bugs zum Berichtszeitpunkt | 0 |

BUG-001 (fehlende KI-Markierung in der Preishistorie) entstand aus dem Co-Testing während Daniels Entwicklungssprint, also vor Beginn der strukturierten QS-Phase. Der Fix ist in ADR 0006 dokumentiert und wurde von mir nachgetestet. Der zugehörige Testfall TC-LLM-01 wurde in die Test-Matrix aufgenommen, um Regressionen vorzubeugen.

Die QS-Phase selbst hat keine neuen Bugs hervorgebracht. Die externen User-Tests brachten fünf Usability-/Verständnis-Findings: drei wurden umgesetzt (F1–F3), eines ist bereits durch das bestehende Design abgedeckt (F4), eines bleibt bewusst out-of-scope (F5, Historienfilter).

---

## **6\. Bewertung aus QS-Sicht**

Die eingesetzte Test-Pyramide ist für einen Prototyp tragfähig:

- **Unten** die automatisierten pytest-Tests von Daniel, die die Kernlogik (Formel-Evaluator, API-Endpoints, Strategie-Handling) absichern und bei jedem Commit mitlaufen können.  
- **Mitte** die manuelle Test-Matrix, die jeden Use Case strukturiert mit Happy Path und Fehlerfällen prüft und die Compliance-Punkte (KI-Badge, Audit-Trail, Validierung) eigenständig abdeckt.  
- **Oben** die externen User-Tests, die den Teil abdecken, den Funktionstests prinzipiell nicht erreichen: Verständlichkeit, Bedienbarkeit, Vertrauen.

Das Zusammenspiel der drei Ebenen ergibt eine glaubwürdige Qualitätsaussage, ohne in Test-Overhead zu kippen, der der Prototyp-Größe nicht angemessen wäre.

---

## 

## **7\. Offene Punkte und Ausblick**

- Keine offenen Bugs.  
- Ein Wontfix aus den User-Tests: Historienfilter bei vielen Produkten. Mobile-Layout bleibt generell out-of-scope (`requirements.md` FR-38); beides wäre für den Produktivbetrieb zu ergänzen.  
- Für eine zweite Iteration empfehlenswert: eine weitere Runde User-Tests nach Umsetzung der Verbesserungen, um die Wirkung der Änderungen zu validieren.  
- Ebenfalls für den Produktivbetrieb relevant: Last- und Performance-Tests mit realistischen Produktmengen (der Prototyp wurde mit acht Seed-Produkten geprüft).
