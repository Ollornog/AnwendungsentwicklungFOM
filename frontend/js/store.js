document.addEventListener('alpine:init', () => {
  Alpine.store('auth', {
    user: null,
    ready: false,

    /** Holt den aktuell eingeloggten User und merkt sich ihn im Store.
     *  Sub-Komponenten pruefen dann `$store.auth.user?.username === 'admin'`
     *  fuer Admin-only-Blöcke, ohne dass jeder Block selbst /auth/me ruft.
     */
    async ensureMe() {
      if (this.ready) return this.user;
      // silent401: auf oeffentlichen Seiten (Impressum/Datenschutz) darf ein
      // fehlender Login nicht zum automatischen Redirect fuehren.
      try {
        this.user = await window.api.get('/auth/me', { silent401: true });
      } catch (_) {
        this.user = null;
      }
      this.ready = true;
      return this.user;
    },

    async login(username, password) {
      this.user = await window.api.post('/auth/login', { username, password });
      this.ready = true;
      return this.user;
    },

    async logout() {
      await window.api.post('/auth/logout');
      this.user = null;
      this.ready = false;
      location.href = '/';
    },

    isAdmin() {
      return this.user && this.user.username === 'admin';
    },
  });
});
