-- PTE-QR Tables Creation Script
-- Создание основных таблиц системы

-- Подключение к базе данных pte_qr
\c pte_qr;

-- Установка поискового пути
SET search_path TO pte_qr, public;

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS pte_qr.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Создание таблицы документов
CREATE TABLE IF NOT EXISTS pte_qr.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_uid VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    document_type VARCHAR(50),
    current_revision VARCHAR(20),
    current_page INTEGER,
    business_status VARCHAR(50),
    enovia_state VARCHAR(50),
    is_actual BOOLEAN DEFAULT TRUE,
    released_at TIMESTAMP WITH TIME ZONE,
    superseded_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES pte_qr.users(id),
    updated_by UUID REFERENCES pte_qr.users(id)
);

-- Создание таблицы QR кодов
CREATE TABLE IF NOT EXISTS pte_qr.qr_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_uid VARCHAR(100) NOT NULL,
    revision VARCHAR(20) NOT NULL,
    page INTEGER NOT NULL,
    qr_data TEXT NOT NULL,
    hmac_signature VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES pte_qr.users(id),
    UNIQUE(doc_uid, revision, page)
);

-- Создание таблицы аудита
CREATE TABLE IF NOT EXISTS pte_qr.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Создание таблицы сессий
CREATE TABLE IF NOT EXISTS pte_qr.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES pte_qr.users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Создание таблицы настроек системы
CREATE TABLE IF NOT EXISTS pte_qr.system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES pte_qr.users(id)
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_username ON pte_qr.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON pte_qr.users(email);
CREATE INDEX IF NOT EXISTS idx_users_external_id ON pte_qr.users(external_id);

CREATE INDEX IF NOT EXISTS idx_documents_doc_uid ON pte_qr.documents(doc_uid);
CREATE INDEX IF NOT EXISTS idx_documents_business_status ON pte_qr.documents(business_status);
CREATE INDEX IF NOT EXISTS idx_documents_enovia_state ON pte_qr.documents(enovia_state);
CREATE INDEX IF NOT EXISTS idx_documents_is_actual ON pte_qr.documents(is_actual);

CREATE INDEX IF NOT EXISTS idx_qr_codes_doc_uid ON pte_qr.qr_codes(doc_uid);
CREATE INDEX IF NOT EXISTS idx_qr_codes_revision ON pte_qr.qr_codes(revision);
CREATE INDEX IF NOT EXISTS idx_qr_codes_page ON pte_qr.qr_codes(page);
CREATE INDEX IF NOT EXISTS idx_qr_codes_is_active ON pte_qr.qr_codes(is_active);

CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON pte_qr.audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_record_id ON pte_qr.audit_logs(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_changed_at ON pte_qr.audit_logs(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_changed_by ON pte_qr.audit_logs(changed_by);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON pte_qr.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token ON pte_qr.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON pte_qr.user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_system_settings_key ON pte_qr.system_settings(key);

-- Создание триггеров для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION pte_qr.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON pte_qr.users
    FOR EACH ROW EXECUTE FUNCTION pte_qr.update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON pte_qr.documents
    FOR EACH ROW EXECUTE FUNCTION pte_qr.update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON pte_qr.system_settings
    FOR EACH ROW EXECUTE FUNCTION pte_qr.update_updated_at_column();

-- Предоставление прав пользователям
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA pte_qr TO pte_qr_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA pte_qr TO pte_qr_user;

-- Комментарии к таблицам
COMMENT ON TABLE pte_qr.users IS 'Пользователи системы';
COMMENT ON TABLE pte_qr.documents IS 'Документы и их статусы';
COMMENT ON TABLE pte_qr.qr_codes IS 'QR коды для документов';
COMMENT ON TABLE pte_qr.audit_logs IS 'Логи аудита изменений';
COMMENT ON TABLE pte_qr.user_sessions IS 'Сессии пользователей';
COMMENT ON TABLE pte_qr.system_settings IS 'Настройки системы';

-- Вывод информации о созданных таблицах
SELECT 'Tables creation completed successfully' as status;
SELECT COUNT(*) as tables_created FROM information_schema.tables 
WHERE table_schema = 'pte_qr' AND table_type = 'BASE TABLE';
