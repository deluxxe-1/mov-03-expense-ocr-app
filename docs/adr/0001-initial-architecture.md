# ADR 0001 — Initial architecture for LedgerLens

- **Status**: Accepted
- **Date**: 2026-11-14
- **Deciders**: LedgerLens maintainers

## Context

We want a receipt-OCR expense manager. The valuable, testable logic is the extraction pipeline and the
categoriser — not the OCR engine itself. The project must be a portfolio-quality scaffold: runnable,
tested backend plus a real mobile screen.

## Decision

1. **Flutter** for the app — a single codebase targeting both iOS and Android with strong camera/OCR plugins.
2. **Python + FastAPI** for the backend — typed models, simple HTTP, easy to test and containerise.
3. **Stubbed OCR** behind a narrow interface, returning deterministic fixture data so tests pass without
   a real engine or image files.
4. **Keyword-based categoriser** — deterministic, explainable, and unit testable.
5. **In-memory storage now, PostgreSQL later** — keeps the scaffold dependency-free while fixing the
   storage interface.
6. **On-device OCR is the production target** (ML Kit/Tesseract); the backend scan endpoint exists so the
   pipeline can be exercised and tested server-side.

## Consequences

- Positive: testable pipeline, no external dependencies, clear extension points.
- Negative: stubbed OCR is not real recognition; in-memory data is not durable (acceptable for scaffold).
- Neutral: PostgreSQL and Drift are referenced but not yet wired.

## Alternatives considered

- **Server-only OCR (Tesseract)**: heavier to deploy; rejected as the default.
- **Cloud OCR APIs (e.g., hosted vision services)**: rejected — cost, latency, and privacy concerns.
- **ML categorisation**: rejected — non-deterministic and harder to test than keywords for a scaffold.
