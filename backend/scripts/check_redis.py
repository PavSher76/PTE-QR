#!/usr/bin/env python3
"""
Simple Redis connection test script
"""

import sys
import time
import redis


def test_redis_connection(host="localhost", port=6379, password=None):
    """Test Redis connection with retries"""
    max_retries = 10
    retry_delay = 2

    print(f"🔍 Testing Redis connection to {host}:{port}")

    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host=host,
                port=port,
                password=password,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            # Test ping
            response = r.ping()
            if response:
                print("✅ Redis ping successful")

                # Test basic operations
                r.set("test_key", "test_value", ex=10)
                value = r.get("test_key")
                if value == "test_value":
                    print("✅ Redis read/write test successful")
                    r.delete("test_key")
                    print("✅ Redis cleanup successful")

                    # Get Redis info
                    info = r.info("server")
                    print(f"✅ Redis version: {info['redis_version']}")
                    print(f"✅ Redis mode: {info['redis_mode']}")

                    return True
                else:
                    print("❌ Redis read/write test failed")
            else:
                print("❌ Redis ping failed")

        except redis.AuthenticationError as e:
            print(f"❌ Redis authentication failed: {e}")
        except redis.ConnectionError as e:
            print(
                f"❌ Redis connection failed "
                f"(attempt {attempt + 1}/{max_retries}): {e}"
            )
        except Exception as e:
            print(f"❌ Redis test failed (attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            print(f"⏳ Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    print("❌ Redis connection test failed after all retries")
    return False


def main():
    """Main function"""
    if len(sys.argv) > 1:
        redis_url = sys.argv[1]
        if redis_url.startswith("redis://"):
            # Parse URL
            from urllib.parse import urlparse

            parsed = urlparse(redis_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 6379
            password = parsed.password
        else:
            print("❌ Invalid Redis URL format. Use: redis://host:port")
            return 1
    else:
        host = "localhost"
        port = 6379
        password = None

    success = test_redis_connection(host, port, password)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
