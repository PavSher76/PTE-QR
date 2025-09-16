#!/bin/bash

# PTE-QR Database Initialization Script
set -e

echo "=== PTE-QR DATABASE INITIALIZATION ==="
echo "📅 Date: $(date)"

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-pte_qr}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Wait for PostgreSQL
wait_for_postgres() {
    print_status "Waiting for PostgreSQL..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
            print_success "PostgreSQL is ready!"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    return 1
}

# Run SQL script
run_sql_script() {
    local script_file="$1"
    local description="$2"
    
    print_status "Running: $description"
    
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -f "$script_file"; then
        print_success "Completed: $description"
        return 0
    else
        return 1
    fi
}

# Main function
main() {
    if ! wait_for_postgres; then
        exit 1
    fi
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Run scripts in order
    run_sql_script "$SCRIPT_DIR/01_init_database.sql" "Database initialization"
    run_sql_script "$SCRIPT_DIR/02_create_tables.sql" "Tables creation"
    run_sql_script "$SCRIPT_DIR/03_insert_initial_data.sql" "Initial data insertion"
    
    print_success "Database initialization completed!"
    print_success "Admin user: admin / admin123"
    print_success "Demo user: demo_user / demo123"
}

main "$@"
