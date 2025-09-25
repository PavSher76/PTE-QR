-- PTE-QR Database Initialization Script
-- Создание базы данных и пользователей

-- Создание базы данных (если не существует)
SELECT 'CREATE DATABASE pte_qr'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pte_qr')\gexec

-- Подключение к базе данных pte_qr
\c pte_qr;

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Создание схемы для приложения
CREATE SCHEMA IF NOT EXISTS pte_qr;

-- Установка поискового пути
SET search_path TO pte_qr, public;

-- Создание пользователя приложения (если не существует)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'pte_qr_user') THEN
        CREATE ROLE pte_qr_user WITH LOGIN PASSWORD 'pte_qr_password';
    END IF;
END
$$;

-- Предоставление прав пользователю
GRANT CONNECT ON DATABASE pte_qr TO pte_qr_user;
GRANT USAGE ON SCHEMA pte_qr TO pte_qr_user;
GRANT CREATE ON SCHEMA pte_qr TO pte_qr_user;

-- Создание пользователя для миграций
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'pte_qr_migrator') THEN
        CREATE ROLE pte_qr_migrator WITH LOGIN PASSWORD 'pte_qr_migrator_password';
    END IF;
END
$$;

-- Предоставление прав для миграций
GRANT CONNECT ON DATABASE pte_qr TO pte_qr_migrator;
GRANT USAGE ON SCHEMA pte_qr TO pte_qr_migrator;
GRANT CREATE ON SCHEMA pte_qr TO pte_qr_migrator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA pte_qr TO pte_qr_migrator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA pte_qr TO pte_qr_migrator;

-- Создание пользователя для чтения (только для мониторинга)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'pte_qr_reader') THEN
        CREATE ROLE pte_qr_reader WITH LOGIN PASSWORD 'pte_qr_reader_password';
    END IF;
END
$$;

-- Предоставление прав только для чтения
GRANT CONNECT ON DATABASE pte_qr TO pte_qr_reader;
GRANT USAGE ON SCHEMA pte_qr TO pte_qr_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA pte_qr TO pte_qr_reader;

-- Создание таблицы для отслеживания миграций
CREATE TABLE IF NOT EXISTS pte_qr.alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Комментарии к таблице
COMMENT ON TABLE pte_qr.alembic_version IS 'Таблица для отслеживания версий миграций Alembic';

-- Логирование успешной инициализации
INSERT INTO pte_qr.alembic_version (version_num) 
VALUES ('initial_setup') 
ON CONFLICT (version_num) DO NOTHING;

-- Вывод информации о созданных объектах
SELECT 'Database initialization completed successfully' as status;
SELECT 'Created database: pte_qr' as database;
SELECT 'Created schema: pte_qr' as schema;
SELECT 'Created users: pte_qr_user, pte_qr_migrator, pte_qr_reader' as users;
