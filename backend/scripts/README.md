# Скрипты проверки сервисов

Этот каталог содержит скрипты для проверки состояния сервисов, необходимых для работы приложения.

## Скрипты

### check_services.py
Основной скрипт для проверки всех сервисов (Redis и PostgreSQL).

**Использование:**
```bash
# С параметрами по умолчанию
python scripts/check_services.py

# С пользовательскими URL
python scripts/check_services.py redis://localhost:6379 postgresql://user:pass@localhost:5432/db

# В CI/CD (без пароля для Redis)
python scripts/check_services.py redis://localhost:6379 postgresql://postgres:postgres@localhost:5432/pte_qr_test
```

### check_redis.py
Специализированный скрипт для тестирования подключения к Redis.

**Использование:**
```bash
# Локальная разработка
python scripts/check_redis.py redis://:redis_password@localhost:6379

# CI/CD (без пароля)
python scripts/check_redis.py redis://localhost:6379
```

### check_db.py
Скрипт для проверки состояния базы данных PostgreSQL.

**Использование:**
```bash
# С переменной окружения
DATABASE_URL=postgresql://user:pass@localhost:5432/db python scripts/check_db.py
```

## Особенности

- **Retry логика**: Все скрипты используют повторные попытки подключения с задержкой
- **Таймауты**: Установлены разумные таймауты для предотвращения зависания
- **Подробные логи**: Детальная информация о процессе проверки
- **CI/CD совместимость**: Поддержка различных конфигураций для локальной разработки и CI

## Переменные окружения

- `DATABASE_URL` - URL подключения к PostgreSQL
- `REDIS_URL` - URL подключения к Redis

## Примеры для разных сред

### Локальная разработка
```bash
python scripts/check_services.py redis://:redis_password@localhost:6379 postgresql://pte_qr:pte_qr_dev@localhost:5432/pte_qr
```

### CI/CD
```bash
python scripts/check_services.py redis://localhost:6379 postgresql://postgres:postgres@localhost:5432/pte_qr_test
```

### Docker Compose
```bash
python scripts/check_services.py redis://:redis_password@redis:6379 postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr
```
