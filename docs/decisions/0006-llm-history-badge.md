# ADR-0006: Semantik des KI-Badges in der Preishistorie

**Status:** Akzeptiert (2026-04-22)
**Datum:** 2026-04-22

## Kontext

Die Preishistorie (`price_history`) ist append-only und dient als
Audit-Trail. Jeder Eintrag trägt das Flag `is_llm_suggestion`, das
in der UI als Badge *KI-Vorschlag* gerendert wird. Mit der Funktion
„Per KI vorschlagen" (Fix- oder Formel-Vorschlag per Gemini) im
Strategie-Modal stellte sich die Frage, **wann genau** ein
History-Eintrag als KI-generiert gilt.

Aufgefallen ist das Thema als Bug: der Auto-Snapshot bei
`PUT /products/{id}/strategy` setzte `is_llm_suggestion` hart auf
`False` – auch wenn der gespeicherte Wert direkt aus dem KI-Vorschlag
stammte. Damit verfehlten KI-Übernahmen die Transparenzpflicht aus
Art. 50 AI Act (vgl. `docs/compliance.md`, Abschnitt *EU AI Act*).

Denkbare Auslegungen für die Semantik:

1. **Session-basiert:** Jeder Speicher-Vorgang nach einem `askAi()`-
   Aufruf wird als KI-generiert markiert.
2. **Wert-basiert:** Nur Einträge, deren gespeicherter Wert
   unverändert aus der KI-Antwort stammt, sind KI-generiert.
3. **Explizite User-Aktion:** Zwei getrennte Speichern-Buttons
   („mit KI speichern" / „manuell speichern").

## Entscheidung

**Variante 2.** Der Badge wird genau dann gesetzt, wenn der
gespeicherte Wert unverändert aus der KI-Antwort übernommen wurde.
Sobald der User den Fix-Input, den Formel-Input oder einen
Token-Button bedient, fällt das Flag zurück auf `false`.

Technisch:

- Frontend führt im Strategie-Modal das Flag `aiUsed`. Es wird beim
  Öffnen und beim Abbrechen auf `false` gesetzt, nach erfolgreicher
  KI-Antwort auf `true`, und über `@input` an beiden Inputfeldern
  sowie in `insertToken()` zurück auf `false`.
- Beim Speichern geht es als `from_llm` im PUT-Body mit.
- Backend übernimmt den Wert in `PriceHistory.is_llm_suggestion`
  des automatisch erzeugten Snapshots. Default ist `false`, damit
  Clients ohne Kenntnis des Felds (z. B. Tests) das alte Verhalten
  behalten.

## Konsequenzen

- ➕ Audit-Trail unterscheidet zuverlässig zwischen reiner
  KI-Übernahme und KI-gestützter Eigenentscheidung – das ist genau
  die Grenze, die Art. 50 AI Act adressiert.
- ➕ UI bleibt schlank: ein Speichern-Button, das Flag wird aus dem
  Verhalten abgeleitet.
- ➕ Kompatibel mit dem bereits vorhandenen Badge-Rendering in
  `frontend/pages/history.html` – kein zusätzliches UI-Element nötig.
- ➖ Die Flag-Logik liegt im Frontend, das Backend vertraut dem
  übergebenen `from_llm`. Ein manipulierter Client könnte falsche
  Werte senden. Für den Prototyp-Scope (interner Login, Mock-Daten)
  akzeptabel; produktiv wäre ein serverseitiger Hash-Abgleich des
  zuletzt ausgelieferten Vorschlags angebracht.
- ➖ Token-Button-Klicks setzen das Flag zurück, auch wenn der User
  den Vorschlag nur strukturell umarrangiert. Akzeptiert: „unverändert"
  ist die defensivste Definition und vermeidet Streit darüber, was
  noch eine kosmetische Anpassung ist.

## Alternativen

- **Variante 1 (Session-basiert):** Würde alle Einträge nach einem
  KI-Klick als KI-generiert markieren – auch komplett umgeschriebene
  Formeln. Entwertet den Audit-Trail.
- **Variante 3 (zwei Buttons):** Verlagert die semantische Entscheidung
  auf den User und bläht die UI auf. Für Demo und Prototyp Overkill.
- **Diff-/Hash-basierte Prüfung serverseitig:** Genauer und nicht
  manipulierbar, für einen Studienprototyp aber Overkill und in der
  Frontend-zentrierten Wertaufbereitung schwierig sauber abzubilden.

## Verweise

- [`docs/use-cases.md`](../use-cases.md) → UC-5 (Preisstrategie durch
  KI vorschlagen lassen)
- [`docs/compliance.md`](../compliance.md) → Abschnitt *EU AI Act*
- [`docs/data-model.md`](../data-model.md) → Tabelle `price_history`,
  Spalte `is_llm_suggestion`
