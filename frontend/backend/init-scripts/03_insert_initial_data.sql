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
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK',
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
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK',
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
) ON CONFLICT (doc_uid) DO NOTHING;

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
) ON CONFLICT (key) DO NOTHING;

-- Вывод статистики вставленных данных
SELECT 'Initial data insertion completed successfully' as status;
SELECT 'Users created: ' || COUNT(*) as users_count FROM pte_qr.users;
SELECT 'Documents created: ' || COUNT(*) as documents_count FROM pte_qr.documents;
SELECT 'System settings created: ' || COUNT(*) as settings_count FROM pte_qr.system_settings;
