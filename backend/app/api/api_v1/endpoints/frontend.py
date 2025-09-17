"""
Frontend-specific endpoints
"""

import structlog
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
logger = structlog.get_logger()


@router.get("/", response_class=HTMLResponse)
async def frontend_root():
    """
    Frontend root endpoint
    """
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PTE QR System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .api-link {
                display: block; margin: 10px 0; padding: 10px;
                background: #f5f5f5; text-decoration: none;
                color: #333; border-radius: 5px;
            }
            .api-link:hover { background: #e5e5e5; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PTE QR System</h1>
                <p>Система проверки актуальности документов через QR-коды</p>
            </div>

            <h2>API Endpoints</h2>
            <a href="/docs" class="api-link">📚 API Documentation (Swagger UI)</a>
            <a href="/redoc" class="api-link">📖 API Documentation (ReDoc)</a>
            <a href="/api/v1/health/" class="api-link">🏥 Health Check</a>
            <a href="/api/v1/health/metrics" class="api-link">
                📊 Prometheus Metrics
            </a>
            <a href="/api/v1/health/status" class="api-link">📈 System Status</a>

            <h2>Document Endpoints</h2>
            <a href="/api/v1/documents/TEST-DOC-001/revisions/A/status?page=1"
               class="api-link">📄 Document Status Check</a>

            <h2>QR Code Endpoints</h2>
            <a href="/api/v1/qrcodes/" class="api-link">🔲 QR Code Generation</a>

            <h2>Authentication</h2>
            <a href="/api/v1/auth/login" class="api-link">🔐 Login</a>
            <a href="/api/v1/auth/me" class="api-link">👤 Current User</a>

            <h2>Admin</h2>
            <a href="/api/v1/admin/stats" class="api-link">📊 System Statistics</a>
            <a href="/api/v1/admin/users" class="api-link">👥 Users Management</a>
        </div>
    </body>
    </html>
    """
