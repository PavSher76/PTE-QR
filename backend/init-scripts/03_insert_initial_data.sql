-- PTE-QR Initial Data Insertion Script
-- Вставка начальных данных в систему

-- Подключение к базе данных pte_qr
\c pte_qr;

-- Установка поискового пути
SET search_path TO pte_qr, public;

-- Вставка администратора по умолчанию
INSERT INTO pte_qr.users (
    username, 
    email, 
    full_name, 
    hashed_password, 
    is_active, 
    is_superuser
) VALUES (
    'admin',
    'admin@pte-qr.local',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK', -- password: admin123
    TRUE,
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Вставка демо пользователя
INSERT INTO pte_qr.users (
    username, 
    email, 
    full_name, 
    hashed_password, 
    is_active, 
    is_superuser
) VALUES (
    'demo_user',
    'demo@pte-qr.local',
    'Demo User',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK', -- password: demo123
    TRUE,
    FALSE
) ON CONFLICT (username) DO NOTHING;

-- Вставка тестовых документов
INSERT INTO pte_qr.documents (
    doc_uid,
    title,
    description,
    document_type,
    current_revision,
    current_page,
    business_status,
    enovia_state,
    is_actual,
    released_at,
    created_by
) VALUES 
(
    '3D-00001234',
    'Техническая спецификация насоса',
    'Основная техническая спецификация центробежного насоса для системы охлаждения',
    'TECHNICAL_SPECIFICATION',
    'B',
    1,
    'APPROVED_FOR_CONSTRUCTION',
    'Released',
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    '3D-00001235',
    'Чертеж сборочного узла',
    'Чертеж сборочного узла клапана регулирования давления',
    'ASSEMBLY_DRAWING',
    'A',
    1,
    'IN_WORK',
    'In Work',
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '15 days',
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    '3D-00001236',
    'Инструкция по эксплуатации',
    'Инструкция по эксплуатации и техническому обслуживанию оборудования',
    'OPERATION_MANUAL',
    'C',
    1,
    'OBSOLETE',
    'Superseded',
    FALSE,
    CURRENT_TIMESTAMP - INTERVAL '90 days',
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
) ON CONFLICT (doc_uid) DO NOTHING;

-- Вставка тестовых QR кодов
INSERT INTO pte_qr.qr_codes (
    doc_uid,
    revision,
    page,
    qr_data,
    hmac_signature,
    expires_at,
    is_active,
    created_by
) VALUES 
(
    '3D-00001234',
    'B',
    1,
    'https://qr.pti.ru/r/3D-00001234/B/1?ts=' || EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT || '&t=abc123def456',
    'test_hmac_signature_1',
    CURRENT_TIMESTAMP + INTERVAL '1 year',
    TRUE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    '3D-00001235',
    'A',
    1,
    'https://qr.pti.ru/r/3D-00001235/A/1?ts=' || EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT || '&t=def456ghi789',
    'test_hmac_signature_2',
    CURRENT_TIMESTAMP + INTERVAL '1 year',
    TRUE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    '3D-00001236',
    'C',
    1,
    'https://qr.pti.ru/r/3D-00001236/C/1?ts=' || EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT || '&t=ghi789jkl012',
    'test_hmac_signature_3',
    CURRENT_TIMESTAMP + INTERVAL '1 year',
    FALSE, -- Неактивный QR код для устаревшего документа
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
) ON CONFLICT (doc_uid, revision, page) DO NOTHING;

-- Вставка системных настроек
INSERT INTO pte_qr.system_settings (
    key,
    value,
    description,
    is_encrypted,
    updated_by
) VALUES 
(
    'system_name',
    'PTE-QR System',
    'Название системы',
    FALSE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    'system_version',
    '1.0.0',
    'Версия системы',
    FALSE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    'enovia_base_url',
    'http://enovia.pti.ru',
    'Базовый URL системы ENOVIA',
    FALSE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    'qr_code_expiry_days',
    '365',
    'Срок действия QR кодов в днях',
    FALSE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    'session_timeout_minutes',
    '480',
    'Таймаут сессии в минутах (8 часов)',
    FALSE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    'max_login_attempts',
    '5',
    'Максимальное количество попыток входа',
    FALSE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    'hmac_secret_key',
    'your-secret-hmac-key-change-in-production',
    'Секретный ключ для HMAC подписи',
    TRUE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
),
(
    'jwt_secret_key',
    'your-secret-jwt-key-change-in-production',
    'Секретный ключ для JWT токенов',
    TRUE,
    (SELECT id FROM pte_qr.users WHERE username = 'admin')
) ON CONFLICT (key) DO NOTHING;

-- Вставка записи аудита для инициализации
INSERT INTO pte_qr.audit_logs (
    table_name,
    record_id,
    action,
    new_values,
    changed_by,
    ip_address,
    user_agent
) VALUES 
(
    'system_initialization',
    uuid_generate_v4(),
    'INSERT',
    '{"message": "Database initialized with initial data", "timestamp": "' || CURRENT_TIMESTAMP || '"}',
    (SELECT id FROM pte_qr.users WHERE username = 'admin'),
    '127.0.0.1',
    'PTE-QR Initialization Script'
);

-- Вывод статистики вставленных данных
SELECT 'Initial data insertion completed successfully' as status;
SELECT 'Users created: ' || COUNT(*) as users_count FROM pte_qr.users;
SELECT 'Documents created: ' || COUNT(*) as documents_count FROM pte_qr.documents;
SELECT 'QR codes created: ' || COUNT(*) as qr_codes_count FROM pte_qr.qr_codes;
SELECT 'System settings created: ' || COUNT(*) as settings_count FROM pte_qr.system_settings;
SELECT 'Audit logs created: ' || COUNT(*) as audit_logs_count FROM pte_qr.audit_logs;
