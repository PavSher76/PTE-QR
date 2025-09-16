"""
Configuration settings for PTE-QR application
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PTE QR/Status API"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # HMAC for QR signature
    QR_HMAC_SECRET: str = "your-qr-hmac-secret-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://pte_qr:pte_qr_dev@localhost:5432/pte_qr"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 900  # 15 minutes
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # ENOVIA Integration
    ENOVIA_BASE_URL: str = "https://your-enovia-instance.com"
    ENOVIA_CLIENT_ID: str = ""
    ENOVIA_CLIENT_SECRET: str = ""
    ENOVIA_SCOPE: str = "api"
    
    # SSO Configuration
    SSO_PROVIDER: str = "3DPassport"  # or "OAuth2"
    SSO_CLIENT_ID: str = ""
    SSO_CLIENT_SECRET: str = ""
    SSO_REDIRECT_URI: str = ""
    SSO_AUTHORIZATION_URL: str = ""
    SSO_TOKEN_URL: str = ""
    SSO_USERINFO_URL: str = ""
    SSO_SCOPE: str = "openid profile email"
    
    # QR Configuration
    QR_SIZE_MM: int = 35  # QR size in millimeters
    QR_DPI: int = 300
    QR_ECC_LEVEL: str = "M"  # Error correction level
    
    # PDF Stamping
    PDF_STAMP_POSITION: str = "bottom-right"  # bottom-right, top-right, top-center
    PDF_STAMP_MARGIN_MM: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
