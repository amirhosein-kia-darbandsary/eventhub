.PHONY: up down test migrate migrate-down seed logs 

up:
	docker compose up --build

down:
	docker compose down

test:
	uv run pytest

migrate:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade base

seed:
	uv run python -m app.db.seed

logs:
	docker compose logs -f api