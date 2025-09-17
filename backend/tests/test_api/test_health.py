"""
Integration tests for health endpoints
"""

from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

    def test_health_check_detailed(self, client: TestClient):
        """Test detailed health check endpoint."""
        response = client.get("/api/v1/health/")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "database" in data
        assert "redis" in data
        assert "enovia" in data

    def test_metrics_endpoint(self, client: TestClient):
        """Test Prometheus metrics endpoint."""
        response = client.get("/api/v1/health/metrics")

        assert response.status_code == 200
        # FastAPI automatically adds charset, so we check for the base content type
        assert "text/plain" in response.headers["content-type"]
        assert "version=0.0.4" in response.headers["content-type"]

        # Check that response contains Prometheus metrics format
        content = response.text
        assert "pte_qr_" in content or "# HELP" in content

    def test_metrics_json_endpoint(self, client: TestClient):
        """Test metrics in JSON format."""
        response = client.get("/api/v1/health/metrics/json")

        assert response.status_code == 200
        data = response.json()
        assert "registry" in data
        assert "timestamp" in data

    def test_detailed_status_endpoint(self, client: TestClient):
        """Test detailed system status endpoint."""
        response = client.get("/api/v1/health/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "system" in data
        assert "application" in data
        assert "cache" in data
        assert "enovia" in data

        # Check system metrics
        system = data["system"]
        assert "cpu_percent" in system
        assert "memory_percent" in system
        assert "disk_percent" in system
