# Отчет о реализации патча системы координат

## Выполненные изменения

### 1. **app/utils/pdf_analyzer.py** - Конвертация координат

#### Новые функции:
```python
def to_pdf_point(x_img: float, y_img: float, page_h: float) -> tuple[float, float]:
    """Конвертирует точку из image-СК в PDF-СК"""
    x_pdf = x_img
    y_pdf = page_h - y_img  # Для точки
    return x_pdf, y_pdf

def to_pdf_bbox(x_img: float, y_img: float, obj_w: float, obj_h: float, page_h: float):
    """Конвертирует bbox из image-СК в PDF-СК"""
    x_pdf = x_img
    y_pdf = page_h - (y_img + obj_h)  # Для bbox (верхний левый угол)
    return x_pdf, y_pdf, obj_w, obj_h
```

#### Новый метод для эвристик:
```python
def compute_heuristics_delta(self, pdf_path: str, page_number: int = 0) -> tuple[float, float]:
    """Вычисляет дельту (dx, dy) для коррекции якоря на основе эвристик"""
    # Возвращает дельту для коррекции базового якоря
    # x_final = x_anchor + dx, y_final = y_anchor + dy
```

### 2. **app/services/pdf_service.py** - Расчёт якоря

#### Новая функция:
```python
def compute_anchor_xy(self, W: float, H: float, qr_w: float, qr_h: float, 
                     margin: float, rotation: int, anchor: str = "bottom-right") -> tuple[float, float]:
    """Вычисляет координаты якоря с учетом поворота страницы"""
    
    # Таблица поворотов для bottom-right якоря:
    if rotation == 0:
        x = W - margin - qr_w
        y = margin
    elif rotation == 90:
        x = margin
        y = margin
    elif rotation == 180:
        x = margin
        y = H - margin - qr_h
    elif rotation == 270:
        x = W - margin - qr_w
        y = H - margin - qr_h
    
    # Клэмп координат
    x = max(0, min(x, W - qr_w))
    y = max(0, min(y, H - qr_h))
    
    return x, y
```

### 3. **config/settings** - Фиксированные настройки

Подтверждены настройки в `backend/app/core/config.py`:
```python
QR_ANCHOR: str = "bottom-right"
QR_MARGIN_PT: float = 12.0
QR_POSITION_BOX: str = "media"
QR_RESPECT_ROTATION: bool = True
QR_SUPPORT_PORTRAIT: bool = False
```

### 4. **tests/test_qr_positioning.py** - Регресс-тесты

#### Новый класс тестов:
```python
class TestQRPositioningRotations:
    """Тесты для позиционирования QR кодов с различными поворотами"""
    
    def test_rotation_0_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 0°"""
        
    def test_rotation_90_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 90°"""
        
    def test_rotation_180_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 180°"""
        
    def test_rotation_270_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 270°"""
        
    def test_coordinate_clamping(self, pdf_service):
        """Тест: клэмп координат в пределах страницы"""
        
    def test_heuristics_delta_calculation(self, pdf_analyzer, tmp_path):
        """Тест: вычисление дельты эвристик"""
```

## Поведение эвристик

### Новый подход:
1. **Базовый якорь**: Вычисляется жёстко по таблице поворотов
2. **Эвристики**: Возвращают дельту `(dx, dy)` для мелких коррекций
3. **Финальная позиция**: `x_final = x_anchor + dx, y_final = y_anchor + dy`
4. **Клэмп**: Координаты ограничиваются пределами страницы
5. **Никакого "перескакивания"**: При `anchor=bottom-right` QR не "прыгает" на верх

### Пример использования:
```python
# 1. Вычисляем базовый якорь
base_x, base_y = pdf_service.compute_anchor_xy(W, H, qr_w, qr_h, margin, rotation, anchor)

# 2. Получаем дельту от эвристик
dx, dy = pdf_analyzer.compute_heuristics_delta(pdf_path, page_number)

# 3. Применяем коррекцию
final_x = base_x + dx
final_y = base_y + dy

# 4. Клэмпим координаты
final_x = max(0, min(final_x, W - qr_w))
final_y = max(0, min(final_y, H - qr_h))
```

## Таблица поворотов

| Поворот | X | Y | Описание |
|---------|---|---|----------|
| 0° | `W - margin - qr_w` | `margin` | Нижний правый угол |
| 90° | `margin` | `margin` | Визуальный нижний правый |
| 180° | `margin` | `H - margin - qr_h` | Визуальный нижний правый |
| 270° | `W - margin - qr_w` | `H - margin - qr_h` | Визуальный нижний правый |

## Результаты

### ✅ **Исправлено:**
1. **Конвертация координат**: Правильные формулы для точки и bbox
2. **Жёсткий якорь**: Базовое позиционирование без эвристик
3. **Повороты**: Правильная таблица для всех углов поворота
4. **Клэмп координат**: Защита от выхода за границы страницы
5. **Эвристики как дельта**: Мелкие коррекции вместо замены якоря
6. **Регресс-тесты**: Полное покрытие всех поворотов

### 🎯 **Готово к использованию:**
- Система координат работает корректно
- Повороты обрабатываются правильно
- Эвристики не "ломают" базовое позиционирование
- Все тесты проходят успешно

## Запуск тестов

```bash
# Запуск всех тестов позиционирования
python -m pytest backend/tests/test_qr_positioning.py -v

# Запуск только тестов поворотов
python -m pytest backend/tests/test_qr_positioning.py::TestQRPositioningRotations -v
```

Патч полностью реализован и готов к использованию! 🚀
