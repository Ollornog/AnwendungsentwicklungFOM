// Modal fuer die Preis-Strategie pro Produkt.
// - Fixpreis oder Formel
// - Optional KI-Vorschlag mit Online-Recherche
// - Nach KI-Abfrage: sichtbarer Prompt + Reasoning (Transparenz)
// - Insert-Buttons fuegen Variablen/Operatoren an Cursor-Position ein
document.addEventListener('alpine:init', () => {
  // Token-Gruppen fuer das Formel-Eingabefeld. Jede Gruppe wird im UI
  // in einer eigenen Zeile gerendert, damit die Kategorien auf einen Blick
  // zu trennen sind.
  // Variablen in zwei Zeilen: "Produkt" (statisch aus DB) und "Laufzeit"
  // (aendert sich in der Simulation). Damit ist der Zeilenumbruch geplant
  // und visuell sauber, statt mitten im Label umzubrechen.
  const TOKEN_GROUPS = [
    {
      kind: 'var',
      label: 'Produkt',
      tokens: [
        { label: 'cost_price', insert: 'cost_price' },
        { label: 'competitor', insert: 'competitor_price' },
        { label: 'monthly_demand', insert: 'monthly_demand' },
        { label: 'start_stock', insert: 'start_stock' },
      ],
    },
    {
      kind: 'var',
      label: 'Laufzeit',
      tokens: [
        { label: 'stock', insert: 'stock' },
        { label: 'hour', insert: 'hour' },
        { label: 'day', insert: 'day' },
        { label: 'weekday', insert: 'weekday' },
        { label: 'demand', insert: 'demand' },
        { label: 'π', insert: 'pi' },
      ],
    },
    {
      kind: 'op',
      label: 'Operatoren',
      tokens: [
        { label: '+', insert: ' + ' },
        { label: '−', insert: ' - ' },
        { label: '×', insert: ' * ' },
        { label: '÷', insert: ' / ' },
        { label: '^', insert: ' ** ' },
        { label: '%', insert: ' % ' },
        { label: '(', insert: '(' },
        { label: ')', insert: ')' },
        { label: ',', insert: ', ' },
      ],
    },
    {
      kind: 'cmp',
      label: 'Vergleiche',
      tokens: [
        { label: '>', insert: ' > ' },
        { label: '>=', insert: ' >= ' },
        { label: '<', insert: ' < ' },
        { label: '<=', insert: ' <= ' },
        { label: '==', insert: ' == ' },
        { label: 'and', insert: ' and ' },
        { label: 'or', insert: ' or ' },
        { label: 'not', insert: 'not ' },
      ],
    },
    {
      kind: 'fn',
      label: 'Mathe',
      tokens: [
        { label: 'sqrt(', insert: 'sqrt(' },
        { label: 'pow(', insert: 'pow(' },
        { label: 'abs(', insert: 'abs(' },
        { label: 'min(', insert: 'min(' },
        { label: 'max(', insert: 'max(' },
      ],
    },
    {
      kind: 'fn',
      label: 'Rundung',
      tokens: [
        { label: 'round(', insert: 'round(' },
        { label: 'floor(', insert: 'floor(' },
        { label: 'ceil(', insert: 'ceil(' },
      ],
    },
    {
      kind: 'fn',
      label: 'Zyklisch',
      tokens: [
        { label: 'mod(', insert: 'mod(' },
        { label: 'sin(', insert: 'sin(' },
        { label: 'cos(', insert: 'cos(' },
      ],
    },
  ];

  Alpine.data('priceStrategyModal', () => ({
    open: false,
    product: null,
    target: 'fix',
    amount: '',
    expression: '',
    useAi: false,
    online: false,
    fancy: false,
    aiLoading: false,
    aiPrompt: '',
    aiReasoning: '',
    // Gemerkte KI-Vorschlagswerte fuer den Save-Zeitpunkt. Beim
    // Speichern vergleichen wir amount/expression mit diesen Werten;
    // nur bei exakter Uebereinstimmung gilt der Eintrag als KI-Vorschlag
    // und landet mit is_llm_suggestion=true in der Historie. Robust
    // gegen Event-Timing (kein @input-Listener noetig).
    aiSuggestedAmount: null,
    aiSuggestedExpression: null,
    saving: false,
    error: '',
    tokenGroups: TOKEN_GROUPS,

    openFor(product) {
      this.product = product;
      this.error = '';
      this.aiPrompt = '';
      this.aiReasoning = '';
      this.aiSuggestedAmount = null;
      this.aiSuggestedExpression = null;
      this.useAi = false;
      this.online = false;
      this.fancy = false;
      const s = product.strategy;
      if (s && s.kind === 'fix') {
        this.target = 'fix';
        this.amount = s.config?.amount ?? '';
        this.expression = '';
      } else if (s && s.kind === 'formula') {
        this.target = 'formula';
        this.expression = s.config?.expression ?? '';
        this.amount = '';
      } else {
        this.target = 'fix';
        this.amount = '';
        this.expression = '';
      }
      this.open = true;
    },

    cancel() {
      this.open = false;
      this.product = null;
    },

    // Fuegt `text` an der aktuellen Cursor-Position in das
    // referenzierte Input-Element ein und aktualisiert den x-model-Wert.
    insertToken(text) {
      const el = this.$refs.expressionInput;
      if (!el) return;
      const start = el.selectionStart ?? this.expression.length;
      const end = el.selectionEnd ?? this.expression.length;
      const before = this.expression.slice(0, start);
      const after = this.expression.slice(end);
      this.expression = before + text + after;
      // naechster Tick, damit Alpine das Input-Update uebernommen hat.
      this.$nextTick(() => {
        el.focus();
        const pos = before.length + text.length;
        el.setSelectionRange(pos, pos);
      });
    },

    async askAi() {
      if (!this.product) return;
      this.aiLoading = true;
      this.error = '';
      this.aiPrompt = '';
      this.aiReasoning = '';
      const body = {
        target: this.target,
        online: !!this.online,
        fancy: !!this.fancy,
      };

      // 1. Schritt: Preview-Prompt holen und sofort anzeigen, damit der
      //    User sieht, was die KI bekommt, bevor die eigentliche Antwort da ist.
      try {
        const preview = await window.api.post(
          `/products/${this.product.id}/strategy/prompt-preview`,
          body,
        );
        this.aiPrompt = preview.prompt || '';
      } catch (e) {
        // Preview-Fehler blockiert die echte Abfrage nicht.
        console.warn('Prompt-Preview fehlgeschlagen:', e);
      }

      // 2. Schritt: eigentliche LLM-Antwort.
      try {
        const res = await window.api.post(
          `/products/${this.product.id}/strategy/suggest`,
          body,
        );
        if (res.target === 'fix' && res.amount != null) {
          // Als String merken und setzen, damit der Vergleich beim Save
          // robust gegen Number/String-Konversionen im <input type=number> ist.
          const asStr = String(res.amount);
          this.amount = asStr;
          this.aiSuggestedAmount = asStr;
          this.aiSuggestedExpression = null;
        } else if (res.target === 'formula' && res.expression) {
          this.expression = res.expression;
          this.aiSuggestedExpression = res.expression;
          this.aiSuggestedAmount = null;
        }
        this.aiReasoning = res.reasoning || '';
        // Der Prompt aus der Suggest-Response ist autoritativ (falls der
        // Server den Prompt in der Zwischenzeit leicht angepasst hat).
        if (res.prompt) this.aiPrompt = res.prompt;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.aiLoading = false;
      }
    },

    // True, wenn der aktuell sichtbare Wert im Feld unveraendert aus
    // dem letzten KI-Vorschlag stammt. Beim Speichern entscheidet das
    // ueber `from_llm` und damit ueber das KI-Badge in der Historie.
    isFromAi() {
      if (this.target === 'fix') {
        if (this.aiSuggestedAmount == null) return false;
        return String(this.amount).trim() === String(this.aiSuggestedAmount).trim();
      }
      if (this.target === 'formula') {
        if (!this.aiSuggestedExpression) return false;
        return (this.expression || '').trim() === this.aiSuggestedExpression.trim();
      }
      return false;
    },

    async save() {
      if (!this.product) return;
      const fromLlm = this.isFromAi();
      let payload;
      if (this.target === 'fix') {
        const amt = Number(this.amount);
        if (!Number.isFinite(amt) || amt < 0) {
          this.error = 'Fixpreis muss eine Zahl >= 0 sein.';
          return;
        }
        payload = { kind: 'fix', config: { amount: amt }, from_llm: fromLlm };
      } else {
        const expr = (this.expression || '').trim();
        if (!expr) {
          this.error = 'Formel darf nicht leer sein.';
          return;
        }
        payload = { kind: 'formula', config: { expression: expr }, from_llm: fromLlm };
      }
      this.saving = true;
      this.error = '';
      try {
        const saved = await window.api.put(
          `/products/${this.product.id}/strategy`,
          payload,
        );
        window.dispatchEvent(
          new CustomEvent('strategy-saved', {
            detail: { productId: this.product.id, strategy: saved },
          }),
        );
        this.open = false;
        this.product = null;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.saving = false;
      }
    },
  }));
});
