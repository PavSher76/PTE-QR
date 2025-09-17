#!/usr/bin/env python3
"""
Check all required services for the application
"""

import sys
import time
import redis
import psycopg2
from urllib.parse import urlparse


def check_redis(redis_url="redis://localhost:6379"):
    """Check if Redis is available"""
    try:
        parsed = urlparse(redis_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        password = parsed.password

        r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
        response = r.ping()
        if response:
            print("✅ Redis is ready")
            return True
    except redis.AuthenticationError:
        # Try without password for CI
        try:
            r = redis.Redis(host=host, port=port, decode_responses=True)
            response = r.ping()
            if response:
                print("✅ Redis is ready (no auth)")
                return True
        except Exception:
            pass
    except Exception as e:
        print(f"❌ Redis check failed: {e}")

    return False


def check_postgresql(
    database_url="postgresql://postgres:postgres@localhost:5432/pte_qr_test",
):
    """Check if PostgreSQL is available"""
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            print("✅ PostgreSQL is ready")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL check failed: {e}")

    return False


def main():
    """Check all services"""
    print("🔍 Checking required services...")

    # Get URLs from environment or use defaults
    redis_url = sys.argv[1] if len(sys.argv) > 1 else "redis://localhost:6379"
    database_url = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "postgresql://postgres:postgres@localhost:5432/pte_qr_test"
    )

    print(f"Redis URL: {redis_url}")
    print(f"Database URL: {database_url}")
    print()

    redis_ok = check_redis(redis_url)
    postgres_ok = check_postgresql(database_url)

    print()
    if redis_ok and postgres_ok:
        print("🎉 All services are ready!")
        return 0
    else:
        print("❌ Some services are not ready")
        return 1


if __name__ == "__main__":
    sys.exit(main())
