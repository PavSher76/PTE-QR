#!/usr/bin/env python3
"""
Debug script to test authentication in tests
"""

import os
import sys

sys.path.append(".")

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_current_user_optional
from app.core.test_database import (
    TestSessionLocal,
    create_test_tables,
    drop_test_tables,
)
from app.main import app
from app.models.document import Document
from app.models.user import User


def test_auth_debug():
    """Debug authentication in tests"""

    # Setup test database
    create_test_tables()

    try:
        # Create test user
        db = TestSessionLocal()
        test_user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )
        db.add(test_user)

        # Create test document
        test_document = Document(
            id=uuid.uuid4(),
            doc_uid="TEST-DOC-001",
            title="Test Document",
            current_revision="A",
            current_page=1,
            business_status="ACTUAL",
            enovia_state="RELEASED",
            is_actual=True,
            created_by=test_user.id,
        )
        db.add(test_document)
        db.commit()

        # Mock authentication
        def mock_get_current_user():
            print("🔍 mock_get_current_user called")
            return test_user

        def mock_get_current_user_optional():
            print("🔍 mock_get_current_user_optional called")
            return test_user

        # Override dependencies
        from app.core.database import get_db

        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_current_user] = mock_get_current_user
        app.dependency_overrides[get_current_user_optional] = (
            mock_get_current_user_optional
        )

        # Test with authenticated client
        with TestClient(app) as client:
            print("🧪 Testing authenticated request...")
            response = client.get(
                "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

            # Check if access_level is full
            data = response.json()
            if "metadata" in data:
                access_level = data["metadata"].get("access_level")
                print(f"Access level: {access_level}")
                if access_level == "full":
                    print("✅ Authentication working correctly!")
                else:
                    print("❌ Authentication not working - got limited access")
            else:
                print("❌ No metadata in response")

    finally:
        # Cleanup
        app.dependency_overrides.clear()
        db.close()
        drop_test_tables()


if __name__ == "__main__":
    test_auth_debug()
