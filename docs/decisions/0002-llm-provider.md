# ADR 0002: LLM-Provider

- **Status:** Akzeptiert (vorläufig, Prototyp)
- **Datum:** 2026-04-19
- **Entscheider:** Projektteam

## Kontext
ADR 0001 ließ die Wahl unter den verbreiteten Cloud-LLM-APIs offen. Für den Prototyp brauchen wir einen einfach zugänglichen Endpoint mit Free-Tier oder günstigen Preisen, damit alle Teammitglieder mit API-Keys entwickeln können.

## Entscheidung
Für den Prototyp verwenden wir die **Google Gemini API**.

## Begründung
- Kostenloser Entwickler-Tier verfügbar – reicht für Demo und Entwicklung.
- Einfach über Google AI Studio API-Keys erhältlich.
- JSON-Structured-Output wird unterstützt (wichtig für unsere validierte Preis-Antwort).
- Ausreichende Qualität für den geforderten Funktionsumfang.

## Konsequenzen
- LLM-Aufrufe werden serverseitig gegen die Gemini-API ausgeführt.
- API-Key liegt in `.env` als `GEMINI_API_KEY`, nie im Code (siehe Leitprinzip 6).
- Es werden ausschließlich Produkt-Whitelist-Felder gesendet (siehe Leitprinzip 5, `docs/compliance.md`).
- Für den Produktivbetrieb wären zu klären: Auftragsverarbeitungsvertrag mit Google, Datenstandort (EU), Opt-out für Trainingsnutzung. Im Prototyp nur dokumentiert, nicht umgesetzt.

## Alternativen
- **OpenAI GPT-4o/mini:** weit verbreitet, jedoch Kostenrahmen für das Team unklar und kein permanenter Free-Tier.
- **Anthropic-API:** sehr gute Antwortqualität, aber im Team zunächst kein kostenloser Zugang.
- **Lokales Open-Source-Modell (z. B. Llama über Ollama):** kein externer Datenabfluss, aber hoher Betriebsaufwand und begrenzte Rechenleistung auf Entwickler-Geräten.

## Offene Punkte
- Kostenüberwachung: Free-Tier-Limits verfolgen, bei Bedarf bezahlten Tarif prüfen.
- Modell-Variante (`gemini-2.x-flash` vs. `gemini-2.x-pro`) final wählen – abhängig von Qualität und Latenz.
