"""
QR Code generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import structlog

from app.core.database import get_db
from app.models.schemas import QRCodeRequest, QRCodeResponse, QRCodeItem, QRCodeFormatEnum
from app.models.document import Document
from app.services.qr_service import qr_service
from app.utils.pdf_stamper import PDFStamper

router = APIRouter()
logger = structlog.get_logger()


@router.post("/", response_model=QRCodeResponse)
async def generate_qr_codes(
    request: QRCodeRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Generate QR codes for document pages
    """
    try:
        # Validate document exists
        document = db.query(Document).filter(Document.doc_uid == request.doc_uid).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate QR codes using service
        qr_results = await qr_service.generate_qr_codes(
            doc_uid=request.doc_uid,
            revision=request.revision,
            pages=request.pages,
            style=request.style,
            dpi=request.dpi
        )
        
        # Prepare response items
        items = []
        for qr_result in qr_results:
            # Generate both PNG and SVG formats
            png_item = QRCodeItem(
                page=qr_result["page"],
                format=QRCodeFormatEnum.PNG,
                data_base64=qr_result["data"]["png"],
                url=qr_result["url"]
            )
            items.append(png_item)
            
            svg_item = QRCodeItem(
                page=qr_result["page"],
                format=QRCodeFormatEnum.SVG,
                data_base64=qr_result["data"]["svg"],
                url=qr_result["url"]
            )
            items.append(svg_item)
        
        # If PDF stamp mode requested, generate PDF
        if request.mode == "pdf-stamp":
            pdf_stamper = PDFStamper()
            # This would generate a PDF with embedded QR codes
            # For now, we'll just add a note that PDF generation is not implemented
            logger.info("PDF stamp mode requested but not implemented yet")
        
        logger.info(
            "QR codes generated",
            doc_uid=request.doc_uid,
            revision=request.revision,
            pages=len(request.pages),
            mode=request.mode
        )
        
        return QRCodeResponse(
            doc_uid=request.doc_uid,
            revision=request.revision,
            items=items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to generate QR codes",
            doc_uid=request.doc_uid,
            revision=request.revision,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
