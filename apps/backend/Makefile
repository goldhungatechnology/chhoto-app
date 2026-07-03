PROJECT_NAME ?= chhoto-backend
TEST_PROJECT_NAME ?= $(PROJECT_NAME)-test
TEST_COMPOSE_FILE ?= ../../docker/docker-compose-test.yml

setup:
	@echo "Setting up development environment with uv..."
	uv pip install -r pyproject.toml
	uv run pre-commit install

lint:
	@echo "Running Ruff code linter..."
	uv run ruff check --fix .

format:
	@echo "Running Ruff code formatter..."
	uv run ruff format .

typecheck:
	@echo "Running pyright type checker..."
	uv run pyright

run:
	@echo "Starting the application locally..."
	PYTHONPATH=. ENVIRONMENT=local uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

test:
	@echo "Starting isolated test database with Docker..."
	@set -e; \
	docker compose -p $(TEST_PROJECT_NAME) -f $(TEST_COMPOSE_FILE) up -d; \
	trap 'docker compose -p $(TEST_PROJECT_NAME) -f $(TEST_COMPOSE_FILE) down -v' EXIT; \
	until docker compose -p $(TEST_PROJECT_NAME) -f $(TEST_COMPOSE_FILE) exec -T db_test pg_isready -U postgres -d chhoto_db_test >/dev/null 2>&1; do \
		echo "Waiting for test database to be ready..."; \
		sleep 2; \
	done; \
	echo "Running test suite..."; \
	PYTHONPATH=. ENVIRONMENT=testing LOG_FILE_PATH=.pytest_logs/app.log uv run pytest -v -s tests/

migration:
	@echo "Creating new database migration..."
	MIGRATION_NAME=$(name) uv run alembic revision -m "$(msg)"

migrate:
	@echo "Applying database migrations..."
	uv run alembic upgrade head

downgrade:
	@echo "Rolling back last database migration..."
	uv run alembic downgrade -1

localup:
	@echo "Starting the application with Docker Compose (Local environment)..."
	PROJECT_NAME=$(PROJECT_NAME) docker compose -p $(PROJECT_NAME)-local -f ../../docker/docker-compose.base.yml -f ../../docker/docker-compose.dev.yml up -d

localdown:
	@echo "Stopping the application with Docker Compose..."
	docker compose -p $(PROJECT_NAME)-local -f ../../docker/docker-compose.base.yml -f ../../docker/docker-compose.dev.yml down

localdownv:
	@echo "Stopping the application and removing volumes with Docker Compose..."
	docker compose -p $(PROJECT_NAME)-local -f ../../docker/docker-compose.base.yml -f ../../docker/docker-compose.dev.yml down -v

create-feature:
	@echo "Creating a new feature context structure..."
	@read -p "Enter feature name: " feature_name; \
	feature_dir="src/modules/$$feature_name"; \
	mkdir -p $$feature_dir && \
	touch "$$feature_dir/__init__.py" && \
	subfolders="application domain infrastructure presentation"; \
	for folder in $$subfolders; do \
		mkdir -p "$$feature_dir/$$folder" && \
		touch "$$feature_dir/$$folder/__init__.py"; \
	done; \
	echo "Feature '$$feature_name' structure created successfully!"
