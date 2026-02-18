setup:
	[ -f .env ] || cp .env.example .env
	uv sync
	docker compose -f docker-compose.dev.yml up -d
	# Wait for DB to be ready and run migrations
	sleep 5
	just migrate

migrate:
	cd packages/database && uv run alembic upgrade head

seed:
	cd packages/database && uv run python -m database.seed

test:
	uv run pytest

lint:
	uv run ruff check . --fix

run-control:
	cd services/control_plane && uv run uvicorn main:app --port 8000 --reload

run-gateway:
	cd services/inference_gateway && uv run uvicorn main:app --port 4000 --reload
