# Compliance (Kurzfassung)

Studentischer Prototyp; kein Produktivsystem. Die öffentliche
Kurzfassung für Besucher steht unter `/pages/legal.html`, die interne
Langfassung (VVT, DPIA, TOMs) hinter Login unter
`/pages/compliance.html`. Dieses Dokument fasst die getroffenen
Abstimmungen für die Modulabgabe zusammen.

## Scope-Abgrenzung

- Verarbeitet werden ausschließlich **Produkt-Stammdaten** (Name,
  Kategorie, Preise, Lagergröße, Nachfrage, Kontext-Freitext) und
  **Login-Konten** (Username, argon2id-Hash, Rolle).
- **Keine Endkundendaten, kein personalisiertes Pricing, keine
  Tracking-Cookies.** Die Anwendung richtet sich an einen Shop-
  Admin und ist hinter Login.
- Alle Produktdaten sind Mock-Daten; die UI weist auf den
  Demo-Charakter hin.

## DSGVO – Bezug auf die Kernartikel

| Artikel | Thema | Status |
| --- | --- | --- |
| Art. 5 | Grundsätze (Rechtmäßigkeit, Zweckbindung, Datenminimierung) | ✅ Umgesetzt – Prompt-Whitelist, Mock-Daten |
| Art. 6 Abs. 1 lit. f | Berechtigtes Interesse (Studienbetrieb) | ✅ Dokumentiert |
| Art. 13 | Informationspflicht | ✅ `/pages/legal.html` |
| Art. 22 | Keine ausschließlich automatisierte Entscheidung | ✅ Human-in-the-Loop, Snapshot nur auf Klick |
| Art. 28 | Auftragsverarbeitung (Google/Gemini) | 🔶 Nur Prototyp – Google Cloud DPA genügt für Demo, produktives AVV ausstehend |
| Art. 30 | Verzeichnis von Verarbeitungstätigkeiten | ✅ Interne Langfassung `/pages/compliance.html` |
| Art. 32 | TOMs | ✅ Tabelle in [`security.md`](./security.md) |
| Art. 35 | DSFA | 🔶 Kurzprüfung (nicht erforderlich) dokumentiert, Langfassung fürs Produktivum |
| Art. 44 ff. | Drittlandtransfer (Gemini/US) | ✅ SCC-Grundlage, nur Produktdaten im Prompt |
| Art. 77 | Beschwerderecht | ✅ In `/pages/legal.html` genannt |

## EU AI Act

Das LLM-gestützte Preisvorschlag-Feature ist gemäß Art. 50 AI Act
ein **KI-System mit begrenztem Risiko** (Transparenzpflicht):

- KI-Vorschläge tragen in UI und Historie das Badge
  *KI-Vorschlag* (Leitprinzip 4).
- Der an das LLM geschickte Prompt ist **vor dem Klick** in der UI
  einsehbar (`prompt-preview`-Endpoint).
- Menschliche Aufsicht gemäß Art. 14 AI Act sinngemäß: Snapshot nur
  nach Bestätigung. Kein Auto-Apply.
- Die Einordnung als „begrenztes Risiko" (statt Hochrisiko) ist im
  internen Compliance-Bereich begründet.
- Art. 4 (KI-Kompetenz): alle Teammitglieder im FOM-Studiengang
  Wirtschaftsinformatik; namentliche Nennung in
  `/pages/compliance.html`.

## UWG & PAngV

| Thema | Status |
| --- | --- |
| Irreführung durch Preis (§ 5 UWG) | 🔶 Sanity-Check: negative Preise werden geblockt; Plausibilitätsprüfung auf Formel-Ergebnisse empfohlen |
| Grundpreis-/Endpreis-Angabe (PAngV) | 📝 Nicht im Scope – kein Endkundenverkauf |
| MwSt.-Ausweis | 📝 Nicht im Scope – nur interne Preisoptimierung |

## NIS-2

Der Studienbetrieb fällt nicht unter NIS-2 (keine wesentliche/wichtige
Einrichtung i. S. d. NIS2UmsuCG). Die in der Richtlinie geforderten
Mindestmaßnahmen (Risikomanagement, Zugriffsbeschränkung, Incident-
Nachvollzug, Lieferkette) werden orientierungshalber umgesetzt und
sind in [`security.md`](./security.md) belegt.

## Verweise

- Öffentliche Kurzfassung: `/pages/legal.html` (Impressum,
  Datenschutz, Betroffenenrechte, AI-Einstufung, Demo-Disclaimer)
- Interne Langfassung: `/pages/compliance.html` (VVT, DPIA,
  AVV-Bewertung, TOMs, NIS-2-Check, KI-Kompetenz)
- Leitprinzipien: [`../CLAUDE.md`](../CLAUDE.md) §3
