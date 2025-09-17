"""
PDF processing endpoints
"""

from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
import structlog
import time

from app.core.database import get_db
from app.services.pdf_service import pdf_service
from app.services.metrics_service import metrics_service
from app.models.document import Document

router = APIRouter()
logger = structlog.get_logger()


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
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Read file content
        pdf_data = await file.read()

        # Validate PDF
        is_valid, error_msg = pdf_service.validate_pdf(pdf_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Parse pages parameter
        if pages:
            try:
                page_list = [int(p.strip()) for p in pages.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid pages format")
        else:
            # Get all pages from PDF
            pdf_info = pdf_service.extract_pdf_info(pdf_data)
            page_list = list(range(1, pdf_info["pages"] + 1))

        # Validate document exists if doc_uid provided
        if doc_uid:
            document = db.query(Document).filter(Document.doc_uid == doc_uid).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
        else:
            # Use default values
            doc_uid = "UNKNOWN"
            revision = "A"

        # Stamp PDF with QR codes
        stamped_pdf = pdf_service.stamp_pdf_with_qr(
            pdf_data=pdf_data,
            doc_uid=doc_uid,
            revision=revision or "A",
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
            "revision": revision or "A",
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
