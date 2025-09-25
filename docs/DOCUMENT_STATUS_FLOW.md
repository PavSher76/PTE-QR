# Диаграмма потока назначения статуса документа

## Общая схема системы

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PTE QR DOCUMENT STATUS SYSTEM                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   QR CODE       │    │   API REQUEST   │    │   DATABASE      │    │   ENOVIA PLM    │
│   SCANNER       │───▶│   PROCESSING    │───▶│   LOOKUP        │───▶│   INTEGRATION   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DOC_UID       │    │   VALIDATION    │    │   DOCUMENT      │    │   REVISION      │
│   REVISION      │    │   CACHING       │    │   STATUS        │    │   METADATA      │
│   PAGE          │    │   AUTH CHECK    │    │   LOOKUP        │    │   FETCH         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Детальный поток обработки

```
                    ┌─────────────────────────────────────────┐
                    │           QR CODE SCAN                  │
                    │  doc_uid: DOC-001                      │
                    │  revision: A                           │
                    │  page: 1                               │
                    │  timestamp: 1642234567                 │
                    │  signature: abc123...                  │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │        SIGNATURE VERIFICATION           │
                    │  HMAC verification of QR signature     │
                    │  Timestamp validation                  │
                    │  Document existence check              │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         CACHE LOOKUP                   │
                    │  Key: status:DOC-001:A:1:auth          │
                    │  TTL: 15 minutes                       │
                    │  Cache hit/miss decision               │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │       DATABASE QUERY                   │
                    │  SELECT * FROM documents               │
                    │  WHERE doc_uid = 'DOC-001'            │
                    │  AND is_actual = true                  │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │      ENOVIA INTEGRATION                │
                    │  GET /api/v1/documents/DOC-001         │
                    │  GET /api/v1/documents/DOC-001/revisions/A │
                    │  OAuth2 authentication                 │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │      STATUS DETERMINATION              │
                    │  maturityState: "Released"             │
                    │  supersededBy: null                    │
                    │  releasedAt: "2024-01-15T10:30:00Z"    │
                    │  is_actual: true                       │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │       RESPONSE GENERATION              │
                    │  Business status mapping               │
                    │  GDPR compliance check                 │
                    │  Link generation                       │
                    │  Metadata enrichment                   │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         CACHE STORAGE                  │
                    │  Store result in cache                 │
                    │  Set TTL to 15 minutes                 │
                    │  Update metrics                        │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         API RESPONSE                   │
                    │  Return status information             │
                    │  Include links and metadata            │
                    │  Log metrics and audit                 │
                    └─────────────────────────────────────────┘
```

## Схема состояний документа

```
                    ┌─────────────────────────────────────────┐
                    │           DOCUMENT LIFECYCLE            │
                    └─────────────────────────────────────────┘

    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   DRAFT     │───▶│   IN_WORK   │───▶│   FROZEN    │───▶│   RELEASED  │
    │   (Черновик)│    │   (В работе)│    │(Заморожен)  │    │  (Выпущен)  │
    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
            │                   │                   │                   │
            │                   │                   │                   │
            ▼                   ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   REJECTED  │    │   REVIEW    │    │   APPROVED  │    │   AFC       │
    │  (Отклонен) │    │  (На обзоре)│    │ (Одобрен)   │    │(Одобрен для │
    │             │    │             │    │             │    │ строительства)│
    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
            │                   │                   │                   │
            │                   │                   │                   │
            ▼                   ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   OBSOLETE  │    │   SUPERSEDED│    │   ACCEPTED  │    │   ACTUAL    │
    │   (Устарел) │    │   (Заменен) │    │ (Принят)    │    │ (Актуальный)│
    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Маппинг статусов ENOVIA → Business

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           STATUS MAPPING TABLE                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────────────────────────────────────────────┐
│   ENOVIA STATE  │    │                BUSINESS STATUS                          │
├─────────────────┤    ├─────────────────────────────────────────────────────────┤
│   Released      │───▶│   APPROVED_FOR_CONSTRUCTION                            │
│   AFC           │───▶│   APPROVED_FOR_CONSTRUCTION                            │
│   Accepted      │───▶│   ACCEPTED_BY_CUSTOMER                                │
│   Approved      │───▶│   ACCEPTED_BY_CUSTOMER                                │
│   Obsolete      │───▶│   CHANGES_INTRODUCED_GET_NEW                          │
│   Superseded    │───▶│   CHANGES_INTRODUCED_GET_NEW                          │
│   In Work       │───▶│   IN_WORK                                             │
│   Frozen        │───▶│   IN_WORK                                             │
└─────────────────┘    └─────────────────────────────────────────────────────────┘
```

