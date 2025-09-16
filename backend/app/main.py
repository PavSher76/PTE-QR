"""
PTE-QR Backend API
FastAPI application for QR code generation and document status checking
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import structlog
import time
from app.api.api_v1.api import api_router
from app.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize FastAPI app
logger.info("Initializing PTE-QR Backend API")
app = FastAPI(
    title="PTE QR/Status API",
    description="API для генерации QR-кодов и проверки актуальности листов документации (ENOVIA/3DEXPERIENCE)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
logger.info("Adding CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "name": "PTE QR/Status API",
        "version": "1.0.0",
        "description": "API для генерации QR-кодов и проверки актуальности документов",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.info("Health endpoint accessed")
    return {"status": "healthy", "service": "PTE-QR Backend"}

# Include API v1 router
logger.info("Including API v1 router", prefix=settings.API_V1_STR)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("PTE-QR Backend API starting up", version="1.0.0")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("PTE-QR Backend API shutting down")

if __name__ == "__main__":
    logger.info("Starting PTE-QR Backend API server", host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)