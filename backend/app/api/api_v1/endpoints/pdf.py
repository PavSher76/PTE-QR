"""
PDF processing endpoints
"""

import time

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.services.metrics_service import metrics_service
from app.services.pdf_service import pdf_service

router = APIRouter()
logger = structlog.get_logger()


def _validate_pdf_file(file: UploadFile) -> None:
    """Validate PDF file"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")


def _parse_pages_parameter(pages: str, pdf_data: bytes) -> list[int]:
    """Parse pages parameter and return page list"""
    if pages:
        try:
            return [int(p.strip()) for p in pages.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid pages format")
    else:
        # Get all pages from PDF
        pdf_info = pdf_service.extract_pdf_info(pdf_data)
        return list(range(1, pdf_info["pages"] + 1))


def _validate_document_exists(doc_uid: str, db: Session) -> None:
    """Validate document exists in database"""
    if doc_uid:
        document = db.query(Document).filter(Document.doc_uid == doc_uid).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")


@router.post("/stamp")
async def stamp_pdf_with_qr(
    file: UploadFile = File(...),
    doc_uid: str = None,
    revision: str = None,
    pages: str = None,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """
    Stamp existing PDF with QR codes
    """
    start_time = time.time()

    try:
        # Validate file
        _validate_pdf_file(file)

        # Read file content
        pdf_data = await file.read()

        # Validate PDF
        is_valid, error_msg = pdf_service.validate_pdf(pdf_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Parse pages parameter
        page_list = _parse_pages_parameter(pages, pdf_data)

        # Validate document exists if doc_uid provided
        _validate_document_exists(doc_uid, db)

        # Use default values if not provided
        if not doc_uid:
            doc_uid = "UNKNOWN"
        if not revision:
            revision = "A"

        # Stamp PDF with QR codes
        stamped_pdf = pdf_service.stamp_pdf_with_qr(
            pdf_data=pdf_data,
            doc_uid=doc_uid,
            revision=revision,
            pages=page_list,
        )

        # Convert to base64
        import base64

        pdf_base64 = base64.b64encode(stamped_pdf).decode()

        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/pdf/stamp", 200, duration)

        logger.info(
            "PDF stamped with QR codes",
            filename=file.filename,
            doc_uid=doc_uid,
            revision=revision,
            pages=len(page_list),
            duration=duration,
        )

        return {
            "filename": file.filename,
            "doc_uid": doc_uid,
            "revision": revision,
            "pages": page_list,
            "pdf_data_base64": pdf_base64,
            "size_bytes": len(stamped_pdf),
        }

    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/pdf/stamp", 400, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/pdf/stamp", 500, duration)

        logger.error(
            "Failed to stamp PDF with QR codes",
            filename=file.filename if file else "unknown",
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/info")
async def get_pdf_info(file: UploadFile = File(...), request: Request = None):
    """
    Get PDF file information
    """
    start_time = time.time()

    try:
        # Validate file
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Read file content
        pdf_data = await file.read()

        # Validate PDF
        is_valid, error_msg = pdf_service.validate_pdf(pdf_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Extract PDF info
        pdf_info = pdf_service.extract_pdf_info(pdf_data)

        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/pdf/info", 200, duration)

        logger.info(
            "PDF info extracted",
            filename=file.filename,
            pages=pdf_info["pages"],
            duration=duration,
        )

        return {
            "filename": file.filename,
            "size_bytes": len(pdf_data),
            "info": pdf_info,
        }

    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/pdf/info", 400, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/pdf/info", 500, duration)

        logger.error(
            "Failed to get PDF info",
            filename=file.filename if file else "unknown",
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")
