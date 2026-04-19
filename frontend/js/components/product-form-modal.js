// Kombiniertes Anlegen-/Bearbeiten-Modal.
//
// Dispatch-Events die hier auflaufen:
//   - 'open-product-form' (detail=null)        -> Anlegen
//   - 'open-product-form' (detail=product)     -> Bearbeiten
//
// Emittiert bei Erfolg eins dieser Events an window:
//   - 'product-created' (detail=product)
//   - 'product-updated' (detail=product)
document.addEventListener('alpine:init', () => {
  Alpine.data('productFormModal', () => ({
    open: false,
    mode: 'create', // 'create' | 'edit'
    editId: null,
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

    show(product) {
      if (product && product.id) {
        this.mode = 'edit';
        this.editId = product.id;
        this.name = product.name ?? '';
        this.category = product.category ?? '';
        this.cost_price = product.cost_price ?? 0;
        this.stock = product.stock ?? 0;
        this.competitor_price = product.competitor_price ?? null;
        this.monthly_demand = product.monthly_demand ?? 0;
        this.daily_usage = product.daily_usage ?? 0;
        this.context = product.context ?? '';
      } else {
        this.mode = 'create';
        this.editId = null;
        this.reset();
      }
      this.error = '';
      this.open = true;
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

    _payload() {
      return {
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
      };
    },

    async submit() {
      this.loading = true;
      this.error = '';
      try {
        if (this.mode === 'edit') {
          const updated = await window.api.put(`/products/${this.editId}`, this._payload());
          window.dispatchEvent(new CustomEvent('product-updated', { detail: updated }));
        } else {
          const created = await window.api.post('/products', this._payload());
          window.dispatchEvent(new CustomEvent('product-created', { detail: created }));
        }
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
