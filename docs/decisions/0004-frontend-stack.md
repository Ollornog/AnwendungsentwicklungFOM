# ADR 0004: Frontend-Stack

- **Status:** Akzeptiert (Prototyp)
- **Datum:** 2026-04-19
- **Entscheider:** Projektteam

## Kontext
CLAUDE.md sah "HTML/JS (vanilla, später ggf. leichtes Framework)" vor. Für die fünf Use Cases (UC-01 bis UC-05) reichen reactive Sprinkles (Formulare, Modal-Dialoge, Listen). Ein volles SPA-Framework wäre Overkill und Klumpenrisiko im 4er-Team.

## Entscheidung
- **Markup:** HTML5.
- **Reactivity:** Alpine.js 3, via CDN eingebunden, kein Build-Schritt.
- **Styling:** Pico.css 2, via CDN, minimale Overrides in `frontend/css/app.css`.
- **HTTP:** `fetch` mit einem eigenen Wrapper `frontend/js/api.js`, `credentials: 'include'`.
- **Auslieferung:** FastAPI `StaticFiles` mit `html=True`, gleiches Origin wie die API.

## Begründung
- Zero-Build: keine npm-Toolchain, keine Version-Drift, kein CI-Aufwand für einen Prototyp.
- Alpine liefert `x-data`, `x-show`, `x-for`, `Alpine.store` – genug für unsere Reactivity.
- Pico bringt brauchbare Defaults auf semantischem HTML, Abschluss-Demo sieht ohne Design-Aufwand ordentlich aus.
- Gleiches Origin vermeidet CORS-Konfiguration im Prototyp.
- Spätere Migration zu Vue/Svelte/React ist möglich, weil wir pro Use Case eine Komponenten-Datei haben.

## Konsequenzen
- Verzeichnis `frontend/` im Repo, strukturiert nach Seiten und Komponenten.
- Alle API-Calls laufen über `frontend/js/api.js` (einheitliche Fehlerbehandlung, Auth-Redirect).
- Leitprinzip 4 (KI-Sichtbarkeit): Backend-Responses müssen `is_llm_suggestion: bool` liefern, Frontend rendert ein Badge in `price-dialog.js` und `history-table.js`.
- Leitprinzip 3 (Human-in-the-Loop): Preisberechnung und Bestätigung sind zwei getrennte Requests (`POST /products/{id}/price` → `POST /products/{id}/price/confirm`), nur der zweite persistiert.

## Alternativen
- **Pures Vanilla:** State-Sync zwischen Liste, Detail, Historie wird ohne Reactivity-Lib schnell unleserlich.
- **HTMX + Jinja2:** Erzwingt server-gerenderte HTML-Fragmente, verwischt die dokumentierte FE/BE-Trennung.
- **Vue/Svelte/React + Vite:** Build-Pipeline, npm-Komplexität und Lernkurve nicht gerechtfertigt für fünf Use Cases.
