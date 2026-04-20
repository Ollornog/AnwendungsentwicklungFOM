// Modal fuer die Preis-Strategie pro Produkt.
// - Fixpreis oder Formel
// - Optional KI-Vorschlag mit Online-Recherche
// - Nach KI-Abfrage: sichtbarer Prompt + Reasoning (Transparenz)
// - Insert-Buttons fuegen Variablen/Operatoren an Cursor-Position ein
document.addEventListener('alpine:init', () => {
  // Token-Gruppen fuer das Formel-Eingabefeld. Jede Gruppe wird im UI
  // in einer eigenen Zeile gerendert, damit die Kategorien auf einen Blick
  // zu trennen sind.
  const TOKEN_GROUPS = [
    {
      kind: 'var',
      label: 'Variablen',
      tokens: [
        { label: 'cost_price', insert: 'cost_price' },
        { label: 'competitor', insert: 'competitor_price' },
        { label: 'monthly_demand', insert: 'monthly_demand' },
        { label: 'start_stock', insert: 'start_stock' },
        { label: 'stock', insert: 'stock' },
        { label: 'usage', insert: 'usage' },
        { label: 'hour', insert: 'hour' },
        { label: 'day', insert: 'day' },
        { label: 'weekday', insert: 'weekday' },
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
      label: 'Funktionen',
      tokens: [
        { label: 'sqrt(', insert: 'sqrt(' },
        { label: 'pow(', insert: 'pow(' },
        { label: 'abs(', insert: 'abs(' },
        { label: 'min(', insert: 'min(' },
        { label: 'max(', insert: 'max(' },
        { label: 'round(', insert: 'round(' },
        { label: 'floor(', insert: 'floor(' },
        { label: 'ceil(', insert: 'ceil(' },
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
    saving: false,
    error: '',
    tokenGroups: TOKEN_GROUPS,

    openFor(product) {
      this.product = product;
      this.error = '';
      this.aiPrompt = '';
      this.aiReasoning = '';
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
          this.amount = res.amount;
        } else if (res.target === 'formula' && res.expression) {
          this.expression = res.expression;
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

    async save() {
      if (!this.product) return;
      let payload;
      if (this.target === 'fix') {
        const amt = Number(this.amount);
        if (!Number.isFinite(amt) || amt < 0) {
          this.error = 'Fixpreis muss eine Zahl >= 0 sein.';
          return;
        }
        payload = { kind: 'fix', config: { amount: amt } };
      } else {
        const expr = (this.expression || '').trim();
        if (!expr) {
          this.error = 'Formel darf nicht leer sein.';
          return;
        }
        payload = { kind: 'formula', config: { expression: expr } };
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
