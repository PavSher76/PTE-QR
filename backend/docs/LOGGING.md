# Система логирования PTE-QR Backend

## Обзор

В проекте PTE-QR Backend реализована расширенная система структурированного логирования с использованием `structlog`. Система обеспечивает детальное логирование всех операций для отладки и мониторинга.

## Конфигурация

### Основные настройки

```python
# app/core/config.py
LOG_LEVEL: str = "DEBUG"           # Уровень логирования
LOG_FORMAT: str = "json"           # Формат: json или text
LOG_FILE: str = "logs/app.log"     # Путь к файлу логов
LOG_MAX_SIZE: int = 10 * 1024 * 1024  # Максимальный размер файла (10MB)
LOG_BACKUP_COUNT: int = 5          # Количество резервных файлов
```

### Инициализация

```python
from app.core.logging import configure_logging, get_logger

# Настройка логирования
configure_logging()

# Получение логгера
logger = get_logger(__name__)
```

## Компоненты системы логирования

### 1. DebugLogger

Расширенный логгер с поддержкой контекста:

```python
from app.core.logging import DebugLogger

debug_logger = DebugLogger(__name__)

# Логирование с контекстом
debug_logger.bind(user_id="123", session_id="abc").info("User action", action="login")

# Различные уровни логирования
debug_logger.debug("Debug message", param="value")
debug_logger.info("Info message", param="value")
debug_logger.warning("Warning message", param="value")
debug_logger.error("Error message", param="value")
debug_logger.exception("Exception message", param="value")
```

### 2. Специализированные функции логирования

#### Логирование вызовов функций

```python
from app.core.logging import log_function_call, log_function_result

def my_function(param1, param2):
    log_function_call("my_function", param1=param1, param2=param2)
    
    # Выполнение функции
    result = process_data(param1, param2)
    
    log_function_result("my_function", result=result)
    return result
```

#### Логирование API запросов

```python
from app.core.logging import log_api_request, log_api_response

# В начале обработки запроса
log_api_request("POST", "/api/endpoint", client_ip="192.168.1.1", user_agent="Mozilla/5.0")

# В конце обработки запроса
log_api_response(200, 0.5, response_size=1024)
```

#### Логирование операций с файлами

```python
from app.core.logging import log_file_operation

log_file_operation("read", "/path/to/file.pdf", file_size=1024000)
log_file_operation("write", "/path/to/output.pdf", file_size=2048000)
```

#### Логирование операций с базой данных

```python
from app.core.logging import log_database_operation

log_database_operation("SELECT", "users", query="SELECT * FROM users WHERE active = true")
log_database_operation("INSERT", "documents", record_count=1)
```

#### Логирование внешних сервисов

```python
from app.core.logging import log_external_service_call

log_external_service_call("ENOVIA", "/api/documents", method="GET", status_code=200)
```

#### Логирование кэша

```python
from app.core.logging import log_cache_operation

log_cache_operation("get", "user:123", hit=True)
log_cache_operation("set", "user:123", ttl=3600)
```

## Логирование в сервисах

### PDF Service

```python
class PDFService:
    def __init__(self):
        log_function_call("PDFService.__init__")
        # Инициализация
        debug_logger.info("PDFService initialized", output_dir=self.output_dir)
        log_function_result("PDFService.__init__", output_dir=self.output_dir)
    
    async def process_pdf_with_qr_codes(self, pdf_path, enovia_id, ...):
        log_function_call("PDFService.process_pdf_with_qr_codes", 
                         pdf_path=pdf_path, enovia_id=enovia_id)
        
        try:
            debug_logger.info("Starting PDF processing", enovia_id=enovia_id)
            
            # Проверка файла
            if not os.path.exists(pdf_path):
                debug_logger.error("PDF file not found", pdf_path=pdf_path)
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            log_file_operation("read", pdf_path, file_size=os.path.getsize(pdf_path))
            
            # Обработка
            # ...
            
            log_function_result("PDFService.process_pdf_with_qr_codes", 
                               result=result, pages_processed=total_pages)
            return result
            
        except Exception as e:
            debug_logger.exception("Error processing PDF", error=str(e), enovia_id=enovia_id)
            raise
```

### QR Service

```python
class QRService:
    def generate_qr_data(self, enovia_id, revision, page_number):
        log_function_call("QRService.generate_qr_data", 
                         enovia_id=enovia_id, revision=revision, page_number=page_number)
        
        try:
            debug_logger.debug("Generating QR code data", enovia_id=enovia_id)
            
            # Генерация данных
            base_url = f"{url_prefix}/r/{enovia_id}/{revision}/{page_number}"
            debug_logger.debug("Created base URL", base_url=base_url)
            
            # Создание подписи
            # ...
            
            return qr_data
            
        except Exception as e:
            debug_logger.exception("Error generating QR data", error=str(e))
            raise
```

### Auth Service

