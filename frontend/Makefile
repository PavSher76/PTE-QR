# PTE-QR System Makefile
.PHONY: help build up down restart logs init-db test-db setup

help: ## Показать справку
	@echo "PTE-QR System Management"
	@echo "========================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Собрать все Docker образы
	docker-compose build

up: ## Запустить все сервисы
	docker-compose up -d

down: ## Остановить все сервисы
	docker-compose down

restart: ## Перезапустить все сервисы
	docker-compose restart

logs: ## Показать логи всех сервисов
	docker-compose logs -f

init-db: ## Инициализировать базу данных
	cd backend/init-scripts && ./init_database.sh

test-db: ## Тестировать подключение к базе данных
	docker exec pte-qr-postgres psql -U postgres -d pte_qr -c "SELECT 'Database connection successful' as status;"

setup: ## Первоначальная настройка системы
	$(MAKE) build
	$(MAKE) up
	sleep 30
	$(MAKE) init-db
	@echo "✅ Setup completed!"

status: ## Показать статус всех сервисов
	docker-compose ps

health: ## Проверить здоровье сервисов
	curl -s http://localhost:8000/health | jq . || echo "Backend not responding"
	curl -s -I http://localhost:80 | head -1 || echo "Frontend not responding"
