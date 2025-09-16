"""
Frontend QR resolution endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
import structlog

from app.core.database import get_db
from app.utils.hmac_signer import HMACSigner

router = APIRouter()
logger = structlog.get_logger()


@router.get("/r/{doc_uid}/{rev}/{page}", response_class=HTMLResponse)
async def resolve_qr(
    doc_uid: str,
    rev: str,
    page: int,
    ts: int = Query(..., description="Timestamp"),
    t: str = Query(..., description="Signature"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Frontend route for QR code resolution
    """
    try:
        # Verify HMAC signature
        hmac_signer = HMACSigner()
        if not hmac_signer.verify_signature(doc_uid, rev, page, ts, t):
            return HTMLResponse(
                content=generate_error_html("QR повреждён/подделан", "Неверная подпись"),
                status_code=400
            )
        
        # Get document status from API
        # In a real implementation, this would call the documents API endpoint
        # For now, we'll generate a simple HTML response
        
        # Log the QR scan
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            "QR code scanned",
            doc_uid=doc_uid,
            revision=rev,
            page=page,
            client_ip=client_ip
        )
        
        # Generate HTML response
        html_content = generate_status_html(doc_uid, rev, page, "APPROVED_FOR_CONSTRUCTION", True)
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(
            "QR resolution failed",
            doc_uid=doc_uid,
            revision=rev,
            page=page,
            error=str(e),
            exc_info=True
        )
        return HTMLResponse(
            content=generate_error_html("Ошибка сервера", "Внутренняя ошибка сервера"),
            status_code=500
        )


def generate_status_html(doc_uid: str, revision: str, page: int, status: str, is_actual: bool) -> str:
    """
    Generate HTML for document status display
    """
    # Status mapping
    status_config = {
        "APPROVED_FOR_CONSTRUCTION": {
            "text": "Утверждена в производство работ",
            "color": "#28a745",
            "icon": "✅"
        },
        "ACCEPTED_BY_CUSTOMER": {
            "text": "Принята Заказчиком",
            "color": "#007bff",
            "icon": "✅"
        },
        "CHANGES_INTRODUCED_GET_NEW": {
            "text": "Внесены изменения — получите новый документ",
            "color": "#dc3545",
            "icon": "⚠️"
        },
        "IN_WORK": {
            "text": "На доработке",
            "color": "#6c757d",
            "icon": "🔄"
        }
    }
    
    config = status_config.get(status, status_config["IN_WORK"])
    
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PTE QR - Статус документа</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                max-width: 500px;
                width: 100%;
                text-align: center;
            }}
            .status-icon {{
                font-size: 4rem;
                margin-bottom: 20px;
            }}
            .status-text {{
                font-size: 1.5rem;
                font-weight: bold;
                color: {config['color']};
                margin-bottom: 20px;
            }}
            .document-info {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 8px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                font-weight: 600;
                color: #6c757d;
            }}
            .info-value {{
                color: #212529;
            }}
            .action-button {{
                background: {config['color']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                margin: 10px;
                text-decoration: none;
                display: inline-block;
            }}
            .action-button:hover {{
                opacity: 0.9;
            }}
            .footer {{
                margin-top: 30px;
                color: #6c757d;
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status-icon">{config['icon']}</div>
            <div class="status-text">{config['text']}</div>
            
            <div class="document-info">
                <div class="info-row">
                    <span class="info-label">Документ:</span>
                    <span class="info-value">{doc_uid}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Ревизия:</span>
                    <span class="info-value">{revision}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Страница:</span>
                    <span class="info-value">{page}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Статус:</span>
                    <span class="info-value">{'Актуален' if is_actual else 'Устарел'}</span>
                </div>
            </div>
            
            <a href="#" class="action-button">Открыть документ</a>
            {f'<a href="#" class="action-button" style="background: #dc3545;">Перейти к актуальной ревизии</a>' if not is_actual else ''}
            
            <div class="footer">
                <p>PTE QR System v1.0</p>
                <p>Проверка актуальности документации</p>
            </div>
        </div>
    </body>
    </html>
    """


def generate_error_html(title: str, message: str) -> str:
    """
    Generate HTML for error display
    """
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PTE QR - Ошибка</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                max-width: 500px;
                width: 100%;
                text-align: center;
            }}
            .error-icon {{
                font-size: 4rem;
                margin-bottom: 20px;
            }}
            .error-title {{
                font-size: 1.5rem;
                font-weight: bold;
                color: #dc3545;
                margin-bottom: 20px;
            }}
            .error-message {{
                color: #6c757d;
                margin-bottom: 30px;
            }}
            .footer {{
                margin-top: 30px;
                color: #6c757d;
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="error-icon">❌</div>
            <div class="error-title">{title}</div>
            <div class="error-message">{message}</div>
            <div class="footer">
                <p>PTE QR System v1.0</p>
            </div>
        </div>
    </body>
    </html>
    """
