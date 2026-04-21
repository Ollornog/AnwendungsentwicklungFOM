from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.models import PriceSuggestion

pytestmark = pytest.mark.integration


def _product_payload():
    return {
        "name": "Sneaker",
        "category": "Schuhe",
        "cost_price": "10.00",
        "stock": 5,
        "competitor_price": "25.00",
    }


def _create_product_with_strategy(client, kind="fix", config=None):
    product = client.post("/api/v1/products", json=_product_payload()).json()
    client.put(
        f"/api/v1/products/{product['id']}/strategy",
        json={"kind": kind, "config": config or {"amount": "19.99"}},
    ).raise_for_status() if hasattr(client, "raise_for_status") else None
    client.put(
        f"/api/v1/products/{product['id']}/strategy",
        json={"kind": kind, "config": config or {"amount": "19.99"}},
    )
    return product


def test_price_without_strategy_400(authed_client):
    product = authed_client.post("/api/v1/products", json=_product_payload()).json()
    response = authed_client.post(f"/api/v1/products/{product['id']}/price")
    assert response.status_code == 400


def test_price_fix_flow_creates_history_only_on_confirm(authed_client):
    product = _create_product_with_strategy(authed_client, "fix", {"amount": "19.99"})

    suggestion = authed_client.post(f"/api/v1/products/{product['id']}/price")
    assert suggestion.status_code == 200
    body = suggestion.json()
    assert body["price"] == "19.99"
    assert body["strategy"] == "fix"
    assert body["is_llm_suggestion"] is False
    assert "suggestion_token" in body

    history_before = authed_client.get(f"/api/v1/products/{product['id']}/history").json()
    assert history_before["items"] == []

    confirm = authed_client.post(
        f"/api/v1/products/{product['id']}/price/confirm",
        json={"suggestion_token": body["suggestion_token"]},
    )
    assert confirm.status_code == 201

    history_after = authed_client.get(f"/api/v1/products/{product['id']}/history").json()
    assert len(history_after["items"]) == 1
    entry = history_after["items"][0]
    assert entry["price"] == "19.99"
    assert entry["strategy"] == "fix"
    assert entry["is_llm_suggestion"] is False


def test_formula_strategy_price(authed_client):
    product = _create_product_with_strategy(
        authed_client, "formula", {"expression": "cost_price * 2"}
    )
    body = authed_client.post(f"/api/v1/products/{product['id']}/price").json()
    assert body["price"] == "20.00"
    assert body["strategy"] == "formula"


def test_legacy_strategy_rejected(authed_client):
    # rule und llm sind seit Migration 0007 nicht mehr im Scope.
    # PUT /strategy muss das klar zurueckweisen (422, Pydantic-Literal).
    product = authed_client.post("/api/v1/products", json=_product_payload()).json()
    for kind in ("rule", "llm"):
        response = authed_client.put(
            f"/api/v1/products/{product['id']}/strategy",
            json={"kind": kind, "config": {}},
        )
        assert response.status_code == 422, f"{kind} sollte abgelehnt werden"


def test_confirm_with_unknown_token_404(authed_client):
    product = _create_product_with_strategy(authed_client)
    response = authed_client.post(
        f"/api/v1/products/{product['id']}/price/confirm",
        json={"suggestion_token": "unknown"},
    )
    assert response.status_code == 404


def test_confirm_expired_token_410(authed_client, db_session):
    product = _create_product_with_strategy(authed_client)
    body = authed_client.post(f"/api/v1/products/{product['id']}/price").json()

    suggestion = db_session.get(PriceSuggestion, body["suggestion_token"])
    assert suggestion is not None
    suggestion.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    response = authed_client.post(
        f"/api/v1/products/{product['id']}/price/confirm",
        json={"suggestion_token": body["suggestion_token"]},
    )
    assert response.status_code == 410


def test_history_in_reverse_chronological_order(authed_client):
    product = _create_product_with_strategy(authed_client, "fix", {"amount": "10.00"})
    pid = product["id"]

    for amount in ("10.00", "20.00", "30.00"):
        authed_client.put(
            f"/api/v1/products/{pid}/strategy", json={"kind": "fix", "config": {"amount": amount}}
        )
        body = authed_client.post(f"/api/v1/products/{pid}/price").json()
        authed_client.post(
            f"/api/v1/products/{pid}/price/confirm",
            json={"suggestion_token": body["suggestion_token"]},
        )

    history = authed_client.get(f"/api/v1/products/{pid}/history").json()
    prices = [item["price"] for item in history["items"]]
    assert prices == ["30.00", "20.00", "10.00"]


def test_ownership_protects_price_endpoints(client, user_factory):
    user_factory(username="alice", password="pw1")
    user_factory(username="bob", password="pw2")

    client.post("/api/v1/auth/login", json={"username": "alice", "password": "pw1"})
    alice_product = client.post("/api/v1/products", json=_product_payload()).json()
    client.put(
        f"/api/v1/products/{alice_product['id']}/strategy",
        json={"kind": "fix", "config": {"amount": "10.00"}},
    )
    client.post("/api/v1/auth/logout")

    client.post("/api/v1/auth/login", json={"username": "bob", "password": "pw2"})
    assert client.post(f"/api/v1/products/{alice_product['id']}/price").status_code == 404
    assert client.get(f"/api/v1/products/{alice_product['id']}/history").status_code == 404
