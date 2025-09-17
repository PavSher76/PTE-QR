# Руководство по установке и настройке PTE-QR

## Содержание

1. [Системные требования](#системные-требования)
2. [Быстрая установка](#быстрая-установка)
3. [Ручная установка](#ручная-установка)
4. [Настройка окружения](#настройка-окружения)
5. [Настройка базы данных](#настройка-базы-данных)
6. [Настройка SSO](#настройка-sso)
7. [Настройка ENOVIA](#настройка-enovia)
8. [Развертывание в продакшене](#развертывание-в-продакшене)
9. [Мониторинг и логирование](#мониторинг-и-логирование)
10. [Устранение неполадок](#устранение-неполадок)

## Системные требования

### Минимальные требования

- **ОС**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **RAM**: 4 GB
- **CPU**: 2 ядра
- **Диск**: 10 GB свободного места
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Рекомендуемые требования

- **ОС**: Linux (Ubuntu 22.04+)
- **RAM**: 8 GB
- **CPU**: 4 ядра
- **Диск**: 50 GB SSD
- **Docker**: 24.0+
- **Docker Compose**: 2.20+

### Сетевые требования

- **Порты**: 80 (HTTP), 443 (HTTPS), 8000 (API), 5432 (PostgreSQL), 6379 (Redis)
- **Интернет**: Доступ к ENOVIA/3DEXPERIENCE и SSO провайдерам
- **Firewall**: Настроить правила для указанных портов

## Быстрая установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd PTE-QR
```

### 2. Запуск системы

```bash
# Запуск всех сервисов
make start

# Или с пересборкой
make rebuild
```

### 3. Проверка работы

- **Frontend**: http://localhost
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Остановка системы

```bash
make stop
```

## Ручная установка

### 1. Установка зависимостей

#### Ubuntu/Debian

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

#### macOS

```bash
# Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка Docker Desktop
brew install --cask docker

# Запуск Docker Desktop
open /Applications/Docker.app
```

#### Windows

1. Скачайте Docker Desktop с официального сайта
2. Установите и запустите Docker Desktop
3. Включите WSL2 (рекомендуется)

### 2. Настройка проекта

```bash
# Клонирование репозитория
git clone <repository-url>
cd PTE-QR

# Создание файла окружения
cp backend/env.example backend/.env

# Редактирование конфигурации
nano backend/.env
```

### 3. Запуск сервисов

```bash
# Сборка образов
docker-compose build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## Настройка окружения

### Файл конфигурации (.env)

Создайте файл `backend/.env` на основе `backend/env.example`:

```env
# База данных
DATABASE_URL=postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr

# Redis
REDIS_URL=redis://:redis_password@redis:6379

# Безопасность
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
QR_HMAC_SECRET=your-qr-hmac-secret-change-in-production

# ENOVIA интеграция
ENOVIA_BASE_URL=https://your-enovia-instance.com
ENOVIA_CLIENT_ID=your-client-id
ENOVIA_CLIENT_SECRET=your-client-secret

# SSO конфигурация
SSO_PROVIDER=3DPassport
SSO_CLIENT_ID=your_sso_client_id
SSO_CLIENT_SECRET=your_sso_client_secret
SSO_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback
SSO_AUTHORIZATION_URL=https://your-sso-provider.com/oauth/authorize
SSO_TOKEN_URL=https://your-sso-provider.com/oauth/token
SSO_USERINFO_URL=https://your-sso-provider.com/oauth/userinfo
SSO_SCOPE=openid profile email

# CORS
ALLOWED_HOSTS=["localhost", "127.0.0.1", "0.0.0.0"]

# Логирование
LOG_LEVEL=INFO
```

### Генерация секретных ключей

```bash
# Генерация SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Генерация JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Генерация QR_HMAC_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Настройка базы данных

### 1. Инициализация базы данных

```bash
# Запуск миграций
docker-compose exec backend alembic upgrade head

# Создание тестовых пользователей
docker-compose exec backend python scripts/create_test_users.py
```

### 2. Проверка подключения

```bash
# Проверка PostgreSQL
docker-compose exec postgres psql -U pte_qr -d pte_qr -c "SELECT version();"

# Проверка Redis
docker-compose exec redis redis-cli ping
```

### 3. Резервное копирование

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U pte_qr pte_qr > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
docker-compose exec -T postgres psql -U pte_qr pte_qr < backup_file.sql
```

## Настройка SSO

### 3DPassport

1. **Получите учетные данные** у администратора 3DPassport
2. **Настройте redirect URI**: `http://your-domain:8000/api/v1/auth/callback`
3. **Обновите конфигурацию**:

```env
SSO_PROVIDER=3DPassport
SSO_CLIENT_ID=your_3dpassport_client_id
SSO_CLIENT_SECRET=your_3dpassport_client_secret
SSO_REDIRECT_URI=http://your-domain:8000/api/v1/auth/callback
SSO_AUTHORIZATION_URL=https://your-3dpassport-instance.com/oauth/authorize
SSO_TOKEN_URL=https://your-3dpassport-instance.com/oauth/token
SSO_USERINFO_URL=https://your-3dpassport-instance.com/oauth/userinfo
```

### OAuth2 (общий)

1. **Настройте OAuth2 провайдера**
2. **Обновите конфигурацию**:

```env
SSO_PROVIDER=OAuth2
SSO_CLIENT_ID=your_oauth2_client_id
SSO_CLIENT_SECRET=your_oauth2_client_secret
SSO_REDIRECT_URI=http://your-domain:8000/api/v1/auth/callback
SSO_AUTHORIZATION_URL=https://your-oauth2-provider.com/oauth/authorize
SSO_TOKEN_URL=https://your-oauth2-provider.com/oauth/token
SSO_USERINFO_URL=https://your-oauth2-provider.com/oauth/userinfo
```

## Настройка ENOVIA

### 1. Получение учетных данных

Обратитесь к администратору ENOVIA для получения:
- URL экземпляра ENOVIA
- Client ID
- Client Secret
- Разрешения на доступ к API

### 2. Настройка конфигурации

```env
ENOVIA_BASE_URL=https://your-enovia-instance.com
ENOVIA_CLIENT_ID=your_enovia_client_id
ENOVIA_CLIENT_SECRET=your_enovia_client_secret
```

### 3. Тестирование подключения

```bash
# Проверка доступности ENOVIA
curl -I https://your-enovia-instance.com

# Тестирование API (требует аутентификации)
docker-compose exec backend python scripts/test_enovia_connection.py
```

## Развертывание в продакшене

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Настройка Docker для продакшена
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Настройка SSL/TLS

```bash
# Создание директории для сертификатов
sudo mkdir -p /etc/nginx/ssl

# Копирование сертификатов
sudo cp your-cert.pem /etc/nginx/ssl/
sudo cp your-key.pem /etc/nginx/ssl/

# Настройка прав доступа
sudo chmod 600 /etc/nginx/ssl/*
sudo chown root:root /etc/nginx/ssl/*
```

### 3. Настройка Nginx

Обновите `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/your-cert.pem;
    ssl_certificate_key /etc/nginx/ssl/your-key.pem;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Настройка мониторинга

```bash
# Запуск с мониторингом
docker-compose -f docker-compose.yml -f monitoring/docker-compose.monitoring.yml up -d
```

### 5. Настройка автозапуска

```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/pte-qr.service
```

```ini
[Unit]
Description=PTE-QR System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/PTE-QR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Включение автозапуска
sudo systemctl enable pte-qr.service
sudo systemctl start pte-qr.service
```

## Мониторинг и логирование

### 1. Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### 2. Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats

# Состояние контейнеров
docker-compose ps
```

### 3. Prometheus + Grafana

```bash
# Запуск мониторинга
docker-compose -f docker-compose.yml -f monitoring/docker-compose.monitoring.yml up -d

# Доступ к Grafana
# http://localhost:3000 (admin/admin)
```

### 4. Ротация логов

```bash
# Настройка logrotate
sudo nano /etc/logrotate.d/pte-qr
```

```
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

## Устранение неполадок

### Проблемы с Docker

**Ошибка "Cannot connect to the Docker daemon":**
```bash
# Перезапуск Docker
sudo systemctl restart docker

# Проверка статуса
sudo systemctl status docker
```

**Ошибка "Port already in use":**
```bash
# Поиск процесса, использующего порт
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# Остановка процесса
sudo kill -9 <PID>
```

### Проблемы с базой данных

**Ошибка подключения к PostgreSQL:**
```bash
# Проверка статуса контейнера
docker-compose ps postgres

# Просмотр логов
docker-compose logs postgres

# Перезапуск базы данных
docker-compose restart postgres
```

**Ошибка миграций:**
```bash
# Сброс миграций
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

### Проблемы с Redis

**Ошибка подключения к Redis:**
```bash
# Проверка статуса
docker-compose ps redis

# Тестирование подключения
docker-compose exec redis redis-cli ping
```

### Проблемы с сетью

**Ошибка CORS:**
```bash
# Проверка настроек CORS в backend/.env
ALLOWED_HOSTS=["your-domain.com", "localhost"]
```

**Ошибка SSL:**
```bash
# Проверка сертификатов
openssl x509 -in /etc/nginx/ssl/your-cert.pem -text -noout

# Проверка конфигурации Nginx
sudo nginx -t
```

### Проблемы с производительностью

**Медленная работа:**
```bash
# Проверка использования ресурсов
docker stats

# Очистка неиспользуемых образов
docker system prune -a

# Увеличение лимитов памяти в docker-compose.yml
```

### Восстановление системы

**Полный сброс:**
```bash
# Остановка всех сервисов
docker-compose down -v

# Удаление всех данных
docker system prune -a --volumes

# Пересборка и запуск
make rebuild
```

## Полезные команды

```bash
# Просмотр всех команд
make help

# Запуск тестов
make test

# Форматирование кода
make format

# Очистка Docker
make clean-docker

# Просмотр логов
make logs

# Перезапуск сервисов
docker-compose restart

# Обновление образов
docker-compose pull
docker-compose up -d
```

---

*Версия документации: 1.0*  
*Дата обновления: 2024*
