setup:
	uv sync
	docker compose -f docker-compose.dev.yml up -d

test:
	uv run pytest

lint:
	uv run ruff check . --fix

run-control:
	cd services/control_plane && uv run uvicorn main:app --port 8000 --reload

run-gateway:
	cd services/inference_gateway && uv run uvicorn main:app --port 4000 --reload
