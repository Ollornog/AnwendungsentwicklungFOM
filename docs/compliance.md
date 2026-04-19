# Compliance

Kurzer Überblick, wie das Projekt Datenschutz, KI-Regulierung und Preisrecht adressiert. Prototyp-Fokus: konzeptionell abdecken, produktiver Ausblick kurz benannt.

## 1. Datenschutz (DSGVO)
- Durch **Leitprinzip 1** (keine personenbezogenen Daten im Scope) liegt keine nennenswerte Verarbeitung personenbezogener Daten vor. Einzige Ausnahme: Login-Daten des Shop-Betreibers – Rechtsgrundlage Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung).
- Produktiv-Ausblick: Würde das Tool personalisierte Preise gegenüber Endkunden erzeugen, wären **Art. 22 DSGVO** (automatisierte Einzelfallentscheidung) und **Art. 13** (Informationspflichten) relevant. Bewusst nicht im Scope.
- LLM-Nutzung produktiv: Mit dem LLM-Anbieter wäre ein **Auftragsverarbeitungsvertrag nach Art. 28 DSGVO** erforderlich. Bei US-Anbietern zusätzlich eine Drittlandtransfer-Grundlage (EU-US Data Privacy Framework oder EU-Hosting). Für den Prototyp genügt der Hinweis.

## 2. EU AI Act
- Einstufung: KI-System mit **begrenztem Risiko** (kein Hochrisiko-System).
- **Transparenzpflichten nach Art. 50** (ab 2. August 2026) werden durch **Leitprinzip 4** (KI-Vorschläge in UI und Historie sichtbar machen) vorausschauend erfüllt.
- **Menschliche Aufsicht** wird durch **Leitprinzip 3** (Human-in-the-Loop, Bestätigung durch den Betreiber) umgesetzt.

## 3. Preisrecht (UWG / PAngV)
- Im Produktivbetrieb wären die **Preisangabenverordnung** (Gesamtpreise inkl. MwSt., 30-Tage-Regel bei Rabatten) und das **UWG** (Verbot irreführender Preisangaben) einzuhalten.
- Ein einfacher **Sanity-Check im Backend** (Plausibilitätsgrenzen + Abgleich mit Input-Werten) stellt sicher, dass eine LLM-Begründung zum Preis passt und keine Fantasieargumente liefert.
