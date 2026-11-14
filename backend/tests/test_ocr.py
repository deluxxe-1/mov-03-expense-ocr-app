"""Unit tests for the stubbed OCR and categoriser."""

from expense_backend.ocr import DEFAULT_CATEGORY, categorize, scan


def test_scan_is_deterministic():
    first = scan("mock://receipt-001")
    second = scan("mock://receipt-001")
    assert first == second


def test_scan_returns_expected_shape():
    result = scan("mock://receipt-42")
    assert result.amount > 0
    assert result.merchant
    assert len(result.date) == 10  # YYYY-MM-DD
    assert 0.0 <= result.confidence <= 1.0


def test_categorize_known_merchants():
    assert categorize("Starbucks Coffee") == "dining"
    assert categorize("Whole Foods Market") == "groceries"
    assert categorize("Shell Station") == "transport"
    assert categorize("Netflix.com") == "subscription"
    assert categorize("CVS Pharmacy") == "health"


def test_categorize_is_case_insensitive():
    assert categorize("STARBUCKS") == "dining"


def test_categorize_unknown_merchant_falls_back():
    assert categorize("Totally Unknown Vendor") == DEFAULT_CATEGORY
    assert categorize("") == DEFAULT_CATEGORY
