"""LedgerLens FastAPI application.

Exposes a liveness probe, a stubbed receipt-scan endpoint, and an in-memory
expense store with automatic categorisation.
"""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from .ocr import DEFAULT_CATEGORY, categorize, scan

if os.getenv("EXPENSE_OCR_MODE", "stub").strip().lower() != "stub":
    raise RuntimeError("Only EXPENSE_OCR_MODE=stub is supported in this scaffold.")

app = FastAPI(title="LedgerLens Expense API", version="0.1.0")


class ScanRequest(BaseModel):
    """Reference to a receipt image (path or mock URI)."""

    image_ref: str = Field(min_length=1, max_length=1024)


class ScanResponse(BaseModel):
    """Stubbed OCR extraction result."""

    amount: float
    merchant: str
    date: str
    confidence: float


class ExpenseModel(BaseModel):
    """A stored expense record."""

    id: str = Field(min_length=1, max_length=64)
    amount: float = Field(ge=0)
    merchant: str = Field(min_length=1, max_length=200)
    date: str = Field(min_length=1)
    category: str | None = None


_expenses: dict[str, ExpenseModel] = {}
_order: list[str] = []


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker and CI."""

    return {"status": "ok", "service": "expense-backend", "version": app.version}


@app.post("/api/receipts/scan", response_model=ScanResponse)
def scan_receipt(payload: ScanRequest) -> ScanResponse:
    """Return a stubbed OCR result; no real OCR is performed."""

    result = scan(payload.image_ref)
    return ScanResponse(
        amount=result.amount,
        merchant=result.merchant,
        date=result.date,
        confidence=result.confidence,
    )


@app.get("/api/expenses", response_model=list[ExpenseModel])
def list_expenses(category: str | None = None) -> list[ExpenseModel]:
    """List stored expenses, optionally filtered by category."""

    items = [_expenses[expense_id] for expense_id in _order]
    if category:
        items = [item for item in items if item.category == category]
    return items


@app.post("/api/expenses", response_model=ExpenseModel, status_code=201)
def create_expense(payload: ExpenseModel) -> ExpenseModel:
    """Store an expense, deriving the category from the merchant when omitted."""

    if payload.id in _expenses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Expense '{payload.id}' already exists.",
        )
    category = payload.category or categorize(payload.merchant) or DEFAULT_CATEGORY
    expense = payload.model_copy(update={"category": category})
    _expenses[expense.id] = expense
    _order.append(expense.id)
    return expense
