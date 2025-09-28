# Отчет: Последовательное использование position_box

## 🎯 **Задача:**
"Один «position_box» последовательно - убедиться, что та же коробка (MediaBox/CropBox) используется и для размеров (W,H), и при вставке изображения (иначе возможен сдвиг)."

## ✅ **Реализованные изменения:**

### **1. Исправлен метод `_add_qr_code_to_page`:**

**Было (неправильно):**
```python
# Get page dimensions for audit
page_width = float(page.mediabox.width)  # ← Всегда MediaBox
page_height = float(page.mediabox.height)  # ← Всегда MediaBox

# Use new unified positioning system
x_position, y_position = self._calculate_unified_qr_position(
    page, qr_size, pdf_path, page_number - 1
)
# ↑ Внутри используется active_box.get("width/height") - может быть CropBox!
```

**Стало (правильно):**
```python
# Use new unified positioning system
x_position, y_position = self._calculate_unified_qr_position(
    page, qr_size, pdf_path, page_number - 1
)

# Get page dimensions for audit (используем тот же position_box, что и в расчетах)
layout_info = self.pdf_analyzer.analyze_page_layout(pdf_path, page_number - 1)
if layout_info:
    coordinate_info = layout_info.get("coordinate_info", {})
    active_box = coordinate_info.get("active_box", {})
    page_width = active_box.get("width", float(page.mediabox.width))  # ← Тот же box!
    page_height = active_box.get("height", float(page.mediabox.height))  # ← Тот же box!
    active_box_type = coordinate_info.get("active_box_type", "media")
else:
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    active_box_type = "media"
```

### **2. Исправлен метод `add_qr_codes_to_pdf`:**

**Было (неправильно):**
```python
# Get actual page dimensions from the PDF page
page_width = float(page.mediabox.width)  # ← Всегда MediaBox
page_height = float(page.mediabox.height)  # ← Всегда MediaBox

# Use intelligent positioning with PDF analysis
x_position, y_position = self._calculate_landscape_qr_position(
    page_width, page_height, qr_size_points, temp_pdf_path, page_number - 1
)
# ↑ Внутри используется active_box.get("width/height") - может быть CropBox!
```

**Стало (правильно):**
```python
# Get actual page dimensions from the PDF page (используем тот же position_box, что и в расчетах)
layout_info = self.pdf_analyzer.analyze_page_layout(pdf_path, i)
if layout_info:
    coordinate_info = layout_info.get("coordinate_info", {})
    active_box = coordinate_info.get("active_box", {})
    page_width = active_box.get("width", float(page.mediabox.width))  # ← Тот же box!
    page_height = active_box.get("height", float(page.mediabox.height))  # ← Тот же box!
else:
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
```

### **3. Обновлено логирование:**

**Новый формат с правильным box:**
```python
debug_logger.info("🔍 COORDINATE PIPELINE AUDIT - Before QR insertion", 
                page=page_number,
                box=active_box_type,  # ← Показывает реальный box (media/crop)
                W=page_width,
                H=page_height,
                rotation="TBD",
                qr=(qr_size, qr_size),
                margin="TBD",
                x_position=x_position,
                y_position=y_position,
                x_cm=round(x_position / 28.35, 2),
                y_cm=round(y_position / 28.35, 2))
```

## 🔧 **Ключевые принципы:**

### **1. Последовательность:**
- **ВСЕ** расчеты используют один и тот же `position_box`
- **ВСЕ** вставки используют тот же `position_box`
- **ВСЕ** логи показывают реальный `active_box_type`

### **2. Логика выбора box:**
```python
if position_box == "crop" and cropbox_info:
    active_box = cropbox_info
    active_box_type = "cropbox"
else:
    active_box = mediabox_info
    active_box_type = "mediabox"
```

### **3. Защита от сдвига:**
- Если расчеты используют CropBox, то и вставка использует CropBox
- Если расчеты используют MediaBox, то и вставка использует MediaBox
- Никаких смешений разных box'ов

## 📊 **Результат:**

### **До исправления:**
- Расчеты: могли использовать CropBox (если `position_box="crop"`)
- Вставка: всегда использовала MediaBox
- **Результат**: возможный сдвиг координат ❌

### **После исправления:**
- Расчеты: используют активный box (MediaBox/CropBox)
- Вставка: использует тот же активный box
- **Результат**: никакого сдвига координат ✅

## 🎯 **Заключение:**

✅ **Один position_box используется последовательно**
✅ **Никакого сдвига между расчетами и вставкой**
✅ **Логи показывают реальный active_box_type**
✅ **Защита от смешения MediaBox/CropBox**

Теперь координаты QR кода будут точно соответствовать расчетам! 🚀
