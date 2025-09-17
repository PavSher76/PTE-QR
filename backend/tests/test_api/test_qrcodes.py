"""
Integration tests for QR code endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestQRCodeEndpoints:
    """Test QR code generation endpoints"""
    
    def test_generate_qr_codes_unauthorized(self, client: TestClient):
        """Test QR code generation without authentication."""
        response = client.post(
            "/api/v1/qrcodes/",
            json={
                "doc_uid": "TEST-DOC-001",
                "revision": "A",
                "pages": [1, 2, 3],
                "style": "BLACK",
                "dpi": 300
            }
        )
        
        # Should require authentication
        assert response.status_code in [401, 403]
    
    def test_generate_qr_codes_invalid_request(self, client: TestClient):
        """Test QR code generation with invalid request data."""
        response = client.post(
            "/api/v1/qrcodes/",
            json={
                "doc_uid": "",  # Invalid empty doc_uid
                "revision": "A",
                "pages": [],  # Invalid empty pages
                "style": "INVALID_STYLE",  # Invalid style
                "dpi": -1  # Invalid DPI
            }
        )
        
        # Should require authentication first
        assert response.status_code == 401  # Unauthorized
    
    def test_generate_qr_codes_missing_fields(self, client: TestClient):
        """Test QR code generation with missing required fields."""
        response = client.post(
            "/api/v1/qrcodes/",
            json={
                "doc_uid": "TEST-DOC-001",
                # Missing revision, pages, etc.
            }
        )
        
        # Should require authentication first
        assert response.status_code == 401  # Unauthorized
    
    def test_generate_qr_codes_invalid_pages(self, client: TestClient):
        """Test QR code generation with invalid page numbers."""
        response = client.post(
            "/api/v1/qrcodes/",
            json={
                "doc_uid": "TEST-DOC-001",
                "revision": "A",
                "pages": [0, -1, 1000],  # Invalid page numbers
                "style": "BLACK",
                "dpi": 300
            }
        )
        
        # Should require authentication first
        assert response.status_code == 401  # Unauthorized
    
    def test_generate_qr_codes_large_pages(self, client: TestClient):
        """Test QR code generation with large number of pages."""
        large_pages = list(range(1, 1001))  # 1000 pages
        
        response = client.post(
            "/api/v1/qrcodes/",
            json={
                "doc_uid": "TEST-DOC-001",
                "revision": "A",
                "pages": large_pages,
                "style": "BLACK",
                "dpi": 300
            }
        )
        
        # Should require authentication first
        assert response.status_code == 401  # Unauthorized
    
    def test_generate_qr_codes_different_styles(self, client: TestClient):
        """Test QR code generation with different styles."""
        styles = ["BLACK", "INVERTED", "WITH_LABEL"]
        
        for style in styles:
            response = client.post(
                "/api/v1/qrcodes/",
                json={
                    "doc_uid": "TEST-DOC-001",
                    "revision": "A",
                    "pages": [1],
                    "style": style,
                    "dpi": 300
                }
            )
            
            # Should require authentication, but request should be valid
            assert response.status_code in [200, 401, 403]
    
    def test_generate_qr_codes_different_dpi(self, client: TestClient):
        """Test QR code generation with different DPI values."""
        dpi_values = [72, 150, 300, 600]
        
        for dpi in dpi_values:
            response = client.post(
                "/api/v1/qrcodes/",
                json={
                    "doc_uid": "TEST-DOC-001",
                    "revision": "A",
                    "pages": [1],
                    "style": "BLACK",
                    "dpi": dpi
                }
            )
            
            # Should require authentication, but request should be valid
            assert response.status_code in [200, 401, 403]
    
    def test_generate_qr_codes_special_characters(self, client: TestClient):
        """Test QR code generation with special characters in document info."""
        response = client.post(
            "/api/v1/qrcodes/",
            json={
                "doc_uid": "TEST-DOC-001@#$%",
                "revision": "A-1.0",
                "pages": [1],
                "style": "BLACK",
                "dpi": 300
            }
        )
        
        # Should require authentication, but request should be valid
        assert response.status_code in [200, 401, 403]
