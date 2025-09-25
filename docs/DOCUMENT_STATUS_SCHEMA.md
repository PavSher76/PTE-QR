# Схема назначения статуса актуального документа/ревизии/листа

## Обзор системы

Система PTE QR управляет статусами документов на трех уровнях:
1. **Документ** (Document) - основной контейнер
2. **Ревизия** (Revision) - версия документа
3. **Страница** (Page) - конкретная страница в ревизии

## Структура данных

### Модель Document
```sql
CREATE TABLE pte_qr.documents (
    id UUID PRIMARY KEY,
    doc_uid VARCHAR(100) UNIQUE NOT NULL,        -- Уникальный идентификатор документа
    title VARCHAR(500),                          -- Название документа
    description TEXT,                            -- Описание
    document_type VARCHAR(50),                   -- Тип документа
    current_revision VARCHAR(20),                -- Текущая ревизия
    current_page INTEGER,                        -- Текущая страница
    business_status VARCHAR(50),                 -- Бизнес-статус
    enovia_state VARCHAR(50),                    -- Статус в ENOVIA
    is_actual BOOLEAN DEFAULT TRUE,              -- Флаг актуальности
    released_at TIMESTAMP WITH TIME ZONE,        -- Дата релиза
    superseded_by VARCHAR(100),                  -- Заменен документом
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);
```

## Статусы документов

### Business Status (Бизнес-статусы)
```python
class DocumentStatusEnum(str, enum.Enum):
    APPROVED_FOR_CONSTRUCTION = "APPROVED_FOR_CONSTRUCTION"  # Одобрен для строительства
    ACCEPTED_BY_CUSTOMER = "ACCEPTED_BY_CUSTOMER"           # Принят заказчиком
    CHANGES_INTRODUCED_GET_NEW = "CHANGES_INTRODUCED_GET_NEW" # Внесены изменения, получить новую версию
    IN_WORK = "IN_WORK"                                     # В работе
```

### ENOVIA State (Статусы в ENOVIA)
```python
class EnoviaStateEnum(str, enum.Enum):
    RELEASED = "Released"        # Выпущен
    AFC = "AFC"                 # Approved For Construction
    ACCEPTED = "Accepted"       # Принят
    APPROVED = "Approved"       # Одобрен
    OBSOLETE = "Obsolete"       # Устарел
    SUPERSEDED = "Superseded"   # Заменен
    IN_WORK = "In Work"         # В работе
    FROZEN = "Frozen"           # Заморожен
```

## Логика определения актуальности

### 1. Проверка актуальности ревизии
```python
def is_revision_actual(self, revision_data: Dict[str, Any]) -> bool:
    """Проверка актуальности ревизии"""
    maturity_state = revision_data.get("maturityState", "")
    superseded_by = revision_data.get("supersededBy")
    
    # Ревизия актуальна если она выпущена и не заменена
    return (
        maturity_state in ["Released", "AFC", "Accepted", "Approved"]
        and not superseded_by
    )
```

### 2. Маппинг статусов ENOVIA → Business
```python
def map_enovia_state_to_business_status(self, enovia_state: str) -> DocumentStatusEnum:
    """Маппинг статуса ENOVIA в бизнес-статус"""
    mapping = {
        "Released": DocumentStatusEnum.APPROVED_FOR_CONSTRUCTION,
        "AFC": DocumentStatusEnum.APPROVED_FOR_CONSTRUCTION,
        "Accepted": DocumentStatusEnum.ACCEPTED_BY_CUSTOMER,
        "Approved": DocumentStatusEnum.ACCEPTED_BY_CUSTOMER,
        "Obsolete": DocumentStatusEnum.CHANGES_INTRODUCED_GET_NEW,
        "Superseded": DocumentStatusEnum.CHANGES_INTRODUCED_GET_NEW,
        "In Work": DocumentStatusEnum.IN_WORK,
        "Frozen": DocumentStatusEnum.IN_WORK,
    }
    return mapping.get(enovia_state, DocumentStatusEnum.IN_WORK)
```

## Процесс проверки статуса

### API Endpoint: GET /documents/{doc_uid}/revisions/{rev}/status

1. **Валидация параметров**
   - Проверка doc_uid
   - Проверка revision
   - Проверка page (должен быть > 0)

2. **Проверка кэша**
   ```python
   cache_key = f"status:{doc_uid}:{rev}:{page}:{auth_status}"
   cached_status = await cache_service.get(cache_key)
   ```