```python
class AuthService:
    def authenticate_user(self, username, password, db):
        log_function_call("AuthService.authenticate_user", username=username)
        
        try:
            debug_logger.debug("Starting user authentication", username=username)
            
            # Поиск пользователя
            log_database_operation("SELECT", "users", username=username)
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                debug_logger.warning("User not found", username=username)
                return None
            
            # Проверка пароля
            if not self.verify_password(password, user.hashed_password):
                debug_logger.warning("Invalid password", username=username)
                return None
            
            debug_logger.info("User authenticated successfully", username=username, user_id=str(user.id))
            return user
            
        except Exception as e:
            debug_logger.exception("Authentication error", error=str(e), username=username)
            raise
```

## Логирование в API endpoints

### Пример endpoint с логированием

```python
@router.post("/login")
async def login(credentials: dict, request: Request, db: Session = Depends(get_db)):
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_api_request("POST", "/login", client_ip=client_ip, user_agent=user_agent)
    debug_logger.info("Login attempt started", client_ip=client_ip, user_agent=user_agent)

    try:
        username = credentials.get("username")
        password = credentials.get("password")

        debug_logger.debug("Login credentials received", 
                          username=username, 
                          has_password=bool(password),
                          password_length=len(password) if password else 0)

        if not username or not password:
            duration = time.time() - start_time
            debug_logger.warning("Login failed: missing credentials", 
                               username=username, duration=duration)
            log_api_response(422, duration, error="Missing credentials")
            raise HTTPException(status_code=422, detail="Username and password are required")

        # Аутентификация
        user = await auth_service.authenticate_user(username, password, db)
        if not user:
            duration = time.time() - start_time
            debug_logger.warning("Login failed: authentication failed", 
                               username=username, duration=duration)
            log_api_response(401, duration, error="Authentication failed")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Создание токена
        token_response = auth_service.create_token_response(user)
        duration = time.time() - start_time

        debug_logger.info("User logged in successfully", 
                         username=username, user_id=str(user.id), duration=duration)
        log_api_response(200, duration, user_id=str(user.id))

        return token_response

    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        debug_logger.exception("Login error", error=str(e), duration=duration)
        log_api_response(500, duration, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Форматы логов

### JSON формат (по умолчанию)

```json
{
  "event": "User logged in successfully",
  "username": "john.doe",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "duration": 0.234,
  "client_ip": "192.168.1.100",
  "logger": "app.api.endpoints.auth",
  "level": "info",
  "timestamp": "2025-09-23T19:15:21.815698Z"
}
```

### Текстовый формат

```
2025-09-23 19:15:21 [info     ] User logged in successfully username=john.doe user_id=123e4567-e89b-12d3-a456-426614174000 duration=0.234 client_ip=192.168.1.100
```

## Уровни логирования

- **DEBUG**: Детальная информация для отладки
- **INFO**: Общая информация о работе приложения
- **WARNING**: Предупреждения о потенциальных проблемах
- **ERROR**: Ошибки, которые не останавливают работу приложения
- **CRITICAL**: Критические ошибки, требующие немедленного внимания

## Ротация логов

Система автоматически ротирует логи при достижении максимального размера файла:

- Максимальный размер: 10MB
- Количество резервных файлов: 5
- Формат резервных файлов: `app.log.1`, `app.log.2`, и т.д.

## Мониторинг и анализ

### Структурированные логи

Все логи имеют структурированный формат, что позволяет легко анализировать их с помощью инструментов типа:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **Fluentd**
- **Splunk**

### Ключевые поля для анализа

- `timestamp`: Время события
- `level`: Уровень логирования
- `logger`: Источник лога
- `event`: Описание события
- `duration`: Время выполнения операции
- `client_ip`: IP адрес клиента
- `user_id`: ID пользователя
- `request_id`: ID запроса
- `error`: Описание ошибки

## Тестирование логирования

Для тестирования системы логирования используйте:

```bash
cd backend
source venv/bin/activate
python test_logging.py
```

## Рекомендации

1. **Используйте контекст**: Всегда добавляйте релевантный контекст к логам
2. **Избегайте логирования чувствительных данных**: Не логируйте пароли, токены, персональные данные
3. **Используйте правильные уровни**: DEBUG для отладки, INFO для важных событий, ERROR для ошибок
4. **Логируйте исключения**: Используйте `debug_logger.exception()` для логирования исключений с трассировкой
5. **Мониторьте производительность**: Логирование не должно замедлять работу приложения

## Примеры использования

### Отладка проблем с PDF

```python
# В PDF сервисе
debug_logger.debug("Processing page", page_number=page_num + 1, total_pages=total_pages)
debug_logger.debug("Generating QR code data", page_number=page_num + 1)
debug_logger.debug("Adding QR code to page", page_number=page_num + 1)
debug_logger.debug("Page processed successfully", page_number=page_num + 1, qr_codes_created=qr_codes_created)
```

### Мониторинг производительности

```python
# Измерение времени выполнения
start_time = time.time()
# ... выполнение операции ...
duration = time.time() - start_time
debug_logger.info("Operation completed", operation="pdf_processing", duration=duration)
```

### Отслеживание пользовательских действий

```python
# В API endpoints
debug_logger.info("User action", 
                 user_id=str(user.id), 
                 action="document_upload", 
                 document_id=str(document.id),
                 file_size=file_size)
```
