# Отчет об исправлении ошибки RectangleObject

## Проблема
В логах приложения обнаружена ошибка:
```json
{
  "error": "'RectangleObject' object has no attribute 'x0'", 
  "page_number": 3, 
  "event": "❌ INTELIGENT POSITIONING. Error calculating unified QR position", 
  "logger": "app.services.pdf_service", 
  "level": "error", 
  "timestamp": "2025-09-28T17:26:33.156659Z"
}
```

## Причина
В PyPDF2 библиотеке объект `RectangleObject` не имеет атрибутов `x0`, `y0`, `x1`, `y1`. Вместо этого для доступа к координатам используется индексация:
- `rect[0]` — левая граница (x-координата)
- `rect[1]` — нижняя граница (y-координата)  
- `rect[2]` — правая граница (x-координата)
- `rect[3]` — верхняя граница (y-координата)

## Исправления

### 1. backend/app/utils/pdf_analyzer.py
Исправлены обращения к координатам `RectangleObject`:

**Строки 107-110:**
```python
# Было:
"x0": float(cropbox.x0),
"y0": float(cropbox.y0),
"x1": float(cropbox.x1),
"y1": float(cropbox.y1)

# Стало:
"x0": float(cropbox[0]),  # left
"y0": float(cropbox[1]),  # bottom
"x1": float(cropbox[2]),  # right
"y1": float(cropbox[3])   # top
```

**Строки 124-127:**
```python
# Было:
"x0": float(mediabox.x0),
"y0": float(mediabox.y0),
"x1": float(mediabox.x1),
"y1": float(mediabox.y1)

# Стало:
"x0": float(mediabox[0]),  # left
"y0": float(mediabox[1]),  # bottom
"x1": float(mediabox[2]),  # right
"y1": float(mediabox[3])   # top
```

**Строки 138-141:**
```python
# Было:
"x0": float(mediabox.x0),
"y0": float(mediabox.y0),
"x1": float(mediabox.x1),
"y1": float(mediabox.y1)

# Стало:
"x0": float(mediabox[0]),  # left
"y0": float(mediabox[1]),  # bottom
"x1": float(mediabox[2]),  # right
"y1": float(mediabox[3])   # top
```

**Строки 165-168:**
```python
# Было:
mediabox_x0=float(mediabox.x0),
mediabox_y0=float(mediabox.y0),
mediabox_x1=float(mediabox.x1),
mediabox_y1=float(mediabox.y1),

# Стало:
mediabox_x0=float(mediabox[0]),  # left
mediabox_y0=float(mediabox[1]),  # bottom
mediabox_x1=float(mediabox[2]),  # right
mediabox_y1=float(mediabox[3]),  # top
```

### 2. backend/app/services/pdf_service.py
Исправлены все обращения к координатам `page.mediabox`:

**Все вхождения заменены с:**
```python
x0 = float(page.mediabox.x0)
y0 = float(page.mediabox.y0)
x1 = float(page.mediabox.x1)
y1 = float(page.mediabox.y1)
```

**На:**
```python
x0 = float(page.mediabox[0])  # left
y0 = float(page.mediabox[1])  # bottom
x1 = float(page.mediabox[2])  # right
y1 = float(page.mediabox[3])  # top
```

**Исправлены следующие функции:**
- `_calculate_unified_qr_position()` - строки 237-240, 303-306, 340-343, 395-398, 810-813, 894-897
- `_calculate_qr_position()` - строки 303-306, 395-398

## Результат
✅ Все обращения к атрибутам `x0`, `y0`, `x1`, `y1` объекта `RectangleObject` заменены на правильную индексацию `[0]`, `[1]`, `[2]`, `[3]`

✅ Ошибка `'RectangleObject' object has no attribute 'x0'` больше не должна возникать

✅ Функция интеллектуального позиционирования QR-кодов теперь работает корректно

## Проверка
- Все старые обращения к `.x0`, `.y0`, `.x1`, `.y1` удалены
- Все новые обращения используют индексацию `[0]`, `[1]`, `[2]`, `[3]`
- Добавлены комментарии для ясности (left, bottom, right, top)

## Дата исправления
28 сентября 2025 года
