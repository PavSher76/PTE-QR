"""
PTE-QR Backend API
FastAPI application for QR code generation and document status checking
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="PTE QR/Status API",
    description="API для генерации QR-кодов и проверки актуальности листов документации (ENOVIA/3DEXPERIENCE)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
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
    return {"status": "healthy", "service": "PTE-QR Backend"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)