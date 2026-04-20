# ADR 0003: Authentifizierung via Session-Cookie

- **Status:** Akzeptiert
- **Datum:** 2026-04-19
- **Entscheider:** Projektteam

## Kontext
Das Backend braucht ein Auth-Verfahren für die Admin-UI. CLAUDE.md §9 listete die Entscheidung als offen. Wahl zwischen Session-Cookie und JWT im LocalStorage / Header.

## Entscheidung
**Starlette-`SessionMiddleware`: signiertes Cookie mit `HttpOnly` und `SameSite=Lax`. Die Session-Nutzlast lebt im Cookie selbst, der Server hält keinen Session-Store.**

## Begründung
- Kein XSS-Auslese-Risiko: Ein `HttpOnly`-Cookie ist aus JavaScript nicht lesbar. JWT im LocalStorage wäre das nicht.
- Für einen Prototyp mit einem Origin (FastAPI liefert Frontend und API aus) ist CSRF über `SameSite=Lax` ausreichend eingedämmt.
- Umsetzung in FastAPI/Starlette ist minimal (`app.add_middleware(SessionMiddleware, secret_key=..., same_site="lax", https_only=False)`), Frontend nutzt `fetch(..., { credentials: 'include' })`.
- JWT bringt Vorteile erst bei Mobile-Clients, Cross-Domain-Setups oder stateless Skalierung – alles explizit out-of-scope.

## Konsequenzen
- Session-Payload ist im signierten Cookie (`itsdangerous`). Kein serverseitiger Session-Store nötig – passt zum Single-Node-Demo.
- `https_only=False` bleibt gesetzt, weil die Anwendung default über HTTP läuft. Bei Nutzung hinter HTTPS funktioniert das Cookie ohne `Secure`-Flag weiterhin, für einen Produktivbetrieb sollte der Flag auf `True` gezogen werden.
- Passwörter werden mit **argon2id** gehasht (`argon2-cffi`).
- Frontend muss `credentials: 'include'` bei jedem API-Call setzen (`js/api.js`).
- `SESSION_SECRET` liegt in `.env`; `install.sh` generiert ihn beim ersten Lauf zufällig (siehe `.env.example`).
- nginx invalidiert das Cookie bei 5xx-Upstream-Fehlern (`@bad_gateway`-Location), damit keine stecken bleibende Session nach Backend-Ausfall Probleme macht.

## Alternativen
- **JWT im LocalStorage:** XSS-Risiko, für Studi-Prototyp nicht angemessen absicherbar.
- **JWT im Cookie:** Überschneidet sich mit Session-Cookie, bringt aber keinen Mehrwert für unseren Scope.
- **Basic Auth:** Keine saubere Logout-Semantik, schwache UX.
