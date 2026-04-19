document.addEventListener('alpine:init', () => {
  Alpine.store('auth', {
    user: null,
    async login(username, password) {
      this.user = await window.api.post('/auth/login', { username, password });
      return this.user;
    },
    async logout() {
      await window.api.post('/auth/logout');
      this.user = null;
      location.href = '/';
    },
  });
});
