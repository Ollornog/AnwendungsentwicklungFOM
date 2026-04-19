document.addEventListener('alpine:init', () => {
  Alpine.data('priceDialog', (productId) => ({
    productId,
    open: false,
    loading: false,
    confirming: false,
    error: '',
    suggestion: null,

    async request() {
      this.loading = true;
      this.error = '';
      this.suggestion = null;
      this.open = true;
      try {
        this.suggestion = await window.api.post(`/products/${this.productId}/price`, {});
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    async confirm() {
      if (!this.suggestion?.suggestion_token) return;
      this.confirming = true;
      this.error = '';
      try {
        await window.api.post(`/products/${this.productId}/price/confirm`, {
          suggestion_token: this.suggestion.suggestion_token,
        });
        this.open = false;
        this.suggestion = null;
        window.dispatchEvent(new CustomEvent('price-confirmed', { detail: { productId: this.productId } }));
      } catch (e) {
        this.error = e.message;
      } finally {
        this.confirming = false;
      }
    },

    cancel() {
      this.open = false;
      this.suggestion = null;
      this.error = '';
    },
  }));
});
