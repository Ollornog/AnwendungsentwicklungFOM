document.addEventListener('alpine:init', () => {
  Alpine.data('strategyPicker', (productId, initial) => ({
    productId,
    kind: initial?.kind || 'fix',
    config: initial?.config || { amount: 0 },
    loading: false,
    error: '',
    saved: false,

    setKind(kind) {
      this.kind = kind;
      this.saved = false;
      if (kind === 'fix') this.config = { amount: 0 };
      if (kind === 'formula') this.config = { expression: 'cost_price * 1.3' };
      if (kind === 'rule') this.config = { rules: [{ when: 'stock < 10', then: 'cost_price * 1.5' }], fallback: 'cost_price * 1.2' };
      if (kind === 'llm') this.config = { prompt_template: 'Schlage einen Preis für {name} in {category} vor. Kosten: {cost_price}. Wettbewerb: {competitor_price}. Antworte als JSON.' };
    },

    async save() {
      this.loading = true;
      this.error = '';
      this.saved = false;
      try {
        await window.api.put(`/products/${this.productId}/strategy`, {
          kind: this.kind,
          config: this.config,
        });
        this.saved = true;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
  }));
});
