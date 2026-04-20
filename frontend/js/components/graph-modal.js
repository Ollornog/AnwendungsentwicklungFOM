// Graph-Modal: plottet den Verkaufspreis des Produkts in Abhaengigkeit
// einer ausgewaehlten Variable.
//
// Strategien: fix (horizontale Linie, konstanter Preis) und formula
// (Kurve). rule/llm koennen clientseitig nicht ausgewertet werden und
// zeigen einen Hinweis.
//
// Event: 'open-graph-modal' mit detail = { product, sim }
document.addEventListener('alpine:init', () => {
  // Range-Definitionen pro Variable. 'stock', 'cost', 'time' sind
  // Sonderfaelle, die `_buildData()` aus dem Produkt-Kontext ableitet.
  const OPTIONS = [
    { key: 'hour',             label: 'Uhrzeit (0–23)',             range: [0, 23, 1] },
    { key: 'day',              label: 'Tag im Monat (1–28)',        range: [1, 28, 1] },
    { key: 'weekday',          label: 'Wochentag (1–7)',            range: [1, 7, 1] },
    { key: 'stock',            label: 'Lagerbestand (0 – Start)',   range: 'stock' },
    { key: 'usage',            label: 'Verbrauch (0–20)',           range: [0, 20, 1] },
    { key: 'monthly_demand',   label: 'Nachfrage / Monat (0–500)',  range: [0, 500, 10] },
    { key: 'cost_price',       label: 'Einkaufspreis (± 50 %)',     range: 'cost' },
    { key: 'competitor_price', label: 'Wettbewerbspreis (± 50 %)',  range: 'cost' },
    { key: 'time',             label: 'Zeit gesamt (1 Monat)',      range: 'time' },
  ];

  Alpine.data('graphModal', () => ({
    open: false,
    product: null,
    sim: null,
    variable: 'hour',
    chart: null,
    options: OPTIONS,
    notSupported: false, // true wenn Strategie nicht auswertbar (rule/llm)

    show(detail) {
      const { product, sim } = detail || {};
      this.product = product;
      this.sim = sim || { hour: 12, day: 15 };
      this.variable = 'hour';
      this.notSupported =
        !product ||
        !product.strategy ||
        (product.strategy.kind !== 'fix' && product.strategy.kind !== 'formula');
      this.open = true;
      // Nach dem x-show-Mount rendern – Canvas existiert dann im DOM.
      this.$nextTick(() => this.render());
    },

    cancel() {
      this.open = false;
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
      this.product = null;
    },

    onVariableChange() {
      this.render();
    },

    _baseVars() {
      const p = this.product;
      const day = Number(this.sim.day) || 1;
      return {
        cost_price: Number(p.cost_price) || 0,
        competitor_price: p.competitor_price != null ? Number(p.competitor_price) : 0,
        monthly_demand: Number(p.monthly_demand) || 0,
        start_stock: Number(p.stock) || 1,
        stock: Number(p._current_stock != null ? p._current_stock : p.stock) || 0,
        usage: Number(p._usage != null ? p._usage : p.daily_usage) || 0,
        hour: Number(this.sim.hour) || 0,
        day: day,
        weekday: ((day - 1) % 7) + 1,
      };
    },

    _compute(override) {
      const p = this.product;
      const kind = p.strategy.kind;
      if (kind === 'fix') {
        const a = Number(p.strategy.config?.amount);
        return Number.isFinite(a) ? a : null;
      }
      const vars = { ...this._baseVars(), ...override };
      // weekday aus day ableiten, falls day im Override mit ist.
      if ('day' in override) vars.weekday = ((override.day - 1) % 7) + 1;
      try {
        const v = window.evaluateFormula(p.strategy.config?.expression || '', vars);
        return Number.isFinite(v) ? v : null;
      } catch (_) {
        return null;
      }
    },

    _buildData() {
      if (!this.product || this.notSupported) return { labels: [], data: [] };
      const opt = this.options.find((o) => o.key === this.variable);
      if (!opt) return { labels: [], data: [] };
      const base = this._baseVars();
      const labels = [];
      const data = [];

      if (opt.range === 'stock') {
        const max = Math.max(1, base.start_stock);
        const step = Math.max(1, Math.round(max / 50));
        for (let x = 0; x <= max; x += step) {
          labels.push(String(x));
          data.push(this._compute({ stock: x }));
        }
      } else if (opt.range === 'cost') {
        const current = base[this.variable] || 1;
        const min = Math.max(0.01, current * 0.5);
        const max = current * 1.5;
        const step = (max - min) / 50;
        for (let i = 0; i <= 50; i++) {
          const x = min + step * i;
          labels.push(x.toFixed(2));
          data.push(this._compute({ [this.variable]: x }));
        }
      } else if (opt.range === 'time') {
        for (let h = 0; h < 24 * 28; h++) {
          const hour = h % 24;
          const day = Math.floor(h / 24) + 1;
          labels.push('D' + day + ' ' + String(hour).padStart(2, '0') + ':00');
          data.push(this._compute({ hour, day }));
        }
      } else {
        const [mn, mx, st] = opt.range;
        for (let x = mn; x <= mx; x += st) {
          labels.push(String(x));
          data.push(this._compute({ [this.variable]: x }));
        }
      }
      return { labels, data };
    },

    render() {
      if (!this.$refs.canvas || this.notSupported) return;
      if (typeof Chart === 'undefined') return; // CDN noch nicht geladen
      const { labels, data } = this._buildData();
      if (this.chart) this.chart.destroy();
      this.chart = new Chart(this.$refs.canvas, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Verkaufspreis (€)',
              data,
              borderColor: '#5a8df5',
              backgroundColor: 'rgba(90, 141, 245, 0.15)',
              tension: 0.25,
              pointRadius: labels.length > 100 ? 0 : 2,
              spanGaps: true,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          scales: {
            y: {
              ticks: {
                callback: (v) => Number(v).toFixed(2) + ' €',
              },
            },
            x: {
              ticks: { autoSkip: true, maxTicksLimit: 12 },
            },
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) =>
                  ctx.parsed.y != null
                    ? Number(ctx.parsed.y).toFixed(2) + ' €'
                    : '—',
              },
            },
          },
        },
      });
    },
  }));
});
