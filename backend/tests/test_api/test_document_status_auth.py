"""
Tests for document status endpoint with authentication and GDPR compliance
"""

from datetime import datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.core.test_config import test_settings


class TestDocumentStatusAuth:
    """Test document status endpoint with authentication and GDPR compliance"""

    def test_document_status_without_auth_limited_info(self, client: TestClient):
        """Test document status without authentication returns limited information (GDPR compliance)."""
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )

        assert response.status_code == 200
        data = response.json()

        # Should contain basic information
        assert "doc_uid" in data
        assert "revision" in data
        assert "page" in data
        assert "is_actual" in data
        assert "business_status" in data
        assert "links" in data
        assert "metadata" in data

        # Should NOT contain sensitive information
        assert "enovia_state" not in data
        assert "released_at" not in data
        assert "superseded_by" not in data
        assert "last_modified" not in data

        # Should contain GDPR compliance metadata
        assert data["metadata"]["access_level"] == "limited"
        assert data["metadata"]["gdpr_compliant"] is True
        assert "note" in data["metadata"]
        assert "privacy requirements" in data["metadata"]["note"]

    def test_document_status_with_auth_full_info(
        self, authenticated_client: TestClient, test_user
    ):
        """Test document status with authentication returns full information."""
        response = authenticated_client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )

        assert response.status_code == 200
        data = response.json()

        # Should contain all information
        assert "doc_uid" in data
        assert "revision" in data
        assert "page" in data
        assert "is_actual" in data
        assert "business_status" in data
        assert "enovia_state" in data
        assert "released_at" in data
        assert "superseded_by" in data
        assert "last_modified" in data
        assert "links" in data
        assert "metadata" in data

        # Should contain full access metadata
        assert data["metadata"]["access_level"] == "full"
        assert data["metadata"]["gdpr_compliant"] is True
        assert "created_by" in data["metadata"]

    def test_document_status_invalid_token(self, client: TestClient):
        """Test document status with invalid token falls back to limited access."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should return limited information due to invalid token
        assert data["metadata"]["access_level"] == "limited"
        assert "privacy requirements" in data["metadata"]["note"]

    def test_document_status_expired_token(self, client: TestClient, test_user):
        """Test document status with expired token falls back to limited access."""
        # Create an expired JWT token
        token_data = {
            "sub": test_user.username,
            "user_id": str(test_user.id),
            "exp": datetime.utcnow() - timedelta(minutes=30),  # Expired
        }
        token = jwt.encode(
            token_data,
            test_settings.JWT_SECRET_KEY,
            algorithm=test_settings.JWT_ALGORITHM,
        )

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should return limited information due to expired token
        assert data["metadata"]["access_level"] == "limited"
        assert "privacy requirements" in data["metadata"]["note"]

    def test_document_status_malformed_auth_header(self, client: TestClient):
        """Test document status with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token123"}
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1", headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should return limited information due to malformed header
        assert data["metadata"]["access_level"] == "limited"

    def test_document_status_missing_auth_header(self, client: TestClient):
        """Test document status without authorization header."""
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )

        assert response.status_code == 200
        data = response.json()

        # Should return limited information
        assert data["metadata"]["access_level"] == "limited"

    def test_document_status_nonexistent_document_without_auth(
        self, client: TestClient
    ):
        """Test document status for non-existent document without authentication."""
        response = client.get("/api/v1/documents/NONEXISTENT/revisions/A/status?page=1")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_document_status_nonexistent_document_with_auth(
        self, client: TestClient, test_user
    ):
        """Test document status for non-existent document with authentication."""
        # Create a valid JWT token
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
        response = client.get(
            "/api/v1/documents/NONEXISTENT/revisions/A/status?page=1", headers=headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_document_status_gdpr_data_minimization(self, client: TestClient):
        """Test that GDPR data minimization is properly implemented."""
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify only necessary data is included
        required_fields = [
            "doc_uid",
            "revision",
            "page",
            "is_actual",
            "business_status",
            "links",
            "metadata",
        ]
        for field in required_fields:
            assert field in data, f"Required field {field} is missing"

        # Verify sensitive fields are excluded
        sensitive_fields = [
            "enovia_state",
            "released_at",
            "superseded_by",
            "last_modified",
        ]
        for field in sensitive_fields:
            assert (
                field not in data
            ), f"Sensitive field {field} should not be included without authentication"

    def test_document_status_gdpr_transparency(self, client: TestClient):
        """Test that GDPR transparency requirements are met."""
        response = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify transparency information is provided
        assert "metadata" in data
        assert "access_level" in data["metadata"]
        assert "gdpr_compliant" in data["metadata"]
        assert "note" in data["metadata"]

        # Verify the note explains the limitation
        note = data["metadata"]["note"]
        assert "privacy" in note.lower()
        assert "authenticate" in note.lower()

    def test_document_status_cache_behavior_with_auth(
        self, authenticated_client: TestClient, test_user
    ):
        """Test that caching works correctly with authentication."""
        # First request
        response1 = authenticated_client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["metadata"]["access_level"] == "full"

        # Second request (should be cached)
        response2 = authenticated_client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["metadata"]["access_level"] == "full"

    def test_document_status_cache_behavior_without_auth(self, client: TestClient):
        """Test that caching works correctly without authentication."""
        # First request
        response1 = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["metadata"]["access_level"] == "limited"

        # Second request (should be cached)
        response2 = client.get(
            "/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["metadata"]["access_level"] == "limited"
