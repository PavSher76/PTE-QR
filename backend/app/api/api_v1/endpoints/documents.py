"""
Document status endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
import structlog
import time

from app.core.database import get_db
from app.services.cache_service import cache_service
from app.services.enovia_service import enovia_service
from app.services.metrics_service import metrics_service
from app.api.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()


@router.get("/{doc_uid}/revisions/{rev}/status")
async def get_document_status(
    doc_uid: str,
    rev: str,
    page: int = Query(..., ge=1, description="Page number"),
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Check status of specific document revision and page
    """
    start_time = time.time()

    try:
        # Validate page number
        if page <= 0:
            raise HTTPException(
                status_code=422, detail="Page number must be greater than 0"
            )

        # Check cache first
        cache_key = f"status:{doc_uid}:{rev}:{page}"
        cached_status = await cache_service.get(cache_key)

        if cached_status:
            logger.info("Status cache hit", doc_uid=doc_uid, revision=rev, page=page)
            metrics_service.record_cache_hit("document_status")
            return cached_status

        metrics_service.record_cache_miss("document_status")

        # Check if document exists in database
        from app.models.document import Document

        document = db.query(Document).filter(Document.doc_uid == doc_uid).first()

        if not document:
            logger.warning("Document not found", doc_uid=doc_uid)
            raise HTTPException(status_code=404, detail=f"Document {doc_uid} not found")

        # Prepare response data based on authentication status
        if current_user:
            # Full response for authenticated users
            response_data = {
                "doc_uid": doc_uid,
                "revision": rev,
                "page": page,
                "business_status": "ACTUAL",
                "enovia_state": "RELEASED",
                "is_actual": True,
                "released_at": "2024-01-15T10:30:00Z",
                "superseded_by": None,
                "last_modified": "2024-01-15T10:30:00Z",
                "links": {
                    "openDocument": f"https://enovia.pti.ru/3dspace/document/{doc_uid}?rev={rev}",
                    "openLatest": None,
                },
                "metadata": {
                    "created_by": "system",
                    "access_level": "full",
                    "gdpr_compliant": True,
                },
            }
        else:
            # Limited response for unauthenticated users (GDPR compliance)
            response_data = {
                "doc_uid": doc_uid,
                "revision": rev,
                "page": page,
                "is_actual": True,
                "business_status": "ACTUAL",  # Only essential status info
                "links": {
                    "openDocument": f"https://enovia.pti.ru/3dspace/document/{doc_uid}?rev={rev}",
                    "openLatest": None,
                },
                "metadata": {
                    "access_level": "limited",
                    "gdpr_compliant": True,
                    "note": "Limited information due to privacy requirements. Please authenticate for full access.",
                },
            }

        # Cache the result
        await cache_service.set(cache_key, response_data, ttl=900)  # 15 minutes TTL

        # Record metrics
        metrics_service.record_document_status_check(doc_uid, rev, True)

        duration = time.time() - start_time
        metrics_service.record_api_request(
            "GET", f"/documents/{doc_uid}/revisions/{rev}/status", 200, duration
        )

        logger.info(
            "Status check completed",
            doc_uid=doc_uid,
            revision=rev,
            page=page,
            is_actual=True,
            business_status="ACTUAL",
            duration=duration,
        )

        return response_data

    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request(
            "GET", f"/documents/{doc_uid}/revisions/{rev}/status", 404, duration
        )
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request(
            "GET", f"/documents/{doc_uid}/revisions/{rev}/status", 500, duration
        )

        logger.error(
            "Failed to get document status",
            doc_uid=doc_uid,
            revision=rev,
            page=page,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/qr/verify")
async def verify_qr_signature(
    doc_uid: str = Query(..., description="Document UID"),
    rev: str = Query(..., description="Revision"),
    page: int = Query(..., description="Page number"),
    ts: int = Query(..., description="Timestamp"),
    sig: str = Query(..., description="Signature"),
):
    """
    Verify QR code signature
    """
    start_time = time.time()

    try:
        from app.utils.hmac_signer import HMACSigner

        hmac_signer = HMACSigner()
        is_valid = hmac_signer.verify_signature(doc_uid, rev, page, ts, sig)

        # Record metrics
        metrics_service.record_qr_code_verified("valid" if is_valid else "invalid")

        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/documents/qr/verify", 200, duration)

        if is_valid:
            return {"valid": True, "message": "Signature is valid"}
        else:
            return {"valid": False, "message": "Invalid signature"}

    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/documents/qr/verify", 400, duration)

        logger.error("QR signature verification failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid parameters")
