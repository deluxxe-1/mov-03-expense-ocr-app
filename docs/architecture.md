# Architecture — LedgerLens

## Goals

1. **Deterministic, testable pipeline**: OCR extraction and categorisation are pure functions that
   can be unit tested without a device or a real OCR engine.
2. **Pluggable OCR**: the scan endpoint depends on an interface, so ML Kit/Tesseract can be added
   later without changing the API.
3. **Confirm-before-save UX**: nothing is persisted until the user validates the extracted fields.

## Components

```
Flutter app (mobile/lib/main.dart)
   │  receipt image / reference
   ▼
FastAPI backend (backend/src/expense_backend/main.py)
   │
   ├─ ocr.scan(image_ref)          → OCRResult(amount, merchant, date, confidence)   [STUB]
   ├─ ocr.categorize(merchant)     → category keyword (groceries, dining, ...)
   ├─ ExpenseStore (in-memory)     → GET/POST /api/expenses
   └─ /health                      → liveness probe
```

## OCR pipeline (stubbed)

`ocr.scan` returns a **deterministic** stub derived from `image_ref` (a stable hash picks from a small
fixture set). This keeps tests reproducible while preserving the exact response shape a real engine
would produce (`amount`, `merchant`, `date`, `confidence`).

## Categorisation

`ocr.categorize(merchant)` lower-cases the merchant name and matches an ordered keyword table
(e.g. "starbucks" → `dining`, "shell" → `transport`). Unmatched merchants fall back to `other`. If
`POST /api/expenses` omits a category, the backend derives it from the merchant.

## Storage

The scaffold uses an in-memory store. The `DATABASE_URL` variable is reserved for a future PostgreSQL
implementation; the endpoint layer only calls `store.list()` / `store.add()`, so swapping the store is
a localised change. On-device, expenses are cached with SQLite + Drift.

## Failure modes

| Failure                | Behaviour                                             |
| ---------------------- | ----------------------------------------------------- |
| Unsupported OCR mode   | `EXPENSE_OCR_MODE != "stub"` raises on startup.       |
| Malformed payload      | HTTP 422 via Pydantic.                                |
| Negative amount        | HTTP 422 (Pydantic `ge=0` constraint).                |
| Server restart         | In-memory expenses are lost — by design for scaffold. |

## Performance notes

- Both `scan` and `categorize` are synchronous, CPU-light, and allocation-bounded.
- Store operations are O(1); listing is O(n) over an ordered list.
