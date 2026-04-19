document.addEventListener('alpine:init', () => {
  Alpine.data('historyTable', (productId) => ({
    productId,
    items: [],
    loading: false,
    error: '',

    async load() {
      this.loading = true;
      this.error = '';
      try {
        const res = await window.api.get(`/products/${this.productId}/history`);
        this.items = res.items || [];
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    formatDate(iso) {
      try { return new Date(iso).toLocaleString('de-DE'); } catch { return iso; }
    },
  }));
});
