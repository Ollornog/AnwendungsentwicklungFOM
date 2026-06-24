# **Manuelle User-Tests**

Dokumentation der drei externen Usability-Tests mit Think-aloud-Protokoll.
Ergänzt die funktionale [`test-matrix.md`](./test-matrix.md) um die
Perspektive, die reine Funktionstests nicht erreichen: Verständlichkeit,
Bedienbarkeit und Vertrauen. Die konsolidierte Bilanz steht zusätzlich in
[`test-report.md`](./test-report.md).

## **1. Zielsetzung**

Drei Personen außerhalb des Teams bedienen den Prototyp ohne vorherige Erklärung. Ziel ist es, **Usability-Probleme** und **Verständnislücken** zu finden, die dem Team durch Betriebsblindheit entgehen. Kein Funktionstest – dafür ist `docs/test-matrix.md` zuständig.

## **2. Vorgehen**

- Testperson erhält nur: URL, Demo-Login (`Demo` / `DemoUser`), ein Satz Kontext („Tool zur Preisoptimierung im E-Commerce, du bist Shop-Betreiber:in").
- Keine Schulung, keine Demo-Vorführung.
- Think-aloud-Protokoll: die Testperson kommentiert laut, was sie sieht und denkt.
- Beobachter:in (Kayathiri) notiert Stolperstellen, hakt nicht nach, greift nur ein, wenn die Person völlig festhängt.
- Dauer pro Test: ca. 20–30 Minuten.
- Vor jeder Session wird die DB über *Einstellungen → Datenbank zurücksetzen* (UC-16) auf den Seed-Stand gebracht.
- Am Ende: kurze Kernfragen (siehe 4.).

## **3. Aufgaben für die Testpersonen**

Die Testpersonen bekommen die folgenden **sechs** Aufgaben in dieser Reihenfolge. Kein Zeitlimit, aber Abbruch erlaubt.

1. **Anmelden** an der Anwendung.
2. **Ein neues Produkt anlegen** – frei wählbare Werte, inklusive Kontext-Text.
3. **Eine Fixpreis-Strategie** zuweisen und speichern.
4. **Eine Formel-Strategie** für ein bestehendes Produkt einrichten, die lager- oder uhrzeitabhängig reagiert.
5. **Einen KI-Vorschlag einholen** für ein Produkt und entscheiden, ob übernommen wird.
6. **Die Preishistorie** eines Produkts öffnen und erklären, was dort zu sehen ist.

## **4. Kernfragen am Ende**

- Was war intuitiv, was nicht?
- Wo warst du unsicher, was das System gerade macht?
- An welcher Stelle hättest du eine Erklärung, einen Tooltip oder ein Beispiel erwartet?
- Hast du dem KI-Vorschlag vertraut? Warum (nicht)?
- Würdest du das Tool in einem echten Shop einsetzen?

## **5. Testpersonen**

| ID | Rolle / Kontext | Erfahrung E-Commerce | Erfahrung mit KI-Tools | Datum |
| :---- | :---- | :---- | :---- | :---- |
| UT-01 | *Controller, kein IT-Background* | mittel | gering | 15.05.2026 |
| UT-02 | *IT-affine Person (Kollegin), kein Shop-Kontext* | gering | hoch | 16.05.2026 |
| UT-03 | *Person mit Shop-Erfahrung (vertreibt Herrenschmuck)* | hoch | mittel | 17.05.2026 |

Namen der Testpersonen werden nicht dokumentiert (DSGVO – Datenminimierung). IDs reichen für die Zuordnung der Findings.

---

## **6. Test UT-01**

**Datum:** 15.05.2026 **Testperson:** UT-01 (Controller, kein IT-Background) **Setting:** Remote, Windows 11, Chrome

### Ablauf und Beobachtungen

| Aufgabe | Erfolgreich? | Dauer | Beobachtung |
| :---- | :---- | :---- | :---- |
| 1. Anmelden | Ja | 1 min | Login sofort verstanden |
| 2. Produkt anlegen | Ja | 3 min | Kontext-Feld wurde ignoriert |
| 3. Fixpreis zuweisen | Ja | 2 min | *Preis*-Button schnell gefunden |
| 4. Formel einrichten | Nein | 6 min | Bedeutung der Variablen nicht verstanden |
| 5. KI-Vorschlag einholen | Ja | 4 min | Vorschlag wurde ungeprüft übernommen |
| 6. Historie öffnen | Ja | 2 min | Historie geöffnet, aber Inhalt nicht eingeordnet |

### Findings

| \# | Finding | Kategorie | Priorität | In Bug-Log? |
| :---- | :---- | :---- | :---- | :---- |
| → F2 | Zweck des Kontext-Felds unklar | Verständlichkeit | Mittel | nein (kein Bug) |
| → F1 | Formelvariablen (`demand`, `stock`) nicht selbsterklärend; Aufgabe 4 abgebrochen | Usability | Hoch | nein (kein Bug) |
| → F4 | KI-Vorschlag ohne Prüfung übernommen; Begründung/KI-Badge nicht aktiv beachtet | Verständlichkeit | Niedrig | nein (kein Bug) |

### Zitate (Think-aloud)

„Ich weiß nicht, was ich in das Kontext-Feld schreiben soll."

„Woher soll ich wissen, was demand oder stock bedeutet?"

### Antworten auf Kernfragen

- **Intuitiv:** Produkt anlegen und Fixpreis setzen.
- **Unsicherheiten:** Formel-Editor.
- **Fehlende Erklärungen:** Variablen im Formelmodus.
- **Vertrauen in KI:** Mittel – Begründung hilft.
- **Einsatzbereitschaft:** Ja, nach kurzer Schulung.

---

## **7. Test UT-02**

**Datum:** 16.05.2026 **Testperson:** UT-02 (IT-affine Kollegin) **Setting:** Remote, macOS, Safari

### Ablauf und Beobachtungen

| Aufgabe | Erfolgreich? | Dauer | Beobachtung |
| :---- | :---- | :---- | :---- |
| 1. Anmelden | Ja | <1 min | Keine Probleme |
| 2. Produkt anlegen | Ja | 2 min | Schnell abgeschlossen |
| 3. Fixpreis zuweisen | Ja | 1 min | Sofort verstanden |
| 4. Formel einrichten | Ja | 3 min | Suchte zuerst nach Vorlagen |
| 5. KI-Vorschlag einholen | Ja | 2 min | Editierte den Vorschlag direkt |
| 6. Historie öffnen | Ja | 1 min | Historie verständlich |

### Findings

| \# | Finding | Kategorie | Priorität | In Bug-Log? |
| :---- | :---- | :---- | :---- | :---- |
| → F3 | Beispiel-/Vorlage-Formeln werden erwartet, aber nicht gefunden | Feature-Wunsch | Mittel | nein (kein Bug) |
| → F4 | Prompt-Vorschau inhaltlich gut, für Laien aber zu technisch | Verständlichkeit | Niedrig | nein (kein Bug) |

### Zitate (Think-aloud)

„Ich hätte erwartet, dass es ein paar Beispiel-Formeln gibt."

„Der Prompt ist interessant, aber für normale Nutzer vielleicht zu technisch."

### Antworten auf Kernfragen

- **Intuitiv:** Gesamte Navigation.
- **Unsicherheiten:** Keine wesentlichen.
- **Fehlende Erklärungen:** Formel-Beispiele.
- **Vertrauen in KI:** Hoch, wegen sichtbarer Prompt-Vorschau.
- **Einsatzbereitschaft:** Ja.

---

## **8. Test UT-03**

**Datum:** 17.05.2026 **Testperson:** UT-03 (Shop-Betreiber Herrenschmuck) **Setting:** Remote, Windows 11, Edge

### Ablauf und Beobachtungen

| Aufgabe | Erfolgreich? | Dauer | Beobachtung |
| :---- | :---- | :---- | :---- |
| 1. Anmelden | Ja | <1 min | Keine Probleme |
| 2. Produkt anlegen | Ja | 2 min | Trug reale Produktdaten ein |
| 3. Fixpreis zuweisen | Ja | 2 min | Verständlich |
| 4. Formel einrichten | Ja | 4 min | Verstand Lagerlogik schnell |
| 5. KI-Vorschlag einholen | Ja | 3 min | Verglich Ergebnis mit eigener Erfahrung |
| 6. Historie öffnen | Ja | 2 min | Fand Historie sehr sinnvoll, öffnete danach spontan den Preisgraph |

### Findings

| \# | Finding | Kategorie | Priorität | In Bug-Log? |
| :---- | :---- | :---- | :---- | :---- |
| → F5 | Historie wird bei vielen Produkten unübersichtlich | Usability | Niedrig | nein (kein Bug) |

Kein funktionaler Defekt. Zusätzlich eine fachliche Einordnung (kein Finding, sondern Bestätigung): Der Wettbewerbspreis ist für diese Person die wichtigste Eingangsgröße – das deckt sich mit der Rolle des Felds in der Formel-Strategie.

### Zitate (Think-aloud)

„Der Wettbewerbspreis ist für mich fast wichtiger als der Einkaufspreis."

„Die Historie ist gut, aber bei vielen Produkten wird sie schnell lang."

### Antworten auf Kernfragen

- **Intuitiv:** Produkt- und Preisverwaltung.
- **Unsicherheiten:** Keine größeren.
- **Fehlende Erklärungen:** Keine.
- **Vertrauen in KI:** Mittel bis hoch.
- **Einsatzbereitschaft:** Ja, besonders für kleinere Shops.

---

## **9. Konsolidierte Findings**

Zusammenfassung über alle drei Tests, sortiert nach Priorität.

| ID | Finding | UT-01 | UT-02 | UT-03 | Priorität | Entscheidung |
| :---- | :---- | :---: | :---: | :---: | :---- | :---- |
| F1 | Formelvariablen (`demand`, `stock`, `cost_price`) nicht selbsterklärend | ✓ | ✓ |  | Hoch | **Fix** – Token-Buttons im Formel-Editor (Variablen per Klick einfügen) plus Hinweiszeile |
| F2 | Zweck des Kontext-Felds unklar | ✓ |  |  | Mittel | **Fix** – beschreibender Platzhalter mit Beispielinhalten; der KI-Bezug ist über die Prompt-Vorschau einsehbar |
| F3 | Beispiel-/Vorlage-Formeln fehlen | | ✓ |  | Mittel | **Fix** – Beispiel-Formel als Platzhalter im Eingabefeld plus Fancy-Formel-Button („Ausführlich"), der per KI eine ausdrucksstarke Formel erzeugt |
| F4 | KI-Vorschlag wird ungeprüft übernommen / Prompt für Laien zu technisch | ✓ | ✓ |  | Niedrig | **By Design** – Prompt-Vorschau, Begründung und KI-Badge adressieren die Transparenz; Human-in-the-Loop bleibt der Schutz |
| F5 | Historie wird bei vielen Produkten unübersichtlich | | | ✓ | Niedrig | **Wontfix** – Historienfilter außerhalb des Prototyp-Scopes |

### Wiederkehrende Muster

- Produktanlage und Fixpreis wurden von allen Testpersonen problemlos verstanden.
- Formel-Strategien benötigen mehr Hilfestellung (Variablen, Beispiele).
- Die Prompt-Vorschau erhöht das Vertrauen in die KI.
- Die Historie wird als nützlich für die Nachvollziehbarkeit wahrgenommen; der Preisgraph wurde – auch über die Aufgaben hinaus – als der verständlichste Einstieg in die Formel-Logik genannt.

### Positive Rückmeldungen

- Übersichtliche Navigation.
- Klare Trennung zwischen Produkten und Strategien.
- Transparente KI-Integration durch die Prompt-Vorschau.
- Historie/Audit-Trail vermittelt Vertrauen.

## **10. Ableitungen für den Prototyp**

- **Umgesetzte Änderungen (vorhanden im Prototyp):**
  - Token-Buttons im Formel-Editor, um Variablen per Klick statt Tippen einzufügen (zu F1).
  - Beispiel-Formel als Platzhalter im Eingabefeld und Fancy-Formel-Button („Ausführlich") für eine KI-generierte Beispielformel (zu F3).
  - Beschreibender Platzhalter im Kontext-Feld, der Beispielinhalte vorgibt (zu F2).
  - Prompt-Vorschau, Begründung und KI-Badge als Transparenz-Schicht (zu F4).
- **Bewusst nicht umgesetzt (Wontfix) mit Begründung:**
  - Historienfilter/-suche bei vielen Produkten – außerhalb des Prototyp-Scopes (zu F5).
  - Erweiterte KI-Optimierungsfunktionen – nicht Teil der Anforderungen.
- **Bugs aus den User-Tests:** keine. Der einzige Bug des Projekts (BUG-001, KI-Markierung) stammt aus dem Co-Testing im Nacht-Sprint, nicht aus den User-Tests – siehe [`bug-log.md`](./bug-log.md).

## **11. Reflexion zur Methode**

Drei Personen sind für einen Prototyp eine tragfähige Stichprobe: Die unterschiedlichen Profile stolperten an unterschiedlichen Stellen (UT-01 an den Formelvariablen, UT-02 wünschte Vorlagen, UT-03 dachte in Mengen-/Lagerszenarien) und ergaben zusammen ein breiteres Bild als drei ähnliche Tester:innen. Für eine zweite Iteration wäre eine weitere Runde nach Umsetzung der Fixes sinnvoll, um deren Wirkung zu verifizieren.
