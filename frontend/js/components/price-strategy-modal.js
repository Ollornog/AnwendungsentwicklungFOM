// Modal fuer die Preis-Strategie pro Produkt.
// - Fixpreis oder Formel
// - Optional KI-Vorschlag mit Online-Recherche
// - Nach KI-Abfrage: sichtbarer Prompt + Reasoning (Transparenz)
// - Insert-Buttons fuegen Variablen/Operatoren an Cursor-Position ein
document.addEventListener('alpine:init', () => {
  // Tokens, die das Formel-Eingabefeld per Knopfdruck einfuegen kann.
  const FORMULA_TOKENS = [
    { label: 'cost_price', insert: 'cost_price', kind: 'var' },
    { label: 'competitor', insert: 'competitor_price', kind: 'var' },
    { label: 'monthly_demand', insert: 'monthly_demand', kind: 'var' },
    { label: 'start_stock', insert: 'start_stock', kind: 'var' },
    { label: 'stock', insert: 'stock', kind: 'var' },
    { label: 'usage', insert: 'usage', kind: 'var' },
    { label: 'hour', insert: 'hour', kind: 'var' },
    { label: 'day', insert: 'day', kind: 'var' },
    { label: '+', insert: ' + ', kind: 'op' },
    { label: '−', insert: ' - ', kind: 'op' },
    { label: '×', insert: ' * ', kind: 'op' },
    { label: '÷', insert: ' / ', kind: 'op' },
    { label: '^', insert: ' ** ', kind: 'op' },
    { label: '%', insert: ' % ', kind: 'op' },
    { label: '(', insert: '(', kind: 'op' },
    { label: ')', insert: ')', kind: 'op' },
    { label: '>', insert: ' > ', kind: 'cmp' },
    { label: '>=', insert: ' >= ', kind: 'cmp' },
    { label: '<', insert: ' < ', kind: 'cmp' },
    { label: '<=', insert: ' <= ', kind: 'cmp' },
    { label: '==', insert: ' == ', kind: 'cmp' },
  ];

  Alpine.data('priceStrategyModal', () => ({
    open: false,
    product: null,
    target: 'fix',
    amount: '',
    expression: '',
    useAi: false,
    online: false,
    aiLoading: false,
    aiPrompt: '',
    aiReasoning: '',
    saving: false,
    error: '',
    tokens: FORMULA_TOKENS,

    openFor(product) {
      this.product = product;
      this.error = '';
      this.aiPrompt = '';
      this.aiReasoning = '';
      this.useAi = false;
      this.online = false;
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
      try {
        const res = await window.api.post(
          `/products/${this.product.id}/strategy/suggest`,
          { target: this.target, online: !!this.online },
        );
        if (res.target === 'fix' && res.amount != null) {
          this.amount = res.amount;
        } else if (res.target === 'formula' && res.expression) {
          this.expression = res.expression;
        }
        this.aiReasoning = res.reasoning || '';
        this.aiPrompt = res.prompt || '';
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
