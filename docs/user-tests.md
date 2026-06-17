# **Externe User-Tests**

Dokumentation der drei externen Usability-Tests mit Think-aloud-Protokoll.
Ergänzt die funktionale [`test-matrix.md`](./test-matrix.md) um die
Perspektive, die reine Funktionstests nicht erreichen: Verständlichkeit,
Bedienbarkeit und Vertrauen. Die konsolidierte Bilanz steht zusätzlich in
[`test-report.md`](./test-report.md).

## **1. Ziel und Methodik**

- **Ziel:** Verständnis- und Bedienprobleme finden, die dem Team durch
  Betriebsblindheit nicht mehr auffallen.
- **Methode:** Think-aloud-Protokoll – die Testperson spricht laut aus,
  was sie sieht, denkt und erwartet. Die Beobachterin (Kayathiri) greift
  nicht ein und notiert Stolperstellen möglichst wörtlich.
- **Dauer:** 20–30 Minuten pro Test, einzeln.
- **Umgebung:** Live-Demo unter <https://fom.ollornog.de/>. Vor jeder
  Session wird die Datenbank über *Einstellungen → Datenbank zurücksetzen*
  (UC-16) auf den Seed-Stand gebracht, damit alle Tester:innen die gleichen
  Startbedingungen haben.
- **Keine Einführung:** Die Tester:innen bekommen nur die Aufgabenliste,
  keine Erklärung der Oberfläche.

## **2. Testpersonen**

Bewusst unterschiedliche Profile, um ein breites Bild zu bekommen.

| ID | Profil | Bezug zu E-Commerce | IT-Affinität |
| :---- | :---- | :---- | :---- |
| UT-01 | Person ohne IT-Hintergrund | gering | niedrig |
| UT-02 | IT-affine Person ohne E-Commerce-Kontext | gering | hoch |
| UT-03 | Person mit eigenem Webshop | hoch | mittel |

## **3. Aufgaben**

Jede:r durchläuft dieselben sechs Aufgaben (die Kernflüsse der Anwendung):

1. Anmelden.
2. Ein Produkt anlegen.
3. Dem Produkt einen **Fixpreis** zuweisen.
4. Eine **Formel**-Strategie einrichten.
5. Einen **KI-Vorschlag** einholen und ansehen.
6. Die **Preishistorie** des Produkts öffnen.

Alle drei Testpersonen haben alle sechs Aufgaben abgeschlossen – teils mit
Nachfragen und Umwegen, aber ohne Eingriff durch die Beobachterin.

## **4. Beobachtungen pro Testperson (Auszug Think-aloud)**

### UT-01 – ohne IT-Hintergrund

- Produkt anlegen gelang flüssig; das Feld **Kontext** löste eine Pause aus:
  *„Was soll ich da reinschreiben? Sieht das ein Kunde?"* → Finding **F2**.
- Fixpreis war sofort klar.
- Bei der Formel zögerte die Person stark: *„`cost_price`, was ist das –
  muss ich da Englisch programmieren?"* → Finding **F1**. Mit den
  Token-Buttons kam sie dann zum Ziel.
- Den **Preisgraph** öffnete sie freiwillig und kommentierte: *„Ah, jetzt
  sehe ich, was die Formel macht."* (positiv).

### UT-02 – IT-affin, ohne E-Commerce

- Formel-Syntax war für diese Person kein Problem.
- Stolperte ebenfalls am **Kontext**-Feld (Zweck unklar) → **F2**.
- Testete die Anwendung am Smartphone und bemängelte die **mobile
  Bedienung** von Slidern und Formel-Editor → Finding **F3**.
- Lobte ausdrücklich die **Prompt-Preview**: *„Gut, dass ich sehe, was an
  die KI rausgeht, bevor ich klicke."* (positiv).

### UT-03 – mit eigenem Webshop

- Ging die Aufgaben routiniert durch, dachte in echten Szenarien
  (Feierabend-Aufschlag, Lagerräumung).
