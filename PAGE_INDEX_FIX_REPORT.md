# Отчет: Исправление индекса страницы и fallback позиционирования

## 🎯 **Диагноз проблемы:**
```
— /tmp/tmplcuosnwx.pdf, total_pages: 1, page_number: 3 → out of range → fallback (14.2, 14.2);
— /tmp/tmpn7aph9p4.pdf, page_number: 4 → out of range → fallback (14.2, 14.2);
— /tmp/tmp345oec2y.pdf, page_number: 5 → out of range → fallback (14.2, 14.2).
```

**Проблема:** Создается временный одностраничный PDF, но передается исходный номер страницы → Page number out of range → неправильный fallback (14.2, 14.2).

## ✅ **Реализованные исправления:**

### **1. Совмещен индекс страницы при анализе:**

**Было (неправильно):**
```python
# Создаем временный одностраничный PDF
temp_writer = PdfWriter()
temp_writer.add_page(page)  # ← Только 1 страница

# Но передаем исходный номер страницы
x_position, y_position = self._calculate_landscape_qr_position(
    page_width, page_height, qr_size_points, temp_pdf_path, page_number - 1  # ← page_number=3/4/5!
)
# Результат: Page number out of range для одностраничного PDF
```

**Стало (правильно):**
```python
# Создаем временный одностраничный PDF
temp_writer = PdfWriter()
temp_writer.add_page(page)  # ← Только 1 страница

# Передаем правильный номер страницы для одностраничного PDF
x_position, y_position = self._calculate_landscape_qr_position(
    page_width, page_height, qr_size_points, temp_pdf_path, 0  # ← page_number=0 для одностраничного PDF!
)
# Результат: Анализ работает корректно
```

### **2. Правильный fallback:**

**Было (неправильно):**
```python
# Fallback к неправильной позиции (14.2, 14.2) - нижний-левый
bottom_margin_cm = 5.5 + 0.5 + 3.5
right_margin_cm = 3.5 + 0.5
x_position = page_width - right_margin_points - qr_size_points  # ← Неправильная формула
y_position = page_height - bottom_margin_points - qr_size_points  # ← Неправильная формула
```

**Стало (правильно):**
```python
# Fallback: используем правильный якорь bottom-right
x0 = 0.0  # MediaBox границы
y0 = 0.0
x1 = page_width
y1 = page_height

base_x, base_y = self.compute_anchor_xy(
    x0=x0, y0=y0, x1=x1, y1=y1,
    qr_w=qr_size_points,
    qr_h=qr_size_points,
    margin_pt=settings.QR_MARGIN_PT,
    stamp_clearance_pt=settings.QR_STAMP_CLEARANCE_PT,
    rotation=0
)

x_position = base_x  # ← Правильная формула: x1 - margin - qr_w
y_position = base_y  # ← Правильная формула: y0 + margin + clearance
```

### **3. Единый активный бокс:**

**Было (неправильно):**
```python
# Предполагали x0=0, y0=0 для landscape
x0 = 0.0  # ← Неправильно для cropbox с x0 != 0
y0 = 0.0
x1 = page_width
y1 = page_height
```

**Стало (правильно):**
```python
# Используем границы активного бокса из layout_info
if layout_info:
    coordinate_info = layout_info.get("coordinate_info", {})
    active_box = coordinate_info.get("active_box", {})
    x0 = active_box.get("x0", 0.0)  # ← Реальные границы активного бокса
    y0 = active_box.get("y0", 0.0)
    x1 = active_box.get("x1", page_width)
    y1 = active_box.get("y1", page_height)
else:
    # Fallback к MediaBox границам
    x0 = 0.0
    y0 = 0.0
    x1 = page_width
    y1 = page_height
```

## 🔧 **Ключевые принципы:**

### **1. Правильный индекс страницы:**
- **Для одностраничного PDF**: всегда используем `page_number = 0`
- **Для многолистового PDF**: используем исходный `page_number`
- **Никаких "Page number out of range"**

### **2. Правильный fallback:**
- **Всегда используем якорь bottom-right**: `x = x1 - margin - qr_w, y = y0 + margin + clearance`
- **Никаких (14.2, 14.2)** - это нижний-левый
- **Правильная формула от правой границы**

### **3. Единый активный бокс:**
- **Используем реальные границы** активного бокса (x0, y0, x1, y1)
- **Важно для cropbox** с ненулевыми x0
- **Правая граница x1**, а не просто ширина

## 📊 **Результат:**

### **До исправления:**
- ❌ `page_number: 3/4/5` для одностраничного PDF → Page number out of range
- ❌ Fallback (14.2, 14.2) → нижний-левый
- ❌ Предположение x0=0 для всех случаев

### **После исправления:**
- ✅ `page_number: 0` для одностраничного PDF → анализ работает
- ✅ Fallback использует правильный якорь bottom-right
- ✅ Реальные границы активного бокса

## 🎯 **Заключение:**

✅ **Индекс страницы исправлен** - для одностраничного PDF используется page_number=0
✅ **Правильный fallback** - всегда bottom-right якорь, никаких (14.2, 14.2)
✅ **Единый активный бокс** - используются реальные границы (x0, y0, x1, y1)
✅ **Никаких "Page number out of range"**

Теперь система будет корректно анализировать одностраничные PDF и использовать правильный fallback! 🚀
