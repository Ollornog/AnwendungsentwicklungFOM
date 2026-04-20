# Datenmodell

Persistiert in PostgreSQL. Migrationen via Alembic (`backend/alembic/versions/`).
Geldbeträge als `numeric(12,2)`, Zeitstempel als `timestamptz` in UTC.
Primärschlüssel sind UUIDs (`gen_random_uuid()`), außer bei Tabellen, bei denen
ein fachlicher Schlüssel natürlicher ist (`app_settings`, `api_rate_usage`,
`price_suggestions`).

## Entitäten

### `users`
Login-Konten. Der bootstrap-Account heißt `admin` und ist in der UI gegen
Passwort-/Rollen-Änderungen und Löschen geschützt.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK |
| `username` | `varchar(64)` | UNIQUE, NOT NULL |
| `password_hash` | `text` | NOT NULL (Argon2id) |
| `role` | `varchar(16)` | NOT NULL, CHECK in (`admin`, `viewer`), Default `admin` |
| `created_at` | `timestamptz` | NOT NULL, Default `now()` |

### `products`
Produkt-Stammdaten des Shop-Betreibers. `stock` ist die Lager-Obergrenze, der
aktuelle Lagerbestand in der Simulation lebt rein im Frontend-Zustand.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK |
| `owner_id` | `uuid` | NOT NULL, FK → `users.id` ON DELETE CASCADE |
| `name` | `varchar(128)` | NOT NULL |
| `category` | `varchar(64)` | NOT NULL |
| `cost_price` | `numeric(12,2)` | NOT NULL, CHECK ≥ 0 |
| `stock` | `integer` | NOT NULL, CHECK ≥ 0 |
| `competitor_price` | `numeric(12,2)` | NULLABLE, CHECK NULL OR ≥ 0 |
| `context` | `text` | NOT NULL, Default `''` (Freitext für KI-Prompt) |
| `monthly_demand` | `integer` | NOT NULL, Default `0`, CHECK ≥ 0 |
| `created_at` | `timestamptz` | NOT NULL, Default `now()` |
| `updated_at` | `timestamptz` | NOT NULL, Default `now()`, on update `now()` |

### `pricing_strategies`
Eine aktive Strategie pro Produkt (1:1). Konfiguration als JSONB, strategie-
spezifisch im Backend validiert.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK |
| `product_id` | `uuid` | UNIQUE, NOT NULL, FK → `products.id` ON DELETE CASCADE |
| `kind` | `varchar(16)` | NOT NULL, CHECK in (`fix`, `formula`, `rule`, `llm`) |
| `config` | `jsonb` | NOT NULL |
| `updated_at` | `timestamptz` | NOT NULL |

### `price_history`
Append-only. Kein `UPDATE`/`DELETE` im normalen Flow (Audit-Trail).

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `id` | `uuid` | PK |
| `product_id` | `uuid` | NOT NULL, FK → `products.id` ON DELETE CASCADE, INDEX |
| `user_id` | `uuid` | NULLABLE, FK → `users.id` ON DELETE SET NULL, INDEX |
| `strategy_kind` | `varchar(16)` | NOT NULL |
| `price` | `numeric(12,2)` | NOT NULL |
| `currency` | `varchar(3)` | NOT NULL, Default `EUR` |
| `is_llm_suggestion` | `boolean` | NOT NULL, Default `false` |
| `inputs` | `jsonb` | NOT NULL (Variablen-Snapshot zum Zeitpunkt der Berechnung) |
| `reasoning` | `text` | NULLABLE |
| `created_at` | `timestamptz` | NOT NULL, Default `now()`, INDEX |

### `price_suggestions`
Ephemere Vorschläge aus dem Zwei-Schritt-Flow (`/price` → `/price/confirm`).
Beim Confirm wird der Eintrag gelesen, in `price_history` überführt und
gelöscht. Abgelaufene Vorschläge liefern `410 Gone`.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `token` | `varchar(64)` | PK |
| `product_id` | `uuid` | NOT NULL, FK → `products.id` ON DELETE CASCADE |
| `strategy_kind` | `varchar(16)` | NOT NULL |
| `price` | `numeric(12,2)` | NOT NULL |
| `currency` | `varchar(3)` | NOT NULL, Default `EUR` |
| `is_llm_suggestion` | `boolean` | NOT NULL |
| `inputs` | `jsonb` | NOT NULL |
| `reasoning` | `text` | NULLABLE |
| `created_at` | `timestamptz` | NOT NULL, Default `now()` |
| `expires_at` | `timestamptz` | NOT NULL (TTL aus `SUGGESTION_TTL_MINUTES`) |

### `app_settings`
Globale Laufzeit-Konfiguration, per Einstellungs-UI änderbar. Eigenständige
Key/Value-Tabelle, damit kein Service-Restart nötig wird.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `key` | `varchar(64)` | PK |
| `value` | `text` | NOT NULL |
| `updated_at` | `timestamptz` | NOT NULL |

Aktuell verwendete Keys: `gemini_api_key`, `https_enabled`, `https_domain`,
`rate_limit_default`, `rate_limit_admin`.

### `api_rate_usage`
Tagesbasiertes Zählwerk für das Rate-Limit pro User. Pro Tag genau eine Zeile
pro Benutzer; ein neuer Tag bedeutet implizit `count = 0`.

| Spalte | Typ | Constraints |
| --- | --- | --- |
| `user_id` | `uuid` | PK, FK → `users.id` ON DELETE CASCADE |
| `day` | `date` | PK |
| `count` | `integer` | NOT NULL, Default `0`, CHECK ≥ 0 |

## Beziehungen

```
users 1 ── n products 1 ── 1 pricing_strategies
              └── n price_history  (FK user_id optional)
              └── n price_suggestions
users 1 ── n price_history
users 1 ── n api_rate_usage

app_settings   — global, keine Fremdschlüssel
```

## Invarianten
- `pricing_strategies.config` passt zum Schema der jeweiligen `kind`-Variante.
  Validierung durch die Strategy-Evaluator-Module im Backend.
- `price_history` wird ausschließlich über den Confirm-Flow oder als
  Snapshot beim Strategie-Upsert erzeugt.
- `price_history.is_llm_suggestion = true` genau dann, wenn die Strategie
  `llm` war oder die KI-Suggest-Route den Preis geliefert hat.

## Migrationen (Stand)

| Revision | Inhalt |
| --- | --- |
| `0001_initial` | Tabellen `users`, `products`, `pricing_strategies`, `price_history`, `price_suggestions` |
| `0002_product_context_demand` | `products.context`, `products.monthly_demand`, `products.daily_usage` (letzteres später wieder entfernt) |
| `0003_app_settings` | Tabelle `app_settings` |
| `0004_price_history_user` | `price_history.user_id` (nullable FK) |
| `0005_drop_daily_usage` | `products.daily_usage` entfernt – Nachfrage treibt Lager-Sim über `monthly_demand` × Live-Faktor `demand` |
| `0006_api_rate_usage` | Tabelle `api_rate_usage` |