- Formelvariablen wirkten zunächst technisch → **F1**; mit dem
  **Fancy-Formel-Button** war die Person zufrieden.
- Beim KI-Vorschlag: *„Die Formel würde ich nochmal selbst prüfen, bevor
  ich sie scharf schalte."* – deckt sich mit dem Human-in-the-Loop-Design.
- Verstand das **KI-Badge** in der Historie sofort.

## **5. Konsolidierte Findings**

| \# | Finding | UT-01 | UT-02 | UT-03 | Kategorie | Priorität | Entscheidung |
| :---- | :---- | :---: | :---: | :---: | :---- | :---- | :---- |
| F1 | Formel-Syntax für Nicht-Programmierer:innen schwer zugänglich – Variablennamen wie `cost_price` wirken technisch | ✓ |  | ✓ | Usability | Mittel | **Fix** – Token-Buttons im Formel-Editor sichtbar gemacht, Fancy-Formel-Button ergänzt |
| F2 | Kontext-Feld beim Produkt unklar – Testpersonen wussten nicht, wofür der Freitext verwendet wird | ✓ | ✓ |  | Verständlichkeit | Mittel | **Fix** – Beschriftung präzisiert, Hinweis ergänzt, dass der Text an die KI übergeben wird |
| F3 | Mobile-Ansicht schlecht bedienbar – Slider und Formel-Editor funktionieren auf kleinen Bildschirmen nicht sauber |  | ✓ |  | Usability | Niedrig | **Wontfix** – Mobile-Layout out-of-scope laut `requirements.md` FR-38; Demo-Zielumgebung ist Desktop-Browser |

Keiner der drei Tests hat einen funktionalen **Bug** erzeugt – die Findings
sind Usability-/Verständnis-Themen. (Der einzige Bug des Projekts, BUG-001,
stammt aus dem Co-Testing im Nacht-Sprint, nicht aus den User-Tests.)

## **6. Positive Rückmeldungen (wiederkehrend)**

- Der **Simulator** mit Slidern wirkte auf alle drei greifbar und gut
  verständlich.
- Der **Preisgraph** wurde spontan als „der beste Einstieg" bezeichnet,
  weil er abstrakte Formeln visuell erfahrbar macht.
- Die **Prompt-Preview** vor dem KI-Aufruf schuf Vertrauen.
- Die **Historie mit KI-Badge** verstanden alle drei auf den ersten Blick.

## **7. Antworten auf die Kernfragen (Tendenzen)**

- **Vertrauen in den KI-Vorschlag:** zwei von drei vertrauten dem Vorschlag
  nur eingeschränkt („ich würde die Formeln immer nochmal prüfen"). Das
  bestätigt das Human-in-the-Loop-Design.
- **Einsatz in einem echten Shop:** zwei von drei würden das Tool als
  Unterstützung einsetzen, sofern es an einen echten Shop angebunden ist.
  Eine Testperson war zurückhaltender.

## **8. Abgeleitete Maßnahmen**

| Aus Finding | Maßnahme | Status |
| :---- | :---- | :---- |
| F1 | Token-Buttons prominent, Fancy-Formel-Button | umgesetzt |
| F2 | Kontext-Feld neu beschriftet, KI-Hinweis ergänzt | umgesetzt |
| F3 | Mobile-Optimierung | bewusst nicht umgesetzt (Wontfix, FR-38) |

## **9. Reflexion zur Methode**

Drei Personen sind für einen Prototyp eine tragfähige Stichprobe: Die
unterschiedlichen Profile haben an unterschiedlichen Stellen gestolpert
(UT-01 an der Formel, UT-02 an Mobile, alle am Kontext-Feld) und zusammen
ein breiteres Bild ergeben als drei ähnliche Tester:innen. Für eine zweite
Iteration wäre eine weitere Runde nach Umsetzung der Fixes sinnvoll, um die
Wirkung der Änderungen zu verifizieren.
