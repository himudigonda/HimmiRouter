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
	uv run uvicorn control_plane.main:app --port 8000 --reload

run-gateway:
	uv run uvicorn inference_gateway.main:app --port 4000 --reload

run-frontend:
	cd apps/dashboard-frontend && bun dev

generate-spec:
	mkdir -p apps/dashboard-frontend/specs
	uv run python -c "import json; from control_plane.main import app; print(json.dumps(app.openapi()))" > apps/dashboard-frontend/specs/openapi-control.json
	uv run python -c "import json; from inference_gateway.main import app; print(json.dumps(app.openapi()))" > apps/dashboard-frontend/specs/openapi-gateway.json

install-frontend: generate-spec
	cd apps/dashboard-frontend && bun install
	cd apps/dashboard-frontend && bun x openapi-typescript-codegen --input specs/openapi-control.json --output ./src/client-control --client fetch
	cd apps/dashboard-frontend && bun x openapi-typescript-codegen --input specs/openapi-gateway.json --output ./src/client-gateway --client fetch

dev:
	# Run this in multiple terminals: just run-control, just run-gateway, just run-frontend
