"""Stubbed OCR extraction and keyword-based expense categorisation.

No real OCR engine is used: ``scan`` returns a deterministic fixture derived from
the image reference so tests are reproducible while preserving the exact response
shape a real engine (ML Kit / Tesseract) would produce.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

# Deterministic fixtures. The same ``image_ref`` always maps to the same entry.
_FIXTURES: list[dict[str, object]] = [
    {"amount": 12.50, "merchant": "Starbucks", "date": "2026-11-14", "confidence": 0.87},
    {"amount": 48.20, "merchant": "Whole Foods", "date": "2026-11-13", "confidence": 0.91},
    {"amount": 63.00, "merchant": "Shell", "date": "2026-11-12", "confidence": 0.82},
    {"amount": 9.99, "merchant": "Netflix", "date": "2026-11-11", "confidence": 0.95},
    {"amount": 23.75, "merchant": "CVS Pharmacy", "date": "2026-11-10", "confidence": 0.78},
]

# Ordered keyword table: the first matching keyword wins.
_CATEGORY_KEYWORDS: list[tuple[str, str]] = [
    ("starbucks", "dining"),
    ("cafe", "dining"),
    ("restaurant", "dining"),
    ("mcdonald", "dining"),
    ("whole foods", "groceries"),
    ("supermarket", "groceries"),
    ("market", "groceries"),
    ("shell", "transport"),
    ("fuel", "transport"),
    ("petro", "transport"),
    ("uber", "transport"),
    ("netflix", "subscription"),
    ("spotify", "subscription"),
    ("cvs", "health"),
    ("pharmacy", "health"),
    ("walgreen", "health"),
]

DEFAULT_CATEGORY = "other"


@dataclass(frozen=True)
class OCRResult:
    """Fields extracted from a receipt image."""

    amount: float
    merchant: str
    date: str
    confidence: float


def scan(image_ref: str) -> OCRResult:
    """Return a deterministic stubbed OCR result for ``image_ref``."""

    key = (image_ref or "").strip()
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(_FIXTURES)
    fixture = _FIXTURES[index]
    return OCRResult(
        amount=float(fixture["amount"]),
        merchant=str(fixture["merchant"]),
        date=str(fixture["date"]),
        confidence=float(fixture["confidence"]),
    )


def categorize(merchant: str) -> str:
    """Map a merchant name to a spending category using keywords."""

    name = (merchant or "").lower()
    for keyword, category in _CATEGORY_KEYWORDS:
        if keyword in name:
            return category
    return DEFAULT_CATEGORY
