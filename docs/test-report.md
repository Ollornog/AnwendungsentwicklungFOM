**Test Report**

Die automatisierten pytest-Tests im Backend liegen in Daniels Verantwortung und sind nicht Gegenstand dieses Reports. Dieser Bericht fasst die Qualitätssicherung aus Sicht der QS-Rolle zusammen.

## **Zusammenfassung**

| Kennzahl | Wert |
| :---- | :---- |
| Testfälle in Test-Matrix | 23 |
| davon bestanden (✅) | 23 |
| davon fehlgeschlagen (⛔) | 0 |
| Externe User-Tests durchgeführt | 3 |
| Bugs aus QS-Phase gemeldet | 0 |
| Bekannte offene Bugs | 0 |
| Usability-Findings mit Umsetzung | 2 |
| Wontfix mit Begründung | 1 |

**Gesamturteil:**  
Der Prototyp erfüllt alle Abnahmekriterien aus `docs/testing.md`.  
Es gibt **keine offenen Bugs**.  
Die Usability-Findings aus den externen User-Tests wurden soweit umgesetzt, wie es im Prototyp-Scope sinnvoll war.

---

## 

## **Test-Matrix – Ergebnisse**

Die Test-Matrix umfasst 23 manuelle Testfälle, verteilt über die sechs Use Cases. Für jeden Use Case wurde mindestens ein Happy-Path-Fall und ein Fehlerfall geprüft.

### Abdeckung nach Use Case

| Use Case | Testfälle | Bestanden | Fehlgeschlagen |
| :---- | ----: | ----: | ----: |
| UC-1 Produkt anlegen | 4 | 4 | 0 |
| UC-2 Strategie zuweisen | 4 | 4 | 0 |
| UC-3 Preis berechnen | 3 | 3 | 0 |
| UC-4 KI-Vorschlag einholen | 4 | 4 | 0 |
| UC-5 Simulator nutzen | 4 | 4 | 0 |
| UC-6 Historie einsehen | 4 | 4 | 0 |
| **Summe** | **23** | **23** | **0** |

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
| F1 | Formel-Syntax für Nicht-Programmierer:innen schwer zugänglich – Variablennamen wie `cost_price` wirken technisch | ✓ |  | ✓ | Usability | Mittel | Fix – Token-Buttons im Formel-Editor sichtbar gemacht, Fancy-Formel-Button ergänzt |
| F2 | Kontext-Feld beim Produkt unklar – Testpersonen wussten nicht, wofür der Freitext verwendet wird | ✓ | ✓ |  | Verständlichkeit | Mittel | Fix – Beschriftung präzisiert, Hinweis ergänzt, dass der Text an die KI übergeben wird |
| F3 | Mobile-Ansicht schlecht bedienbar – Slider und Formel-Editor funktionieren auf kleinen Bildschirmen nicht sauber |  | ✓ |  | Usability | Niedrig | Wontfix – Mobile-Layout explizit out-of-scope laut `requirements.md` FR-38; Demo-Zielumgebung ist Desktop-Browser |

### 

### Positive Rückmeldungen (wiederkehrend)

- Simulator mit Slidern wirkte auf alle drei Testpersonen greifbar und gut verständlich  
- Preisgraph wurde spontan als „der beste Einstieg" bezeichnet, weil er abstrakte Formeln visuell erfahrbar macht  
- Prompt-Preview vor dem KI-Aufruf schuf Vertrauen – zwei Testpersonen kommentierten positiv, dass der Prompt vorher sichtbar ist  
- Historie mit KI-Badge verstanden alle drei auf den ersten Blick

### 

### Antworten auf die Kernfragen (Tendenzen)

- **Vertrauen in KI-Vorschlag:** zwei von drei vertrauten dem Vorschlag eingeschränkt („ich würde die Formeln immer nochmal prüfen"). Das bestätigt das Human-in-the-Loop-Design.  
- **Einsatz in echtem Shop:** zwei von drei würden das Tool als Unterstützung einsetzen, sofern es an einen echten Shop angebunden ist. Eine Testperson sah den Einsatz zurückhaltender.

---

## **5\. Bug-Bilanz**

| Status | Anzahl |
| :---- | ----: |
| Bugs aus Co-Testing im Nacht-Sprint (vor QS-Phase) | 1 (BUG-001, behoben) |
| Bugs aus manueller Test-Matrix | 0 |
| Bugs aus externen User-Tests | 0 |
| Offene Bugs zum Berichtszeitpunkt | 0 |

BUG-001 (fehlende KI-Markierung in der Preishistorie) entstand aus dem Co-Testing während Daniels Entwicklungssprint, also vor Beginn der strukturierten QS-Phase. Der Fix ist in ADR 0004 dokumentiert und wurde von mir nachgetestet. Der zugehörige Testfall TC-LLM-01 wurde in die Test-Matrix aufgenommen, um Regressionen vorzubeugen.

Die QS-Phase selbst hat keine neuen Bugs hervorgebracht. Die Prüfung hat aber zwei Usability-Findings gebracht, die als Verbesserungen umgesetzt wurden, und ein drittes, das bewusst nicht adressiert wird.

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
- Ein Wontfix: Mobile-Layout. Bei einem Produktivbetrieb wäre ein responsives Layout zu ergänzen.  
- Für eine zweite Iteration empfehlenswert: eine weitere Runde User-Tests nach Umsetzung der Verbesserungen, um die Wirkung der Änderungen zu validieren.  
- Ebenfalls für den Produktivbetrieb relevant: Last- und Performance-Tests mit realistischen Produktmengen (der Prototyp wurde mit acht Seed-Produkten geprüft).
