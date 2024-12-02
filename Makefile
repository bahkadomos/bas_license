HOST ?= 0.0.0.0
PORT ?= 8000

start:
    uvicorn --app-dir ./src main:app --host $(HOST) --port $(PORT) --reload
typecheck:
    mypy
lint:
    ruff check
test:
    pytest
keys:
    python ./scripts/generate_keys.py
migrations:
    alembic upgrade head
