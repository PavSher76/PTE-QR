#!/usr/bin/env python3
"""
Script to run tests with proper setup
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    """Main function to run tests"""

    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["REDIS_URL"] = "redis://localhost:6380"
    os.environ["CACHE_ENABLED"] = "false"

    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Run tests
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--color=yes",
    ]

    print("🚀 Запуск тестов...")
    print(f"📁 Рабочая директория: {backend_dir}")
    print(f"🔧 Команда: {' '.join(cmd)}")
    print("=" * 50)

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Тесты прерваны пользователем")
        return 1
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
