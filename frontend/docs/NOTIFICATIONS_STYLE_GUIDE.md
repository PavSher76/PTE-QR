# Руководство по стилю уведомлений

## Обзор

Система уведомлений PTE-QR Frontend была обновлена для соответствия общему дизайну приложения. Уведомления теперь используют современный дизайн с улучшенной типографикой, цветовой схемой и анимациями.

## Дизайн-система

### Цветовая схема

Уведомления используют цветовую палитру, определенную в `tailwind.config.js`:

- **Success**: `success-*` цвета (зеленые оттенки)
- **Error**: `danger-*` цвета (красные оттенки)  
- **Warning**: `warning-*` цвета (желтые оттенки)
- **Info**: `primary-*` цвета (синие оттенки)

### Типографика

- **Заголовок**: `text-sm font-semibold` - полужирный шрифт для заголовков
- **Сообщение**: `text-sm` - обычный шрифт для описания
- **Цвета текста**: 
  - Светлая тема: `text-gray-900` (заголовок), `text-gray-600` (сообщение)
  - Темная тема: `text-white` (заголовок), `text-gray-300` (сообщение)

## Структура компонента

### Основной контейнер

```tsx
<div className="fixed right-4 top-4 z-50 space-y-3">
```

- **Позиционирование**: Фиксированное в правом верхнем углу
- **Z-index**: 50 для отображения поверх других элементов
- **Отступы**: 3 единицы между уведомлениями

### Карточка уведомления

```tsx
<div className="pointer-events-auto w-full max-w-md overflow-hidden rounded-xl border shadow-lg transition-all duration-300 ease-in-out hover:shadow-xl notification-enter">
```

**Ключевые особенности:**
- **Размер**: Максимальная ширина `max-w-md` (28rem)
- **Скругление**: `rounded-xl` для современного вида
- **Тени**: `shadow-lg` с эффектом `hover:shadow-xl`
- **Анимации**: Плавные переходы и кастомная анимация появления
- **Границы**: Цветные границы в зависимости от типа

### Иконки

Каждый тип уведомления имеет уникальную иконку в круглом контейнере:

```tsx
<div className="flex h-8 w-8 items-center justify-center rounded-full bg-success-100 dark:bg-success-900">
  <svg className="h-5 w-5 text-success-600 dark:text-success-400">
    {/* SVG иконка */}
  </svg>
</div>
```

**Особенности иконок:**
- **Размер контейнера**: 8x8 (32px)
- **Размер иконки**: 5x5 (20px)
- **Фон**: Светлый цвет с темным вариантом для темной темы
- **Цвет иконки**: Соответствует типу уведомления

### Кнопка закрытия

```tsx
<button className="inline-flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:hover:bg-gray-700 dark:hover:text-gray-300">
```

**Особенности кнопки:**
- **Размер**: 8x8 (32px) для удобного нажатия
- **Форма**: Круглая (`rounded-full`)
- **Состояния**: Hover и focus с плавными переходами
- **Доступность**: Поддержка клавиатурной навигации

## Анимации

### CSS анимации

Определены в `globals.css`:

```css
@keyframes slideInFromRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification-enter {
  animation: slideInFromRight 0.3s ease-out forwards;
}
```

### Задержка анимации

```tsx
style={{
  animationDelay: `${index * 100}ms`,
  animationFillMode: 'both',
}}
```

- **Задержка**: 100ms между появлением уведомлений
- **Заполнение**: Анимация сохраняет конечное состояние

## Адаптивность

### Темная тема

Все элементы поддерживают темную тему через классы `dark:`:

```tsx
className="bg-white dark:bg-gray-800 border-success-200 dark:border-success-800"
```

### Мобильные устройства

- **Позиционирование**: Адаптируется для мобильных экранов
- **Размер**: Максимальная ширина ограничена для удобства чтения
- **Отступы**: Оптимизированы для touch-интерфейса

## Использование

### Добавление уведомления

```tsx
const { addNotification } = useNotifications()

addNotification({
  type: 'success',
  title: 'Успешно!',
  message: 'Операция выполнена успешно'
})
```

### Типы уведомлений

```tsx
// Успех
addNotification({
  type: 'success',
  title: 'Успешно',
  message: 'Документ загружен'
})

// Ошибка
addNotification({
  type: 'error',
  title: 'Ошибка',
  message: 'Не удалось загрузить файл'
})

// Предупреждение
addNotification({
  type: 'warning',
  title: 'Внимание',
  message: 'Проверьте данные'
})

// Информация
addNotification({
  type: 'info',
  title: 'Информация',
  message: 'Новая версия доступна'
})
```

## Доступность

### ARIA атрибуты

- **Кнопка закрытия**: `aria-label` через `sr-only` текст
- **Семантическая структура**: Правильная иерархия заголовков
- **Клавиатурная навигация**: Поддержка Tab и Enter

### Screen Reader поддержка

```tsx
<span className="sr-only">{t('notification.dismiss')}</span>
```

## Тестирование

### Unit тесты

Компонент покрыт тестами в `__tests__/NotificationContainer.test.tsx`:

- Рендеринг уведомлений
- Корректные CSS классы
- Обработка кликов
- Доступность
- Анимации

### Запуск тестов

```bash
npm test -- --testPathPattern=NotificationContainer.test.tsx
```

## Стилизация

### Кастомизация цветов

Для изменения цветов обновите `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      success: {
        // Ваши цвета
      },
      danger: {
        // Ваши цвета
      }
    }
  }
}
```

### Кастомизация анимаций

Измените анимации в `globals.css`:

```css
.notification-enter {
  animation: yourCustomAnimation 0.3s ease-out forwards;
}
```

## Лучшие практики

1. **Краткость**: Заголовки и сообщения должны быть краткими
2. **Ясность**: Используйте понятный язык
3. **Контекст**: Предоставляйте достаточно информации для понимания
4. **Действия**: Включайте действия, если необходимо
5. **Время**: Уведомления должны исчезать автоматически

## Примеры

### Успешная обработка документа

```tsx
addNotification({
  type: 'success',
  title: 'Документ обработан',
  message: 'PDF файл "название_документа.pdf" успешно обработан. Создано 15 QR-кодов.'
})
```

### Ошибка валидации

```tsx
addNotification({
  type: 'error',
  title: 'Ошибка валидации',
  message: 'Пожалуйста, выберите PDF файл размером не более 10MB'
})
```

### Предупреждение о сессии

```tsx
addNotification({
  type: 'warning',
  title: 'Сессия истекает',
  message: 'Ваша сессия истечет через 5 минут. Сохраните работу.'
})
```

### Информационное сообщение

```tsx
addNotification({
  type: 'info',
  title: 'Новая функция',
  message: 'Теперь доступна поддержка QR кодов для документов'
})
```

