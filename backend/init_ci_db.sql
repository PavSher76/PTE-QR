-- CI Database initialization script
-- This script sets up the test database for GitHub Actions

-- Create schema
CREATE SCHEMA IF NOT EXISTS pte_qr;

-- Create user_roles table
CREATE TABLE IF NOT EXISTS pte_qr.user_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create users table
CREATE TABLE IF NOT EXISTS pte_qr.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create user_user_roles association table
CREATE TABLE IF NOT EXISTS pte_qr.user_user_roles (
    user_id UUID REFERENCES pte_qr.users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES pte_qr.user_roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Create documents table
CREATE TABLE IF NOT EXISTS pte_qr.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_uid VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200),
    description TEXT,
    created_by UUID REFERENCES pte_qr.users(id),
    updated_by UUID REFERENCES pte_qr.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create qr_codes table
CREATE TABLE IF NOT EXISTS pte_qr.qr_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES pte_qr.documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    qr_data TEXT NOT NULL,
    qr_url VARCHAR(500) NOT NULL,
    signature VARCHAR(500) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create qr_code_generations table
CREATE TABLE IF NOT EXISTS pte_qr.qr_code_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES pte_qr.documents(id) ON DELETE CASCADE,
    generated_by UUID REFERENCES pte_qr.users(id),
    pages TEXT NOT NULL, -- JSON array of page numbers
    style VARCHAR(50) DEFAULT 'default',
    dpi INTEGER DEFAULT 300,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS pte_qr.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES pte_qr.users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Insert initial data
INSERT INTO pte_qr.user_roles (name, description, permissions) VALUES
('user', 'Regular user', '["read:documents", "generate:qr_codes"]'),
('admin', 'Administrator', '["read:documents", "write:documents", "generate:qr_codes", "admin:users"]')
ON CONFLICT (name) DO NOTHING;

-- Insert test users
INSERT INTO pte_qr.users (id, username, email, full_name, hashed_password, is_active, is_superuser) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'testuser', 'test@example.com', 'Test User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s8i2', true, false),
('550e8400-e29b-41d4-a716-446655440001', 'adminuser', 'admin@example.com', 'Admin User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s8i2', true, true)
ON CONFLICT (username) DO NOTHING;

-- Insert test documents
INSERT INTO pte_qr.documents (id, doc_uid, title, description, created_by, updated_by) VALUES
('550e8400-e29b-41d4-a716-446655440002', 'TEST-DOC-001', 'Test Document 1', 'Test document for testing', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000'),
('550e8400-e29b-41d4-a716-446655440003', 'TEST-DOC-002', 'Test Document 2', 'Another test document', '550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001')
ON CONFLICT (doc_uid) DO NOTHING;

-- Assign roles to users
INSERT INTO pte_qr.user_user_roles (user_id, role_id) VALUES
('550e8400-e29b-41d4-a716-446655440000', 1), -- testuser -> user role
('550e8400-e29b-41d4-a716-446655440001', 2)  -- adminuser -> admin role
ON CONFLICT (user_id, role_id) DO NOTHING;
