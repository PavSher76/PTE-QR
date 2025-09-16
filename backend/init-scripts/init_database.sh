#!/bin/bash

# PTE-QR Database Initialization Script
# Скрипт для инициализации базы данных PostgreSQL

set -e

echo "=== PTE-QR DATABASE INITIALIZATION ==="
echo "📅 Date: $(date)"
echo "🎯 Initializing PostgreSQL database for PTE-QR system"

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-pte_qr}"
DB_USER="${DB_USER:-pte_qr}"
DB_PASSWORD="${DB_PASSWORD:-pte_qr_dev}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if PostgreSQL is ready
wait_for_postgres() {
    print_status "Waiting for PostgreSQL to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
            print_success "PostgreSQL is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - PostgreSQL not ready yet, waiting 2 seconds..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "PostgreSQL is not ready after $max_attempts attempts"
    return 1
}

# Function to run SQL script
run_sql_script() {
    local script_file="$1"
    local description="$2"
    
    print_status "Running: $description"
    
    if [ ! -f "$script_file" ]; then
        print_error "Script file not found: $script_file"
        return 1
    fi
    
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -f "$script_file"; then
        print_success "Completed: $description"
        return 0
    else
        print_error "Failed: $description"
        return 1
    fi
}

# Function to run Alembic migrations
run_alembic_migrations() {
    print_status "Running Alembic migrations..."
    
    # Set environment variables for Alembic
    export DATABASE_URL="postgresql://pte_qr_user:pte_qr_password@$DB_HOST:$DB_PORT/$DB_NAME"
    
    # Change to backend directory
    cd "$(dirname "$0")/.."
    
    # Run migrations
    if alembic upgrade head; then
        print_success "Alembic migrations completed successfully"
        return 0
    else
        print_error "Alembic migrations failed"
        return 1
    fi
}

# Main initialization function
main() {
    print_status "Starting database initialization..."
    
    # Wait for PostgreSQL to be ready
    if ! wait_for_postgres; then
        exit 1
    fi
    
    # Get the directory of this script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Run initialization scripts in order
    print_status "Running database initialization scripts..."
    
    # 1. Initialize database and users
    if ! run_sql_script "$SCRIPT_DIR/01_init_database.sql" "Database and users initialization"; then
        exit 1
    fi
    
    # 2. Create tables
    if ! run_sql_script "$SCRIPT_DIR/02_create_tables.sql" "Tables creation"; then
        exit 1
    fi
    
    # 3. Insert initial data
    if ! run_sql_script "$SCRIPT_DIR/03_insert_initial_data.sql" "Initial data insertion"; then
        exit 1
    fi
    
    # 4. Run Alembic migrations (optional, for schema versioning)
    print_status "Running Alembic migrations (optional)..."
    if run_alembic_migrations; then
        print_success "Alembic migrations completed"
    else
        print_warning "Alembic migrations failed, but continuing..."
    fi
    
    # Final verification
    print_status "Verifying database initialization..."
    
    if PGPASSWORD="pte_qr_password" psql -h "$DB_HOST" -p "$DB_PORT" -U "pte_qr_user" -d "$DB_NAME" -c "SELECT COUNT(*) as user_count FROM pte_qr.users;" >/dev/null 2>&1; then
        print_success "Database initialization completed successfully!"
        print_success "Database: $DB_NAME"
        print_success "Schema: pte_qr"
        print_success "Users created: pte_qr_user, pte_qr_migrator, pte_qr_reader"
        print_success "Tables created: users, documents, qr_codes, audit_logs, user_sessions, system_settings"
        print_success "Initial data inserted: admin user, demo documents, system settings"
        
        echo ""
        print_status "Connection details:"
        echo "  Host: $DB_HOST"
        echo "  Port: $DB_PORT"
        echo "  Database: $DB_NAME"
        echo "  User: pte_qr_user"
        echo "  Password: pte_qr_password"
        
        echo ""
        print_status "Default admin credentials:"
        echo "  Username: admin"
        echo "  Password: admin"
        echo "  Email: admin@pte-qr.local"
        
        echo ""
        print_status "Test user credentials:"
        echo "  Username: user"
        echo "  Password: testuser"
        echo "  Email: user@pte-qr.local"
        
        echo ""
        print_status "Demo user credentials:"
        echo "  Username: demo_user"
        echo "  Password: demo123"
        echo "  Email: demo@pte-qr.local"
        
    else
        print_error "Database verification failed"
        exit 1
    fi
}

# Run main function
main "$@"
