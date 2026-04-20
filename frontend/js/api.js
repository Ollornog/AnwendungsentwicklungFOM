(function () {
  const API_BASE = '/api/v1';

  async function request(method, path, body, opts) {
    const options = opts || {};
    const res = await fetch(`${API_BASE}${path}`, {
      method,
      credentials: 'include',
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401) {
      // `silent401`: Rufer moechte selbst entscheiden, was bei "nicht
      // angemeldet" passiert (z. B. oeffentliche Seiten). Default ist
      // der automatische Redirect zur Login-Seite.
      if (!options.silent401 && location.pathname !== '/' && location.pathname !== '/index.html') {
        location.href = '/';
      }
      throw new Error('Nicht authentifiziert');
    }

    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail || detail;
      } catch (_) { /* ignore */ }
      throw new Error(`API ${res.status}: ${detail}`);
    }

    if (res.status === 204) return null;
    return res.json();
  }

  window.api = {
    get: (p, opts) => request('GET', p, undefined, opts),
    post: (p, b, opts) => request('POST', p, b, opts),
    put: (p, b, opts) => request('PUT', p, b, opts),
    del: (p, opts) => request('DELETE', p, undefined, opts),
  };
})();
