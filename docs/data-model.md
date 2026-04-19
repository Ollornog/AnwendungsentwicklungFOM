# Datenmodell

Persistiert in PostgreSQL 16. Migrations via Alembic (`backend/alembic/`). Geldbeträge als `numeric(12,2)`, Zeitstempel als `timestamptz` in UTC.

## Entitäten

### `users`
| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK, Default `gen_random_uuid()` |
| `username` | `text` | UNIQUE, NOT NULL |
| `password_hash` | `text` | NOT NULL (argon2) |
| `role` | `text` | NOT NULL, CHECK in (`admin`, `viewer`), Default `admin` |
| `created_at` | `timestamptz` | NOT NULL, Default `now()` |

### `products`
| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK, Default `gen_random_uuid()` |
| `owner_id` | `uuid` | NOT NULL, FK → `users.id` ON DELETE CASCADE |
| `name` | `text` | NOT NULL |
| `category` | `text` | NOT NULL |
| `cost_price` | `numeric(12,2)` | NOT NULL, CHECK ≥ 0 |
| `stock` | `integer` | NOT NULL, CHECK ≥ 0 |
| `competitor_price` | `numeric(12,2)` | NULLABLE, CHECK ≥ 0 |
| `created_at` | `timestamptz` | NOT NULL, Default `now()` |
| `updated_at` | `timestamptz` | NOT NULL, Default `now()` |

### `pricing_strategies`
Eine aktive Strategie pro Produkt (1:1). Konfiguration als JSONB, validiert strategie-spezifisch im Backend.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK, Default `gen_random_uuid()` |
| `product_id` | `uuid` | UNIQUE, NOT NULL, FK → `products.id` ON DELETE CASCADE |
| `kind` | `text` | NOT NULL, CHECK in (`fix`, `formula`, `rule`, `llm`) |
| `config` | `jsonb` | NOT NULL |
| `updated_at` | `timestamptz` | NOT NULL, Default `now()` |

### `price_history`
Append-only. Kein `UPDATE`/`DELETE` im normalen Flow (Audit-Trail, Leitprinzip 7).

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK, Default `gen_random_uuid()` |
| `product_id` | `uuid` | NOT NULL, FK → `products.id` ON DELETE CASCADE, INDEX |
| `strategy_kind` | `text` | NOT NULL |
| `price` | `numeric(12,2)` | NOT NULL |
| `currency` | `text` | NOT NULL, Default `EUR` |
| `is_llm_suggestion` | `boolean` | NOT NULL, Default `false` |
| `inputs` | `jsonb` | NOT NULL (Produkt-Snapshot zum Zeitpunkt der Berechnung) |
| `reasoning` | `text` | NULLABLE (LLM-Begründung oder ausgelöste Regel) |
| `created_at` | `timestamptz` | NOT NULL, Default `now()`, INDEX |

### `price_suggestions`
Ephemer: Vorschläge aus dem Zwei-Schritt-Flow (UC-03). Wird beim Confirm verbraucht oder läuft ab.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `token` | `text` | PK |
| `product_id` | `uuid` | NOT NULL, FK → `products.id` ON DELETE CASCADE |
| `strategy_kind` | `text` | NOT NULL |
| `price` | `numeric(12,2)` | NOT NULL |
| `currency` | `text` | NOT NULL, Default `EUR` |
| `is_llm_suggestion` | `boolean` | NOT NULL |
| `inputs` | `jsonb` | NOT NULL |
| `reasoning` | `text` | NULLABLE |
| `created_at` | `timestamptz` | NOT NULL, Default `now()` |
| `expires_at` | `timestamptz` | NOT NULL (z. B. `now() + 15 minutes`) |

## Beziehungen
```
users 1 ── n products 1 ── 1 pricing_strategies
                   └── n price_history
                   └── n price_suggestions
```

## Invarianten
- `pricing_strategies.config` entspricht dem Schema der jeweiligen `kind`-Variante (Backend-Validierung, siehe `docs/pricing-strategies.md`).
- `price_history` wird nur durch einen bestätigten Vorschlag (`price_suggestions` → Confirm) erzeugt.
- `price_history.is_llm_suggestion = true` genau dann, wenn `strategy_kind = 'llm'`.
