"""
QR Code generation endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
import structlog
import time

from app.services.qr_service import qr_service
from app.services.metrics_service import metrics_service

router = APIRouter()
logger = structlog.get_logger()


@router.post("/")
async def generate_qr_codes(
    request: dict,
    http_request: Request
):
    """
    Generate QR codes for document pages
    """
    start_time = time.time()
    
    try:
        # Validate request
        doc_uid = request.get("doc_uid")
        revision = request.get("revision")
        pages = request.get("pages", [])
        style = request.get("style", "BLACK")
        dpi = request.get("dpi", 300)
        mode = request.get("mode", "qr-only")
        
        if not doc_uid:
            raise HTTPException(status_code=422, detail="doc_uid is required")
        if not revision:
            raise HTTPException(status_code=422, detail="revision is required")
        if not pages:
            raise HTTPException(status_code=422, detail="pages is required")
        if not isinstance(pages, list):
            raise HTTPException(status_code=422, detail="pages must be a list")
        if any(page <= 0 for page in pages):
            raise HTTPException(status_code=422, detail="Page numbers must be greater than 0")
        if len(pages) > 1000:
            raise HTTPException(status_code=422, detail="Too many pages (max 1000)")
        
        # Generate QR codes
        qr_results = qr_service.generate_qr_codes(
            doc_uid=doc_uid,
            revision=revision,
            pages=pages,
            style=style,
            dpi=dpi
        )
        
        # Prepare response items
        items = []
        for qr_result in qr_results:
            # Add PNG format
            items.append({
                "page": qr_result["page"],
                "format": "PNG",
                "data_base64": qr_result["data"]["png"],
                "url": qr_result["url"]
            })
            
            # Add SVG format
            items.append({
                "page": qr_result["page"],
                "format": "SVG",
                "data_base64": qr_result["data"]["svg"],
                "url": qr_result["url"]
            })
        
        # Record metrics
        for page in pages:
            metrics_service.record_qr_code_generated(doc_uid, revision)
        
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/qrcodes/", 200, duration)
        
        logger.info(
            "QR codes generated",
            doc_uid=doc_uid,
            revision=revision,
            pages=len(pages),
            style=style,
            mode=mode,
            duration=duration
        )
        
        return {
            "doc_uid": doc_uid,
            "revision": revision,
            "mode": mode,
            "items": items
        }
        
    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/qrcodes/", 422, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/qrcodes/", 500, duration)
        
        logger.error(
            "Failed to generate QR codes",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/pdf-stamp")
async def generate_pdf_with_qr_codes(
    request: dict,
    http_request: Request
):
    """
    Generate PDF with embedded QR codes
    """
    start_time = time.time()
    
    try:
        from app.services.pdf_service import pdf_service
        
        # Validate request
        doc_uid = request.get("doc_uid")
        revision = request.get("revision")
        pages = request.get("pages", [])
        title = request.get("title", "")
        dpi = request.get("dpi", 300)
        
        if not doc_uid:
            raise HTTPException(status_code=422, detail="doc_uid is required")
        if not revision:
            raise HTTPException(status_code=422, detail="revision is required")
        if not pages:
            raise HTTPException(status_code=422, detail="pages is required")
        if not isinstance(pages, list):
            raise HTTPException(status_code=422, detail="pages must be a list")
        if any(page <= 0 for page in pages):
            raise HTTPException(status_code=422, detail="Page numbers must be greater than 0")
        
        # Generate PDF with QR codes
        pdf_data = pdf_service.create_pdf_with_qr_codes(
            doc_uid=doc_uid,
            revision=revision,
            pages=pages,
            title=title or f"Document {doc_uid}",
            dpi=dpi
        )
        
        # Convert to base64
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode()
        
        # Record metrics
        for page in pages:
            metrics_service.record_qr_code_generated(doc_uid, revision)
        
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/qrcodes/pdf-stamp", 200, duration)
        
        logger.info(
            "PDF with QR codes generated",
            doc_uid=doc_uid,
            revision=revision,
            pages=len(pages),
            duration=duration
        )
        
        return {
            "doc_uid": doc_uid,
            "revision": revision,
            "pages": pages,
            "pdf_data_base64": pdf_base64,
            "size_bytes": len(pdf_data)
        }
        
    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/qrcodes/pdf-stamp", 422, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/qrcodes/pdf-stamp", 500, duration)
        
        logger.error(
            "Failed to generate PDF with QR codes",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")