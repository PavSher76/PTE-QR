# PTE-QR System Makefile
# Управление системой и базой данных

.PHONY: help build up down restart logs clean init-db test-db backup-db restore-db

# Default target
help: ## Показать справку
	@echo "PTE-QR System Management"
	@echo "========================"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Docker commands
build: ## Собрать все Docker образы
	@echo "🔨 Building Docker images..."
	docker-compose build

up: ## Запустить все сервисы
	@echo "🚀 Starting services..."
	docker-compose up -d

down: ## Остановить все сервисы
	@echo "🛑 Stopping services..."
	docker-compose down

restart: ## Перезапустить все сервисы
	@echo "🔄 Restarting services..."
	docker-compose restart

logs: ## Показать логи всех сервисов
	@echo "📋 Showing logs..."
	docker-compose logs -f

logs-backend: ## Показать логи backend
	@echo "📋 Backend logs..."
	docker-compose logs -f backend

logs-frontend: ## Показать логи frontend
	@echo "📋 Frontend logs..."
	docker-compose logs -f frontend

logs-db: ## Показать логи базы данных
	@echo "📋 Database logs..."
	docker-compose logs -f postgres

# Database commands
init-db: ## Инициализировать базу данных
	@echo "🗄️ Initializing database..."
	@if [ -f backend/init-scripts/init_database.sh ]; then \
		cd backend/init-scripts && ./init_database.sh; \
	else \
		echo "❌ Database initialization script not found"; \
		exit 1; \
	fi

test-db: ## Тестировать подключение к базе данных
	@echo "🧪 Testing database connection..."
	@docker exec pte-qr-postgres psql -U postgres -d pte_qr -c "SELECT 'Database connection successful' as status;"

backup-db: ## Создать резервную копию базы данных
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@docker exec pte-qr-postgres pg_dump -U postgres pte_qr > backups/pte_qr_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

restore-db: ## Восстановить базу данных из резервной копии
	@echo "📥 Restoring database from backup..."
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Please specify BACKUP_FILE=path/to/backup.sql"; \
		exit 1; \
	fi
	@docker exec -i pte-qr-postgres psql -U postgres pte_qr < $(BACKUP_FILE)
	@echo "✅ Database restored from $(BACKUP_FILE)"

# Development commands
dev: ## Запустить в режиме разработки
	@echo "🛠️ Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-logs: ## Показать логи в режиме разработки
	@echo "📋 Development logs..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Testing commands
test: ## Запустить все тесты
	@echo "🧪 Running tests..."
	@echo "Backend tests..."
	@docker exec pte-qr-backend pytest
	@echo "Frontend tests..."
	@docker exec pte-qr-frontend npm test

test-backend: ## Запустить тесты backend
	@echo "🧪 Running backend tests..."
	@docker exec pte-qr-backend pytest

test-frontend: ## Запустить тесты frontend
	@echo "🧪 Running frontend tests..."
	@docker exec pte-qr-frontend npm test

# Cleanup commands
clean: ## Очистить все контейнеры и образы
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f

clean-all: ## Полная очистка (включая образы)
	@echo "🧹 Full cleanup..."
	docker-compose down -v --rmi all
	docker system prune -af

# Status commands
status: ## Показать статус всех сервисов
	@echo "📊 Service status..."
	docker-compose ps

health: ## Проверить здоровье сервисов
	@echo "🏥 Health check..."
	@echo "Backend health:"
	@curl -s http://localhost:8000/health | jq . || echo "Backend not responding"
	@echo "Frontend health:"
	@curl -s -I http://localhost:80 | head -1 || echo "Frontend not responding"

# Database management
db-shell: ## Подключиться к базе данных
	@echo "🗄️ Connecting to database..."
	docker exec -it pte-qr-postgres psql -U postgres -d pte_qr

db-reset: ## Сбросить базу данных
	@echo "⚠️ Resetting database..."
	@read -p "Are you sure? This will delete all data! (y/N): " confirm && [ "$$confirm" = "y" ]
	docker exec pte-qr-postgres psql -U postgres -c "DROP DATABASE IF EXISTS pte_qr;"
	docker exec pte-qr-postgres psql -U postgres -c "CREATE DATABASE pte_qr;"
	$(MAKE) init-db

# Monitoring commands
monitor: ## Показать мониторинг ресурсов
	@echo "📊 Resource monitoring..."
	@echo "Docker stats:"
	@docker stats --no-stream
	@echo ""
	@echo "Disk usage:"
	@docker system df

# Setup commands
setup: ## Первоначальная настройка системы
	@echo "⚙️ Setting up PTE-QR system..."
	$(MAKE) build
	$(MAKE) up
	@echo "⏳ Waiting for services to start..."
	@sleep 30
	$(MAKE) init-db
	@echo "✅ Setup completed!"
	@echo "🌐 Frontend: http://localhost:80"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

# Production commands
prod-build: ## Собрать для продакшена
	@echo "🏭 Building for production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Запустить в продакшене
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Utility commands
update: ## Обновить зависимости
	@echo "📦 Updating dependencies..."
	@echo "Backend dependencies..."
	@docker exec pte-qr-backend pip install --upgrade -r requirements.txt
	@echo "Frontend dependencies..."
	@docker exec pte-qr-frontend npm update

version: ## Показать версии компонентов
	@echo "📋 Component versions..."
	@echo "Docker Compose:"
	@docker-compose --version
	@echo "Docker:"
	@docker --version
	@echo "Backend Python:"
	@docker exec pte-qr-backend python --version
	@echo "Frontend Node:"
	@docker exec pte-qr-frontend node --version
