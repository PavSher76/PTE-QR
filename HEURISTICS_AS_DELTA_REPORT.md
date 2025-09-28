# Отчет: Эвристики как коррекции (дельта)

## 🎯 **Задача:**
"Дальше любой результат pdf_analyzer трактуйте как «коррекцию», а не как новый якорь"

## ✅ **Реализованные изменения:**

### **1. Исправлен метод `_calculate_landscape_qr_position`:**

**Было (неправильно):**
```python
# Get detected positions using new algorithm
free_space = layout_info.get("free_space_3_5cm")
horizontal_line = layout_info.get("horizontal_line_18cm")
right_frame_edge = layout_info.get("right_frame_edge")

# Use new algorithm: search for free space 3.5x3.5 cm
if free_space:
    x_position = free_space["x"]  # ← Использование как полные координаты!
    y_position = free_space["y"]  # ← Использование как полные координаты!
    return x_position, y_position
```

**Стало (правильно):**
```python
# 1. СНАЧАЛА вычисляем базовый якорь bottom-right
base_x, base_y = self.compute_anchor_xy(
    W=page_width,
    H=page_height,
    qr_w=qr_size,
    qr_h=qr_size,
    margin=settings.QR_MARGIN_PT,
    rotation=0,  # Предполагаем поворот 0° для landscape
    anchor=settings.QR_ANCHOR
)

# 2. ПОТОМ получаем дельту от эвристик
dx, dy = self.pdf_analyzer.compute_heuristics_delta(pdf_path, page_number)

# 3. Применяем дельту к базовому якорю
x_position = base_x + dx
y_position = base_y + dy

# 4. Клэмпим координаты в пределах страницы
x_position = max(0, min(x_position, page_width - qr_size))
y_position = max(0, min(y_position, page_height - qr_size))
```

### **2. Удален старый fallback код:**

**Удалено:**
- Старые алгоритмы FALLBACK 1 и FALLBACK 2
- Прямое использование результатов `detect_free_space_3_5cm` как координат
- Сложная логика поиска по рамкам и линиям

**Заменено на:**
- Единый подход: базовый якорь + дельта эвристик
- Простая и предсказуемая логика

### **3. Обновлено логирование:**

**Новый формат для landscape:**
```python
debug_logger.info("🔍 LANDSCAPE - Base anchor + heuristics delta", 
                page=page_number,
                box="media",
                W=page_width,
                H=page_height,
                rot=0,
                anchor=settings.QR_ANCHOR,
                qr=(qr_size, qr_size),
                margin=settings.QR_MARGIN_PT,
                base=(base_x, base_y),      # ← Базовый якорь
                delta=(dx, dy),             # ← Дельта эвристик
                final=(x_position, y_position))  # ← Финальная позиция
```

## 🔧 **Ключевые принципы:**

### **1. Единообразие:**
- **ВСЕ** методы позиционирования используют одинаковую логику
- **ВСЕ** результаты `pdf_analyzer` трактуются как коррекции
- **НИ ОДИН** результат не используется как полные координаты

### **2. Предсказуемость:**
- Базовый якорь всегда вычисляется первым
- Эвристики всегда применяются как дельта
- Финальная позиция = базовый якорь + дельта + клэмп

### **3. Надежность:**
- При любых ошибках используется базовый якорь
- Дельта ограничена ±50 pt
- Координаты всегда в пределах страницы

## 📊 **Результат:**

### **До исправления:**
- `_calculate_unified_qr_position`: ✅ базовый якорь + дельта
- `_calculate_landscape_qr_position`: ❌ прямые координаты от эвристик

### **После исправления:**
- `_calculate_unified_qr_position`: ✅ базовый якорь + дельта
- `_calculate_landscape_qr_position`: ✅ базовый якорь + дельта

## 🎯 **Заключение:**

✅ **Все результаты `pdf_analyzer` теперь трактуются как коррекции**
✅ **Единообразная логика во всех методах позиционирования**
✅ **Предсказуемое поведение: якорь + дельта + клэмп**
✅ **Удален устаревший fallback код**

Система теперь полностью соответствует принципу "эвристики как коррекции"! 🚀
