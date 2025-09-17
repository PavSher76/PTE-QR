"""
Integration tests for document status endpoint with authentication workflow
"""

from datetime import datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings


class TestDocumentStatusIntegration:
    """Integration tests for document status endpoint with authentication workflow"""

    def test_full_workflow_with_authentication(self, client: TestClient, test_user):
        """Test complete workflow: login -> get document status with full access."""
        # Step 1: Login to get authentication token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "secret",  # Default test password
            },
        )

        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert "token_type" in login_data
        assert login_data["token_type"] == "bearer"

        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Get document status with authentication
        status_response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )

        assert status_response.status_code == 200
        status_data = status_response.json()

        # Verify full access is granted
        assert status_data["metadata"]["access_level"] == "full"
        assert "enovia_state" in status_data
        assert "released_at" in status_data
        assert "last_modified" in status_data
        assert "created_by" in status_data["metadata"]

    def test_workflow_without_authentication(self, client: TestClient):
        """Test workflow without authentication returns limited access."""
        # Get document status without authentication
        status_response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )

        assert status_response.status_code == 200
        status_data = status_response.json()

        # Verify limited access is granted
        assert status_data["metadata"]["access_level"] == "limited"
        assert "enovia_state" not in status_data
        assert "released_at" not in status_data
        assert "last_modified" not in status_data
        assert "privacy requirements" in status_data["metadata"]["note"]

    def test_workflow_with_expired_token(self, client: TestClient, test_user):
        """Test workflow with expired token falls back to limited access."""
        # Create an expired token
        token_data = {
            "sub": test_user.username,
            "user_id": str(test_user.id),
            "exp": datetime.utcnow() - timedelta(minutes=30),  # Expired
        }
        expired_token = jwt.encode(
            token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        status_response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )

        assert status_response.status_code == 200
        status_data = status_response.json()

        # Should fall back to limited access due to expired token
        assert status_data["metadata"]["access_level"] == "limited"
        assert "privacy requirements" in status_data["metadata"]["note"]

    def test_workflow_with_invalid_token(self, client: TestClient):
        """Test workflow with invalid token falls back to limited access."""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        status_response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )

        assert status_response.status_code == 200
        status_data = status_response.json()

        # Should fall back to limited access due to invalid token
        assert status_data["metadata"]["access_level"] == "limited"
        assert "privacy requirements" in status_data["metadata"]["note"]

    def test_workflow_with_malformed_auth_header(self, client: TestClient):
        """Test workflow with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat some_token"}
        status_response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )

        assert status_response.status_code == 200
        status_data = status_response.json()

        # Should fall back to limited access due to malformed header
        assert status_data["metadata"]["access_level"] == "limited"

    def test_workflow_with_different_users(
        self, client: TestClient, test_user, test_admin_user
    ):
        """Test that different users get the same full access when authenticated."""
        # Test with regular user
        token_data_user = {
            "sub": test_user.username,
            "user_id": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        user_token = jwt.encode(
            token_data_user, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        user_response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert user_response.status_code == 200
        user_data = user_response.json()
        assert user_data["metadata"]["access_level"] == "full"

        # Test with admin user
        token_data_admin = {
            "sub": test_admin_user.username,
            "user_id": str(test_admin_user.id),
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        admin_token = jwt.encode(
            token_data_admin, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        admin_response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert admin_response.status_code == 200
        admin_data = admin_response.json()
        assert admin_data["metadata"]["access_level"] == "full"

        # Both should have the same level of access
        assert (
            user_data["metadata"]["access_level"]
            == admin_data["metadata"]["access_level"]
        )

    def test_workflow_with_nonexistent_document(self, client: TestClient, test_user):
        """Test workflow with non-existent document returns 404 regardless of authentication."""
        # Test without authentication
        response_no_auth = client.get(
            "/api/v1/documents/NONEXISTENT/revisions/A/status?page=1"
        )
        assert response_no_auth.status_code == 404

        # Test with authentication
        token_data = {
            "sub": test_user.username,
            "user_id": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        token = jwt.encode(
            token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        response_with_auth = client.get(
            "/api/v1/documents/NONEXISTENT/revisions/A/status?page=1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response_with_auth.status_code == 404

    def test_workflow_caching_behavior(self, client: TestClient, test_user):
        """Test that caching works correctly with different authentication states."""
        # First request without authentication
        response1 = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["metadata"]["access_level"] == "limited"

        # Second request without authentication (should be cached)
        response2 = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["metadata"]["access_level"] == "limited"

        # Request with authentication (should get fresh data)
        token_data = {
            "sub": test_user.username,
            "user_id": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        token = jwt.encode(
            token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        response3 = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response3.status_code == 200
        data3 = response3.json()
        assert data3["metadata"]["access_level"] == "full"

    def test_workflow_error_handling(self, client: TestClient):
        """Test error handling in the workflow."""
        # Test with invalid page number
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=0"
        )
        assert response.status_code == 422

        # Test with missing page parameter
        response = client.get("/api/v1/documents/TEST-DOC-001/revisions/A/status")
        assert response.status_code == 422

        # Test with invalid revision format
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/INVALID/status?page=1"
        )
        assert (
            response.status_code == 200
        )  # Should still work, just with different revision

    def test_workflow_performance_with_auth(self, client: TestClient, test_user):
        """Test that authentication doesn't significantly impact performance."""
        import time

        token_data = {
            "sub": test_user.username,
            "user_id": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        token = jwt.encode(
            token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Measure time for authenticated request
        start_time = time.time()
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )
        auth_time = time.time() - start_time

        assert response.status_code == 200
        assert auth_time < 1.0  # Should complete within 1 second

        # Measure time for unauthenticated request
        start_time = time.time()
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        no_auth_time = time.time() - start_time

        assert response.status_code == 200
        assert no_auth_time < 1.0  # Should complete within 1 second

        # Both should be reasonably fast
        assert abs(auth_time - no_auth_time) < 0.5  # Difference should be minimal
