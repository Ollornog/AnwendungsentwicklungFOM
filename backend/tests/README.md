# Backend-Tests

Pytest-basiert, zwei Ebenen.

## 1. Unit-Tests (keine DB)
Laufen immer, kein Setup nötig.

- `test_evaluator.py` — AST-Evaluator inklusive Security (kein `eval`, kein Funktionsaufruf, keine Attribute, keine Imports).
- `test_strategies.py` — die vier Preisstrategien (Fixpreis, Formel, Regel, LLM mit Monkeypatch des Gemini-Clients).

```bash
pytest -m "not integration"
```

## 2. Integration-Tests (Postgres erforderlich)
Laufen nur, wenn `TEST_DATABASE_URL` gesetzt ist. Ohne werden sie automatisch geskippt.

- `test_api_auth.py` — Login, Logout, `/me`, falsches Passwort, unauthentifiziert.
- `test_api_products.py` — CRUD, Ownership-Isolation zwischen Usern, Strategie-Upsert und -Validierung.
- `test_api_pricing.py` — Zwei-Schritt-Flow (Price → Confirm), Historie, abgelaufener Token, fehlende Strategie.

```bash
createdb preisopt_test
export TEST_DATABASE_URL="postgresql+psycopg://preisopt:preisopt@localhost:5432/preisopt_test"
pytest
```

Die Test-DB wird bei Session-Start via `Base.metadata.create_all` eingerichtet und bei Session-Ende wieder gedroppt. Zwischen Tests werden alle Tabellen geleert, kein Zustand leckt.

## Nützliche Aufrufe
```bash
pytest -v                            # verbose
pytest tests/test_evaluator.py       # nur eine Datei
pytest -k "llm"                      # Filter nach Name
pytest -m integration                # nur DB-Tests
```
