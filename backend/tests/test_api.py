"""Tests for the LedgerLens HTTP API surface."""

import pytest
from fastapi.testclient import TestClient

from expense_backend import main
from expense_backend.main import app


@pytest.fixture(autouse=True)
def _reset_store():
    main._expenses.clear()
    main._order.clear()
    yield


client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "expense-backend"


def test_scan_returns_stubbed_fields():
    response = client.post("/api/receipts/scan", json={"image_ref": "mock://receipt-001"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"amount", "merchant", "date", "confidence"}


def test_scan_rejects_empty_ref():
    response = client.post("/api/receipts/scan", json={"image_ref": ""})
    assert response.status_code == 422


def test_create_expense_auto_categorizes():
    payload = {"id": "e1", "amount": 12.5, "merchant": "Starbucks", "date": "2026-11-14"}
    response = client.post("/api/expenses", json=payload)
    assert response.status_code == 201
    assert response.json()["category"] == "dining"


def test_create_expense_conflict():
    payload = {"id": "e1", "amount": 1.0, "merchant": "Other", "date": "2026-11-14"}
    assert client.post("/api/expenses", json=payload).status_code == 201
    assert client.post("/api/expenses", json=payload).status_code == 409


def test_list_expenses_filter_by_category():
    base = {"amount": 5.0, "date": "2026-11-14"}
    client.post("/api/expenses", json={**base, "id": "e1", "merchant": "Starbucks"})
    client.post("/api/expenses", json={**base, "id": "e2", "merchant": "Shell"})
    dining = client.get("/api/expenses", params={"category": "dining"}).json()
    assert [e["id"] for e in dining] == ["e1"]
