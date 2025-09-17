#!/usr/bin/env python3
"""
Check all required services for the application
"""

import sys
from urllib.parse import urlparse

import psycopg2
import redis


def check_redis(redis_url="redis://localhost:6379"):
    """Check if Redis is available"""
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            parsed = urlparse(redis_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 6379
            password = parsed.password

            r = redis.Redis(
                host=host,
                port=port,
                password=password,
                decode_responses=True,
                socket_timeout=5,
            )
            response = r.ping()
            if response:
                print("✅ Redis is ready")
                return True
        except redis.AuthenticationError:
            # Try without password for CI
            try:
                r = redis.Redis(
                    host=host, port=port, decode_responses=True, socket_timeout=5
                )
                response = r.ping()
                if response:
                    print("✅ Redis is ready (no auth)")
                    return True
            except Exception as e:
                print(
                    f"❌ Redis auth check failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
        except Exception as e:
            print(f"❌ Redis check failed (attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            print(f"⏳ Retrying Redis connection in {retry_delay} seconds...")
            import time

            time.sleep(retry_delay)

    print("❌ Redis is not available after all retries")
    return False


def check_postgresql(
    database_url="postgresql://postgres:postgres@localhost:5432/pte_qr_test",
):
    """Check if PostgreSQL is available"""
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(database_url, connect_timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                print("✅ PostgreSQL is ready")
                return True
        except Exception as e:
            print(
                f"❌ PostgreSQL check failed (attempt {attempt + 1}/{max_retries}): {e}"
            )

        if attempt < max_retries - 1:
            print(f"⏳ Retrying PostgreSQL connection in {retry_delay} seconds...")
            import time

            time.sleep(retry_delay)

    print("❌ PostgreSQL is not available after all retries")
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
