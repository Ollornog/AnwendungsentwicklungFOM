# ADR-0002: LLM-Provider

**Status:** Akzeptiert (2026-04-19)
**Datum:** 2026-04-19

## Kontext

Für den KI-Preisvorschlag benötigen wir einen LLM-Endpoint. ADR 0001
hatte die konkrete Wahl offengelassen. Anforderungen:

- Kostenlose Nutzung für den Demo-Umfang (vier Teammitglieder,
  Abschluss-Demo).
- JSON-Structured-Output für validierbare Antworten (Preis oder
  Formel + Begründung).
- Austauschbarkeit – keine Tiefen-Kopplung an den Anbieter.

## Entscheidung

Für den Prototyp wird die **Google Gemini API** verwendet.
Architektonisch ist der Anbieter austauschbar: der Aufruf ist
komplett in `backend/app/llm.py` gekapselt, die Router arbeiten gegen
`suggest_price` / `suggest_strategy` / `suggest_competitor_prices`.

## Konsequenzen

- ➕ Kostenloser Developer-Tier reicht für Entwicklung und Demo.
- ➕ `response_mime_type=application/json` + Prompt-Templates liefern
  stabil parsebare Antworten.
- ➕ Key kann über `.env` **oder** per UI (Tabelle `app_settings`)
  gesetzt werden – DB-Wert gewinnt, kein Service-Restart nötig.
- ➖ Drittlandtransfer in die USA. Rechtsgrundlage SCCs;
  Zweckbindung durch Whitelist-Prompt (keine Kundendaten).
- ➖ Wechsel zu einem anderen Anbieter erfordert Anpassungen in
  `llm.py` (z. B. HTTP-Client, Auth-Header, Response-Schema).

## Alternativen

- **OpenAI GPT-4o/mini:** breit etabliert, aber kein permanenter
  Free-Tier und Kostenrahmen für das Team unklar.
- **Anthropic-API:** sehr gute Antwortqualität, im Team aber kein
  kostenloser Zugang vorhanden.
- **Lokales Modell via Ollama (Llama/Mistral):** kein externer
  Datenabfluss, dafür Hardware-Anforderungen auf Entwickler-Laptops
  und deutlich mehr Betriebsaufwand – für eine Demo überdimensioniert.
