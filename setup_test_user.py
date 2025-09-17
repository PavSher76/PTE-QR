#!/usr/bin/env python3
"""
Скрипт для создания тестового пользователя в системе PTE-QR
"""

import requests
import json
from typing import Dict, Any

# Конфигурация API
API_BASE_URL = "http://localhost:8000/api/v1"
REGISTER_ENDPOINT = f"{API_BASE_URL}/auth/register"

# Данные тестового пользователя
TEST_USER_DATA = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "test_password",
    "roles": ["user"],
}


def register_test_user() -> bool:
    """Регистрация тестового пользователя"""
    try:
        print(f"👤 Регистрация тестового пользователя: {TEST_USER_DATA['username']}")

        response = requests.post(
            REGISTER_ENDPOINT,
            json=TEST_USER_DATA,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 201:
            data = response.json()
            print(f"✅ Пользователь успешно зарегистрирован")
            print(f"   ID: {data.get('id')}")
            print(f"   Username: {data.get('username')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Roles: {data.get('roles')}")
            return True
        elif response.status_code == 409:
            print(f"ℹ️  Пользователь уже существует")
            return True
        else:
            print(f"❌ Ошибка регистрации: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при регистрации пользователя: {e}")
        return False


def check_api_health() -> bool:
    """Проверка доступности API"""
    try:
        health_url = f"{API_BASE_URL.replace('/api/v1', '')}/health"
        print(f"🔍 Проверка доступности API: {health_url}")

        response = requests.get(health_url, timeout=5)

        if response.status_code == 200:
            print(f"✅ API доступен")
            return True
        else:
            print(f"❌ API недоступен: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при проверке API: {e}")
        return False


def main():
    """Основная функция скрипта"""
    print("🚀 Настройка тестового пользователя")
    print("=" * 40)

    # Проверяем доступность API
    if not check_api_health():
        print("❌ API недоступен. Убедитесь, что сервер запущен.")
        return

    print()

    # Регистрируем тестового пользователя
    if register_test_user():
        print("\n🎉 Настройка завершена успешно!")
        print("Теперь можно запустить generate_qr_codes.py")
    else:
        print("\n❌ Не удалось настроить тестового пользователя")


if __name__ == "__main__":
    main()