## Критерии актуальности

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ACTUALITY CRITERIA                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────┐
                    │         DOCUMENT IS ACTUAL              │
                    │                                         │
                    │  ✓ is_actual = TRUE                    │
                    │  ✓ superseded_by = NULL                │
                    │  ✓ enovia_state in [Released, AFC,     │
                    │    Accepted, Approved]                  │
                    │  ✓ released_at IS NOT NULL             │
                    │  ✓ maturityState in [Released, AFC,    │
                    │    Accepted, Approved]                  │
                    └─────────────────────────────────────────┘

                    ┌─────────────────────────────────────────┐
                    │       DOCUMENT IS OUTDATED              │
                    │                                         │
                    │  ✗ is_actual = FALSE                   │
                    │  ✗ superseded_by IS NOT NULL           │
                    │  ✗ enovia_state in [Obsolete,          │
                    │    Superseded]                          │
                    │  ✗ business_status =                   │
                    │    CHANGES_INTRODUCED_GET_NEW          │
                    └─────────────────────────────────────────┘
```

## Интеграция с ENOVIA PLM

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ENOVIA INTEGRATION FLOW                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OAUTH2        │    │   DOCUMENT      │    │   REVISION      │    │   STATUS        │
│   AUTHENTICATION│───▶│   METADATA      │───▶│   METADATA      │───▶│   MAPPING       │
│                 │    │   FETCH         │    │   FETCH         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ACCESS TOKEN  │    │   Document ID   │    │   Revision      │    │   Business      │
│   Management    │    │   Title         │    │   Maturity      │    │   Status        │
│   Token Refresh │    │   Type          │    │   State         │    │   Determination │
│   Expiry Check  │    │   Created/Updated│   │   Superseded By │    │   Actual Flag   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Безопасность и GDPR

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SECURITY & GDPR COMPLIANCE                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AUTHENTICATED │    │   UNAUTHENTICATED│   │   GDPR          │    │   AUDIT         │
│   USER          │    │   USER          │    │   COMPLIANCE    │    │   LOGGING       │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Full Access   │    │   Limited       │    │   Data          │    │   Request       │
│   - All status  │    │   Access        │    │   Minimization  │    │   Tracking      │
│   - Metadata    │    │   - Basic       │    │   - Only        │    │   - User        │
│   - Links       │    │     status      │    │     essential   │    │     Actions     │
│   - Creator     │    │   - Limited     │    │     data        │    │   - IP Address  │
│   - Timestamps  │    │     links       │    │   - Consent     │    │   - Timestamps  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Метрики и мониторинг

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           METRICS & MONITORING                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API METRICS   │    │   CACHE METRICS │    │   ENOVIA        │    │   SYSTEM        │
│                 │    │                 │    │   METRICS       │    │   METRICS       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Request Count │    │   Cache Hits    │    │   API Calls     │    │   CPU Usage     │
│   Response Time │    │   Cache Misses  │    │   Response Time │    │   Memory Usage  │
│   Error Rate    │    │   Hit Ratio     │    │   Error Rate    │    │   Disk Usage    │
│   Status Codes  │    │   TTL Expiry    │    │   Auth Failures │    │   Active Conns  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Примеры ответов API

### Аутентифицированный пользователь
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AUTHENTICATED RESPONSE                               │
└─────────────────────────────────────────────────────────────────────────────────┘

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

### Неаутентифицированный пользователь
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         UNAUTHENTICATED RESPONSE                               │
└─────────────────────────────────────────────────────────────────────────────────┘

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
