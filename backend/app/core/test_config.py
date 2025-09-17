"""
Test configuration settings for PTE-QR application
"""

import os


# Simple test configuration without pydantic
class TestSettings:
    """Test application settings"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PTE QR/Status API Test"
    VERSION: str = "1.0.0-test"

    # Security
    SECRET_KEY: str = "test-secret-key"
    JWT_SECRET_KEY: str = "test-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # HMAC for QR signature
    QR_HMAC_SECRET: str = "test-qr-hmac-secret"

    # Database - Use SQLite for tests
    DATABASE_URL: str = "sqlite:///./test.db"

    # Redis - Disable caching for tests
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 0  # Disable caching
    CACHE_ENABLED: bool = False  # Disable caching completely

    # CORS
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]

    # ENOVIA Integration - Mock URLs for tests
    ENOVIA_BASE_URL: str = "https://test-enovia-instance.com"
    ENOVIA_CLIENT_ID: str = "test-client-id"
    ENOVIA_CLIENT_SECRET: str = "test-client-secret"

    # Logging
    LOG_LEVEL: str = "DEBUG"

    # QR Code settings
    QR_CODE_SIZE: int = 200
    QR_CODE_BORDER: int = 4
    QR_CODE_ERROR_CORRECTION: str = "M"

    # PDF settings
    PDF_QR_SIZE: int = 50
    PDF_QR_POSITION: str = "bottom-right"

    # Rate limiting - Disable for tests
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = ["application/pdf", "image/png", "image/jpeg"]

    # SSO settings - Mock for tests
    SSO_PROVIDER: str = "3DPassport"
    SSO_CLIENT_ID: str = "test-sso-client-id"
    SSO_CLIENT_SECRET: str = "test-sso-client-secret"
    SSO_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    SSO_AUTHORIZATION_URL: str = "https://test-sso.com/auth"
    SSO_TOKEN_URL: str = "https://test-sso.com/token"
    SSO_USERINFO_URL: str = "https://test-sso.com/userinfo"
    SSO_SCOPE: str = "openid profile email"

    # Test specific settings
    TESTING: bool = True
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    TEST_REDIS_URL: str = "redis://localhost:6379"


# Create test settings instance
test_settings = TestSettings()

# Override main settings with test settings
from app.core.config import settings

for key, value in test_settings.__dict__.items():
    if not key.startswith("__"):
        setattr(settings, key, value)

# Set TESTING environment variable
os.environ["TESTING"] = "true"

# Recreate auth service with test settings
from app.services.auth_service import AuthService

_auth_service_instance = AuthService()
