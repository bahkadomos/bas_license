typecheck:
	mypy
lint:
	ruff check
test:
	pytest
keys:
	python ./scripts/generate_keys.py