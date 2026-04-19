document.addEventListener('alpine:init', () => {
  Alpine.data('productForm', (onCreated) => ({
    name: '',
    category: '',
    cost_price: 0,
    stock: 0,
    competitor_price: null,
    loading: false,
    error: '',

    async submit() {
      this.loading = true;
      this.error = '';
      try {
        const created = await window.api.post('/products', {
          name: this.name,
          category: this.category,
          cost_price: Number(this.cost_price),
          stock: Number(this.stock),
          competitor_price: this.competitor_price === null || this.competitor_price === ''
            ? null
            : Number(this.competitor_price),
        });
        this.name = '';
        this.category = '';
        this.cost_price = 0;
        this.stock = 0;
        this.competitor_price = null;
        if (typeof onCreated === 'function') onCreated(created);
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
  }));
});
