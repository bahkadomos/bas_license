start:
	uvicorn --app-dir ./src main:app --host 0.0.0.0 --port 8000 --reload
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
