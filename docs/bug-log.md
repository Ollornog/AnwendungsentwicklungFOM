**Bug Log**

| ID | Titel | Priorität | Status | Gefunden |
| :---- | :---- | :---- | :---- | :---- |
| BUG-001 | KI-Markierung fehlt in Preishistorie | Mittel | ✅ Behoben | T4 |

## **BUG-001 – KI-Markierung fehlt in Preishistorie**

**Komponente:** `schemas.py`, `routers/products.py`, `web/static/js/price-strategy-modal.js`, `web/templates/products.html` **Gefunden von:** Co-Tester während Nacht-Sprint **Betroffener Use Case:** UC-5 „KI-Vorschlag einholen und übernehmen"

### Beschreibung

History-Einträge, die durch Auto-Snapshot beim Strategie-Wechsel entstehen, trugen das KI-Badge (`is_llm_suggestion`) nie – auch dann nicht, wenn der gespeicherte Wert unverändert aus der Gemini-Antwort stammte. Der Audit-Trail konnte damit nicht zwischen „User hat Vorschlag übernommen" und „User hat manuell eingegeben" unterscheiden.

### Reproduktion (vor Fix)

1. Produkt öffnen → Strategie-Modal  
2. „KI-Vorschlag" klicken → Gemini liefert Fix- oder Formel-Vorschlag  
3. Vorschlag unverändert übernehmen → speichern  
4. History des Produkts öffnen  
5. **Erwartet:** neuer Eintrag mit KI-Badge  
6. **Tatsächlich:** neuer Eintrag ohne KI-Badge

### Root Cause

Beim Auto-Snapshot im `PUT /products/{id}/strategy` wurde `PriceHistory.is_llm_suggestion` hart auf `False` gesetzt. Das Frontend übergab kein Signal, ob der Wert KI-generiert war.

### Fix

- `schemas.StrategyUpsert`: optionales Feld `from_llm: bool = False`  
- `routers/products.py`: Auto-Snapshot übernimmt `from_llm` in `PriceHistory.is_llm_suggestion`  
- `price-strategy-modal.js`: internes Flag `aiUsed`  
  - `open()` \+ `cancel()` → `false`  
  - nach erfolgreichem `askAi()` → `true`  
  - `@input` auf Fix-/Formel-Input und Token-Buttons → `false`  
  - `save()` sendet `from_llm: aiUsed`  
- `products.html`: `@input="aiUsed = false"` an beiden Eingabefeldern  
- `docs/use-cases.md`: UC-5 Nachbedingung angepasst

### Verifikation

- Manuell: Re-Test der obigen 6 Schritte → Badge erscheint  
- Gegenprobe: nach `askAi()` im Input tippen → Badge erscheint **nicht** (korrekt, da User den Vorschlag editiert hat)  
- Siehe Testfall **TC-LLM-01** in `docs/test-matrix.md`

### Relevanz

Betrifft die Nachvollziehbarkeit KI-gestützter Entscheidungen (Art. 50 AI Act, Art. 5 Abs. 2 DSGVO – Rechenschaftspflicht). Ohne korrektes Badge wäre der Audit-Trail unvollständig.  
