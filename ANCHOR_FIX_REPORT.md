# Отчет об исправлении якоря bottom-right

## 🎯 **Задача:**
Закрепить якорь `bottom-right` и использовать эвристики только как дельту.

## ✅ **Реализованные изменения:**

### **1. Новая логика позиционирования в `_calculate_unified_qr_position`:**

**Было:**
```python
# Использовался старый метод из pdf_analyzer
x_position, y_position = self.pdf_analyzer.compute_qr_anchor(
    page_box=page_box,
    qr_size=qr_size,
    rotation=rotation
)
```

**Стало:**
```python
# 1. СНАЧАЛА вычисляем базовый якорь bottom-right с учетом rotation
base_x, base_y = self.compute_anchor_xy(
    W=page_width,
    H=page_height, 
    qr_w=qr_size,
    qr_h=qr_size,
    margin=settings.QR_MARGIN_PT,
    rotation=rotation,
    anchor=settings.QR_ANCHOR
)

# 2. ПОТОМ получаем дельту от эвристик (если нужно)
dx, dy = self.pdf_analyzer.compute_heuristics_delta(pdf_path, page_number)

# 3. Применяем дельту к базовому якорю
x_position = base_x + dx
y_position = base_y + dy

# 4. Клэмпим координаты в пределах страницы
x_position = max(0, min(x_position, page_width - qr_size))
y_position = max(0, min(y_position, page_height - qr_size))
```

### **2. Обновленное логирование:**

**Новый формат DEBUG логов:**
```python
debug_logger.info("🔍 COORDINATE PIPELINE AUDIT - Detailed calculation", 
                page=page_number,
                box=coordinate_info.get("active_box_type", "media"),
                W=page_width,
                H=page_height,
                rot=rotation,
                anchor=settings.QR_ANCHOR,
                qr=(qr_size, qr_size),
                margin=settings.QR_MARGIN_PT,
                base=(base_x, base_y),      # ← Базовый якорь
                delta=(dx, dy),             # ← Дельта эвристик
                final=(x_position, y_position),  # ← Финальная позиция
                respect_rotation=settings.QR_RESPECT_ROTATION)
```

### **3. Обновленные fallback механизмы:**

**Fallback при отсутствии layout_info:**
```python
# Fallback: используем базовый якорь без эвристик
base_x, base_y = self.compute_anchor_xy(
    W=page_width,
    H=page_height,
    qr_w=qr_size,
    qr_h=qr_size,
    margin=settings.QR_MARGIN_PT,
    rotation=rotation,
    anchor=settings.QR_ANCHOR
)
```

**Fallback при исключении:**
```python
# Fallback: используем базовый якорь без эвристик
base_x, base_y = self.compute_anchor_xy(...)
```

## 🔧 **Ключевые принципы:**

### **1. Жёсткий якорь:**
- Базовый якорь `bottom-right` вычисляется **ПЕРВЫМ**
- Используется правильная таблица поворотов (0°/90°/180°/270°)
- Якорь **НЕ ЗАВИСИТ** от эвристик

### **2. Эвристики как дельта:**
- Эвристики возвращают только **мелкие коррекции** (±50 pt максимум)
- Дельта **НЕ МОЖЕТ** "поднять" QR в верх
- Применяется формула: `final = base + delta`

### **3. Клэмп координат:**
- Финальные координаты ограничиваются в пределах страницы
- `x = max(0, min(x, W - qr_w))`
- `y = max(0, min(y, H - qr_h))`

## 📊 **Ожидаемые результаты:**

### **Для поворота 0°:**
- **Базовый якорь**: `(W - margin - qr_w, margin)`
- **Эвристики**: мелкие коррекции ±50 pt
- **Финальная позиция**: близко к нижнему правому углу

### **Для поворота 90°:**
- **Базовый якорь**: `(margin, margin)` (визуальный нижний правый)
- **Эвристики**: мелкие коррекции ±50 pt
- **Финальная позиция**: близко к визуальному нижнему правому

### **Для поворота 180°:**
- **Базовый якорь**: `(margin, H - margin - qr_h)` (визуальный нижний правый)
- **Эвристики**: мелкие коррекции ±50 pt
- **Финальная позиция**: близко к визуальному нижнему правому

### **Для поворота 270°:**
- **Базовый якорь**: `(W - margin - qr_w, H - margin - qr_h)` (визуальный нижний правый)
- **Эвристики**: мелкие коррекции ±50 pt
- **Финальная позиция**: близко к визуальному нижнему правому

## 🎯 **Заключение:**

✅ **Якорь `bottom-right` закреплен** - всегда вычисляется первым
✅ **Эвристики работают как дельта** - только мелкие коррекции
✅ **Повороты обрабатываются правильно** - визуальный нижний правый угол
✅ **Клэмп координат** - защита от выхода за границы
✅ **Детальное логирование** - полная трассировка процесса

Система теперь работает согласно техническому заданию! 🚀
