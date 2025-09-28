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

## Система координат QR позиционирования

### PDF координатная система

Система использует стандартную PDF координатную систему:
- **Origin**: нижний левый угол страницы
- **Единицы**: точки (points, pt), где 1 pt = 1/72 дюйма ≈ 0.353 мм
- **Оси**: X направлена вправо, Y направлена вверх

#### PDF-origin vs Image-origin

В системе используются две координатные системы:

**PDF-СК (PDF Coordinate System):**
- Origin: нижний левый угол (0, 0)
- Y-ось направлена вверх
- Используется для финального позиционирования QR кода

**Image-СК (Image Coordinate System):**
- Origin: верхний левый угол (0, 0) 
- Y-ось направлена вниз
- Используется при анализе растрированных изображений PDF

#### Правила конверсии координат

Для конверсии из Image-СК в PDF-СК используются две функции:

```python
# Для точки (без высоты объекта)
def to_pdf_point(x_img: float, y_img: float, page_h: float) -> Tuple[float, float]:
    """Конвертирует точку из image-СК в PDF-СК"""
    x_pdf = x_img
    y_pdf = page_h - y_img  # Для точки
    return x_pdf, y_pdf

# Для bbox (верхний левый угол объекта)
def to_pdf_bbox(x_img: float, y_img: float, obj_w: float, obj_h: float, page_h: float):
    """Конвертирует bbox из image-СК в PDF-СК"""
    x_pdf = x_img
    y_pdf = page_h - (y_img + obj_h)  # Для bbox
    return x_pdf, y_pdf, obj_w, obj_h
```

**Пример конверсии:**
- Image-СК: (100, 50) - точка на 100px справа, 50px от верха
- PDF-СК: (100, 742) - та же точка, но 742pt от низа (для A4: 792 - 50 = 742)

**Подробная документация:** См. [COORDINATE_FIXES_REPORT.md](COORDINATE_FIXES_REPORT.md) и [PATCH_IMPLEMENTATION_REPORT.md](PATCH_IMPLEMENTATION_REPORT.md)

### Конфигурация позиционирования

В файле `backend/app/core/config.py` доступны следующие настройки:

```python
# QR Code positioning settings
QR_ANCHOR: str = "bottom-right"  # Якорь позиционирования
QR_MARGIN_PT: float = 12.0       # Отступ в точках
QR_POSITION_BOX: str = "media"   # Бокс для позиционирования
QR_RESPECT_ROTATION: bool = True # Учет поворота страницы
QR_DEBUG_FRAME: bool = False     # Отрисовка debug рамки
QR_SUPPORT_PORTRAIT: bool = False # Поддержка портретных страниц
```

#### Ограничения

- **Портретные страницы**: В настоящее время система поддерживает только альбомные страницы. Портретные страницы пропускаются с сообщением "Portrait page detected - skipping QR code placement".
- **Повороты**: Поддерживаются повороты 0°, 90°, 180°, 270° с правильным пересчетом координат.

#### Доступные якоря:
- `bottom-right`: нижний правый угол (по умолчанию)
- `bottom-left`: нижний левый угол
- `top-right`: верхний правый угол
- `top-left`: верхний левый угол

#### Боксы для позиционирования:
- `media`: MediaBox (по умолчанию) - физический размер страницы
- `crop`: CropBox - область отображения (если доступна)

### Примеры позиционирования

#### A4 страница (612×792 pt) без поворота (rotation=0°):
```
bottom-right: (500.8, 12.0) pt  # 12 pt отступ от краев
bottom-left:  (12.0, 12.0) pt
top-right:    (500.8, 680.8) pt
top-left:     (12.0, 680.8) pt
```

#### A4 страница с поворотом 90° (rotation=90°):
```
bottom-right: (12.0, 500.8) pt  # Координаты пересчитаны по таблице поворотов
bottom-left:  (12.0, 12.0) pt
top-right:    (680.8, 500.8) pt
top-left:     (680.8, 12.0) pt
```

#### A4 страница с поворотом 180° (rotation=180°):
```
bottom-right: (12.0, 680.8) pt  # Координаты пересчитаны по таблице поворотов
bottom-left:  (500.8, 680.8) pt
top-right:    (12.0, 12.0) pt
top-left:     (500.8, 12.0) pt
```

#### A4 страница с поворотом 270° (rotation=270°):
```
bottom-right: (680.8, 12.0) pt  # Координаты пересчитаны по таблице поворотов
bottom-left:  (680.8, 500.8) pt
top-right:    (12.0, 12.0) pt
top-left:     (12.0, 500.8) pt
```

#### Таблица поворотов для bottom-right якоря:

| Поворот | Формула X | Формула Y | Описание |
|---------|-----------|-----------|----------|
| 0° | `width - qr_size - margin` | `margin` | Нижний правый угол |
| 90° | `margin` | `margin` | Визуальный нижний правый |
| 180° | `margin` | `height - margin - qr_size` | Визуальный нижний правый |
| 270° | `width - margin - qr_size` | `height - margin - qr_size` | Визуальный нижний правый |

**Примечание**: После поворота координаты клэмпируются в пределах страницы:
- `x = clamp(x, 0, width - qr_size)`
- `y = clamp(y, 0, height - qr_size)`

### CLI для тестирования

Используйте CLI скрипт для тестирования и настройки позиционирования:

```bash
# Показать текущую конфигурацию
python backend/scripts/qr_positioning_cli.py --show-config

# Анализировать PDF файл
python backend/scripts/qr_positioning_cli.py --analyze /path/to/file.pdf

# Тестировать разные якоря
python backend/scripts/qr_positioning_cli.py --test-coordinates /path/to/file.pdf

# Анализировать с настройками
python backend/scripts/qr_positioning_cli.py --analyze /path/to/file.pdf \
  --anchor bottom-left --margin-pt 20 --debug-frame
```

### Генерация тестовых PDF

Для тестирования системы координат создайте тестовые PDF файлы:

```bash
python generate_test_pdfs.py
```

Это создаст 6 тестовых PDF файлов с разными размерами и поворотами, а также файл `expected_coordinates.json` с ожидаемыми координатами QR кодов.

### Регресс-тесты

Запустите регресс-тесты для проверки корректности системы координат:

```bash
python test_coordinate_regression.py
```

Тесты проверяют:
- ✅ Позиционирование для A4/A3 портрет и ландшафт
- ✅ Повороты 0°, 90°, 180°, 270°
- ✅ Разные якоря (bottom-right, bottom-left, top-right, top-left)
- ✅ Точность координат (±1 pt допуск)

Результаты сохраняются в `test_results/coordinate_regression_results.json`.

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
