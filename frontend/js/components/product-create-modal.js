// Modal hinter dem '+'-FAB. Liefert beim Speichern ein 'product-created'
// CustomEvent (gleiches Schema wie zuvor das Inline-Formular), damit die
// Liste das neue Produkt direkt einreihen kann.
document.addEventListener('alpine:init', () => {
  Alpine.data('productCreateModal', () => ({
    open: false,
    name: '',
    category: '',
    cost_price: 0,
    stock: 0,
    competitor_price: null,
    monthly_demand: 0,
    daily_usage: 0,
    context: '',
    loading: false,
    error: '',

    show() {
      this.open = true;
      this.error = '';
    },

    cancel() {
      this.open = false;
    },

    reset() {
      this.name = '';
      this.category = '';
      this.cost_price = 0;
      this.stock = 0;
      this.competitor_price = null;
      this.monthly_demand = 0;
      this.daily_usage = 0;
      this.context = '';
    },

    async submit() {
      this.loading = true;
      this.error = '';
      try {
        const created = await window.api.post('/products', {
          name: this.name,
          category: this.category,
          cost_price: Number(this.cost_price),
          stock: Number(this.stock),
          competitor_price:
            this.competitor_price === null || this.competitor_price === ''
              ? null
              : Number(this.competitor_price),
          monthly_demand: Number(this.monthly_demand) || 0,
          daily_usage: Number(this.daily_usage) || 0,
          context: this.context || '',
        });
        window.dispatchEvent(new CustomEvent('product-created', { detail: created }));
        this.reset();
        this.open = false;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
  }));
});
