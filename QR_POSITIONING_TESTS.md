# Тесты QR позиционирования

## Обзор

Этот документ описывает тесты для проверки корректности позиционирования QR кодов в PDF документах.

## Структура тестов

### 1. Unit тесты (`backend/tests/test_qr_positioning.py`)

**TestQRPositioning** - основные unit тесты:

- `test_bottom_right_anchor_positioning()` - проверка позиционирования внизу справа
- `test_different_anchors_positioning()` - тест всех якорей (bottom-right, bottom-left, top-right, top-left)
- `test_rotation_handling()` - проверка обработки поворотов страницы (0°, 90°, 180°, 270°)
- `test_coordinate_system_consistency()` - проверка консистентности системы координат
- `test_margin_configuration()` - тест настройки отступов
- `test_page_size_handling()` - проверка разных размеров страниц (A4, A3, портрет, ландшафт)

**TestQRPositioningIntegration** - интеграционные тесты:

- `test_full_pdf_processing_pipeline()` - полный пайплайн обработки PDF
- `test_error_handling()` - обработка ошибок

### 2. Тест верификации (`test_qr_positioning_verification.py`)

**Функции:**

- `test_qr_positioning_accuracy()` - проверка точности позиционирования QR кода
- `test_different_anchors()` - тест всех якорей с созданием PDF файлов
- `create_test_pdf_with_frame()` - создание тестового PDF с рамкой

### 3. Скрипт запуска (`run_qr_positioning_tests.py`)

Автоматический запуск всех тестов с выводом результатов.

## Запуск тестов

### Все тесты сразу:
```bash
python run_qr_positioning_tests.py
```

### Только pytest тесты:
```bash
python -m pytest backend/tests/test_qr_positioning.py -v
```

### Только тест верификации:
```bash
python test_qr_positioning_verification.py
```

## Проверяемые параметры

### Точность позиционирования
- **Допуск**: ±1 pt для всех координат
- **Якоря**: bottom-right, bottom-left, top-right, top-left
- **Повороты**: 0°, 90°, 180°, 270°

### Ожидаемые координаты для A4 (612×792 pt)

| Якорь | X (pt) | Y (pt) | X (см) | Y (см) |
|-------|--------|--------|--------|--------|
| bottom-right | 500.8 | 12.0 | 17.7 | 0.4 |
| bottom-left | 12.0 | 12.0 | 0.4 | 0.4 |
| top-right | 500.8 | 680.8 | 17.7 | 24.0 |
| top-left | 12.0 | 680.8 | 0.4 | 24.0 |

### Формулы расчета

**Для bottom-right якоря:**
```python
x = page_width - qr_size - margin
y = margin
```

**Для других якорей:**
```python
# bottom-left
x = margin
y = margin

# top-right  
x = page_width - qr_size - margin
y = page_height - qr_size - margin

# top-left
x = margin
y = page_height - qr_size - margin
```

## Результаты тестов

### Файлы результатов

- `/app/tmp/original_test.pdf` - оригинальный тестовый PDF
- `/app/tmp/result_with_qr.pdf` - PDF с QR кодом
- `/app/tmp/result_*.pdf` - PDF файлы для разных якорей
- `/app/tmp/anchor_test_results.json` - результаты тестирования якорей

### Логи

Все тесты выводят детальную информацию:
- Размеры страницы
- Ожидаемые и фактические координаты
- Разница в координатах
- Статус теста (PASSED/FAILED)

## Конфигурация

Тесты используют настройки из `backend/app/core/config.py`:

```python
QR_ANCHOR: str = "bottom-right"  # Якорь позиционирования
QR_MARGIN_PT: float = 12.0       # Отступ в точках
QR_POSITION_BOX: str = "media"   # Бокс для позиционирования
QR_RESPECT_ROTATION: bool = True # Учет поворота страницы
```

## Устранение неполадок

### Тесты не проходят

1. Проверьте, что все зависимости установлены
2. Убедитесь, что директория `/app/tmp` существует
3. Проверьте логи на наличие ошибок

### Неточное позиционирование

1. Проверьте настройки в `config.py`
2. Убедитесь, что используется правильная система координат
3. Проверьте формулы расчета координат

### Ошибки импорта

1. Убедитесь, что путь `/app` добавлен в `sys.path`
2. Проверьте, что все модули доступны
3. Запустите тесты из корневой директории проекта
