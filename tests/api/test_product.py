import json
import pytest


def test_create_product_invalid_json(test_app):
    response = test_app.post("/products/", content=json.dumps({"eid": "something"}))
    assert response.status_code == 422

    response = test_app.post(
        "/products/", content=json.dumps({"eid": "1", "name": "2"})
    )
    assert response.status_code == 422


def test_get_product(test_app, monkeypatch):
    from licensing.crud import product
    test_data = {"id": 1, "eid": "123", "name": "something", "description": "something else"}

    async def mock_get_product(session, eid):
        return test_data

    monkeypatch.setattr(product, "get_product", mock_get_product)

    response = test_app.get("/products/1")
    assert response.status_code == 200
    assert response.json() == test_data