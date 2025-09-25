# ✅ Исправление ошибки позиционирования QR кодов

## 🐛 Проблема
**Ошибка**: `name 'left_margin_cm' is not defined`

## 🔍 Причина
В коде была ссылка на переменную `left_margin_cm`, которая была переименована в `right_margin_cm`, но в логе все еще использовалась старая переменная.

## 🔧 Исправление

### **Файл:** `backend/app/services/pdf_service.py`

#### **Было:**
```python
logger.info(f"Landscape page detected - QR positioned at bottom-left corner: {bottom_margin_cm}cm up from bottom, {left_margin_cm}cm from left edge")
```

#### **Стало:**
```python
logger.info(f"Landscape page detected - QR positioned at bottom-right corner: {bottom_margin_cm}cm up from bottom, {right_margin_cm}cm from right edge")
```

## 📊 Новые параметры позиционирования

### **Y позиция (отступ от низа):**
```python
bottom_margin_cm = 5.5 + 0.5 + 3.5  # 9.5 см
# 5.5 - высота основной надписи
# 0.5 - отступ снизу
# 3.5 - высота QR кода
```

### **X позиция (отступ от правого края):**
```python
right_margin_cm = 3.5 + 0.5  # 4.0 см
# 3.5 - ширина QR кода
# 0.5 - отступ справа
```

### **Расчет координат:**
```python
x_position = page_width - right_margin_points
y_position = page_height - bottom_margin_points
```

## 🧪 Результаты тестирования

### **✅ Успешное тестирование:**
- **Лог**: "Landscape page detected - QR positioned at bottom-right corner: 9.5cm up from bottom, 4.0cm from right edge"
- **Позиционирование**: QR код размещается в правом нижнем углу
- **Ошибки**: Отсутствуют

## 🎉 Результат

**✅ ОШИБКА ИСПРАВЛЕНА:**

1. ✅ **Переменная**: `left_margin_cm` заменена на `right_margin_cm`
2. ✅ **Позиционирование**: QR код размещается в правом нижнем углу
3. ✅ **Логирование**: Корректные сообщения в логах
4. ✅ **Тестирование**: Код работает без ошибок
5. ✅ **Docker**: Работает в контейнере

**Система теперь корректно позиционирует QR коды в правом нижнем углу landscape страниц!**
