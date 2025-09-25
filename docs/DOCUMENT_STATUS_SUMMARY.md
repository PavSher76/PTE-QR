# Краткая схема назначения статуса документа

## 🎯 Основные принципы

### Трехуровневая структура:
1. **Документ** (Document) - основной контейнер с уникальным `doc_uid`
2. **Ревизия** (Revision) - версия документа (A, B, C, etc.)
3. **Страница** (Page) - конкретная страница в ревизии

### Ключевые поля для определения статуса:
- `is_actual` - флаг актуальности документа
- `superseded_by` - ID документа, который заменил текущий
- `business_status` - бизнес-статус (APPROVED_FOR_CONSTRUCTION, ACCEPTED_BY_CUSTOMER, etc.)
- `enovia_state` - статус в системе ENOVIA PLM
- `released_at` - дата выпуска документа

## 🔄 Процесс определения статуса

### 1. Сканирование QR-кода
```
QR-код содержит: doc_uid + revision + page + timestamp + signature
```

### 2. Проверка подписи HMAC
```
Верификация подписи для защиты от подделки
```

### 3. Поиск в кэше
```
Ключ кэша: status:{doc_uid}:{revision}:{page}:{auth_status}
TTL: 15 минут
```

### 4. Запрос к базе данных
```sql
SELECT * FROM documents 
WHERE doc_uid = ? AND is_actual = true
```

### 5. Интеграция с ENOVIA
```
GET /api/v1/documents/{doc_uid}/revisions/{revision}
OAuth2 аутентификация
```

### 6. Определение актуальности
```python
def is_actual(document):
    return (
        document.is_actual == True and
        document.superseded_by is None and
        document.enovia_state in ["Released", "AFC", "Accepted", "Approved"] and
        document.released_at is not None
    )
```

## 📊 Статусы документов

### Бизнес-статусы:
- **APPROVED_FOR_CONSTRUCTION** - одобрен для строительства
- **ACCEPTED_BY_CUSTOMER** - принят заказчиком  
- **CHANGES_INTRODUCED_GET_NEW** - внесены изменения, получить новую версию
- **IN_WORK** - в работе

### Статусы ENOVIA:
- **Released** → APPROVED_FOR_CONSTRUCTION
- **AFC** → APPROVED_FOR_CONSTRUCTION
- **Accepted** → ACCEPTED_BY_CUSTOMER
- **Approved** → ACCEPTED_BY_CUSTOMER
- **Obsolete** → CHANGES_INTRODUCED_GET_NEW
- **Superseded** → CHANGES_INTRODUCED_GET_NEW
- **In Work** → IN_WORK
- **Frozen** → IN_WORK

## 🔒 Безопасность

### Аутентифицированные пользователи:
- Полная информация о статусе
- Метаданные документа
- Ссылки на документы
- Информация о создателе

### Неаутентифицированные пользователи:
- Только базовый статус актуальности
- Ограниченные ссылки
- GDPR-совместимый ответ

## 📈 Мониторинг

### Метрики:
- Количество проверок статуса
- Попадания/промахи кэша
- Запросы к ENOVIA
- Время ответа API

### Логирование:
- Все запросы к API
- Ошибки интеграции
- Изменения статусов
- Аудит доступа

## 🚀 Пример использования

### Запрос:
```
GET /api/v1/documents/DOC-001/revisions/A/status?page=1
```

### Ответ (актуальный документ):
```json
{
  "doc_uid": "DOC-001",
  "revision": "A", 
  "page": 1,
  "is_actual": true,
  "business_status": "APPROVED_FOR_CONSTRUCTION",
  "enovia_state": "RELEASED",
  "released_at": "2024-01-15T10:30:00Z",
  "superseded_by": null
}
```

### Ответ (устаревший документ):
```json
{
  "doc_uid": "DOC-001",
  "revision": "A",
  "page": 1, 
  "is_actual": false,
  "business_status": "CHANGES_INTRODUCED_GET_NEW",
  "enovia_state": "SUPERSEDED",
  "superseded_by": "DOC-001-B"
}
```
