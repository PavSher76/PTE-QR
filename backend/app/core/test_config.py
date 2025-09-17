"""
Test configuration settings for PTE-QR application
"""

import os


class TestSettings:
    """Test application settings"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PTE QR/Status API Test"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "test-secret-key"
    JWT_SECRET_KEY: str = "test-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # HMAC for QR signature
    QR_HMAC_SECRET: str = "test-qr-hmac-secret"

    # Database - use environment variable or default to test DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pte_qr_test"
    )

    # Redis - use environment variable or default to test Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL_SECONDS: int = 900  # 15 minutes

    # CORS
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]

    # ENOVIA Integration (mocked in tests)
    ENOVIA_BASE_URL: str = "https://test-enovia-instance.com"
    ENOVIA_CLIENT_ID: str = "test-client-id"
    ENOVIA_CLIENT_SECRET: str = "test-client-secret"

    # Logging
    LOG_LEVEL: str = "WARNING"  # Reduce log noise in tests

    # QR Code settings
    QR_CODE_SIZE: int = 200
    QR_CODE_BORDER: int = 4
    QR_CODE_ERROR_CORRECTION: str = "M"

    # PDF settings
    PDF_QR_SIZE: int = 50
    PDF_QR_POSITION: str = "bottom-right"

    # Rate limiting (relaxed for tests)
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = ["application/pdf", "image/png", "image/jpeg"]

    # SSO settings (mocked in tests)
    SSO_PROVIDER: str = "3DPassport"
    SSO_CLIENT_ID: str = "test-sso-client-id"
    SSO_CLIENT_SECRET: str = "test-sso-client-secret"
    SSO_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    SSO_AUTHORIZATION_URL: str = "https://test-sso.com/auth"
    SSO_TOKEN_URL: str = "https://test-sso.com/token"
    SSO_USERINFO_URL: str = "https://test-sso.com/userinfo"
    SSO_SCOPE: str = "openid profile email"


# Create test settings instance
test_settings = TestSettings()
