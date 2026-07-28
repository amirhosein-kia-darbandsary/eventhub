.PHONY: up down test migrate logs

up:
	docker compose up --build

down:
	docker compose down

test:
	uv run pytest

migrate:
	uv run alembic upgrade head

logs:
	docker compose logs -f api