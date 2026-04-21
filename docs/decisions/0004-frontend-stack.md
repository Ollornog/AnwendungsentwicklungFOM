# ADR-0004: Frontend-Stack

**Status:** Akzeptiert (2026-04-19)
**Datum:** 2026-04-19

## Kontext

Die UI deckt sechs Use Cases ab (Anlegen/Bearbeiten, Strategie,
Live-Simulation, KI-Vorschlag, Graph, Historie). Das sind reactive
Sprinkles – Formulare, Modal-Dialoge, Listen mit Live-Update – keine
komplexen Routing-Szenarien. Ein volles SPA-Framework wäre Overkill
im 4er-Team und würde eine Build-Pipeline nach sich ziehen.

## Entscheidung

- **Markup:** HTML5.
- **Reactivity:** Alpine.js 3 via CDN, kein Build-Schritt.
- **Styling:** Pico.css 2 via CDN, wenige Overrides in `frontend/css/app.css`.
- **Charts:** Chart.js 4 via CDN (nur auf `graph-modal`).
- **HTTP:** eigener Wrapper `frontend/js/api.js` über `fetch`,
  `credentials: 'include'`.
- **Auslieferung:** FastAPI `StaticFiles(html=True)` im gleichen
  Origin wie die API.

## Konsequenzen

- ➕ **Zero-Build:** keine npm-Toolchain, keine Version-Drift, kein
  CI-Setup – ein Entwicklungs-Check-out läuft ohne `npm install`.
- ➕ `x-data` / `x-show` / `x-for` / `Alpine.store` reichen für
  unsere Interaktionsmuster. Gleiches Origin vermeidet CORS-Konfig.
- ➕ Einheitliches Fehler- und Auth-Handling zentral in `api.js`,
  optional `silent401` für öffentliche Seiten.
- ➕ Transparenz-Pflicht (AI Act Art. 50) ist sichtbar im Frontend
  umgesetzt: `badge-ai` für KI-Vorschläge und `readonly`-Textareas
  für Prompt + Begründung.
- ➖ Kein TypeScript, keine statische Typisierung im Frontend. Für
  den Scope akzeptabel; Refactoring auf TS bei Bedarf machbar.
- ➖ Ohne Build kein Bundling/Minification. Traffic-mäßig vernachlässig-
  bar, im Demo-Setup kein Problem.

## Alternativen

- **Pure Vanilla JS:** State-Sync zwischen Produktliste, Modals und
  Simulation wäre ohne Reactivity-Lib schnell unleserlich.
- **HTMX + Jinja2-Templates:** erzwingt server-gerenderte Fragmente
  und verwischt die dokumentierte Frontend/Backend-Trennung.
- **Vue / Svelte / React + Vite:** Build-Pipeline, npm-Komplexität
  und Lernkurve sind für sechs Use Cases nicht gerechtfertigt.
- **Laravel mit Blade-Templates:** verworfen mit ADR 0001 (Python-
  Backend). Zudem kein saubere Client-side-Reactivity.
