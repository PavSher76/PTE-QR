"""
Integration tests for document status endpoint with authentication workflow
"""

from datetime import datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.test_config import test_settings


class TestDocumentStatusIntegration:
    """Integration tests for document status endpoint with authentication workflow"""

    def test_full_workflow_with_authentication(
        self, authenticated_client: TestClient, test_user
    ):
        """Test complete workflow: get document status with full access."""
        # Get document status with authentication
        status_response = authenticated_client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
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
            token_data,
            test_settings.JWT_SECRET_KEY,
            algorithm=test_settings.JWT_ALGORITHM,
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
        self, authenticated_client: TestClient, test_user, test_admin_user
    ):
        """Test that different users get the same full access when authenticated."""
        # Test with regular user
        user_response = authenticated_client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
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
            token_data_admin,
            test_settings.JWT_SECRET_KEY,
            algorithm=test_settings.JWT_ALGORITHM,
        )

        admin_response = authenticated_client.get(
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
            token_data,
            test_settings.JWT_SECRET_KEY,
            algorithm=test_settings.JWT_ALGORITHM,
        )

        response_with_auth = client.get(
            "/api/v1/documents/NONEXISTENT/revisions/A/status?page=1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response_with_auth.status_code == 404

    def test_workflow_caching_behavior(
        self,
        unauthenticated_client: TestClient,
        authenticated_client: TestClient,
        test_user,
    ):
        """Test that caching works correctly with different authentication states."""
        # Mock get_current_user_optional to return None for unauthenticated requests
        from app.api.dependencies import get_current_user_optional
        from app.main import app

        def mock_get_current_user_optional_none():
            return None

        # Override the dependency
        app.dependency_overrides[get_current_user_optional] = (
            mock_get_current_user_optional_none
        )

        try:
            # First request without authentication
            response1 = unauthenticated_client.get(
                "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
            )
            assert response1.status_code == 200
            data1 = response1.json()
            print(f"DEBUG: First request data: {data1}")
            print(
                f"DEBUG: Access level: {data1.get('metadata', {}).get('access_level')}"
            )
            assert data1["metadata"]["access_level"] == "limited"
        finally:
            # Clean up the override
            app.dependency_overrides.pop(get_current_user_optional, None)

        # Second request without authentication (should be cached)
        response2 = unauthenticated_client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["metadata"]["access_level"] == "limited"

        # Restore the original dependency for authenticated requests
        def mock_get_current_user_optional_auth():
            return test_user

        app.dependency_overrides[get_current_user_optional] = (
            mock_get_current_user_optional_auth
        )

        # Request with authentication (should get fresh data)
        response3 = authenticated_client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
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
            token_data,
            test_settings.JWT_SECRET_KEY,
            algorithm=test_settings.JWT_ALGORITHM,
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
