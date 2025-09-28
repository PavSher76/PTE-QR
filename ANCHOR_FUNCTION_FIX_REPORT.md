# Отчет: Исправление единой функции якоря (визуально bottom-right)

## 🎯 **Задача:**
Реализовать единую функцию якоря с правильными границами бокса (x0, y0, x1, y1) для визуального bottom-right позиционирования.

## ✅ **Реализованные изменения:**

### **1. Обновлена функция `compute_anchor_xy`:**

**Было (неправильно):**
```python
def compute_anchor_xy(self, W: float, H: float, qr_w: float, qr_h: float, 
                     margin: float, rotation: int, anchor: str = "bottom-right"):
    # Использовались только ширина и высота
    if rotation == 0:
        x = W - margin - qr_w  # ← Неправильно для cropbox с x0 != 0
        y = margin
```

**Стало (правильно):**
```python
def compute_anchor_xy(self, x0: float, y0: float, x1: float, y1: float, 
                     qr_w: float, qr_h: float, margin_pt: float, 
                     stamp_clearance_pt: float, rotation: int):
    # Границы активного бокса (mediabox/cropbox):
    W = x1 - x0
    H = y1 - y0
    
    # Визуально "низ-право" после учёта rotation:
    if rotation == 0:
        x = x1 - margin_pt - qr_w            # <— ОТ ПРАВОЙ ГРАНИЦЫ!
        y = y0 + margin_pt + stamp_clearance_pt
    elif rotation == 180:
        x = x0 + margin_pt
        y = y1 - margin_pt - qr_h - stamp_clearance_pt
    elif rotation == 90:
        x = x0 + margin_pt
        y = y0 + margin_pt + stamp_clearance_pt
    elif rotation == 270:
        x = x1 - margin_pt - qr_w
        y = y1 - margin_pt - qr_h - stamp_clearance_pt
    
    # Клэмп в пределах бокса:
    x = max(x0, min(x, x1 - qr_w))
    y = max(y0, min(y, y1 - qr_h))
```

### **2. Добавлена настройка `QR_STAMP_CLEARANCE_PT`:**

```python
# В config.py:
QR_STAMP_CLEARANCE_PT: float = 0.0  # Additional clearance from stamp in points
```

### **3. Обновлены все вызовы функции:**

**Все вызовы теперь используют границы активного бокса:**
```python
# Получаем границы активного бокса
x0 = active_box.get("x0", float(page.mediabox.x0))
y0 = active_box.get("y0", float(page.mediabox.y0))
x1 = active_box.get("x1", float(page.mediabox.x1))
y1 = active_box.get("y1", float(page.mediabox.y1))

# Вызываем функцию с правильными границами
base_x, base_y = self.compute_anchor_xy(
    x0=x0, y0=y0, x1=x1, y1=y1,
    qr_w=qr_size,
    qr_h=qr_size,
    margin_pt=settings.QR_MARGIN_PT,
    stamp_clearance_pt=settings.QR_STAMP_CLEARANCE_PT,
    rotation=rotation
)
```

### **4. Обновлено логирование:**

**Новый формат с границами бокса:**
```python
debug_logger.info("🔍 COORDINATE PIPELINE AUDIT - Detailed calculation", 
                page=page_number,
                box=coordinate_info.get("active_box_type", "media"),
                x0=x0, x1=x1, y0=y0, y1=y1,  # ← Границы бокса
                W=x1-x0, H=y1-y0,            # ← Размеры
                rot=rotation,
                qr=(qr_size, qr_size),
                margin=settings.QR_MARGIN_PT,
                stamp_clearance=settings.QR_STAMP_CLEARANCE_PT,
                anchor=(base_x, base_y),
                delta=(dx, dy),
                final=(x_position, y_position))
```

### **5. Исправлен клэмп координат:**

**Было (неправильно):**
```python
x_position = max(0, min(x_position, page_width - qr_size))
y_position = max(0, min(y_position, page_height - qr_size))
```

**Стало (правильно):**
```python
x_position = max(x0, min(x_position, x1 - qr_size))
y_position = max(y0, min(y_position, y1 - qr_size))
```

## 🔧 **Ключевые принципы:**

### **1. Правильные границы:**
- **Используются x0, y0, x1, y1** активного бокса
- **Формула x = x1 - margin - qr_w** для rotation=0
- **Никаких смещений влево** при cropbox с x0 != 0

### **2. Визуальный bottom-right:**
- **rotation=0**: x=x1-margin-qr_w, y=y0+margin+clearance
- **rotation=180**: x=x0+margin, y=y1-margin-qr_h-clearance
- **rotation=90**: x=x0+margin, y=y0+margin+clearance
- **rotation=270**: x=x1-margin-qr_w, y=y1-margin-qr_h-clearance

### **3. Клэмп в пределах бокса:**
- **x = max(x0, min(x, x1 - qr_w))**
- **y = max(y0, min(y, y1 - qr_h))**

## 📊 **Результат:**

### **До исправления:**
- ❌ `x = W - margin - qr_w` (неправильно для cropbox)
- ❌ Смещение влево при cropbox.x0 != 0
- ❌ Клэмп от 0 вместо x0

### **После исправления:**
- ✅ `x = x1 - margin - qr_w` (правильно от правой границы)
- ✅ Никакого смещения влево
- ✅ Клэмп в пределах активного бокса

## 🎯 **Заключение:**

✅ **Единая функция якоря реализована**
✅ **Правильные границы бокса (x0, y0, x1, y1)**
✅ **Визуальный bottom-right для всех поворотов**
✅ **Клэмп в пределах активного бокса**
✅ **Детальное логирование с границами**

Теперь QR коды будут позиционироваться правильно от правой границы активного бокса! 🚀
