"""
Configuration settings for PTE-QR application
"""


# Simple configuration without pydantic
class Settings:
    """Application settings"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PTE QR/Status API"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # HMAC for QR signature
    QR_HMAC_SECRET: str = "your-qr-hmac-secret-change-in-production"

    # Database
    DATABASE_URL: str = "postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr"

    # Redis
    REDIS_URL: str = "redis://redis:6379"
    CACHE_TTL_SECONDS: int = 900  # 15 minutes

    # CORS
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1", "0.0.0.0"]

    # ENOVIA Integration
    ENOVIA_BASE_URL: str = "https://your-enovia-instance.com"
    ENOVIA_CLIENT_ID: str = ""
    ENOVIA_CLIENT_SECRET: str = ""

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: str = "logs/app.log"  # Relative path for local development
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # QR Code settings
    QR_CODE_SIZE: int = 200
    QR_CODE_BORDER: int = 4
    QR_CODE_ERROR_CORRECTION: str = "M"

    # PDF settings
    PDF_QR_SIZE: int = 50
    PDF_QR_POSITION: str = "bottom-right"
    
    # QR Code positioning settings
    QR_ANCHOR: str = "bottom-right"  # bottom-right, bottom-left, top-right, top-left
    QR_MARGIN_PT: float = 12.0  # Margin in points (1 pt = 1/72 inch)
    QR_POSITION_BOX: str = "media"  # media or crop (MediaBox or CropBox)
    QR_RESPECT_ROTATION: bool = True  # Whether to respect page rotation
    QR_DEBUG_FRAME: bool = False  # Draw debug frame around QR position
    QR_SUPPORT_PORTRAIT: bool = False  # Support portrait pages (currently limited to landscape only)

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = ["application/pdf", "image/png", "image/jpeg"]

    # SSO settings
    SSO_PROVIDER: str = "3DPassport"
    SSO_CLIENT_ID: str = ""
    SSO_CLIENT_SECRET: str = ""
    SSO_REDIRECT_URI: str = ""
    SSO_AUTHORIZATION_URL: str = ""
    SSO_TOKEN_URL: str = ""
    SSO_USERINFO_URL: str = ""
    SSO_SCOPE: str = "openid profile email"


# Create settings instance
settings = Settings()
