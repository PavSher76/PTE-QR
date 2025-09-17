#!/usr/bin/env python3
"""
Database connection check script for CI/CD
"""

import os
import sys
from urllib.parse import urlparse

import psycopg2


def check_database_connection():
    """Check if we can connect to the database"""
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr"
    )

    try:
        # Parse the database URL
        parsed = urlparse(database_url)

        # Connect to the database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
        )

        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        if result[0] == 1:
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed: Unexpected result")
            return False

    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def check_schema_exists():
    """Check if the pte_qr schema exists"""
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr"
    )

    try:
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
        )

        cursor = conn.cursor()
        cursor.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pte_qr'"
        )
        result = cursor.fetchone()

        if result:
            print("✅ Schema 'pte_qr' exists!")
            return True
        else:
            print("❌ Schema 'pte_qr' does not exist!")
            return False

    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def check_tables_exist():
    """Check if required tables exist"""
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr"
    )

    required_tables = [
        "users",
        "user_roles",
        "documents",
        "qr_codes",
        "qr_code_generations",
        "audit_logs",
    ]

    try:
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
        )

        cursor = conn.cursor()

        for table in required_tables:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'pte_qr' 
                    AND table_name = %s
                )
            """,
                (table,),
            )

            exists = cursor.fetchone()[0]
            if exists:
                print(f"✅ Table 'pte_qr.{table}' exists!")
            else:
                print(f"❌ Table 'pte_qr.{table}' does not exist!")
                return False

        return True

    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    print("🔍 Checking database setup...")
    print(
        f"Database URL: {os.getenv('DATABASE_URL', 'postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr')}"
    )
    print()

    # Check connection
    if not check_database_connection():
        sys.exit(1)

    print()

    # Check schema
    if not check_schema_exists():
        print("💡 Run: make setup-db")
        sys.exit(1)

    print()

    # Check tables
    if not check_tables_exist():
        print("💡 Run: make setup-db")
        sys.exit(1)

    print()
    print("🎉 Database setup is complete and ready for testing!")
