# PTE-QR Project Makefile

.PHONY: help test test-backend test-frontend test-ci setup-db clean-docker

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && docker-compose exec backend pytest -v --cov=app --cov-report=xml

test-frontend: ## Run frontend tests
	cd frontend && npm test -- --coverage --watchAll=false

test-ci: ## Run tests in CI mode (with proper database setup)
	cd backend && \
	docker-compose up -d postgres redis && \
	sleep 10 && \
	PGPASSWORD=postgres psql -h localhost -U postgres -d pte_qr_test -f init_ci_db.sql && \
	DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pte_qr_test \
	REDIS_URL=redis://localhost:6379 \
	pytest -v --cov=app --cov-report=xml

setup-db: ## Setup test database
	cd backend && \
	docker-compose up -d postgres && \
	sleep 5 && \
	docker-compose exec postgres createdb -U pte_qr pte_qr_test && \
	docker cp init_ci_db.sql pte-qr-postgres:/tmp/init_ci_db.sql && \
	docker-compose exec postgres psql -U pte_qr -d pte_qr_test -f /tmp/init_ci_db.sql

clean-docker: ## Clean up Docker containers and volumes
	docker-compose down -v
	docker system prune -f

start: ## Start all services
	docker-compose up -d

stop: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

build: ## Build all Docker images
	docker-compose build

rebuild: clean-docker build start ## Clean, build and start all services