# PTE-QR System

Система проверки актуальности документов через QR-коды с интеграцией в ENOVIA PLM.

## Описание

PTE-QR обеспечивает на каждом листе PDF-документа машиночитаемую ссылку (QR) на онлайн-проверку актуальности конкретной ревизии документа и страницы.

## Архитектура

- **Backend**: FastAPI + PostgreSQL + Redis
- **Frontend**: React/Next.js с поддержкой темной темы и локализации
- **Аутентификация**: SSO через 3DPassport или OAuth2
- **Интеграция**: ENOVIA PLM через OAuth2
- **Контейнеризация**: Docker

## Структура проекта

```
PTE-QR/
├── backend/           # FastAPI backend
├── frontend/          # React/Next.js frontend
├── docs/             # Документация
├── docker-compose.yml # Локальная разработка
└── README.md
```

## Быстрый старт

1. Клонировать репозиторий
2. Запустить `make setup` для полной настройки системы
3. Открыть http://localhost:80 для frontend
4. API доступно на http://localhost:8000

### Учетные данные по умолчанию

После инициализации базы данных доступны следующие пользователи:

- **Администратор**: `admin` / `admin`
- **Тестовый пользователь**: `user` / `testuser`  
- **Демо пользователь**: `demo_user` / `demo123`

## API Документация

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Конфигурация SSO

Система поддерживает аутентификацию через SSO провайдеры:

### 3DPassport
```env
SSO_PROVIDER=3DPassport
SSO_CLIENT_ID=your_client_id
SSO_CLIENT_SECRET=your_client_secret
SSO_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback
SSO_AUTHORIZATION_URL=https://your-3dpassport-instance.com/oauth/authorize
SSO_TOKEN_URL=https://your-3dpassport-instance.com/oauth/token
SSO_USERINFO_URL=https://your-3dpassport-instance.com/oauth/userinfo
```

### OAuth2
```env
SSO_PROVIDER=OAuth2
SSO_CLIENT_ID=your_client_id
SSO_CLIENT_SECRET=your_client_secret
SSO_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback
SSO_AUTHORIZATION_URL=https://your-oauth2-provider.com/oauth/authorize
SSO_TOKEN_URL=https://your-oauth2-provider.com/oauth/token
SSO_USERINFO_URL=https://your-oauth2-provider.com/oauth/userinfo
```

## Особенности Frontend

- **Темная тема**: Автоматическое переключение между светлой и темной темой
- **Локализация**: Поддержка русского, английского и китайского языков
- **Уведомления**: Система уведомлений для пользователей
- **Адаптивный дизайн**: Оптимизация для мобильных устройств
- **SSO интеграция**: Автоматическая аутентификация через SSO

## Лицензия

Внутренний проект ООО "ПроТех Инжиниринг"
