# **Demo-Skript (Soll-Ablauf des Screen-Recordings)**

Schritt-für-Schritt-Ablauf für die Bildschirmaufnahme im Demo-Block des
Präsentationsvideos (Block 5 in [`video-script.md`](./video-script.md)).
Der **Sprechertext** liegt im Drehbuch bzw. im finalen Skript; dieses
Dokument beschreibt ausschließlich, **was auf dem Bildschirm passiert**,
damit die Aufnahme den tatsächlichen Soll-Ablauf zeigt und kein Klick fehlt.

Die fünf Szenen entsprechen den Demo-Abschnitten 5a–5e und den Use Cases
aus [`use-cases.md`](./use-cases.md).

## **Vorbereitung (vor der Aufnahme)**

1. Datenbank auf Seed-Stand bringen: *Einstellungen → Datenbank
   zurücksetzen* (UC-16). Garantiert reproduzierbare Mock-Produkte.
2. Mit einem normalen Team-/Demo-Account einloggen (kein Admin nötig, hält
   den Fokus auf den Kern-Flows).
3. Gültigen Gemini-API-Key hinterlegt lassen (für Szene 5c). Ohne Key
   liefert die KI bewusst HTTP 503 – das wäre eine andere Demo.
4. Browser im Vollbild, Lesezeichenleiste aus, Zoom 100–110 %, Cursor gut
   sichtbar. Demo-Disclaimer-Hinweis im UI nicht wegklicken.
5. Eine ruhige Maus führen; an den markierten Stellen kurz innehalten,
   damit der Schnitt Luft hat.

## **Szene 5a – Produkt anlegen + Fixpreis** *(Sprecher: Tamara · UC-1, UC-4)*

| Schritt | Aktion | Sichtbar / Erwartet |
| :---- | :---- | :---- |
| 1 | Produktliste öffnen | Seed-Produkte als Liste |
| 2 | *Produkt hinzufügen* klicken | Modal öffnet sich |
| 3 | Felder ausfüllen: Name, Kategorie, Einkaufspreis, Wettbewerbspreis, Lager, Verbrauch/Monat, **Kontext-Freitext** | Eingaben sichtbar; kurz auf das Kontext-Feld zeigen (Brücke zur KI) |
| 4 | *Speichern* | Neues Produkt erscheint oben in der Liste |
| 5 | In der Produktzeile *Preis* → Strategie-Modal | Modal mit Auswahl *Fixpreis / Formel* |
| 6 | *Fixpreis* wählen, `49,99` eintragen, *Speichern* | Strategie gesetzt, Verkaufspreis = 49,99 € |

## **Szene 5b – Formel-Strategie** *(Sprecher: Daniel · UC-4)*

| Schritt | Aktion | Sichtbar / Erwartet |
| :---- | :---- | :---- |
| 1 | Strategie-Modal erneut öffnen, auf **Formel** umschalten | Formel-Editor mit Token-Buttons |
| 2 | Formel mit Token-Buttons bauen, z. B. `cost_price * 1.8 + (hour >= 18) * 2` | Ausdruck im Editor |
| 3 | Live-Preview beobachten | Berechneter Verkaufspreis erscheint sofort |
| 4 | Kurz auf die Variablen-Übersicht rechts zeigen | Liste verfügbarer Variablen/Funktionen |
| 5 | Zur Demonstration einen Tippfehler einbauen, *Speichern* | 422-Fehlermeldung; **alte Strategie bleibt aktiv** (kein Unsinn-Preis) |
| 6 | Fehler korrigieren, *Speichern* | Formel-Strategie aktiv |

## **Szene 5c – KI-Vorschlag + Transparenz** *(Sprecher: Okan · UC-5)*

| Schritt | Aktion | Sichtbar / Erwartet |
| :---- | :---- | :---- |
| 1 | Im Strategie-Modal Checkbox **Per KI vorschlagen** aktivieren | Prompt-Preview-Bereich wird sichtbar |
| 2 | Kurz auf den **Prompt-Text** zoomen | Vollständiger Prompt vor dem Call sichtbar (Art. 50 AI Act) |
| 3 | *KI fragen* klicken | Vorschlag (Fix oder Formel) **mit Begründung** erscheint |
| 4 | Vorschlag **unverändert** übernehmen, *Speichern* | Strategie gesetzt |
| 5 | Kurz auf die Historie verweisen | Eintrag trägt das **KI-Badge** (unveränderte Übernahme) |

## **Szene 5d – Simulator-Dynamik** *(Sprecher: Sven · UC-7)*

| Schritt | Aktion | Sichtbar / Erwartet |
| :---- | :---- | :---- |
| 1 | Simulator-Bereich sichtbar machen | Globale Slider Stunde/Tag, pro Produkt Lager/Nachfrage |
| 2 | **Stunden-Slider** über 18 Uhr ziehen | Preis springt sichtbar um +2 € (Formel-Bedingung greift) |
| 3 | **Lager-Slider** bewegen | Preis rechnet live nach |
| 4 | **Nachfrage-Slider** bewegen | Preis rechnet live nach |
| 5 | Play-Button (▶) kurz antippen, dann pausieren | Zeit tickt stundenweise, Preise laufen mit; keine Backend-Calls |

## **Szene 5e – Preisgraph + Historie** *(Sprecher: Kayathiri · UC-8, UC-10)*

| Schritt | Aktion | Sichtbar / Erwartet |
| :---- | :---- | :---- |
| 1 | In der Produktzeile *Graph* öffnen | Graph-Modal |
| 2 | Variable **Zeit gesamt (Monat)** wählen | Kurve über 672 Stunden rendert |
| 3 | Kurz auf Tiefs und Spitzen zeigen | Tagesrhythmus der Formel sichtbar |
| 4 | Graph schließen, *Historie* desselben Produkts öffnen | Liste der Einträge |
| 5 | Auf einen Eintrag mit **KI-Badge** zeigen | Zeitstempel, Strategie, Inputs, Begründung, KI-Badge (Audit-Trail) |

## **Aufnahme-Hinweise**

- Auflösung 1080p, 30 fps, eine durchgehende Aufnahme pro Szene (Schnitt
  später in DaVinci Resolve).
- Maus nicht zappeln lassen; nach jedem *Speichern* kurz warten, bis die
  UI reagiert hat.
- Keine echten Daten – die Mock-Produkte und der Demo-Disclaimer machen den
  Prototyp-Charakter sichtbar (vgl. `legal.html`).
- Gesamtlänge des Demo-Blocks ca. 4:30 (5a 0:45 · 5b 1:00 · 5c 1:00 ·
  5d 0:45 · 5e 1:00).
