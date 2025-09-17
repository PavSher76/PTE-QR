#!/usr/bin/env python3
"""
Redis health check script
"""

import sys
import time
import redis
from urllib.parse import urlparse


def check_redis(redis_url="redis://localhost:6379", max_retries=30, retry_delay=2):
    """Check if Redis is available and responding"""

    try:
        # Parse Redis URL
        parsed = urlparse(redis_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        password = parsed.password

        print(f"Checking Redis at {host}:{port}...")

        # Create Redis connection
        r = redis.Redis(host=host, port=port, password=password, decode_responses=True)

        for attempt in range(max_retries):
            try:
                # Try to ping Redis
                response = r.ping()
                if response:
                    print("✅ Redis is ready and responding!")
                    return True
            except redis.AuthenticationError as e:
                print(
                    f"❌ Redis authentication failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                # For CI, we expect no password, so try without password
                if attempt == 0 and password:
                    print("ℹ️  Trying without password (CI mode)...")
                    r = redis.Redis(host=host, port=port, decode_responses=True)
                    try:
                        response = r.ping()
                        if response:
                            print(
                                "✅ Redis is ready and responding (without password)!"
                            )
                            return True
                    except Exception:
                        pass
            except redis.ConnectionError as e:
                print(
                    f"❌ Redis connection failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
            except Exception as e:
                print(
                    f"❌ Redis check failed (attempt {attempt + 1}/{max_retries}): {e}"
                )

            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)

        print("❌ Redis is not available after all retries")
        return False

    except Exception as e:
        print(f"❌ Failed to check Redis: {e}")
        return False


if __name__ == "__main__":
    redis_url = sys.argv[1] if len(sys.argv) > 1 else "redis://localhost:6379"
    success = check_redis(redis_url)
    sys.exit(0 if success else 1)
