# ADR-0003: Auth via Session-Cookie

**Status:** Akzeptiert (2026-04-19)
**Datum:** 2026-04-19

## Kontext

Das Backend braucht ein Auth-Verfahren für die Admin-UI. Die UI läuft
im gleichen Origin wie die API (FastAPI liefert `frontend/` via
`StaticFiles` aus). Der Scope ist ein Demo-Prototyp, keine Mobile-
Clients, keine Cross-Domain-Aufrufe.

## Entscheidung

Starlette-`SessionMiddleware` mit **signiertem Cookie**
(`HttpOnly`, `SameSite=Lax`). Die Session-Nutzlast liegt im Cookie
selbst (signiert mit `SESSION_SECRET` über `itsdangerous`), der
Server hält keinen Session-Store.

Passwörter werden mit **argon2id** (`argon2-cffi`) gehasht.

## Konsequenzen

- ➕ Kein Server-Side-Store erforderlich – passt zum Single-Node-
  Deployment.
- ➕ `HttpOnly` verhindert Auslesen via XSS; `SameSite=Lax` deckt
  CSRF im Single-Origin-Setup ausreichend ab.
- ➕ Frontend muss nur `credentials: 'include'` bei jedem Call
  setzen (zentral in `frontend/js/api.js`).
- ➕ Kompatibel mit `nginx`-Regel, die bei 5xx-Upstream-Fehlern das
  Cookie invalidiert (`@bad_gateway`-Location).
- ➖ `https_only=False` bleibt gesetzt, weil das Deployment default
  über HTTP läuft; bei HTTPS sollte der `Secure`-Flag auf `True`
  gezogen werden.

## Alternativen

- **JWT im LocalStorage:** anfällig für XSS-Auslese, für einen
  Studien-Prototyp ohne MFA nicht angemessen absicherbar.
- **JWT im Cookie:** überschneidet sich mit dem Session-Cookie ohne
  Mehrwert im Scope.
- **Basic Auth:** keine saubere Logout-Semantik, UX schwach.
