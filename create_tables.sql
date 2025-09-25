-- Создание таблиц для PTE-QR системы
-- Подключение к базе данных pte_qr
\c pte_qr;

-- Установка поискового пути
SET search_path TO pte_qr, public;

-- Создание таблицы ролей пользователей
CREATE TABLE IF NOT EXISTS pte_qr.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS pte_qr.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    external_id VARCHAR(255),
    external_provider VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Создание таблицы связи пользователей и ролей
CREATE TABLE IF NOT EXISTS pte_qr.user_user_roles (
    user_id UUID REFERENCES pte_qr.users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES pte_qr.user_roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Создание таблицы настроек системы
CREATE TABLE IF NOT EXISTS pte_qr.system_settings (
    id SERIAL PRIMARY KEY,
    settings_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы документов
CREATE TABLE IF NOT EXISTS pte_qr.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enovia_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type VARCHAR(50),
    revision VARCHAR(50) NOT NULL,
    current_page INTEGER,
    business_status VARCHAR(50),
    enovia_state VARCHAR(50),
    is_actual BOOLEAN DEFAULT TRUE,
    released_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES pte_qr.users(id)
);

-- Создание таблицы QR кодов
CREATE TABLE IF NOT EXISTS pte_qr.qr_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enovia_id VARCHAR(100) NOT NULL,
    document_id UUID REFERENCES pte_qr.documents(id) ON DELETE CASCADE,
    revision VARCHAR(50) NOT NULL,
    page_number INTEGER NOT NULL,
    qr_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES pte_qr.users(id)
);

-- Создание таблицы аудита
CREATE TABLE IF NOT EXISTS pte_qr.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES pte_qr.users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_users_username ON pte_qr.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON pte_qr.users(email);
CREATE INDEX IF NOT EXISTS idx_documents_enovia_id ON pte_qr.documents(enovia_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_enovia_id ON pte_qr.qr_codes(enovia_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_document_id ON pte_qr.qr_codes(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_changed_by ON pte_qr.audit_logs(changed_by);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON pte_qr.audit_logs(changed_at);

-- Вставка ролей
INSERT INTO pte_qr.user_roles (name, description) VALUES 
    ('admin', 'Administrator role with full access'),
    ('user', 'Regular user role'),
    ('viewer', 'Read-only user role')
ON CONFLICT (name) DO NOTHING;

-- Вставка тестовых пользователей
INSERT INTO pte_qr.users (username, email, full_name, hashed_password, is_active, is_superuser) VALUES 
    ('admin', 'admin@pte-qr.local', 'System Administrator', '$2b$12$arF.8K5vrAY0xRLse97GDue5bZ9iK8ns7XfB89WQS.WTbEQqcpYia', true, true),
    ('user', 'user@pte-qr.local', 'Test User', '$2b$12$Zvug9csBPo7b0lPbysnak.CL3w5wBisCDP5Haj9qj3Kghx6i7U9zW', true, false),
    ('demo_user', 'demo@pte-qr.local', 'Demo User', '$2b$12$PKfUgkkGkwuwzy8eMA2YUeV.fAFzxNuLDCnE/XzSfcqmCpmdPws8O', true, false)
ON CONFLICT (username) DO NOTHING;

-- Назначение ролей
INSERT INTO pte_qr.user_user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM pte_qr.users u, pte_qr.user_roles r 
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO pte_qr.user_user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM pte_qr.users u, pte_qr.user_roles r 
WHERE u.username = 'user' AND r.name = 'user'
ON CONFLICT DO NOTHING;

INSERT INTO pte_qr.user_user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM pte_qr.users u, pte_qr.user_roles r 
WHERE u.username = 'demo_user' AND r.name = 'user'
ON CONFLICT DO NOTHING;

-- Вставка тестовых документов
INSERT INTO pte_qr.documents (enovia_id, title, description, document_type, revision, current_page, business_status, enovia_state, is_actual, released_at, created_by) VALUES 
    ('3D-00001234', 'Техническая спецификация насоса', 'Основная техническая спецификация центробежного насоса для системы охлаждения', 'TECHNICAL_SPECIFICATION', 'B', 1, 'APPROVED_FOR_CONSTRUCTION', 'Released', TRUE, CURRENT_TIMESTAMP - INTERVAL '30 days', (SELECT id FROM pte_qr.users WHERE username = 'admin')),
    ('3D-00001235', 'Чертеж сборочного узла', 'Детальный чертеж сборочного узла насосной системы', 'DRAWING', 'A', 1, 'APPROVED_FOR_CONSTRUCTION', 'Released', TRUE, CURRENT_TIMESTAMP - INTERVAL '15 days', (SELECT id FROM pte_qr.users WHERE username = 'admin'))
ON CONFLICT (enovia_id) DO NOTHING;

SELECT 'Tables created successfully' as status;
