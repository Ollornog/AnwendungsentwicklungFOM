import pytest

pytestmark = pytest.mark.integration


def _valid_product_payload(**overrides):
    base = {
        "name": "Sneaker",
        "category": "Schuhe",
        "cost_price": "29.90",
        "stock": 10,
        "competitor_price": "59.00",
    }
    base.update(overrides)
    return base


def test_list_requires_auth(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 401


def test_create_and_list(authed_client):
    response = authed_client.post("/api/v1/products", json=_valid_product_payload())
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["name"] == "Sneaker"

    listed = authed_client.get("/api/v1/products").json()
    assert len(listed["items"]) == 1
    assert listed["items"][0]["id"] == created["id"]


def test_get_product(authed_client):
    created = authed_client.post("/api/v1/products", json=_valid_product_payload()).json()
    response = authed_client.get(f"/api/v1/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_unknown_product_404(authed_client):
    response = authed_client.get("/api/v1/products/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_product_partial(authed_client):
    created = authed_client.post("/api/v1/products", json=_valid_product_payload()).json()
    response = authed_client.put(f"/api/v1/products/{created['id']}", json={"stock": 99})
    assert response.status_code == 200
    assert response.json()["stock"] == 99
    assert response.json()["name"] == "Sneaker"


def test_update_rejects_negative_stock(authed_client):
    created = authed_client.post("/api/v1/products", json=_valid_product_payload()).json()
    response = authed_client.put(f"/api/v1/products/{created['id']}", json={"stock": -1})
    assert response.status_code == 422


def test_delete_product(authed_client):
    created = authed_client.post("/api/v1/products", json=_valid_product_payload()).json()
    response = authed_client.delete(f"/api/v1/products/{created['id']}")
    assert response.status_code == 204
    assert authed_client.get(f"/api/v1/products/{created['id']}").status_code == 404


def test_ownership_isolation(client, user_factory):
    user_factory(username="alice", password="pw1")
    user_factory(username="bob", password="pw2")

    client.post("/api/v1/auth/login", json={"username": "alice", "password": "pw1"})
    alice_product = client.post("/api/v1/products", json=_valid_product_payload()).json()
    client.post("/api/v1/auth/logout")

    client.post("/api/v1/auth/login", json={"username": "bob", "password": "pw2"})
    assert client.get(f"/api/v1/products/{alice_product['id']}").status_code == 404
    assert client.get("/api/v1/products").json()["items"] == []


def test_create_rejects_invalid_payload(authed_client):
    response = authed_client.post("/api/v1/products", json=_valid_product_payload(cost_price="-1"))
    assert response.status_code == 422


def test_strategy_upsert_creates_and_updates(authed_client):
    product = authed_client.post("/api/v1/products", json=_valid_product_payload()).json()
    pid = product["id"]

    first = authed_client.put(
        f"/api/v1/products/{pid}/strategy",
        json={"kind": "fix", "config": {"amount": "19.99"}},
    )
    assert first.status_code == 200
    assert first.json()["kind"] == "fix"

    updated = authed_client.put(
        f"/api/v1/products/{pid}/strategy",
        json={"kind": "formula", "config": {"expression": "cost_price * 2"}},
    )
    assert updated.status_code == 200
    assert updated.json()["kind"] == "formula"

    detail = authed_client.get(f"/api/v1/products/{pid}").json()
    assert detail["strategy"]["kind"] == "formula"


def test_strategy_rejects_invalid_kind(authed_client):
    product = authed_client.post("/api/v1/products", json=_valid_product_payload()).json()
    response = authed_client.put(
        f"/api/v1/products/{product['id']}/strategy",
        json={"kind": "quantum", "config": {}},
    )
    assert response.status_code == 422
