#!/usr/bin/env python3
"""
PTE-QR Authentication Test Script
Скрипт для тестирования аутентификации пользователей
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USERS = [
    {"username": "admin", "password": "admin", "role": "Administrator"},
    {"username": "user", "password": "testuser", "role": "Test User"},
    {"username": "demo_user", "password": "demo123", "role": "Demo User"},
]

def test_api_health() -> bool:
    """Test if API is responding"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print(f"❌ API Health Check: Failed (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Health Check: Connection failed - {e}")
        return False

def test_user_login(username: str, password: str, role: str) -> Dict[str, Any]:
    """Test user login"""
    print(f"\n🔐 Testing login for {role} ({username})...")
    
    try:
        # Test login endpoint
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful for {username}")
            print(f"   Access token: {data.get('access_token', 'N/A')[:20]}...")
            return {"success": True, "data": data}
        else:
            print(f"❌ Login failed for {username} (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed for {username}: {e}")
        return {"success": False, "error": str(e)}

def test_protected_endpoint(token: str, username: str) -> bool:
    """Test access to protected endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/auth/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Protected endpoint access successful for {username}")
            print(f"   User info: {data.get('username', 'N/A')}")
            return True
        else:
            print(f"❌ Protected endpoint access failed for {username} (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Protected endpoint request failed for {username}: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PTE-QR Authentication Test")
    print("=" * 40)
    
    # Test API health
    if not test_api_health():
        print("\n❌ API is not available. Please start the system first.")
        print("   Run: make up")
        sys.exit(1)
    
    # Test user logins
    successful_logins = 0
    successful_protected_access = 0
    
    for user in TEST_USERS:
        result = test_user_login(
            user["username"], 
            user["password"], 
            user["role"]
        )
        
        if result["success"]:
            successful_logins += 1
            
            # Test protected endpoint
            token = result["data"].get("access_token")
            if token and test_protected_endpoint(token, user["username"]):
                successful_protected_access += 1
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    print(f"Total users tested: {len(TEST_USERS)}")
    print(f"Successful logins: {successful_logins}")
    print(f"Successful protected access: {successful_protected_access}")
    
    if successful_logins == len(TEST_USERS):
        print("\n🎉 All authentication tests passed!")
        return 0
    else:
        print(f"\n⚠️ {len(TEST_USERS) - successful_logins} authentication tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
