# 📋 Руководство по работе с логами

## ✅ Логи работают!

Логирование в приложении настроено и функционирует корректно. Логи отображаются в JSON формате с эмодзи для удобства чтения.

## 🔍 Как увидеть логи

### 1. В локальной среде

```bash
cd backend
source venv/bin/activate
python -c "
from app.core.logging import configure_logging
configure_logging()
from app.utils.pdf_analyzer import PDFAnalyzer
analyzer = PDFAnalyzer()
analyzer.logger.debug('🔍 Тест debug лога')
analyzer.logger.info('ℹ️ Тест info лога')
"
```

### 2. В Docker контейнере

```bash
docker-compose exec backend python -c "
from app.core.logging import configure_logging
configure_logging()
from app.utils.pdf_analyzer import PDFAnalyzer
analyzer = PDFAnalyzer()
analyzer.logger.debug('🔍 Тест debug лога')
analyzer.logger.info('ℹ️ Тест info лога')
"
```

### 3. Просмотр логов приложения

```bash
# Логи backend контейнера
docker-compose logs backend

# Логи в реальном времени
docker-compose logs -f backend

# Логи с фильтром по уровню
docker-compose logs backend | grep "debug"
```

## 📊 Формат логов

Логи выводятся в JSON формате:

```json
{
  "event": "🔍 Starting stamp detection for landscape page",
  "logger": "app.utils.pdf_analyzer",
  "level": "debug",
  "timestamp": "2025-09-24T20:12:05.577568Z",
  "pdf_path": "/tmp/test_stamp.pdf",
  "page_number": 0
}
```

## 🎯 Уровни логирования

- **DEBUG** 🔍 - Подробная диагностическая информация
- **INFO** ℹ️ - Общая информация о работе
- **WARNING** ⚠️ - Предупреждения
- **ERROR** ❌ - Ошибки

## 🔧 Настройка логирования

### Конфигурация в `app/core/config.py`:

```python
# Logging
LOG_LEVEL: str = "DEBUG"        # Уровень логирования
LOG_FORMAT: str = "json"        # Формат: json или text
LOG_FILE: str = "logs/app.log"  # Файл логов
LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT: int = 5       # Количество backup файлов
```

### Изменение уровня логирования:

```python
# В коде
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Через переменные окружения
export LOG_LEVEL=DEBUG
```

## 📝 Примеры использования

### 1. Тестирование функции детекции штампа

```python
from app.core.logging import configure_logging
configure_logging()
from app.utils.pdf_analyzer import PDFAnalyzer

analyzer = PDFAnalyzer()
result = analyzer.detect_stamp_top_edge_landscape("document.pdf", 0)
# Логи автоматически выводятся в консоль
```

### 2. Просмотр логов файла

```bash
# Локально
tail -f logs/app.log

# В Docker
docker-compose exec backend tail -f logs/app.log
```

### 3. Фильтрация логов

```bash
# Только ошибки
docker-compose logs backend | grep "ERROR"

# Только debug сообщения
docker-compose logs backend | grep "debug"

# Логи конкретного модуля
docker-compose logs backend | grep "pdf_analyzer"
```

## 🚀 Быстрый тест

Для быстрой проверки работы логов:

```bash
# Локально
cd backend && source venv/bin/activate && python -c "
from app.core.logging import configure_logging
configure_logging()
from app.utils.pdf_analyzer import PDFAnalyzer
analyzer = PDFAnalyzer()
analyzer.logger.info('✅ Логи работают!')
"

# В Docker
docker-compose exec backend python -c "
from app.core.logging import configure_logging
configure_logging()
from app.utils.pdf_analyzer import PDFAnalyzer
analyzer = PDFAnalyzer()
analyzer.logger.info('✅ Логи работают в Docker!')
"
```

## 📋 Что логируется

### PDF анализатор логирует:
- 🔍 Начало детекции штампа
- 📄 Размеры страницы
- 🖼️ Конвертация изображения
- 📊 Обработка изображения
- 🔍 Детекция краев
- 📐 Детекция контуров
- 🎯 Выбор штампа
- 🔄 Конвертация координат
- ✅ Результат детекции

### Fallback режим логирует:
- 🔄 Использование fallback метода
- 📄 Анализ страницы
- ✅ Результат fallback детекции

## ⚠️ Важные замечания

1. **Инициализация**: Всегда вызывайте `configure_logging()` перед использованием логгеров
2. **Формат**: Логи в JSON формате для структурированной обработки
3. **Уровни**: DEBUG логи показывают максимальную детализацию
4. **Файлы**: Логи также сохраняются в файл `logs/app.log`
5. **Ротация**: Файлы логов автоматически ротируются при достижении 10MB

## 🎉 Статус

✅ **Логи полностью функциональны** - все уровни логирования работают как в локальной среде, так и в Docker контейнере. Подробные debug логи доступны для диагностики процесса распознавания основной надписи.
