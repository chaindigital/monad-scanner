.PHONY: install dev lint fmt test run migrate

install:
	pip install -U pip
	pip install -e .

dev:
	pip install -e ".[dev]"

run:
	python -m scanner.main

migrate:
	alembic upgrade head

lint:
	ruff check src

fmt:
	ruff format src

test:
	pytest -q
