# ADR 0003: Authentifizierung via Session-Cookie

- **Status:** Akzeptiert
- **Datum:** 2026-04-19
- **Entscheider:** Projektteam

## Kontext
Das Backend braucht ein Auth-Verfahren für die Admin-UI. CLAUDE.md §9 listete die Entscheidung als offen. Wahl zwischen Session-Cookie und JWT im LocalStorage / Header.

## Entscheidung
**Server-seitige Session, transportiert über ein HTTP-Cookie mit `HttpOnly` und `SameSite=Lax`.**

## Begründung
- Kein XSS-Auslese-Risiko: Ein `HttpOnly`-Cookie ist aus JavaScript nicht lesbar. JWT im LocalStorage wäre das nicht.
- Für einen Prototyp mit einem Origin (FastAPI liefert Frontend und API aus) ist CSRF über `SameSite=Lax` ausreichend eingedämmt.
- Umsetzung in FastAPI ist minimal (`response.set_cookie(..., httponly=True, samesite="lax")`), Frontend nutzt `fetch(..., { credentials: 'include' })`.
- JWT bringt Vorteile erst bei Mobile-Clients, Cross-Domain-Setups oder stateless Skalierung – alles explizit out-of-scope.

## Konsequenzen
- Backend hält Session-State (In-Memory für den Prototyp, für Produktiv wäre Redis o. ä. nötig).
- Passwörter werden mit argon2 oder bcrypt gehasht (siehe `docs/security.md`).
- Frontend muss `credentials: 'include'` bei jedem API-Call setzen.
- `SESSION_SECRET` liegt in `.env` (siehe `.env.example`).

## Alternativen
- **JWT im LocalStorage:** XSS-Risiko, für Studi-Prototyp nicht angemessen absicherbar.
- **JWT im Cookie:** Überschneidet sich mit Session-Cookie, bringt aber keinen Mehrwert für unseren Scope.
- **Basic Auth:** Keine saubere Logout-Semantik, schwache UX.