3. **Поиск документа в БД**
   ```python
   document = db.query(Document).filter(Document.doc_uid == doc_uid).first()
   ```

4. **Определение статуса**
   - Если пользователь аутентифицирован → полная информация
   - Если не аутентифицирован → ограниченная информация (GDPR)

5. **Кэширование результата**
   ```python
   await cache_service.set(cache_key, response_data, ttl=900)  # 15 минут
   ```

## Схема состояний документа

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IN_WORK       │───▶│   RELEASED      │───▶│   SUPERSEDED    │
│   (В работе)    │    │   (Выпущен)     │    │   (Заменен)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FROZEN        │    │   AFC           │    │   OBSOLETE      │
│   (Заморожен)   │    │   (Одобрен)     │    │   (Устарел)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Критерии актуальности

### Документ считается актуальным если:
1. **is_actual = TRUE** в базе данных
2. **superseded_by = NULL** (не заменен другим документом)
3. **enovia_state** в статусе "Released", "AFC", "Accepted", "Approved"
4. **released_at** не NULL (документ был выпущен)

### Документ считается устаревшим если:
1. **is_actual = FALSE**
2. **superseded_by** содержит ID нового документа
3. **enovia_state** в статусе "Obsolete", "Superseded"
4. **business_status = CHANGES_INTRODUCED_GET_NEW**

## Интеграция с ENOVIA

### Получение метаданных документа
```python
async def get_document_meta(self, doc_uid: str) -> Optional[Dict[str, Any]]:
    """Получение метаданных документа из ENOVIA"""
    data = await self._make_request("GET", f"/api/v1/documents/{doc_uid}")
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "number": data.get("number"),
        "type": data.get("type"),
        "created_at": data.get("createdAt"),
        "updated_at": data.get("updatedAt"),
    }
```

### Получение метаданных ревизии
```python
async def get_revision_meta(self, doc_uid: str, revision: str) -> Optional[Dict[str, Any]]:
    """Получение метаданных ревизии из ENOVIA"""
    data = await self._make_request("GET", f"/api/v1/documents/{doc_uid}/revisions/{revision}")
    return {
        "revision": data.get("revision"),
        "maturityState": data.get("maturityState"),
        "supersededBy": data.get("supersededBy"),
        "releasedAt": data.get("releasedAt"),
        "createdAt": data.get("createdAt"),
    }
```

## Безопасность и GDPR

### Аутентифицированные пользователи получают:
- Полную информацию о статусе
- Метаданные документа
- Ссылки на документы
- Информацию о создателе/редакторе

### Неаутентифицированные пользователи получают:
- Только базовую информацию о статусе
- Флаг актуальности
- Ограниченные ссылки
- Уведомление о необходимости аутентификации

## Метрики и мониторинг

### Отслеживаемые метрики:
- `pte_qr_document_status_checks_total` - количество проверок статуса
- `pte_qr_cache_hits_total` - попадания в кэш
- `pte_qr_cache_misses_total` - промахи кэша
- `pte_qr_enovia_requests_total` - запросы к ENOVIA

### Логирование:
- Все запросы к API
- Ошибки интеграции с ENOVIA
- Изменения статусов документов
- Аудит доступа к документам

## Примеры использования

### Проверка статуса документа
```bash
GET /api/v1/documents/DOC-001/revisions/A/status?page=1
```

### Ответ для аутентифицированного пользователя
```json
{
  "doc_uid": "DOC-001",
  "revision": "A",
  "page": 1,
  "business_status": "APPROVED_FOR_CONSTRUCTION",
  "enovia_state": "RELEASED",
  "is_actual": true,
  "released_at": "2024-01-15T10:30:00Z",
  "superseded_by": null,
  "last_modified": "2024-01-15T10:30:00Z",
  "links": {
    "openDocument": "https://enovia.pti.ru/3dspace/document/DOC-001?rev=A",
    "openLatest": null
  },
  "metadata": {
    "created_by": "system",
    "access_level": "full",
    "gdpr_compliant": true
  }
}
```

### Ответ для неаутентифицированного пользователя
```json
{
  "doc_uid": "DOC-001",
  "revision": "A",
  "page": 1,
  "is_actual": true,
  "business_status": "ACTUAL",
  "links": {
    "openDocument": "https://enovia.pti.ru/3dspace/document/DOC-001?rev=A",
    "openLatest": null
  },
  "metadata": {
    "access_level": "limited",
    "gdpr_compliant": true,
    "note": "Limited information due to privacy requirements. Please authenticate for full access."
  }
}
```
