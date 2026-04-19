// Modal fuer die Preis-Strategie pro Produkt.
// Ziel: Fixpreis ODER Formel, optional per KI vorschlagen (mit optional
// Online-Recherche). Nach "Speichern" wird via PUT /products/{id}/strategy
// die Strategie persistiert und das Event "strategy-saved" dispatcht.
document.addEventListener('alpine:init', () => {
  Alpine.data('priceStrategyModal', () => ({
    open: false,
    product: null,
    target: 'fix', // 'fix' | 'formula'
    amount: '',
    expression: '',
    useAi: false,
    online: false,
    aiLoading: false,
    aiReasoning: '',
    saving: false,
    error: '',

    // Oeffnen mit vorhandener Strategie, damit man nachjustieren kann.
    openFor(product) {
      this.product = product;
      this.error = '';
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
        // rule/llm/keine: Dialog zeigt Fixpreis-Tab, User kann aber wechseln.
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

    async askAi() {
      if (!this.product) return;
      this.aiLoading = true;
      this.error = '';
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
            detail: { productId: this.product.id, strategy: saved, aiReasoning: this.aiReasoning },
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
