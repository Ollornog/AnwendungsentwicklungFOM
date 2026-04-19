# Datenmodell

> Erste Skizze. Wird mit jedem Schema-Change aktualisiert.

## Entitäten (Entwurf)
- **User** – Shop-Betreiber, der sich am Tool anmeldet.
- **Product** – Produkt, dessen Preis verwaltet wird.
- **PricingStrategy** – Konfiguration einer der vier Strategien (Fix, Formel, Regel, LLM), 1:1 oder n:1 zum Produkt (TBD).
- **PriceHistory** – jeder berechnete Preis mit Zeitstempel, Strategie-Verweis und Begründung.

## Beziehungen (Entwurf)
- `User 1 — n Product`
- `Product 1 — 1 PricingStrategy` (jeweils aktuell aktive)
- `Product 1 — n PriceHistory`

## Offene Punkte
- Mehrere parallele Strategien pro Produkt erlauben? Aktuelle Annahme: nein, eine aktive.
- Versionierung der Strategie-Konfiguration: in `PricingStrategy` oder über `PriceHistory`?
- Genaues Schema (Spalten, Typen, Constraints) – wird mit ADR zur DB-Struktur festgelegt.
