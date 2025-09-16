.PHONY: help test test-unit test-integration test-e2e test-cov test-watch clean install lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest -m unit

test-integration: ## Run integration tests only
	pytest -m integration

test-e2e: ## Run end-to-end tests only
	pytest -m e2e

test-cov: ## Run tests with coverage report
	pytest --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	pytest-watch

clean: ## Clean up test artifacts
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf test.db
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

lint: ## Run linting
	flake8 app tests
	black --check app tests
	isort --check-only app tests

format: ## Format code
	black app tests
	isort app tests

run: ## Run the application
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the application in production mode
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

docker-build: ## Build Docker image
	docker build -t pte-qr-backend .

docker-run: ## Run Docker container
	docker run -p 8000:8000 pte-qr-backend

docker-test: ## Run tests in Docker
	docker run --rm pte-qr-backend pytest

setup-dev: install ## Setup development environment
	pre-commit install

ci: lint test-cov ## Run CI pipeline
