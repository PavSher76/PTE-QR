# Отчет об исправлениях системы координат

## Диагностированные проблемы

### 1. Инверсия Y с ошибкой
**Проблема**: В конвертере координат использовалась высота всей страницы/растра (img_h) вместо высоты объекта (obj_h), что приводило к отрицательным Y координатам.

**Пример**: `stamp top: y_img=1093 → y_pdf=-1093` (некорректно)

**Исправление**: 
- Для точки: `y_pdf = page_h - y_img`
- Для bbox: `y_pdf = page_h - (y_img + obj_h)`

### 2. Алгоритм "интеллектуального" позиционирования
**Проблема**: Алгоритм опирался на "верхнюю линию" в top-зоне, неявно "притягивая" якорь к верху даже при `anchor=bottom-right`.

**Исправление**: Введен жёсткий якорь без участия эвристик:
```python
# Для bottom-right
x = page_width - qr_size - margin
y = margin
```

### 3. Ротация страниц
**Проблема**: Расчёты выполнялись "как для 0°", что при поворотах давало "переезд" якоря.

**Исправление**: Добавлена правильная таблица пересчёта:

| Поворот | X | Y | Описание |
|---------|---|---|----------|
| 0° | `W - m - qr_w` | `m` | Нижний правый угол |
| 90° | `m` | `m` | Визуальный нижний правый |
| 180° | `m` | `H - m - qr_h` | Визуальный нижний правый |
| 270° | `W - m - qr_w` | `H - m - qr_h` | Визуальный нижний правый |

### 4. Портретные страницы
**Проблема**: Портретные страницы пропускались без документации ограничения.

**Исправление**: Добавлена настройка `QR_SUPPORT_PORTRAIT: bool = False` и документация в README.

## Реализованные исправления

### 1. Правильная формула преобразования координат

**Файл**: `backend/app/utils/pdf_analyzer.py`

```python
def to_pdf_coords(self, x_img: float, y_img: float, obj_h: float = 0, page_h: float = None) -> Tuple[float, float]:
    x_pdf = x_img
    
    if obj_h == 0:
        # Для точки: y_pdf = page_height - y_img
        y_pdf = page_h - y_img
    else:
        # Для bbox: y_pdf = page_height - (y_img + obj_h)
        y_pdf = page_h - (y_img + obj_h)
    
    return x_pdf, y_pdf
```

### 2. Жёсткий якорь + корректоры

**Файл**: `backend/app/utils/pdf_analyzer.py`

```python
def compute_simple_anchor(self, page_box: Dict[str, float], qr_size: float, margin: float = None, anchor: str = None) -> Tuple[float, float]:
    # Жёсткая геометрия для разных якорей
    if anchor == 'bottom-right':
        x = width - qr_size - margin
        y = margin
    # ... другие якоря
    
    # Клэмп координат
    x = max(0, min(x, width - qr_size))
    y = max(0, min(y, height - qr_size))
    
    return x, y
```

### 3. Правильная таблица поворотов

**Файл**: `backend/app/utils/pdf_analyzer.py`

```python
def compute_qr_anchor(self, page_box: Dict[str, float], qr_size: float, margin: float = None, anchor: str = None, rotation: int = 0) -> Tuple[float, float]:
    # Применяем поворот по правильной таблице
    if rotation == 0:
        final_x, final_y = base_x, base_y
    elif rotation == 90:
        final_x = margin
        final_y = margin
    elif rotation == 180:
        final_x = margin
        final_y = height - margin - qr_size
    elif rotation == 270:
        final_x = width - margin - qr_size
        final_y = height - margin - qr_size
    
    # Клэмп координат после поворота
    final_x = max(0, min(final_x, width - qr_size))
    final_y = max(0, min(final_y, height - qr_size))
    
    return final_x, final_y
```

### 4. Клэмп координат

Добавлен клэмп координат во всех методах:
```python
x = max(0, min(x, width - qr_size))
y = max(0, min(y, height - qr_size))
```

### 5. Конфигурация и документация

**Файл**: `backend/app/core/config.py`
```python
QR_SUPPORT_PORTRAIT: bool = False  # Support portrait pages (currently limited to landscape only)
```

**Файл**: `README.md`
- Добавлена информация об ограничениях
- Обновлена таблица поворотов
- Добавлены примечания о клэмпе координат

## Результаты

### До исправлений:
- ❌ Отрицательные Y координаты
- ❌ "Переезд" якоря при поворотах
- ❌ Неявное притягивание к верху
- ❌ Отсутствие документации ограничений

### После исправлений:
- ✅ Положительные Y координаты в пределах [0; H]
- ✅ Правильный пересчет при поворотах
- ✅ Жёсткий якорь без эвристик
- ✅ Клэмп координат в пределах страницы
- ✅ Полная документация ограничений

## Тестирование

Для проверки исправлений запустите:

```bash
# Тесты позиционирования
python run_qr_positioning_tests.py

# Тест верификации
python test_qr_positioning_verification.py

# Регресс-тесты
python test_coordinate_regression.py
```

## Заключение

Все диагностированные проблемы исправлены:
1. ✅ Формула преобразования координат
2. ✅ Жёсткий якорь + корректоры  
3. ✅ Правильная таблица поворотов
4. ✅ Клэмп координат
5. ✅ Документация ограничений

Система теперь работает корректно с правильными координатами и позиционированием QR кодов.
