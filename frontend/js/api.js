(function () {
  const API_BASE = '/api/v1';

  async function request(method, path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
      method,
      credentials: 'include',
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401) {
      if (location.pathname !== '/' && location.pathname !== '/index.html') {
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
    get: (p) => request('GET', p),
    post: (p, b) => request('POST', p, b),
    put: (p, b) => request('PUT', p, b),
    del: (p) => request('DELETE', p),
  };
})();
