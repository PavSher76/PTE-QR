#!/usr/bin/env python3
"""
PTE-QR Authentication Test Script
"""

import json
import sys

import requests

API_BASE_URL = "http://localhost:8000"
TEST_USERS = [
    {"username": "admin", "password": "admin", "role": "Administrator"},
    {"username": "user", "password": "testuser", "role": "Test User"},
    {"username": "demo_user", "password": "demo123", "role": "Demo User"},
]


def test_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print(f"❌ API Health Check: Failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health Check: Connection failed - {e}")
        return False


def test_user_login(username, password, role):
    print(f"\n🔐 Testing login for {role} ({username})...")

    try:
        login_data = {"username": username, "password": password}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login", json=login_data, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful for {username}")
            return {"success": True, "data": data}
        else:
            print(f"❌ Login failed for {username} (Status: {response.status_code})")
            return {"success": False, "error": response.text}
    except Exception as e:
        print(f"❌ Login request failed for {username}: {e}")
        return {"success": False, "error": str(e)}


def main():
    print("🧪 PTE-QR Authentication Test")
    print("=" * 40)

    if not test_api_health():
        print("\n❌ API is not available. Please start the system first.")
        sys.exit(1)

    successful_logins = 0
    for user in TEST_USERS:
        result = test_user_login(user["username"], user["password"], user["role"])
        if result["success"]:
            successful_logins += 1

    print(f"\n📊 Test Summary: {successful_logins}/{len(TEST_USERS)} logins successful")

    if successful_logins == len(TEST_USERS):
        print("\n🎉 All authentication tests passed!")
        return 0
    else:
        print(f"\n⚠️ {len(TEST_USERS) - successful_logins} authentication tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
