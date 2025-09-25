"""
PTE-QR Backend API
FastAPI application for QR code generation and document status checking
"""

import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

# Configure enhanced logging
configure_logging()
logger = get_logger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("PTE-QR Backend API starting up", version="1.0.0")
    yield
    # Shutdown
    logger.info("PTE-QR Backend API shutting down")


# Initialize FastAPI app
logger.info("Initializing PTE-QR Backend API")
app = FastAPI(
    title="PTE QR/Status API",
    description=(
        "API для генерации QR-кодов и проверки актуальности листов "
        "документации (ENOVIA/3DEXPERIENCE)"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
        "health": "/health",
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.info("Health endpoint accessed")
    return {"status": "healthy", "service": "PTE-QR Backend", "timestamp": time.time()}


# Include API v1 router
logger.info("Including API v1 router", prefix=settings.API_V1_STR)
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    logger.info("Starting PTE-QR Backend API server", host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
