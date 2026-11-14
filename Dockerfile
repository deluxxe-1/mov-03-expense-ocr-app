FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/src ./backend/src

RUN pip install --upgrade pip && pip install ./backend

RUN useradd --create-home --uid 10001 expense
USER expense

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status == 200 else 1)"

CMD ["uvicorn", "expense_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
