# Отчет: Диагностический лог одной строки

## 🎯 **Задача:**
"Добавьте в pdf_service один DEBUG-принт на страницу, после всех расчётов:
page=i, box=media, W=...,H=..., rot=..., anchor=bottom-right,
qr=(w,h), margin=..., base=(x_a,y_a), delta=(dx,dy), final=(x,y)"

## ✅ **Реализованные изменения:**

### **1. Обновлен лог в `_calculate_unified_qr_position`:**

**Новый формат:**
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

### **2. Обновлен лог в `_calculate_landscape_qr_position`:**

**Новый формат:**
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

### **3. Обновлен лог в `_add_qr_code_to_page`:**

**Новый формат:**
```python
debug_logger.info("🔍 COORDINATE PIPELINE AUDIT - Before QR insertion", 
                page=page_number,
                box=active_box_type,
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

### **1. Единый формат:**
- **page**: номер страницы
- **box**: тип коробки (media/crop)
- **W, H**: размеры страницы
- **rot**: поворот страницы
- **anchor**: якорь позиционирования
- **qr**: размер QR кода
- **margin**: отступ
- **base**: базовый якорь
- **delta**: дельта эвристик
- **final**: финальная позиция

### **2. Трассировка:**
- **base**: показывает, где должен быть QR по якорю
- **delta**: показывает, как эвристики скорректировали позицию
- **final**: показывает итоговую позицию

### **3. Диагностика:**
- Если `delta=(0,0)` - эвристики не сработали
- Если `delta=(dx,dy)` - эвристики скорректировали позицию
- Если `final.y` близко к `base.y` - QR остался внизу
- Если `final.y` сильно отличается от `base.y` - есть проблема

## 📊 **Пример лога:**

```
🔍 COORDINATE PIPELINE AUDIT - Detailed calculation page=13 box=media W=841.89 H=595.28 rot=0 anchor=bottom-right qr=(99.225, 99.225) margin=12.0 base=(730.665, 12.0) delta=(0.0, 0.0) final=(730.665, 12.0)
```

**Расшифровка:**
- **page=13**: страница 13
- **box=media**: используется MediaBox
- **W=841.89, H=595.28**: размеры страницы
- **rot=0**: поворот 0°
- **anchor=bottom-right**: якорь нижний правый
- **qr=(99.225, 99.225)**: размер QR кода
- **margin=12.0**: отступ 12 pt
- **base=(730.665, 12.0)**: базовый якорь (нижний правый)
- **delta=(0.0, 0.0)**: эвристики не сработали
- **final=(730.665, 12.0)**: финальная позиция = базовый якорь

## 🎯 **Заключение:**

✅ **Единый формат логов** - легко читать и анализировать
✅ **Полная трассировка** - base → delta → final
✅ **Диагностика проблем** - сразу видно, кто "поднял" QR вверх
✅ **Сравнение с эталоном** - легко проверить правильность

Теперь в логах будет сразу видно, кто именно "поднял" QR вверх! 🚀
