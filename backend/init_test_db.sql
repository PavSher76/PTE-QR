-- Скрипт инициализации тестовой базы данных PTE-QR
-- Создает схему и таблицы для тестирования

-- Создание схемы pte_qr если не существует
CREATE SCHEMA IF NOT EXISTS pte_qr;

-- Создание enum типов
DO $$ BEGIN
    CREATE TYPE pte_qr.auditactionenum AS ENUM (
        'CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 
        'QR_GENERATE', 'QR_VERIFY', 'DOCUMENT_STATUS_CHECK'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE pte_qr.documentstatusenum AS ENUM (
        'IN_WORK', 'APPROVED_FOR_CONSTRUCTION', 'ACCEPTED_BY_CUSTOMER', 
        'CHANGES_INTRODUCED_GET_NEW', 'OBSOLETE'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE pte_qr.enoviastateenum AS ENUM (
        'In Work', 'Released', 'AFC', 'Accepted', 'Approved', 
        'Obsolete', 'Superseded', 'Frozen'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE pte_qr.qrcodeformatenum AS ENUM ('PNG', 'SVG', 'PDF');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE pte_qr.qrcodestyleenum AS ENUM ('BLACK', 'WHITE', 'COLORED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE pte_qr.userroleenum AS ENUM ('admin', 'user', 'viewer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Создание таблицы users
CREATE TABLE IF NOT EXISTS pte_qr.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    external_id VARCHAR(255),
    external_provider VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Создание таблицы user_roles
CREATE TABLE IF NOT EXISTS pte_qr.user_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Создание таблицы user_user_roles (ассоциативная таблица)
CREATE TABLE IF NOT EXISTS pte_qr.user_user_roles (
    user_id UUID REFERENCES pte_qr.users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES pte_qr.user_roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Создание таблицы documents
CREATE TABLE IF NOT EXISTS pte_qr.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_uid VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    document_type VARCHAR(50),
    current_revision VARCHAR(20),
    current_page INTEGER,
    business_status VARCHAR(50),
    enovia_state VARCHAR(50),
    is_actual BOOLEAN DEFAULT true,
    released_at TIMESTAMP WITH TIME ZONE,
    superseded_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES pte_qr.users(id),
    updated_by UUID REFERENCES pte_qr.users(id)
);

-- Создание таблицы qr_codes
CREATE TABLE IF NOT EXISTS pte_qr.qr_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES pte_qr.documents(id) ON DELETE CASCADE,
    doc_uid VARCHAR(100) NOT NULL,
    revision VARCHAR(20) NOT NULL,
    page INTEGER NOT NULL,
    qr_data TEXT NOT NULL,
    hmac_signature VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_by UUID REFERENCES pte_qr.users(id)
);

-- Создание таблицы qr_code_generations
CREATE TABLE IF NOT EXISTS pte_qr.qr_code_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES pte_qr.users(id),
    doc_uid VARCHAR(100) NOT NULL,
    revision VARCHAR(20) NOT NULL,
    pages TEXT NOT NULL, -- JSON array of page numbers
    style pte_qr.qrcodestyleenum NOT NULL,
    dpi INTEGER DEFAULT 300,
    mode VARCHAR(50) DEFAULT 'qr-only',
    client_ip VARCHAR(45),
    user_agent TEXT,
    qr_codes_count INTEGER NOT NULL,
    total_size_bytes INTEGER,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Создание таблицы audit_logs
CREATE TABLE IF NOT EXISTS pte_qr.audit_logs (
    id SERIAL PRIMARY KEY,
    changed_by UUID REFERENCES pte_qr.users(id),
    action pte_qr.auditactionenum NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    client_ip VARCHAR(45),
    user_agent TEXT,
    request_data JSON,
    response_status INTEGER,
    response_data JSON,
    details TEXT,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Создание индексов для улучшения производительности
CREATE INDEX IF NOT EXISTS idx_users_username ON pte_qr.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON pte_qr.users(email);
CREATE INDEX IF NOT EXISTS idx_documents_doc_uid ON pte_qr.documents(doc_uid);
CREATE INDEX IF NOT EXISTS idx_qr_codes_doc_uid ON pte_qr.qr_codes(doc_uid);
CREATE INDEX IF NOT EXISTS idx_qr_codes_document_id ON pte_qr.qr_codes(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_changed_by ON pte_qr.audit_logs(changed_by);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON pte_qr.audit_logs(created_at);

-- Вставка тестовых данных
INSERT INTO pte_qr.user_roles (name, description) VALUES 
    ('admin', 'Administrator role with full access'),
    ('user', 'Regular user role'),
    ('viewer', 'Read-only user role')
ON CONFLICT (name) DO NOTHING;

-- Создание тестового пользователя
INSERT INTO pte_qr.users (username, email, hashed_password, is_active, is_superuser) VALUES 
    ('testuser', 'test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true, false),
    ('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true, true)
ON CONFLICT (username) DO NOTHING;

-- Создание тестового документа
INSERT INTO pte_qr.documents (doc_uid, title, description, document_type, current_revision, current_page, business_status, enovia_state, is_actual, released_at) VALUES 
    ('TEST-DOC-001', 'Test Document', 'Test document description', 'Drawing', 'A', 1, 'APPROVED_FOR_CONSTRUCTION', 'Released', true, '2024-01-01T00:00:00Z')
ON CONFLICT (doc_uid) DO NOTHING;

-- Назначение ролей тестовым пользователям
INSERT INTO pte_qr.user_user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM pte_qr.users u, pte_qr.user_roles r 
WHERE u.username = 'testuser' AND r.name = 'user'
ON CONFLICT DO NOTHING;

INSERT INTO pte_qr.user_user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM pte_qr.users u, pte_qr.user_roles r 
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;
