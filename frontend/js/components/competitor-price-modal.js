// Modal fuer die KI-gestuetzte Wettbewerbspreis-Schaetzung.
//
// Ablauf: beim Oeffnen ruft die Komponente POST /products/competitor-prices/
// suggest auf. Die KI schlaegt pro Produkt einen Preis vor; der User sieht
// alt/neu und entscheidet pro Zeile, ob er uebernehmen will (Human-in-the-
// Loop). "Alle uebernehmen" ist ein Bulk-PUT durch alle Zeilen.
//
// Events:
//  - eingehend:  'open-competitor-modal'
//  - ausgehend:  'product-updated' (per Uebernehmen-Klick, damit die
//                Produkt-Liste den neuen Wettbewerbspreis sofort sieht)
document.addEventListener('alpine:init', () => {
  Alpine.data('competitorPriceModal', () => ({
    open: false,
    loading: false,
    error: '',
    items: [], // [{id, name, category, current_competitor_price, suggested_price, reasoning, applied}]
    applyingAll: false,

    async show() {
      this.open = true;
      this.loading = true;
      this.error = '';
      this.items = [];
      try {
        const res = await window.api.post('/products/competitor-prices/suggest', {});
        this.items = (res.items || []).map((it) => ({ ...it, applied: false, applying: false }));
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    cancel() {
      this.open = false;
      this.items = [];
      this.error = '';
    },

    _delta(it) {
      if (it.current_competitor_price == null) return null;
      return Number(it.suggested_price) - Number(it.current_competitor_price);
    },

    deltaText(it) {
      const d = this._delta(it);
      if (d == null) return '—';
      const sign = d > 0 ? '+' : '';
      return sign + d.toFixed(2);
    },

    deltaClass(it) {
      const d = this._delta(it);
      if (d == null) return '';
      return d >= 0 ? 'delta-up' : 'delta-down';
    },

    async applyOne(it) {
      it.applying = true;
      try {
        const updated = await window.api.put(`/products/${it.id}`, {
          competitor_price: Number(it.suggested_price),
        });
        it.current_competitor_price = updated.competitor_price;
        it.applied = true;
        window.dispatchEvent(new CustomEvent('product-updated', { detail: updated }));
      } catch (e) {
        this.error = e.message;
      } finally {
        it.applying = false;
      }
    },

    async applyAll() {
      this.applyingAll = true;
      this.error = '';
      for (const it of this.items) {
        if (it.applied) continue;
        await this.applyOne(it);
      }
      this.applyingAll = false;
    },
  }));
});
